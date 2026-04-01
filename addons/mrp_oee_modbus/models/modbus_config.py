import logging
import threading

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Thread registry: {config_id: (threading.Event, threading.Thread)}
_polling_threads = {}


class MrpModbusConfig(models.Model):
    _name = 'mrp.modbus.config'
    _description = 'Modbus TCP Configuration'
    _order = 'name'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    name = fields.Char(string='Profile Name', required=True,
                       help='e.g. "Mesin Induksi #1"')
    host = fields.Char(string='Host / IP Address', required=True, default='192.168.1.1',
                       help='IP address of Modbus TCP server (PLC/HMI)')
    port = fields.Integer(string='Port', default=502)
    slave_id = fields.Integer(string='Slave ID / Unit ID', default=1)
    timeout = fields.Float(string='Timeout (s)', default=3.0)
    retries = fields.Integer(string='Retries', default=3)
    reconnect_delay = fields.Float(string='Reconnect Delay (s)', default=0.1)
    polling_interval = fields.Integer(string='Polling Interval (s)', default=5,
                                      help='How often to read registers (seconds)')
    is_active = fields.Boolean(string='Active', default=True)

    # Real-time operational state (drives statusbar + button visibility)
    polling_state = fields.Selection([
        ('stopped',    '⏹ Stopped'),
        ('testing',    '🔌 Testing Connection...'),
        ('connecting', '⏳ Connecting...'),
        ('polling',    '🔄 Polling Active'),
        ('error',      '🔴 Error'),
    ], string='Operational State', default='stopped', readonly=True,
       help='Real-time state of the Modbus connection/polling')

    # Legacy connection status kept for list view decoration
    connection_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
    ], string='Connection Status', default='disconnected', readonly=True)

    last_connected = fields.Datetime(string='Last Connected', readonly=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center',
                                    help='Linked work center for OEE sync')
    register_map_ids = fields.One2many('mrp.modbus.register.map', 'config_id',
                                       string='Register Map')
    log_ids = fields.One2many('mrp.modbus.log', 'config_id', string='Activity Log')
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Profile name must be unique.'),
    ]

    # -------------------------------------------------------------------------
    # Logging helper
    # -------------------------------------------------------------------------

    def _log(self, message, level='info'):
        """Write a compact log entry to this config's activity log."""
        self.ensure_one()
        self.env['mrp.modbus.log'].sudo().create({
            'config_id': self.id,
            'level': level,
            'message': message,
        })
        log_fn = getattr(_logger, level if level != 'warning' else 'warning', _logger.info)
        log_fn("[%s] %s", self.name, message)

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _get_client(self):
        """Return a configured ModbusOEEClient instance (not yet connected)."""
        self.ensure_one()
        from odoo.addons.mrp_oee_modbus.services.modbus_client import ModbusOEEClient
        return ModbusOEEClient(self)

    # -------------------------------------------------------------------------
    # Action: Test Connection
    # -------------------------------------------------------------------------

    def action_test_connection(self):
        """Set state to Testing, open wizard."""
        self.ensure_one()
        self.write({'polling_state': 'testing'})
        self._log("Test connection initiated → %s:%s" % (self.host, self.port))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Test Modbus Connection'),
            'res_model': 'mrp.modbus.test.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_config_id': self.id,
            },
        }

    def action_reset_state(self):
        """Manually reset polling_state back to stopped (after test wizard closes)."""
        self.ensure_one()
        if self.polling_state == 'testing':
            self.write({'polling_state': 'stopped'})
        return True

    # -------------------------------------------------------------------------
    # Action: Start / Stop Polling
    # -------------------------------------------------------------------------

    def _send_notification(self, title, message, notif_type='success'):
        """Send a bus notification to the current user (allows returning False for form reload)."""
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,
            'simple_notification',
            {'title': title, 'message': message, 'type': notif_type, 'sticky': False},
        )

    def action_start_polling(self):
        """Test connection first, then start a background polling thread."""
        self.ensure_one()
        config_id = self.id

        # Check if a polling thread is truly alive
        if config_id in _polling_threads:
            stop_event, thread = _polling_threads[config_id]
            if thread.is_alive() and not stop_event.is_set():
                # Thread is alive — auto-stop it so user can restart
                _logger.info("Auto-stopping existing polling thread for config %s before restart", config_id)
                stop_event.set()
                thread.join(timeout=5)
            # Clean up stale entry
            if config_id in _polling_threads:
                del _polling_threads[config_id]
            _logger.info("Cleaned up polling thread for config %s", config_id)

        host = self.host
        port = self.port
        interval = self.polling_interval
        db_name = self._cr.dbname

        # --- Phase 1: Set "connecting" and verify actual Modbus connection ---
        self.write({'polling_state': 'connecting', 'connection_status': 'disconnected'})
        self._log("⏳ Connecting to %s:%s …" % (host, port))

        client = self._get_client()
        try:
            connected = client.connect()
        except Exception as e:
            connected = False
            _logger.error("Connection probe failed: %s", e)
        finally:
            try:
                client.disconnect()
            except Exception:
                pass

        if not connected:
            self.write({'polling_state': 'error', 'connection_status': 'error'})
            self._log("🔴 Connection FAILED to %s:%s" % (host, port), level='error')
            self._send_notification(
                _("🔴 Connection Failed"),
                _("Cannot reach %s:%s — check host/port and try again.") % (host, port),
                'danger',
            )
            return False  # reload form to show error state

        # --- Phase 2: Connection OK → start polling thread ---
        stop_event = threading.Event()

        self.write({
            'polling_state': 'polling',
            'connection_status': 'connected',
            'last_connected': fields.Datetime.now(),
        })
        self._log("▶ Polling STARTED — %s:%s every %ds" % (host, port, interval))

        def poll_loop():
            import odoo
            cycle = 0
            while not stop_event.is_set():
                cycle += 1
                try:
                    registry = odoo.registry(db_name)
                    with registry.cursor() as cr:
                        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                        config = env['mrp.modbus.config'].browse(config_id)
                        if not config.exists():
                            _logger.warning("Poll cycle %d: config %s no longer exists, stopping", cycle, config_id)
                            break
                        if not config.is_active:
                            _logger.info("Poll cycle %d: config '%s' is_active=False, skipping", cycle, config.name)
                        elif not config.workcenter_id:
                            _logger.warning("Poll cycle %d: config '%s' has no Work Center linked, skipping", cycle, config.name)
                        else:
                            _logger.info("Poll cycle %d: syncing OEE for '%s' → WC '%s'", cycle, config.name, config.workcenter_id.name)
                            config._do_oee_sync()
                            cr.commit()
                            _logger.info("Poll cycle %d: sync completed OK", cycle)
                except Exception as e:
                    _logger.error("Poll cycle %d error for config %s: %s", cycle, config_id, e)
                    try:
                        registry = odoo.registry(db_name)
                        with registry.cursor() as cr:
                            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                            config = env['mrp.modbus.config'].browse(config_id)
                            if config.exists():
                                config.write({'polling_state': 'error',
                                              'connection_status': 'error'})
                                config._log("Polling error: %s" % e, level='error')
                                cr.commit()
                    except Exception:
                        pass
                stop_event.wait(timeout=interval)

        t = threading.Thread(target=poll_loop, daemon=True, name=f"modbus_poll_{config_id}")
        t.start()
        _polling_threads[config_id] = (stop_event, t)

        self._send_notification(
            _("▶ Polling Started"),
            _("'%s' polling every %ds — Status: 🔄 Polling Active") % (self.name, interval),
            'success',
        )
        return False  # reload form to show updated state

    def action_stop_polling(self):
        """Signal the background polling thread to stop."""
        self.ensure_one()
        config_id = self.id
        entry = _polling_threads.pop(config_id, None)
        if entry:
            stop_event, thread = entry
            stop_event.set()
            self.write({'polling_state': 'stopped', 'connection_status': 'disconnected'})
            self._log("⏹ Polling STOPPED")
        else:
            self.write({'polling_state': 'stopped'})
            self._log("Stop requested — no active polling thread", level='warning')
        self._send_notification(
            _("⏹ Polling Stopped"),
            _("'%s' polling stopped.") % self.name,
            'warning',
        )
        return False  # reload form to show updated state

    def action_clear_logs(self):
        """Clear all log entries for this config."""
        self.ensure_one()
        self.log_ids.sudo().unlink()
        return True

    # -------------------------------------------------------------------------
    # OEE Sync (called from poll loop — uses config directly, no back-ref)
    # -------------------------------------------------------------------------

    def _do_oee_sync(self):
        """
        Read sensor inputs from Modbus, compute OEE fresh from work order
        data, and write computed OEE values back to HMI registers.

        OEE is computed directly here (not read from stored computed fields)
        to avoid stale cached/stored values in background thread contexts.
        """
        self.ensure_one()
        wc = self.workcenter_id
        if not wc:
            _logger.warning("_do_oee_sync: config '%s' has no Work Center", self.name)
            return

        client = self._get_client()
        connected = False
        try:
            connected = client.connect()
            if not connected:
                self.write({'connection_status': 'error'})
                _logger.warning("_do_oee_sync: cannot connect for '%s'", self.name)
                return

            self.write({
                'connection_status': 'connected',
                'last_connected': fields.Datetime.now(),
            })

            # Step 1: Read sensor data from Modbus (for logging / future use)
            data = client.read_all_oee_inputs(self.register_map_ids)
            _logger.info("Modbus sensor data for '%s': %s", self.name, data)

            # Step 2: Compute OEE fresh from work order / productivity data
            # (stored computed fields can be stale in background threads)
            availability_pct, performance_pct, quality_pct, oee_pct = \
                self._compute_oee_fresh(wc)

            _logger.info(
                "OEE computed for WC '%s': A=%.1f%% P=%.1f%% Q=%.1f%% OEE=%.1f%%",
                wc.name, availability_pct, performance_pct, quality_pct, oee_pct,
            )

            # Step 3: Write OEE values to HMI via Modbus
            oee_results = {
                'oee_availability': availability_pct,
                'oee_performance':  performance_pct,
                'oee_quality':      quality_pct,
                'oee_overall':      oee_pct,
            }
            write_regs = self.register_map_ids.filtered(lambda r: r.direction in ('write', 'read_write'))
            _logger.info(
                "Writing OEE to %d registers: %s",
                len(write_regs), oee_results,
            )
            client.write_all_oee_outputs(self.register_map_ids, oee_results)

        except Exception as e:
            _logger.exception("_do_oee_sync failed for '%s'", self.name)
            self.write({'connection_status': 'error'})
            raise
        finally:
            if connected:
                client.disconnect()

    def _compute_oee_fresh(self, wc):
        """
        Compute OEE directly from productivity records and work orders.
        Returns (availability_pct, performance_pct, quality_pct, oee_pct)
        all as percentages (e.g. 80.4 for 80.4%).
        """
        productivities = self.env['mrp.workcenter.productivity'].sudo().search([
            ('workcenter_id', '=', wc.id),
            ('date_end', '!=', False),
        ])

        if not productivities:
            _logger.info("_compute_oee_fresh: no productivity records for WC '%s'", wc.name)
            return (0.0, 0.0, 0.0, 0.0)

        planned_time = 0.0
        operating_time = 0.0
        for prod in productivities:
            duration = (prod.date_end - prod.date_start).total_seconds() / 3600.0
            planned_time += duration
            if prod.loss_type == 'productive':
                operating_time += duration

        work_orders = self.env['mrp.workorder'].sudo().search([
            ('workcenter_id', '=', wc.id),
        ])
        total_good = sum(work_orders.mapped('good_count'))
        total_reject = sum(work_orders.mapped('reject_count'))
        total_count = total_good + total_reject

        # Availability
        availability = operating_time / planned_time if planned_time > 0 else 0.0

        # Performance
        cycle_minutes = 1.0
        try:
            if hasattr(wc, 'time_cycle_manual') and wc.time_cycle_manual > 0:
                cycle_minutes = wc.time_cycle_manual
            elif hasattr(wc, 'time_cycle') and wc.time_cycle > 0:
                cycle_minutes = wc.time_cycle
        except Exception:
            pass
        ideal_cycle_time_hours = cycle_minutes / 60.0
        if operating_time > 0 and ideal_cycle_time_hours > 0 and total_count > 0:
            performance = min((ideal_cycle_time_hours * total_count) / operating_time, 1.0)
        elif operating_time > 0 and total_count > 0:
            performance = 1.0
        else:
            performance = 0.0

        # Quality
        quality = total_good / total_count if total_count > 0 else 0.0

        # OEE
        oee_val = availability * performance * quality * 100.0

        availability_pct = round(availability * 100.0, 2)
        performance_pct = round(performance * 100.0, 2)
        quality_pct = round(quality * 100.0, 2)
        oee_pct = round(oee_val, 2)

        _logger.debug(
            "OEE fresh: planned=%.2fh, operating=%.2fh, good=%d, reject=%d, total=%d",
            planned_time, operating_time, total_good, total_reject, total_count,
        )

        return (availability_pct, performance_pct, quality_pct, oee_pct)

    # -------------------------------------------------------------------------
    # Cron: Poll all active configs
    # -------------------------------------------------------------------------

    @api.model
    def _cron_poll_all_active_configs(self):
        """Called by ir.cron every minute. Triggers sync on all active configs."""
        active_configs = self.search([('is_active', '=', True), ('workcenter_id', '!=', False)])
        for config in active_configs:
            try:
                config._do_oee_sync()
            except Exception as e:
                _logger.error("Cron poll error for config '%s': %s", config.name, e)
                config._log("Cron sync error: %s" % e, level='error')
                config.write({'polling_state': 'error', 'connection_status': 'error'})

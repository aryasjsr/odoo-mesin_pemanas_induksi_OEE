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
    reason_map_ids = fields.One2many('mrp.modbus.reason.map', 'config_id', string='Reason Code Map')
    notes = fields.Text(string='Notes')

    # State machine fields (persisted across poll cycles)
    last_m_status = fields.Integer(string='Last M_STATUS', default=-1, readonly=True,
                                   help='-1=unknown, 0=Stop, 1=Running')
    last_good_count = fields.Integer(string='Last GOOD_COUNT', default=0, readonly=True)
    last_reject_count = fields.Integer(string='Last REJECT_COUNT', default=0, readonly=True)
    active_productivity_id = fields.Many2one(
        'mrp.workcenter.productivity', string='Active Productivity Record',
        readonly=True, ondelete='set null',
        help='Currently open (no date_end) productivity record created by polling')

    # HMI real-time display fields (updated each poll cycle)
    hmi_m_status = fields.Integer(string='HMI Machine Status', default=0, readonly=True)
    hmi_good_count = fields.Integer(string='HMI Good Count', default=0, readonly=True)
    hmi_reject_count = fields.Integer(string='HMI Reject Count', default=0, readonly=True)
    hmi_wo_id = fields.Integer(string='HMI Active WO ID', default=0, readonly=True)

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
    # OEE Sync (called from poll loop — full state machine + delta counter)
    # -------------------------------------------------------------------------

    REASON_CODE_MAP = {
        0: 'None',
        1: 'Setup',
        2: 'Equipment Failure',
        3: 'Material Shortage',
        4: 'Process Defect',
    }

    def _get_loss_for_reason(self, reason_code):
        """Map REASON_CODE integer to mrp.workcenter.productivity.loss record.

        First checks configurable reason_map_ids on this config.
        Falls back to searching by name, then any availability loss.
        """
        # 1. Try configurable mapping first
        mapping = self.reason_map_ids.filtered(lambda r: r.reason_code == reason_code)
        if mapping and mapping[0].loss_id:
            return mapping[0].loss_id

        # 2. Fallback: search by conventional name
        Loss = self.env['mrp.workcenter.productivity.loss'].sudo()
        name_map = {
            1: 'Setup',
            2: 'Equipment Failure',
            3: 'Material Shortage',
            4: 'Process Defect',
        }
        name = name_map.get(reason_code)
        if name:
            loss = Loss.search([('name', '=', name)], limit=1)
            if loss:
                return loss

        # 3. Last resort: any availability loss
        loss = Loss.search([('loss_type', '=', 'availability')], limit=1)
        if not loss:
            loss = Loss.search([], limit=1)
        return loss

    def _get_productive_loss(self):
        """Get the 'Productive' loss record (loss_type='productive')."""
        Loss = self.env['mrp.workcenter.productivity.loss'].sudo()
        loss = Loss.search([('loss_type', '=', 'productive')], limit=1)
        if not loss:
            loss = Loss.search([], limit=1)
        return loss

    def _do_oee_sync(self):
        """
        Full poll cycle: state machine + delta counter + MO list + OEE write.

        1. Read M_STATUS, GOOD_COUNT, REJECT_COUNT, REASON_CODE, WO_ID from HMI
        2. Detect M_STATUS transitions → create/close productivity records
        3. Compute delta counter → update WO good/reject counts
        4. Compute OEE from productivity records
        5. Write MO list to register 40006–40025
        6. Write OEE to register 40030–40033
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

            # ---- Step 1: Read all input registers from HMI ----
            data = client.read_all_oee_inputs(self.register_map_ids)
            _logger.info("Modbus READ for '%s': %s", self.name, data)

            m_status = int(data.get('m_status', 0) or 0)
            good_count = int(data.get('good_count', 0) or 0)
            reject_count = int(data.get('reject_count', 0) or 0)
            reason_code = int(data.get('reason_code', 0) or 0)
            wo_id = int(data.get('wo_id', 0) or 0)

            # Update HMI display fields
            self.write({
                'hmi_m_status': m_status,
                'hmi_good_count': good_count,
                'hmi_reject_count': reject_count,
                'hmi_wo_id': wo_id,
            })

            now = fields.Datetime.now()
            last_status = self.last_m_status

            # ---- Step 2: Find active WO (from wo_id sent by HMI) ----
            active_wo = None
            if wo_id:
                active_wo = self.env['mrp.workorder'].sudo().search([
                    ('production_id.id', '=', wo_id),
                    ('workcenter_id', '=', wc.id),
                ], limit=1)
                if not active_wo:
                    # Try matching production_id directly (mo ID as integer)
                    mo = self.env['mrp.production'].sudo().browse(wo_id)
                    if mo.exists():
                        active_wo = self.env['mrp.workorder'].sudo().search([
                            ('production_id', '=', mo.id),
                            ('workcenter_id', '=', wc.id),
                        ], limit=1)

            # ---- Step 3: State machine — M_STATUS transitions ----
            # Transitions drive both productivity records AND shopfloor WO card state
            if last_status != -1 and last_status != m_status:
                if last_status == 0 and m_status == 1:
                    # STOP → RUNNING: Start or Resume WO → shopfloor card updates automatically
                    _logger.info("[%s] M_STATUS 0→1 START/RESUME", self.name)
                    if active_wo and active_wo.state not in ('done', 'cancel'):
                        if active_wo.machine_state == 'paused':
                            active_wo.sudo().action_machine_resume()
                        else:
                            active_wo.sudo().action_machine_start()
                        self.write({'active_productivity_id': active_wo.current_productivity_id.id})
                    else:
                        # Fallback: no WO linked — workcenter-level productivity only
                        self._close_active_productivity(now)
                        prod = self._create_productivity(wc, wo_id, self._get_productive_loss(), now,
                                                         'Production (Modbus)')
                        self.write({'active_productivity_id': prod.id})

                elif last_status == 1 and m_status == 0:
                    # RUNNING → STOP: Block WO with reason → shopfloor card shows "Blocked"
                    _logger.info("[%s] M_STATUS 1→0 STOP reason=%d", self.name, reason_code)
                    loss = self._get_loss_for_reason(reason_code)
                    if active_wo and active_wo.state not in ('done', 'cancel'):
                        active_wo.sudo().action_machine_block(loss_id=loss.id)
                        self.write({'active_productivity_id': active_wo.current_productivity_id.id})
                    else:
                        # Fallback: no WO linked
                        self._close_active_productivity(now)
                        reason_name = self.REASON_CODE_MAP.get(reason_code, 'Unknown')
                        prod = self._create_productivity(wc, wo_id, loss, now,
                                                         'Downtime (%s) (Modbus)' % reason_name)
                        self.write({'active_productivity_id': prod.id})

            elif last_status == -1:
                # First poll — initialize state
                if m_status == 1:
                    _logger.info("[%s] First poll: machine running", self.name)
                    if active_wo and active_wo.state not in ('done', 'cancel') \
                            and active_wo.machine_state != 'running':
                        active_wo.sudo().action_machine_start()
                        self.write({'active_productivity_id': active_wo.current_productivity_id.id})
                    elif not active_wo:
                        prod = self._create_productivity(wc, wo_id, self._get_productive_loss(), now,
                                                         'Production (Modbus init)')
                        self.write({'active_productivity_id': prod.id})

            # ---- Step 4: Delta counter ----
            if active_wo and self.last_good_count >= 0 and self.last_reject_count >= 0:
                delta_good = good_count - self.last_good_count
                delta_reject = reject_count - self.last_reject_count

                # Sanity: ignore negative deltas (counter reset)
                if delta_good < 0:
                    _logger.info("[%s] GOOD_COUNT counter reset detected (%d → %d)", self.name, self.last_good_count, good_count)
                    delta_good = 0
                if delta_reject < 0:
                    _logger.info("[%s] REJECT_COUNT counter reset detected (%d → %d)", self.name, self.last_reject_count, reject_count)
                    delta_reject = 0

                if delta_good > 0:
                    new_good = active_wo.good_count + delta_good
                    active_wo.sudo().write({
                        'good_count': new_good,
                        'qty_produced': new_good,
                    })
                    _logger.info("[%s] WO %s good_count += %d → %d", self.name, active_wo.display_name, delta_good, new_good)

                if delta_reject > 0:
                    new_reject = active_wo.reject_count + delta_reject
                    active_wo.sudo().write({'reject_count': new_reject})
                    _logger.info("[%s] WO %s reject_count += %d → %d", self.name, active_wo.display_name, delta_reject, new_reject)

            # Save last known counters
            self.write({
                'last_m_status': m_status,
                'last_good_count': good_count,
                'last_reject_count': reject_count,
            })

            # ---- Step 4: Compute OEE from productivity records ----
            availability_pct, performance_pct, quality_pct, oee_pct = \
                self._compute_oee_fresh(wc)

            _logger.info(
                "OEE for WC '%s': A=%.1f%% P=%.1f%% Q=%.1f%% OEE=%.1f%%",
                wc.name, availability_pct, performance_pct, quality_pct, oee_pct,
            )

            # ---- Step 5: Write MO list to register 40006–40025 ----
            self._write_mo_list(client, wc)

            # ---- Step 6: Close WO if HMI set FINISHED_STATUS = 1 ----
            finished_status = int(data.get('finished_status', 0) or 0)
            if finished_status == 1 and active_wo and active_wo.state not in ('done', 'cancel'):
                _logger.info("[%s] FINISHED_STATUS=1 received → closing WO %s", self.name, active_wo.display_name)
                active_wo.sudo().action_close_production()

            # ---- Step 7: Write OEE to register 40030–40033 ----
            oee_results = {
                'oee_availability': availability_pct,
                'oee_performance':  performance_pct,
                'oee_quality':      quality_pct,
                'oee_overall':      oee_pct,
            }
            client.write_all_oee_outputs(self.register_map_ids, oee_results)

        except Exception as e:
            _logger.exception("_do_oee_sync failed for '%s'", self.name)
            self.write({'connection_status': 'error'})
            raise
        finally:
            if connected:
                client.disconnect()

    def _close_active_productivity(self, now):
        """Close the currently active productivity record if it exists."""
        if self.active_productivity_id and not self.active_productivity_id.date_end:
            self.active_productivity_id.sudo().write({'date_end': now})
            _logger.info("[%s] Closed productivity record #%d", self.name, self.active_productivity_id.id)

    def _create_productivity(self, wc, wo_id, loss, now, description):
        """Create a new mrp.workcenter.productivity record."""
        Prod = self.env['mrp.workcenter.productivity'].sudo()
        vals = {
            'workcenter_id': wc.id,
            'date_start': now,
            'loss_id': loss.id if loss else False,
            'description': description,
        }
        # Link to workorder if we can find one
        if wo_id:
            wo = self.env['mrp.workorder'].sudo().search([
                ('production_id.id', '=', wo_id),
                ('workcenter_id', '=', wc.id),
            ], limit=1)
            if wo:
                vals['workorder_id'] = wo.id
        prod = Prod.create(vals)
        _logger.info("[%s] Created productivity #%d (%s)", self.name, prod.id, description)
        return prod

    def _write_mo_list(self, client, wc):
        """Write active MO list + operator codes to register slots 40006–40025."""
        # Find active MOs via workorders assigned to this work center
        active_wos = self.env['mrp.workorder'].sudo().search([
            ('workcenter_id', '=', wc.id),
            ('state', 'not in', ['done', 'cancel']),
        ], limit=10, order='id asc')
        mos = active_wos.mapped('production_id')

        # Build slot data
        slot_data = {}
        for i in range(10):
            if i < len(mos):
                mo = mos[i]
                mo_id = mo.id
                # Get operator code from responsible user
                op_code = 0
                if mo.user_id and hasattr(mo.user_id, 'operator_code') and mo.user_id.operator_code:
                    try:
                        op_code = int(mo.user_id.operator_code)
                    except (ValueError, TypeError):
                        op_code = 0
                slot_data['mo_slot_%d_id' % i] = mo_id
                slot_data['mo_slot_%d_op' % i] = op_code
            else:
                slot_data['mo_slot_%d_id' % i] = 0
                slot_data['mo_slot_%d_op' % i] = 0

        # Write via register map
        for reg in self.register_map_ids:
            if reg.variable_key in slot_data:
                client.write_register(
                    reg.register_address,
                    slot_data[reg.variable_key],
                    reg.data_type,
                    reg.scale_factor,
                )

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

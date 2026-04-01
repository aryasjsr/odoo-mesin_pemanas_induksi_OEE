import logging
from odoo import models, fields, _, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MrpWorkcenterModbus(models.Model):
    _inherit = 'mrp.workcenter'

    modbus_config_id = fields.Many2one(
        'mrp.modbus.config',
        string='Modbus Configuration',
        help='Link this Work Center to a Modbus TCP config for OEE data sync',
    )

    def action_sync_oee_from_modbus(self):
        """
        Read OEE input data from Modbus, compute OEE metrics, write back to HMI.

        Steps:
          1. Get modbus_config_id and instantiate ModbusOEEClient
          2. Connect
          3. Read all input registers → dict of variable values
          4. Compute OEE (Availability, Performance, Quality, Overall)
          5. Write OEE results back to HMI output registers
          6. Update mrp.workcenter.productivity records in Odoo
          7. Disconnect
        """
        self.ensure_one()
        config = self.modbus_config_id
        if not config:
            raise UserError(_("No Modbus configuration linked to work center '%s'.") % self.name)

        client = config._get_client()
        connected = False
        try:
            connected = client.connect()
            if not connected:
                config.write({'connection_status': 'error'})
                _logger.warning("Could not connect to Modbus for config '%s'", config.name)
                return

            config.write({
                'connection_status': 'connected',
                'last_connected': fields.Datetime.now(),
            })

            # --- Step 3: Read all input registers ---
            data = client.read_all_oee_inputs(config.register_map_ids)
            _logger.info("Modbus data read for WC '%s': %s", self.name, data)

            # --- Step 4: Compute OEE ---
            planned_time = float(data.get('planned_time', 0) or 0)
            run_time     = float(data.get('run_time', 0) or 0)
            produced_qty = float(data.get('produced_qty', 0) or 0)
            ideal_qty    = float(data.get('ideal_qty', 0) or 0)
            defect_qty   = float(data.get('defect_qty', 0) or 0)

            availability = run_time / planned_time if planned_time > 0 else 0.0
            performance  = produced_qty / ideal_qty if ideal_qty > 0 else 0.0
            quality      = (produced_qty - defect_qty) / produced_qty if produced_qty > 0 else 0.0
            oee_overall  = availability * performance * quality * 100.0

            # Clamp to 0–100%
            availability_pct = round(min(availability * 100.0, 100.0), 2)
            performance_pct  = round(min(performance * 100.0, 100.0), 2)
            quality_pct      = round(min(quality * 100.0, 100.0), 2)
            oee_pct          = round(min(oee_overall, 100.0), 2)

            _logger.info(
                "OEE computed for '%s': A=%.1f%% P=%.1f%% Q=%.1f%% OEE=%.1f%%",
                self.name, availability_pct, performance_pct, quality_pct, oee_pct,
            )

            # --- Step 5: Write OEE results back to HMI ---
            oee_results = {
                'oee_availability': availability_pct,
                'oee_performance':  performance_pct,
                'oee_quality':      quality_pct,
                'oee_overall':      oee_pct,
            }
            write_regs = config.register_map_ids.filtered(lambda r: r.direction in ('write', 'read_write'))
            _logger.info(
                "Writing OEE to %d output registers: %s",
                len(write_regs), oee_results,
            )
            client.write_all_oee_outputs(config.register_map_ids, oee_results)

            # --- Step 6: Update Odoo OEE fields on the workcenter ---
            self.write({
                'oee_availability': availability_pct,
                'oee_performance':  performance_pct,
                'oee_quality':      quality_pct,
                'oee_total':        oee_pct,
                'oee':              oee_pct,
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('OEE Synced'),
                    'message': _(
                        "A: %.1f%% | P: %.1f%% | Q: %.1f%% | OEE: %.1f%%"
                    ) % (availability_pct, performance_pct, quality_pct, oee_pct),
                    'type': 'success',
                }
            }

        except Exception as e:
            _logger.exception("action_sync_oee_from_modbus failed for '%s'", self.name)
            config.write({'connection_status': 'error'})
            raise UserError(_("Modbus sync failed: %s") % e)
        finally:
            if connected:
                client.disconnect()

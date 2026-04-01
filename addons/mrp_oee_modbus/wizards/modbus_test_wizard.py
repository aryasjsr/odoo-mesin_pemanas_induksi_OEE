import logging
from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class MrpModbusTestWizard(models.TransientModel):
    _name = 'mrp.modbus.test.wizard'
    _description = 'Modbus Connection Test Wizard'

    config_id = fields.Many2one('mrp.modbus.config', string='Configuration',
                                required=True, readonly=True)
    test_result = fields.Text(string='Test Result', readonly=True)
    connection_ok = fields.Boolean(string='Connection OK', readonly=True, default=False)

    def action_run_test(self):
        """Test connection and read all configured registers. Show results."""
        self.ensure_one()
        config = self.config_id
        client = config._get_client()

        lines = []
        lines.append(f"=== Modbus Connection Test: {config.name} ===")
        lines.append(f"Target: {config.host}:{config.port} | Slave ID: {config.slave_id}")
        lines.append("")

        connected = False
        ok = False
        try:
            connected = client.connect()
            if not connected:
                lines.append("❌ CONNECTION FAILED")
                lines.append(f"   Could not reach {config.host}:{config.port}")
                config.write({'polling_state': 'error', 'connection_status': 'error'})
                config._log("Test FAILED — could not connect to %s:%s" % (config.host, config.port), level='error')
            else:
                lines.append("✅ CONNECTION SUCCESSFUL")
                config.write({
                    'polling_state': 'stopped',
                    'connection_status': 'connected',
                    'last_connected': fields.Datetime.now(),
                })
                config._log("Test OK — connected to %s:%s" % (config.host, config.port))
                ok = True
                lines.append("")
                lines.append("=== Register Read Test ===")

                for reg in config.register_map_ids:
                    if reg.direction not in ('read', 'read_write'):
                        lines.append(f"  [{reg.variable_key}] @ addr {reg.register_address} → SKIP (write-only)")
                        continue
                    value, error_detail = client.read_register_with_detail(
                        reg.register_address,
                        reg.register_type,
                        reg.data_type,
                        reg.scale_factor,
                    )
                    if value is None:
                        lines.append(f"  ❌ [{reg.variable_key}] addr {reg.register_address} → {error_detail}")
                        config._log("Register read error: %s @ addr %s — %s" % (reg.variable_key, reg.register_address, error_detail), level='warning')
                    else:
                        lines.append(f"  ✅ [{reg.variable_key}] addr {reg.register_address} = {value}")

        except Exception as e:
            lines.append(f"❌ EXCEPTION: {e}")
            config.write({'polling_state': 'error', 'connection_status': 'error'})
            config._log("Test exception: %s" % e, level='error')
        finally:
            if connected:
                client.disconnect()

        self.write({
            'test_result': '\n'.join(lines),
            'connection_ok': ok,
        })

        # Reload same wizard to show results
        return {
            'type': 'ir.actions.act_window',
            'name': _('Test Modbus Connection'),
            'res_model': 'mrp.modbus.test.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

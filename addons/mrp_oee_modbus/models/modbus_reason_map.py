from odoo import models, fields


class MrpModbusReasonMap(models.Model):
    _name = 'mrp.modbus.reason.map'
    _description = 'Modbus Reason Code → Loss Mapping'
    _order = 'reason_code'

    config_id = fields.Many2one(
        'mrp.modbus.config', string='Modbus Config',
        required=True, ondelete='cascade',
    )
    reason_code = fields.Integer(
        string='Nomor Code',
        required=True,
        help='Integer value from REASON_CODE register (e.g. 1, 2, 3, 4)',
    )
    loss_id = fields.Many2one(
        'mrp.workcenter.productivity.loss',
        string='Productivity Loss',
        required=True,
        help='Loss reason to use when this REASON_CODE is received from HMI',
    )
    description = fields.Char(
        string='Description',
        help='Human-readable label for this reason code',
    )

    _sql_constraints = [
        ('unique_code_per_config', 'unique(config_id, reason_code)',
         'Reason code must be unique within a config profile.'),
    ]

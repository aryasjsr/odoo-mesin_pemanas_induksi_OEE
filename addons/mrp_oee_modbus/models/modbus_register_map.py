import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

VARIABLE_KEY_SELECTION = [
    ('planned_time',     'Planned Time (min)'),
    ('run_time',         'Run Time (min)'),
    ('downtime',         'Downtime (min)'),
    ('produced_qty',     'Produced Quantity'),
    ('ideal_qty',        'Ideal / Target Quantity'),
    ('defect_qty',       'Defect / Reject Quantity'),
    ('machine_status',   'Machine Status (ON/OFF)'),
    ('oee_availability', 'OEE Availability % → HMI'),
    ('oee_performance',  'OEE Performance % → HMI'),
    ('oee_quality',      'OEE Quality % → HMI'),
    ('oee_overall',      'OEE Overall % → HMI'),
]


class MrpModbusRegisterMap(models.Model):
    _name = 'mrp.modbus.register.map'
    _description = 'Modbus Register Map Entry'
    _order = 'register_address'

    config_id = fields.Many2one('mrp.modbus.config', string='Config', required=True,
                                ondelete='cascade')
    name = fields.Char(string='Label', required=True,
                       help='Human-readable name, e.g. "Run Time"')
    variable_key = fields.Selection(VARIABLE_KEY_SELECTION, string='Variable Key',
                                    required=True)
    register_type = fields.Selection([
        ('holding',  'Holding Register'),
        ('input',    'Input Register'),
        ('coil',     'Coil'),
        ('discrete', 'Discrete Input'),
    ], string='Register Type', required=True, default='holding')
    register_address = fields.Integer(string='Register Address (0-based)',
                                      required=True, default=0)
    data_type = fields.Selection([
        ('uint16',  'UINT16 (0–65535)'),
        ('int16',   'INT16 (−32768–32767)'),
        ('float32', 'FLOAT32 (2 registers)'),
        ('bool',    'BOOL (coil/discrete)'),
    ], string='Data Type', required=True, default='uint16')
    scale_factor = fields.Float(string='Scale Factor', default=1.0,
                                help='Raw value × scale_factor = engineering value'
                                     ' (e.g. 0.01 means 8550 → 85.50%)')
    direction = fields.Selection([
        ('read',       'Read (HMI → Odoo)'),
        ('write',      'Write (Odoo → HMI)'),
        ('read_write', 'Read & Write'),
    ], string='Direction', required=True, default='read')
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('unique_key_per_config', 'unique(config_id, variable_key)',
         'Each variable key must be unique within a config profile.'),
    ]

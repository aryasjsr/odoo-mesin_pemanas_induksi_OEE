import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

VARIABLE_KEY_SELECTION = [
    # READ — HMI → Odoo (register 40001–40005)
    ('m_status',         'M_STATUS (0=Stop, 1=Running)'),
    ('good_count',       'GOOD_COUNT (accumulative)'),
    ('reject_count',     'REJECT_COUNT (accumulative)'),
    ('reason_code',      'REASON_CODE (downtime reason)'),
    ('wo_id',            'WO_ID (active MO selected on HMI)'),
    # WRITE — Odoo → HMI: MO List slots (register 40006–40025)
    ('mo_slot_0_id',     'MO Slot 0 — ID'),
    ('mo_slot_0_op',     'MO Slot 0 — Operator Code'),
    ('mo_slot_1_id',     'MO Slot 1 — ID'),
    ('mo_slot_1_op',     'MO Slot 1 — Operator Code'),
    ('mo_slot_2_id',     'MO Slot 2 — ID'),
    ('mo_slot_2_op',     'MO Slot 2 — Operator Code'),
    ('mo_slot_3_id',     'MO Slot 3 — ID'),
    ('mo_slot_3_op',     'MO Slot 3 — Operator Code'),
    ('mo_slot_4_id',     'MO Slot 4 — ID'),
    ('mo_slot_4_op',     'MO Slot 4 — Operator Code'),
    ('mo_slot_5_id',     'MO Slot 5 — ID'),
    ('mo_slot_5_op',     'MO Slot 5 — Operator Code'),
    ('mo_slot_6_id',     'MO Slot 6 — ID'),
    ('mo_slot_6_op',     'MO Slot 6 — Operator Code'),
    ('mo_slot_7_id',     'MO Slot 7 — ID'),
    ('mo_slot_7_op',     'MO Slot 7 — Operator Code'),
    ('mo_slot_8_id',     'MO Slot 8 — ID'),
    ('mo_slot_8_op',     'MO Slot 8 — Operator Code'),
    ('mo_slot_9_id',     'MO Slot 9 — ID'),
    ('mo_slot_9_op',     'MO Slot 9 — Operator Code'),
    # WRITE — Odoo → HMI: OEE feedback (register 40030–40033)
    ('oee_availability', 'OEE Availability % → HMI'),
    ('oee_performance',  'OEE Performance % → HMI'),
    ('oee_quality',      'OEE Quality % → HMI'),
    ('oee_overall',      'OEE Overall % → HMI'),
    # READ — HMI → Odoo: WO close command (register 40034)
    ('finished_status',  'FINISHED_STATUS (HMI sets 1 → Odoo closes WO)'),
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

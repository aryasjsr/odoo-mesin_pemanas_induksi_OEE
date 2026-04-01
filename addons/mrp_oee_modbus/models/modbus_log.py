import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class MrpModbusLog(models.Model):
    _name = 'mrp.modbus.log'
    _description = 'Modbus Activity Log'
    _order = 'timestamp desc'
    _rec_name = 'message'

    config_id = fields.Many2one('mrp.modbus.config', string='Config',
                                required=True, ondelete='cascade', index=True)
    timestamp = fields.Datetime(string='Time', default=fields.Datetime.now,
                                readonly=True, required=True)
    level = fields.Selection([
        ('info', '🟢 Info'),
        ('warning', '🟡 Warning'),
        ('error', '🔴 Error'),
    ], string='Level', default='info', required=True)
    message = fields.Char(string='Message', required=True)

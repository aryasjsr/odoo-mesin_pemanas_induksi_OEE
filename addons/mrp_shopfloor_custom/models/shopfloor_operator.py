import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class ShopfloorOperator(models.Model):
    _name = 'shopfloor.operator'
    _description = 'Shop Floor Operator Clock-In Record'
    _order = 'clock_in_time desc'

    user_id = fields.Many2one('res.users', string='Operator', required=True, ondelete='cascade')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center', required=True, ondelete='cascade')
    clock_in_time = fields.Datetime(string='Clock In', default=fields.Datetime.now)
    clock_out_time = fields.Datetime(string='Clock Out')
    is_active = fields.Boolean(string='Active', default=True)

    def name_get(self):
        return [(rec.id, f"{rec.user_id.name} @ {rec.workcenter_id.name}") for rec in self]

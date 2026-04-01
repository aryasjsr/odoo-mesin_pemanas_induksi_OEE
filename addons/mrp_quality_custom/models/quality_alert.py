from odoo import models, fields


class QualityAlert(models.Model):
    _name = 'quality.alert'
    _description = 'Quality Alert'
    _order = 'create_date desc'

    name = fields.Char(string='Alert Title', required=True)
    check_id = fields.Many2one('quality.check', string='Related Check', ondelete='set null')
    product_id = fields.Many2one('product.product', string='Product')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center')
    stage_id = fields.Many2one('quality.alert.stage', string='Stage',
                                group_expand='_read_group_stage_ids',
                                default=lambda self: self._default_stage())
    description = fields.Text(string='Description')
    root_cause = fields.Text(string='Root Cause Analysis')
    corrective_action = fields.Text(string='Corrective Action')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
    ], string='Priority', default='0')
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    date_closed = fields.Datetime(string='Date Closed')

    def _default_stage(self):
        return self.env['quality.alert.stage'].search([], order='sequence', limit=1)

    @staticmethod
    def _read_group_stage_ids(stages, domain, order):
        """Show all stages in kanban view even if empty."""
        return stages.search([], order=order)

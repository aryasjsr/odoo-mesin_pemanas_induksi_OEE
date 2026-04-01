import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class QualityCheck(models.Model):
    _name = 'quality.check'
    _description = 'Quality Check'
    _order = 'create_date desc'

    name = fields.Char(string='Reference', readonly=True, default='New')
    control_point_id = fields.Many2one('quality.control.point', string='Control Point',
                                       required=True, ondelete='cascade')
    workorder_id = fields.Many2one('mrp.workorder', string='Work Order', ondelete='set null')
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order',
                                    related='workorder_id.production_id', store=True)
    product_id = fields.Many2one('product.product', string='Product',
                                  related='control_point_id.product_id', store=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center',
                                     related='workorder_id.workcenter_id', store=True)

    check_type = fields.Selection(related='control_point_id.check_type', store=True)
    instructions = fields.Text(related='control_point_id.instructions')

    # Results
    state = fields.Selection([
        ('todo', 'To Do'),
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    ], string='Status', default='todo', tracking=True)

    # Pass/Fail
    result_passfail = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')],
                                        string='Result')

    # Measure
    measure_value = fields.Float(string='Measured Value')
    measure_min = fields.Float(related='control_point_id.measure_min')
    measure_max = fields.Float(related='control_point_id.measure_max')
    measure_uom = fields.Char(related='control_point_id.measure_uom')

    # Picture
    picture = fields.Binary(string='Photo', attachment=True)
    picture_filename = fields.Char(string='Photo Filename')

    # Link to alert (auto-created on fail)
    alert_id = fields.Many2one('quality.alert', string='Quality Alert', readonly=True)

    note = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('quality.check') or 'New'
        return super().create(vals_list)

    def action_pass(self):
        """Mark the check as passed."""
        self.ensure_one()
        self.write({'state': 'pass', 'result_passfail': 'pass'})
        _logger.info("Quality Check %s PASSED", self.name)
        return True

    def action_fail(self):
        """Mark the check as failed and auto-create a Quality Alert."""
        self.ensure_one()
        self.write({'state': 'fail', 'result_passfail': 'fail'})
        _logger.info("Quality Check %s FAILED — creating alert", self.name)

        alert = self.env['quality.alert'].sudo().create({
            'name': f"Alert: {self.name}",
            'check_id': self.id,
            'product_id': self.product_id.id if self.product_id else False,
            'workcenter_id': self.workcenter_id.id if self.workcenter_id else False,
            'description': f"Quality check [{self.name}] failed.\n"
                           f"Control Point: {self.control_point_id.name}\n"
                           f"Check Type: {self.check_type}",
        })
        self.alert_id = alert.id
        return True

    def action_submit_measure(self, value):
        """Submit a measurement value and auto-determine pass/fail."""
        self.ensure_one()
        self.measure_value = value
        if self.measure_min <= value <= self.measure_max:
            self.action_pass()
        else:
            self.action_fail()
        return True

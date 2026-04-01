from odoo import models, fields


class QualityControlPoint(models.Model):
    _name = 'quality.control.point'
    _description = 'Quality Control Point'
    _order = 'sequence, id'

    name = fields.Char(string='Title', required=True)
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', string='Product',
                                 help='Leave blank to apply to all products')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center',
                                    help='Leave blank to apply to all work centers')
    operation_id = fields.Many2one('mrp.routing.workcenter', string='Operation',
                                   help='Link to a specific BoM operation. Leave blank to apply to all operations')
    trigger = fields.Selection([
        ('on_wo_start', 'When Work Order starts'),
        ('on_wo_finish', 'When Work Order finishes'),
        ('on_mo_complete', 'When MO is completed'),
        ('on_production', 'After each production record'),
        ('manual', 'Manual trigger only'),
    ], string='Trigger', default='manual', required=True)

    check_type = fields.Selection([
        ('passfail', 'Pass / Fail'),
        ('measure', 'Measure (Value)'),
        ('picture', 'Take a Picture'),
    ], string='Check Type', default='passfail', required=True)

    measure_min = fields.Float(string='Min Tolerance', help='For Measure type')
    measure_max = fields.Float(string='Max Tolerance', help='For Measure type')
    measure_uom = fields.Char(string='Unit of Measure', default='°C')
    instructions = fields.Text(string='Instructions',
                               help='Detailed instructions for the operator performing this quality check')
    active = fields.Boolean(default=True)

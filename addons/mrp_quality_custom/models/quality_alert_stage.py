from odoo import models, fields


class QualityAlertStage(models.Model):
    _name = 'quality.alert.stage'
    _description = 'Quality Alert Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(string='Folded in Kanban', default=False)

from odoo import models, fields


class ResUsersModbus(models.Model):
    _inherit = 'res.users'

    operator_code = fields.Char(
        string='Operator Code',
        size=4,
        help='4-digit code sent to HMI via Modbus (e.g. 0023)',
    )

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    # --- Machine State Fields ---
    machine_state = fields.Selection([
        ('stop', 'Stop'),
        ('running', 'Running'),
        ('paused', 'Paused'),
    ], string='Machine State', default='stop', tracking=True)

    reason_code = fields.Selection([
        ('0', 'None'),
        ('1', 'Setup'),
        ('2', 'Equipment Failure'),
        ('3', 'Material Shortage'),
    ], string='Downtime Reason', default='0')

    good_count = fields.Integer(string='Good Count', default=0)
    reject_count = fields.Integer(string='Reject Count', default=0)
    total_count = fields.Integer(
        string='Total Count', compute='_compute_total_count', store=True,
    )

    employee_id = fields.Many2one(
        'hr.employee', string='Current Operator',
        help='Employee currently operating this work order',
    )

    current_productivity_id = fields.Many2one(
        'mrp.workcenter.productivity',
        string='Current Productivity Tracking',
        ondelete='set null',
    )

    @api.depends('good_count', 'reject_count')
    def _compute_total_count(self):
        for rec in self:
            rec.total_count = rec.good_count + rec.reject_count

    # ------------------------------------------------------------------
    # Machine Actions
    # ------------------------------------------------------------------

    def action_machine_start(self, user=None):
        """Start production. Auto clock-in the user as operator."""
        self.ensure_one()
        _logger.info("Machine START for WO %s (ID: %s)", self.display_name, self.id)

        # Close any dangling productivity record
        if self.current_productivity_id and not self.current_productivity_id.date_end:
            self.current_productivity_id.write({'date_end': fields.Datetime.now()})

        # Auto clock-in: find or create shopfloor.operator for this user
        employee = self.env['hr.employee']
        if user:
            employee = self._auto_clock_in(user)

        prod_vals = {
            'workcenter_id': self.workcenter_id.id,
            'workorder_id': self.id,
            'date_start': fields.Datetime.now(),
            'loss_id': self._get_productive_loss_id(),
            'description': f"Production: {self.display_name}",
        }
        productivity = self.env['mrp.workcenter.productivity'].sudo().create(prod_vals)

        write_vals = {
            'machine_state': 'running',
            'state': 'progress',
            'current_productivity_id': productivity.id,
        }
        if employee:
            write_vals['employee_id'] = employee.id
        self.write(write_vals)

        self._auto_create_quality_checks('on_wo_start')
        return True

    def action_machine_block(self, loss_id=None):
        """Block/pause with a specific loss reason (from loss_id)."""
        self.ensure_one()
        _logger.info("Machine BLOCK for WO %s, loss_id=%s", self.display_name, loss_id)
        now = fields.Datetime.now()

        # Close current productive record
        if self.current_productivity_id and not self.current_productivity_id.date_end:
            self.current_productivity_id.write({'date_end': now})

        # Determine loss record
        if loss_id:
            loss = self.env['mrp.workcenter.productivity.loss'].sudo().browse(int(loss_id))
            if not loss.exists():
                loss_id = self._get_loss_id_for_reason('0')
            else:
                loss_id = loss.id
        else:
            loss_id = self._get_loss_id_for_reason('0')

        loss_rec = self.env['mrp.workcenter.productivity.loss'].sudo().browse(loss_id)
        productivity = self.env['mrp.workcenter.productivity'].sudo().create({
            'workcenter_id': self.workcenter_id.id,
            'workorder_id': self.id,
            'date_start': now,
            'loss_id': loss_id,
            'description': f"Downtime ({loss_rec.name}): {self.display_name}",
        })

        self.write({
            'machine_state': 'paused',
            'current_productivity_id': productivity.id,
        })
        return True

    def action_machine_pause(self, reason_code='0'):
        """Legacy pause (kept for backward compat). Delegates to block."""
        return self.action_machine_block(loss_id=self._get_loss_id_for_reason(reason_code))

    def action_machine_resume(self):
        """Resume production after block/pause."""
        self.ensure_one()
        _logger.info("Machine RESUME for WO %s", self.display_name)
        now = fields.Datetime.now()

        if self.current_productivity_id and not self.current_productivity_id.date_end:
            self.current_productivity_id.write({'date_end': now})

        employee = self._get_active_employee()
        prod_vals = {
            'workcenter_id': self.workcenter_id.id,
            'workorder_id': self.id,
            'date_start': now,
            'loss_id': self._get_productive_loss_id(),
            'description': f"Production (resumed): {self.display_name}",
        }
        productivity = self.env['mrp.workcenter.productivity'].sudo().create(prod_vals)

        self.write({
            'machine_state': 'running',
            'reason_code': '0',
            'current_productivity_id': productivity.id,
        })
        return True

    def action_machine_stop(self):
        """Stop production (but don't close WO yet)."""
        self.ensure_one()
        _logger.info("Machine STOP for WO %s", self.display_name)
        now = fields.Datetime.now()

        if self.current_productivity_id and not self.current_productivity_id.date_end:
            self.current_productivity_id.write({'date_end': now})

        self.write({
            'machine_state': 'stop',
            'reason_code': '0',
        })
        self._auto_create_quality_checks('on_wo_finish')
        return True

    def action_close_production(self):
        """Close production: stop timer, sync qty_produced, mark WO done."""
        self.ensure_one()
        _logger.info("CLOSE PRODUCTION for WO %s", self.display_name)

        # Stop timer first
        if self.machine_state != 'stop':
            self.action_machine_stop()

        # Sync qty_produced from good_count
        if self.good_count > 0:
            self.write({'qty_produced': self.good_count})

        # Try to mark WO as done
        try:
            if self.state not in ('done', 'cancel'):
                self.button_finish()
                _logger.info("WO %s marked as done", self.display_name)
        except Exception as e:
            _logger.warning("Could not finish WO %s: %s", self.display_name, e)

        return True

    def action_update_count(self, good_count=0, reject_count=0):
        """Update production counts."""
        self.ensure_one()
        _logger.info("Count UPDATE for WO %s: good=%s, reject=%s", self.id, good_count, reject_count)
        self.write({
            'good_count': good_count,
            'reject_count': reject_count,
        })
        return True

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def _auto_clock_in(self, user):
        """Auto clock-in: create shopfloor.operator if not exists, return employee."""
        ShopOp = self.env['shopfloor.operator'].sudo()
        existing = ShopOp.search([
            ('user_id', '=', user.id),
            ('workcenter_id', '=', self.workcenter_id.id),
            ('is_active', '=', True),
        ], limit=1)

        if not existing:
            ShopOp.create({
                'user_id': user.id,
                'workcenter_id': self.workcenter_id.id,
                'clock_in_time': fields.Datetime.now(),
                'is_active': True,
            })

        employee = self.env['hr.employee'].sudo().search([
            ('user_id', '=', user.id),
        ], limit=1)
        return employee

    def _get_active_employee(self):
        """Find active employee from shopfloor operator records."""
        op_record = self.env['shopfloor.operator'].sudo().search([
            ('workcenter_id', '=', self.workcenter_id.id),
            ('is_active', '=', True),
        ], limit=1)
        if op_record and op_record.user_id:
            employee = self.env['hr.employee'].sudo().search([
                ('user_id', '=', op_record.user_id.id),
            ], limit=1)
            return employee
        return self.env['hr.employee']

    def _get_productive_loss_id(self):
        """Return loss_id for productive (no loss) type."""
        productive_loss = self.env['mrp.workcenter.productivity.loss'].sudo().search(
            [('loss_type', '=', 'productive')], limit=1,
        )
        if not productive_loss:
            productive_loss = self.env['mrp.workcenter.productivity.loss'].sudo().create({
                'name': 'Productive',
                'loss_type': 'productive',
                'manual': False,
            })
        return productive_loss.id

    def _get_loss_id_for_reason(self, reason_code):
        """Map reason_code to an Odoo loss record."""
        reason_map = {
            '0': ('No Reason', 'availability'),
            '1': ('Setup / Changeover', 'availability'),
            '2': ('Equipment Failure', 'availability'),
            '3': ('Material Shortage', 'availability'),
        }
        name, loss_type = reason_map.get(str(reason_code), ('Unknown', 'availability'))
        loss = self.env['mrp.workcenter.productivity.loss'].sudo().search(
            [('name', '=', name)], limit=1,
        )
        if not loss:
            loss = self.env['mrp.workcenter.productivity.loss'].sudo().create({
                'name': name,
                'loss_type': loss_type,
                'manual': True,
            })
        return loss.id

    def _auto_create_quality_checks(self, trigger_type):
        """Auto-create quality.check records based on matching QCPs."""
        self.ensure_one()
        QCP = self.env.get('quality.control.point')
        if QCP is None:
            return

        domain = [
            ('trigger', '=', trigger_type),
            ('active', '=', True),
            '|', ('workcenter_id', '=', self.workcenter_id.id),
                 ('workcenter_id', '=', False),
        ]
        if self.product_id:
            domain = domain + [
                '|', ('product_id', '=', self.product_id.id),
                     ('product_id', '=', False),
            ]

        qcps = QCP.sudo().search(domain)
        QualityCheck = self.env.get('quality.check')
        if QualityCheck is None:
            return

        for qcp in qcps:
            QualityCheck.sudo().create({
                'control_point_id': qcp.id,
                'workorder_id': self.id,
            })
            _logger.info(
                "Auto-created quality check for QCP '%s' (trigger=%s) on WO %s",
                qcp.name, trigger_type, self.display_name,
            )

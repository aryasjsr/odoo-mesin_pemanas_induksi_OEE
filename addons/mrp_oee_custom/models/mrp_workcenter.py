import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'
    oee_availability = ()

    # --- OEE Computed Fields ---
    oee_availability = fields.Float(
        string='Availability (%)', compute='_compute_oee', store=True,
        help='Operating Time / Planned Production Time × 100',
    )
    oee_performance = fields.Float(
        string='Performance (%)', compute='_compute_oee', store=True,
        help='(Ideal Cycle Time × Total Count) / Operating Time × 100 (max 100%)',
    )
    oee_quality = fields.Float(
        string='Quality (%)', compute='_compute_oee', store=True,
        help='Good Count / Total Count × 100',
    )
    oee_total = fields.Float(
        string='OEE (%)', compute='_compute_oee', store=True,
        help='Availability × Performance × Quality',
    )

    @api.depends('order_ids.good_count', 'order_ids.reject_count',
                 'order_ids.machine_state')
    def _compute_oee(self):
        """Compute OEE metrics for each workcenter.
        Also assigns the base mrp.workcenter 'oee' field."""
        for wc in self:
            # Guard: skip unsaved records (NewId)
            if not wc.id or isinstance(wc.id, models.NewId):
                wc.oee_availability = 0.0
                wc.oee_performance = 0.0
                wc.oee_quality = 0.0
                wc.oee_total = 0.0
                wc.oee = 0.0  # base field
                continue

            try:
                productivities = self.env['mrp.workcenter.productivity'].sudo().search([
                    ('workcenter_id', '=', wc.id),
                    ('date_end', '!=', False),
                ])

                if not productivities:
                    wc.oee_availability = 0.0
                    wc.oee_performance = 0.0
                    wc.oee_quality = 0.0
                    wc.oee_total = 0.0
                    wc.oee = 0.0
                    continue

                planned_time = 0.0
                operating_time = 0.0

                for prod in productivities:
                    duration = (prod.date_end - prod.date_start).total_seconds() / 3600.0
                    planned_time += duration
                    if prod.loss_type == 'productive':
                        operating_time += duration

                work_orders = self.env['mrp.workorder'].sudo().search([
                    ('workcenter_id', '=', wc.id),
                ])
                total_good = sum(work_orders.mapped('good_count'))
                total_reject = sum(work_orders.mapped('reject_count'))
                total_count = total_good + total_reject

                availability = operating_time / planned_time if planned_time > 0 else 0.0

                # Cycle time: try available fields, fallback to 1 min/unit
                cycle_minutes = 1.0
                try:
                    if hasattr(wc, 'time_cycle_manual') and wc.time_cycle_manual > 0:
                        cycle_minutes = wc.time_cycle_manual
                    elif hasattr(wc, 'time_cycle') and wc.time_cycle > 0:
                        cycle_minutes = wc.time_cycle
                except Exception:
                    pass
                ideal_cycle_time_hours = cycle_minutes / 60.0
                if operating_time > 0 and ideal_cycle_time_hours > 0 and total_count > 0:
                    performance = min((ideal_cycle_time_hours * total_count) / operating_time, 1.0)
                elif operating_time > 0 and total_count > 0:
                    performance = 1.0
                else:
                    performance = 0.0

                quality = total_good / total_count if total_count > 0 else 0.0
                oee_val = availability * performance * quality * 100.0

                wc.oee_availability = round(availability * 100.0, 2)
                wc.oee_performance = round(performance * 100.0, 2)
                wc.oee_quality = round(quality * 100.0, 2)
                wc.oee_total = round(oee_val, 2)
                wc.oee = round(oee_val, 2)  # base field

            except Exception as e:
                _logger.warning("OEE compute error for WC %s: %s", wc.id, e)
                wc.oee_availability = 0.0
                wc.oee_performance = 0.0
                wc.oee_quality = 0.0
                wc.oee_total = 0.0
                wc.oee = 0.0

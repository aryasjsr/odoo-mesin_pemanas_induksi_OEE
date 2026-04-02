import logging
from odoo import http
from odoo.http import request
from odoo.fields import Datetime

_logger = logging.getLogger(__name__)


class OEEAPIController(http.Controller):
    """JSON API endpoint for the OWL OEE Dashboard."""

    @http.route('/api/oee/dashboard_data', type='json', auth='user', methods=['POST'], csrf=False)
    def get_dashboard_data(self, **kwargs):
        """Return OEE data for all workcenters, computed live on every call."""
        try:
            workcenters = request.env['mrp.workcenter'].sudo().search([])
            data = []
            now = Datetime.now()

            for wc in workcenters:
                # ---- Fetch all productivity records for this WC ----
                productivities = request.env['mrp.workcenter.productivity'].sudo().search([
                    ('workcenter_id', '=', wc.id),
                    ('date_start', '!=', False),
                ])

                planned_minutes = 0.0
                operating_minutes = 0.0
                blocked_minutes = 0.0

                for prod in productivities:
                    end = prod.date_end or now
                    duration_min = (end - prod.date_start).total_seconds() / 60.0
                    if duration_min <= 0:
                        continue
                    planned_minutes += duration_min
                    # Use loss_type directly from productivity record (stored related field)
                    if prod.loss_type == 'productive':
                        operating_minutes += duration_min
                    else:
                        blocked_minutes += duration_min

                # ---- Work orders for this WC (not cancelled) ----
                work_orders = request.env['mrp.workorder'].sudo().search([
                    ('workcenter_id', '=', wc.id),
                    ('state', 'not in', ['cancel']),
                ])
                total_good = sum(work_orders.mapped('good_count'))
                total_reject = sum(work_orders.mapped('reject_count'))
                total_count = total_good + total_reject

                # ---- OEE Formula ----
                # Availability = Operating Time / Planned Time
                availability = (operating_minutes / planned_minutes) if planned_minutes > 0 else 0.0

                # Performance = (Ideal Cycle Time * Total Count) / Operating Time
                # Odoo 18 workcenter has time_start/time_stop but no time_cycle_manual
                # Use a default of 1 min/unit if not available, can be configured via
                # the workcenter's "Default Duration" or we use a safe fallback
                cycle_min = 1.0  # default: 1 minute per unit
                try:
                    # Try different possible field names
                    if hasattr(wc, 'time_cycle_manual') and wc.time_cycle_manual > 0:
                        cycle_min = wc.time_cycle_manual
                    elif hasattr(wc, 'time_cycle') and wc.time_cycle > 0:
                        cycle_min = wc.time_cycle
                except Exception:
                    pass

                if operating_minutes > 0 and total_count > 0:
                    performance = min((cycle_min * total_count) / operating_minutes, 1.0)
                else:
                    performance = 0.0

                # Quality = Good Count / Total Count
                quality = (total_good / total_count) if total_count > 0 else 0.0

                oee_val = availability * performance * quality * 100.0

                # ---- Current machine state & active WO ----
                active_wo = request.env['mrp.workorder'].sudo().search([
                    ('workcenter_id', '=', wc.id),
                    ('machine_state', '=', 'running'),
                ], limit=1)
                current_wo = request.env['mrp.workorder'].sudo().search([
                    ('workcenter_id', '=', wc.id),
                    ('machine_state', '!=', 'stop'),
                ], limit=1, order='write_date desc')

                # Modbus HMI realtime status (if polling is active)
                modbus_config = request.env['mrp.modbus.config'].sudo().search([
                    ('workcenter_id', '=', wc.id),
                    ('polling_state', '=', 'polling'),
                ], limit=1)

                data.append({
                    'id': wc.id,
                    'name': wc.name,
                    'availability': round(availability * 100.0, 1),
                    'performance': round(performance * 100.0, 1),
                    'quality': round(quality * 100.0, 1),
                    'oee': round(oee_val, 1),
                    # durations in minutes (2 decimal places)
                    'planned_minutes': round(planned_minutes, 2),
                    'operating_minutes': round(operating_minutes, 2),
                    'blocked_minutes': round(blocked_minutes, 2),
                    'machine_state': current_wo.machine_state if current_wo else 'stop',
                    'active_wo': active_wo.display_name if active_wo else '-',
                    'good_count': total_good,
                    'reject_count': total_reject,
                    'total_count': total_count,
                    # Modbus HMI realtime status
                    'hmi_m_status': modbus_config.hmi_m_status if modbus_config else None,
                    'modbus_polling': bool(modbus_config),
                })

            return {'status': 'ok', 'data': data}

        except Exception as e:
            _logger.exception("OEE Dashboard API error")
            return {'status': 'error', 'message': str(e)}

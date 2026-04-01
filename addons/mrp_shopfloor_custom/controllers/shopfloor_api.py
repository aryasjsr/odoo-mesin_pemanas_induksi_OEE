import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ShopfloorAPIController(http.Controller):
    """JSON API endpoints for the Shop Floor OWL UI."""

    @http.route('/api/shopfloor/data', type='json', auth='user', methods=['POST'], csrf=False)
    def get_shopfloor_data(self, workcenter_id=None, **kwargs):
        """Return all data needed by the Shop Floor OWL UI."""
        try:
            # --- Workcenters ---
            workcenters = request.env['mrp.workcenter'].sudo().search([])
            wc_data = [{'id': wc.id, 'name': wc.name} for wc in workcenters]

            # --- Work Orders (not done/cancel) ---
            wo_domain = [('state', 'not in', ['done', 'cancel'])]
            if workcenter_id:
                wo_domain.append(('workcenter_id', '=', int(workcenter_id)))

            work_orders = request.env['mrp.workorder'].sudo().search(wo_domain, order='id desc')
            wo_data = []
            for wo in work_orders:
                from odoo.fields import Datetime
                now = Datetime.now()
                running_seconds = 0
                current_blocked_seconds = 0

                for prod in wo.time_ids:
                    if not prod.date_start:
                        continue
                    end = prod.date_end or now
                    sec = int((end - prod.date_start).total_seconds())
                    if prod.loss_type == 'productive':
                        running_seconds += sec

                if wo.machine_state == 'paused' and wo.current_productivity_id and not wo.current_productivity_id.date_end:
                    current_blocked_seconds = int((now - wo.current_productivity_id.date_start).total_seconds())


                # Responsible user from MO
                responsible_user_id = False
                responsible_name = '-'
                if wo.production_id and wo.production_id.user_id:
                    responsible_user_id = wo.production_id.user_id.id
                    responsible_name = wo.production_id.user_id.name

                wo_data.append({
                    'id': wo.id,
                    'name': wo.display_name,
                    'product_name': wo.product_id.display_name if wo.product_id else '-',
                    'product_qty': wo.qty_production,
                    'qty_produced': wo.qty_produced,
                    'machine_state': wo.machine_state or 'stop',
                    'reason_code': wo.reason_code or '0',
                    'good_count': wo.good_count,
                    'reject_count': wo.reject_count,
                    'total_count': wo.total_count,
                    'workcenter_id': wo.workcenter_id.id,
                    'workcenter_name': wo.workcenter_id.name,
                    'mo_name': wo.production_id.name if wo.production_id else '-',
                    'running_seconds': running_seconds,
                    'current_blocked_seconds': current_blocked_seconds,
                    'worksheet_notes': wo.worksheet or '',
                    'responsible_user_id': responsible_user_id,
                    'responsible_name': responsible_name,
                })

            # --- Assigned operators (unique responsible users from WOs) ---
            operators = []
            seen_user_ids = set()
            for wo in wo_data:
                uid = wo.get('responsible_user_id')
                if uid and uid not in seen_user_ids:
                    seen_user_ids.add(uid)
                    operators.append({
                        'id': uid,
                        'user_id': uid,
                        'name': wo.get('responsible_name', '-'),
                    })

            return {
                'status': 'ok',
                'workcenters': wc_data,
                'work_orders': wo_data,
                'operators': operators,
            }

        except Exception as e:
            _logger.exception("Shopfloor API error")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/shopfloor/loss_reasons', type='json', auth='user', methods=['POST'], csrf=False)
    def get_loss_reasons(self, **kwargs):
        """Return all loss reasons for the Block popup."""
        try:
            losses = request.env['mrp.workcenter.productivity.loss'].sudo().search([
                ('loss_type', '!=', 'productive'),
            ], order='sequence, name')
            data = [{'id': l.id, 'name': l.name, 'loss_type': l.loss_type} for l in losses]
            return {'status': 'ok', 'loss_reasons': data}
        except Exception as e:
            _logger.exception("Loss reasons API error")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/shopfloor/close_production', type='json', auth='user', methods=['POST'], csrf=False)
    def close_production(self, wo_id=None, **kwargs):
        """Close production for a WO: stop + mark done."""
        try:
            if not wo_id:
                return {'status': 'error', 'message': 'wo_id is required'}

            workorder = request.env['mrp.workorder'].sudo().browse(int(wo_id))
            if not workorder.exists():
                return {'status': 'error', 'message': f'Work Order {wo_id} not found'}

            workorder.action_close_production()
            _logger.info("API: close_production OK for WO %s", wo_id)
            return {'status': 'ok'}

        except Exception as e:
            _logger.exception("Close production API error")
            return {'status': 'error', 'message': str(e)}

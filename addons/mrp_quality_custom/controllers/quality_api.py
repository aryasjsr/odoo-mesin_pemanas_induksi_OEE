import logging
import base64
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class QualityAPIController(http.Controller):
    """JSON API endpoints for Quality Dashboard and QC Check submission."""

    @http.route('/api/quality/dashboard_data', type='json', auth='user', methods=['POST'], csrf=False)
    def get_dashboard_data(self, **kwargs):
        """Return quality overview data for the OWL dashboard."""
        try:
            pending = request.env['quality.check'].sudo().search_count([('state', '=', 'todo')])
            alerts = request.env['quality.alert'].sudo().search_count([])
            recent_checks = request.env['quality.check'].sudo().search([], limit=10, order='create_date desc')

            checks_data = []
            for c in recent_checks:
                checks_data.append({
                    'id': c.id,
                    'name': c.name,
                    'control_point': c.control_point_id.name,
                    'check_type': c.check_type,
                    'state': c.state,
                    'product': c.product_id.display_name if c.product_id else '-',
                    'workcenter': c.workcenter_id.name if c.workcenter_id else '-',
                })

            return {
                'status': 'ok',
                'pending_count': pending,
                'alert_count': alerts,
                'recent_checks': checks_data,
            }
        except Exception as e:
            _logger.exception("Quality dashboard error")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/quality/check/submit', type='json', auth='user', methods=['POST'], csrf=False)
    def submit_check(self, check_id=None, result=None, measure_value=None,
                     picture_base64=None, note=None, **kwargs):
        """Submit a QC check result.

        Params:
            check_id (int): Quality Check ID
            result (str): 'pass' or 'fail'
            measure_value (float): For measure type checks
            picture_base64 (str): Base64 encoded photo
            note (str): Optional notes
        """
        try:
            if not check_id:
                return {'status': 'error', 'message': 'check_id required'}

            check = request.env['quality.check'].sudo().browse(int(check_id))
            if not check.exists():
                return {'status': 'error', 'message': 'Check not found'}

            if note:
                check.note = note

            if check.check_type == 'passfail':
                if result == 'pass':
                    check.action_pass()
                else:
                    check.action_fail()

            elif check.check_type == 'measure':
                if measure_value is not None:
                    check.action_submit_measure(float(measure_value))
                else:
                    return {'status': 'error', 'message': 'measure_value required'}

            elif check.check_type == 'picture':
                if picture_base64:
                    check.picture = picture_base64
                if result == 'pass':
                    check.action_pass()
                else:
                    check.action_fail()

            return {
                'status': 'ok',
                'check_state': check.state,
                'alert_id': check.alert_id.id if check.alert_id else None,
            }

        except Exception as e:
            _logger.exception("QC submit error")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/quality/reject_notify', type='json', auth='user', csrf=False, methods=['POST'])
    def reject_notify(self, wo_id=None, reject_count=0, **kwargs):
        """Called by middleware when REJECT_COUNT increases.
        Returns data for the toast notification.
        """
        try:
            return {
                'status': 'ok',
                'toast': {
                    'title': 'Reject Detected!',
                    'message': f'WO #{wo_id}: {reject_count} reject(s) recorded',
                    'type': 'danger',
                }
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

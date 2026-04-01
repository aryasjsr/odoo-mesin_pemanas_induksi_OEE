import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MachineAPIController(http.Controller):
    """HTTP API endpoints for machine actions (Shop Floor UI + external middleware)."""

    # ------------------------------------------------------------------
    # POST /api/machine/start
    # ------------------------------------------------------------------
    @http.route('/api/machine/start', type='json', auth='user', csrf=False, methods=['POST'])
    def machine_start(self, wo_id=None, **kwargs):
        """Start production. Auto clock-in current user."""
        try:
            if not wo_id:
                return {'status': 'error', 'message': 'wo_id is required'}

            workorder = request.env['mrp.workorder'].sudo().browse(int(wo_id))
            if not workorder.exists():
                return {'status': 'error', 'message': f'Work Order {wo_id} not found'}

            workorder.action_machine_start(user=request.env.user)
            _logger.info("API: machine_start OK for WO %s, user=%s", wo_id, request.env.user.name)
            return {'status': 'ok'}

        except Exception as e:
            _logger.exception("API: machine_start FAILED")
            return {'status': 'error', 'message': str(e)}

    # ------------------------------------------------------------------
    # POST /api/machine/block  (pause with loss reason)
    # ------------------------------------------------------------------
    @http.route('/api/machine/block', type='json', auth='user', csrf=False, methods=['POST'])
    def machine_block(self, wo_id=None, loss_id=None, **kwargs):
        """Block/pause with a specific loss reason."""
        try:
            if not wo_id:
                return {'status': 'error', 'message': 'wo_id is required'}

            workorder = request.env['mrp.workorder'].sudo().browse(int(wo_id))
            if not workorder.exists():
                return {'status': 'error', 'message': f'Work Order {wo_id} not found'}

            workorder.action_machine_block(loss_id=loss_id)
            _logger.info("API: machine_block OK for WO %s, loss_id=%s", wo_id, loss_id)
            return {'status': 'ok'}

        except Exception as e:
            _logger.exception("API: machine_block FAILED")
            return {'status': 'error', 'message': str(e)}

    # ------------------------------------------------------------------
    # POST /api/machine/resume
    # ------------------------------------------------------------------
    @http.route('/api/machine/resume', type='json', auth='user', csrf=False, methods=['POST'])
    def machine_resume(self, wo_id=None, **kwargs):
        """Resume production after block."""
        try:
            if not wo_id:
                return {'status': 'error', 'message': 'wo_id is required'}

            workorder = request.env['mrp.workorder'].sudo().browse(int(wo_id))
            if not workorder.exists():
                return {'status': 'error', 'message': f'Work Order {wo_id} not found'}

            workorder.action_machine_resume()
            _logger.info("API: machine_resume OK for WO %s", wo_id)
            return {'status': 'ok'}

        except Exception as e:
            _logger.exception("API: machine_resume FAILED")
            return {'status': 'error', 'message': str(e)}

    # ------------------------------------------------------------------
    # POST /api/machine/update_count
    # ------------------------------------------------------------------
    @http.route('/api/machine/update_count', type='json', auth='user', csrf=False, methods=['POST'])
    def machine_update_count(self, wo_id=None, good_count=0, reject_count=0, **kwargs):
        """Update production counts."""
        try:
            if not wo_id:
                return {'status': 'error', 'message': 'wo_id is required'}

            workorder = request.env['mrp.workorder'].sudo().browse(int(wo_id))
            if not workorder.exists():
                return {'status': 'error', 'message': f'Work Order {wo_id} not found'}

            workorder.action_update_count(
                good_count=int(good_count),
                reject_count=int(reject_count),
            )
            _logger.info("API: update_count OK for WO %s", wo_id)
            return {'status': 'ok'}

        except Exception as e:
            _logger.exception("API: update_count FAILED")
            return {'status': 'error', 'message': str(e)}

    # ------------------------------------------------------------------
    # POST /api/machine/stop
    # ------------------------------------------------------------------
    @http.route('/api/machine/stop', type='json', auth='user', csrf=False, methods=['POST'])
    def machine_stop(self, wo_id=None, **kwargs):
        """Stop production (without closing WO)."""
        try:
            if not wo_id:
                return {'status': 'error', 'message': 'wo_id is required'}

            workorder = request.env['mrp.workorder'].sudo().browse(int(wo_id))
            if not workorder.exists():
                return {'status': 'error', 'message': f'Work Order {wo_id} not found'}

            workorder.action_machine_stop()
            _logger.info("API: machine_stop OK for WO %s", wo_id)
            return {'status': 'ok'}

        except Exception as e:
            _logger.exception("API: machine_stop FAILED")
            return {'status': 'error', 'message': str(e)}

    # ------------------------------------------------------------------
    # POST /api/machine/scrap
    # ------------------------------------------------------------------
    @http.route('/api/machine/scrap', type='json', auth='user', csrf=False, methods=['POST'])
    def machine_scrap(self, wo_id=None, reject_qty=0, **kwargs):
        """Create scrap record from reject count."""
        try:
            if not wo_id:
                return {'status': 'error', 'message': 'wo_id is required'}
            if not reject_qty or int(reject_qty) <= 0:
                return {'status': 'error', 'message': 'reject_qty must be > 0'}

            reject_qty = int(reject_qty)
            workorder = request.env['mrp.workorder'].sudo().browse(int(wo_id))
            if not workorder.exists():
                return {'status': 'error', 'message': f'Work Order {wo_id} not found'}

            production = workorder.production_id
            if not production:
                return {'status': 'error', 'message': 'No Manufacturing Order linked'}

            product = production.product_id
            location = production.location_src_id or request.env.ref(
                'stock.stock_location_stock', raise_if_not_found=False)

            scrap = request.env['stock.scrap'].sudo().create({
                'product_id': product.id,
                'scrap_qty': reject_qty,
                'product_uom_id': product.uom_id.id,
                'location_id': location.id if location else False,
                'production_id': production.id,
                'company_id': production.company_id.id,
            })

            try:
                scrap.action_validate()
                _logger.info("Scrap created+validated: ID=%s, qty=%s", scrap.id, reject_qty)
            except Exception as val_err:
                _logger.warning("Scrap validation failed: %s", val_err)

            # Also update reject_count on the WO
            new_reject = workorder.reject_count + reject_qty
            workorder.action_update_count(
                good_count=workorder.good_count,
                reject_count=new_reject,
            )

            return {'status': 'ok', 'scrap_id': scrap.id}

        except Exception as e:
            _logger.exception("API: scrap FAILED")
            return {'status': 'error', 'message': str(e)}

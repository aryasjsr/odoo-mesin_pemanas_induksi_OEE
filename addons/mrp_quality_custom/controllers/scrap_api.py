import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ScrapAPIController(http.Controller):
    """HTTP API endpoint to auto-create scrap records from reject sensor signals."""

    @http.route('/api/machine/scrap_legacy', type='json', auth='user', csrf=False, methods=['POST'])
    def create_scrap(self, wo_id=None, reject_qty=0, **kwargs):
        """Create an mrp.scrap record from reject count (legacy endpoint)."""
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
                _logger.info("Scrap created+validated: ID=%s, qty=%s, WO=%s", scrap.id, reject_qty, wo_id)
            except Exception as val_err:
                _logger.warning("Scrap ID=%s validation failed: %s", scrap.id, val_err)

            return {'status': 'ok', 'scrap_id': scrap.id, 'scrap_name': scrap.name}

        except Exception as e:
            _logger.exception("API: create_scrap FAILED")
            return {'status': 'error', 'message': str(e)}

## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class SaleOrderLineModel(osv.osv):
    _inherit = "sale.order.line"

    def get_currency(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        for line in self.browse(cr, uid, ids):
            result[line.id] = line.order_id.pricelist_id.currency_id
        return result

    def get_order_date(self, cr, uid, ids, field_names=None, arg=None, context=None):
        return dict([(i, self.get_order_date_internal(cr, uid, i, field_names=None, arg=None, context=None)) for i in ids])

    def browse_product_id(self, cr, uid, ids, context):
        ## Check the argument type:
        if isinstance(ids, (int, long)):
            ids = [ids]

        ## Get the object:
        obj = self.browse(cr, uid, ids, context=context)[0]

        ## Return the actionable:
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "product.product",
            "res_id": obj.product_id.id,
            "type": "ir.actions.act_window",
            "target": "current",
            "context": context,
            "nodestroy": True
        }

    _columns = {
        "product_oem": fields.many2one("product.product", "OEM", select=True),
        "date_order": fields.related("order_id", "date_order", string="Order Date", readonly=True, type="datetime"),
        "currency_id": fields.function(get_currency, type="many2one", relation="res.currency", string="Currency"),
    }


SaleOrderLineModel()


class SaleOrderModel(osv.osv):
    _inherit = "sale.order"

    _columns = {
        "xremarks": fields.text("Remarks"),
        "xsalesman": fields.char("Salesman", size=128),
        "xdeliverydate": fields.char("Delivery Date", size=256),
    }


SaleOrderModel()

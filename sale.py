## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class SaleOrderLineModel(osv.osv):
    _inherit = "sale.order.line"

    def get_order_date_internal(self, cr, uid, id, field_names=None, arg=None, context=None):
        try:
            jj = self.pool.get('sale.order.line').read(cr, uid, id, ["order_id"], context=None)["order_id"][0]
            return self.pool.get('sale.order').read(cr, uid, jj, ["date_order"], context=None)["date_order"]
        except:
            pass
        return "#N/A"

    def get_order_date(self, cr, uid, ids, field_names=None, arg=None, context=None):
        return dict([(i, self.get_order_date_internal(cr, uid, i, field_names=None, arg=None, context=None)) for i in ids])

    _columns = {
        "product_oem": fields.many2one("product.product", "OEM", select=True),
        "order_date": fields.function(get_order_date, type="text", string="Order Date"),
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

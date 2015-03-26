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


    def write(self, cr, uid, ids, vals, context=None):
        retval = super(SaleOrderLineModel, self).write(cr, uid, ids, vals, context=context)
        ## Update taxes:
        print "Abbauv: ", retval, ids, vals
        return retval


SaleOrderLineModel()


class SaleOrderModel(osv.osv):
    _inherit = "sale.order"

    _columns = {
        "tax_id": fields.many2one("account.tax", 'Tax', domain=[('type_tax_use', '=', "sale")], change_default=True),
        "xremarks": fields.text("Remarks"),
        "xsalesman": fields.char("Salesman", size=128),
        "xdeliverydate": fields.char("Delivery Date", size=256),
    }

    def write(self, cr, uid, ids, vals, context=None):
        retval = super(SaleOrderModel, self).write(cr, uid, ids, vals, context=context)
        ## Update taxes:
        for id in ids:
            tax_id = self.search_read(cr, uid, [("id", "=", id)], fields=["tax_id"], context=context)[0]["tax_id"]
            if tax_id:
                lm = self.pool.get("sale.order.line")
                which = lm.search(cr, uid, [("order_id", "=", id)], context=context)
                print which
                lm.write(cr, uid, which, dict(tax_id=[(6, 0, [tax_id[0]])]), context=context)
        print "Saving: ", retval
        return retval


SaleOrderModel()

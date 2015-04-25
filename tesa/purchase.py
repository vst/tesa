## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class PurchaseOrderLineModel(osv.osv):
    _inherit = "purchase.order.line"

    def get_currency(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        for line in self.browse(cr, uid, ids):
            result[line.id] = line.order_id.currency_id
        return result

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
        "currency_id": fields.function(get_currency, type="many2one", relation="res.currency", string="Currency"),
    }

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
                            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
                            name=False, price_unit=False, state='draft', context=None):
        res = super(PurchaseOrderLineModel, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order, fiscal_position_id, date_planned,
            name, price_unit, state, context)

        product_obj = self.pool.get('product.product')
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id)
        context_partner = {'lang': partner.lang, 'partner_id': partner_id}
        product_obj = product_obj.browse(cr, uid, product_id, context=context_partner)

        res['value']['name'] = "[%s] %s" % (product_obj.default_code, product_obj.name)
        return res


PurchaseOrderLineModel()


class PurchaseOrderModel(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        "xremarks": fields.char("Reference/Description", size=128),
    }

PurchaseOrderModel()

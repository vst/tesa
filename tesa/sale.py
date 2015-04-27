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


    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
        ## Get from super:
        res = super(SaleOrderLineModel, self).product_id_change(
            cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)

        product_obj = self.pool.get('product.product')
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id)
        context_partner = {'lang': partner.lang, 'partner_id': partner_id}
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        if not flag:
            res['value']['name'] = "[%s] %s" % (product_obj.default_code, product_obj.name)
        return res


SaleOrderLineModel()


class SaleOrderModel(osv.osv):
    _inherit = "sale.order"

    _columns = {
        "stype": fields.selection(
            [
                ("cash", "Cash Sales"),
                ("local", "Local Sales"),
                ("export", "Export Sales"),
                ("NA", "Unknown"),
            ],
            "Sales Type",
            required=True,
            readonly=False,
            states={'draft': [('readonly', False)], 'done': [('readonly', True)]},
            help="""Used to indicate the type of the sales"""),
        "tax_id": fields.many2one("account.tax", 'Tax', domain=[('type_tax_use', '=', "sale")], change_default=True),
        "xchassis": fields.char("Chassis", size=128),
        "xcontact": fields.char("Contact Number", size=128),
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

    def _get_default_stype(self, cr, uid, context):
        return context["stype"] if "stype" in context else "local"

    def _get_default_tax_id(self, cr, uid, context):
        if context.get("stype") == "export":
            rate = 0
        else:
            rate = 0.07

        tax = self.pool.get("account.tax").search(cr, uid, [("amount", "=", rate), ("type_tax_use", "=", "sale"), ("active", "=", True)])
        if len(tax) > 0:
            return tax[0]
        return None

    def _get_default_pricelist_id(self, cr, uid, context):
        ccy = self.pool.get("res.currency").search(cr, uid, [("name", "=", "SGD")])
        if len(ccy) > 0:
            ccy = ccy[0]
        else:
            return None
        pl = self.pool.get("product.pricelist").search(cr, uid, [("currency_id", "=", ccy), ("type", "=", "sale"), ("active", "=", True)])
        if len(pl) > 0:
            return pl[0]
        return None

    _defaults = {
        "stype": _get_default_stype,
        "tax_id": _get_default_tax_id,
        "pricelist_id": _get_default_pricelist_id,
    }


SaleOrderModel()

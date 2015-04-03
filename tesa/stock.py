# -*- coding: utf-8 -*-
## Imports
from openerp.osv import fields, osv
import logging
import json

## Get the logger:
_logger = logging.getLogger(__name__)


class StockPickingModel(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        "sizing": fields.char("Package Size", size=256),
    }


StockPickingModel()


class ExtendedStockMove(osv.osv):
    _inherit = "stock.move"

    def get_related_sales_info(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            this = self.browse(cr, uid, id, context=context)
            related_oems = self.pool.get('product.product').read(cr, uid, this.product_id.id, ["related_oems"], context=None)["related_oems"]
            ## Get all the products to be searched:
            oems = list(set([this.product_id.id] + related_oems))

            ## Get the picking type ids:
            picking_type_ids = self.pool.get('stock.picking.type').search(cr, uid, [("name", "=", "Outgoing")], context=None)

            ## Get related pickings:
            related_ids = self.search(cr, uid, [("product_id", "in", oems),
                                                ("picking_type_id", "in", picking_type_ids),
                                                ("state", "in", ["waiting", "confirmed", "assigned"])], context=context)

            ## Append sales indormation:
            result[id] = []
            for sm in self.read(cr, uid, related_ids, ["product_id", "product_qty", "origin", "picking_id"]):
                ## Attempt to get the sales order:
                if sm["origin"]:
                    ## sales order:
                    so = self.pool.get("sale.order").search_read(cr, uid, [("name", "=", sm["origin"])], fields=["user_id", "partner_id"], limit=1, context=None)
                    sm["salesman"] = ""
                    sm["customer"] = ""
                    try:
                        sm["salesman"] = so[0]["user_id"][1]
                        sm["customer"] = so[0]["partner_id"][1]
                    except Exception, e:
                        print e
                result[id] += [sm]

            ## Prepare the string representation:
            def _item(item):
                item["customer"] = item["customer"].split("]")[0][1:]
                item["p"] = item["product_id"][1].split("]")[0][1:]
                item["picking"] = item["picking_id"][1]
                return u"» %(origin)s %(customer)s\n%(picking)s %(salesman)s\n%(p)s: %(product_qty)d" % item
            result[id] = "\n".join([_item(i) for i in result[id]])
            #result[id] = json.dumps(result[id])
        return result

    _columns = {
        "xpackage": fields.char("Pack", size=64),
        "related_sales_info": fields.function(get_related_sales_info, type="text", string="Related Sales Order Line"),
    }



ExtendedStockMove()

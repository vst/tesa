## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class PurchaseOrderLineModel(osv.osv):
    _inherit = "purchase.order.line"

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


PurchaseOrderLineModel()


class PurchaseOrderModel(osv.osv):
    _inherit = "purchase.order"


PurchaseOrderModel()

## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class InvoiceModel(osv.osv):
    _inherit = "account.invoice"

    def get_order(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        so = self.pool.get("sale.order")
        for line in self.browse(cr, uid, ids):
            if line.origin and line.origin != "":
                # Attempt to get it:
                item = so.search(cr, uid, [("name", "=", line.origin)],  context=context)
                if len(item) == 1:
                    result[line.id] = item[0]
                else:
                    result[line.id] = None
            else:
                result[line.id] = None
        return result

    _columns = {
        "order": fields.function(get_order, type="many2one", relation="sale.order", string="Order"),
    }


InvoiceModel()

## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class BrandModel(osv.osv):
    _name = "product.brand"
    _columns = {
        "manufactured": fields.char("Manufactured In", size=128),
        "name": fields.char("Name", size=128, required=True),
        "description": fields.text("Description"),
    }

    def name_get(self, cr, uid, ids, context=None):
        ## Check the argument type:
        if isinstance(ids, (int, long)):
            ids = [ids]

        ## Return immediately if no ids:
        if not len(ids):
            return []

        ## Declare the return value:
        res = []

        ## Read products and iterate:
        for product in self.read(cr, uid, ids, ["name"], context=context):
            name = ""
            if product.get("name", False):
                name = product.get("name")
            res.append((product["id"], name))

        ## Done, return:
        return res


BrandModel()

## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class StockPickingModel(osv.osv):
    _inherit = "stock.picking"

    _columns = {
        "sizing": fields.char("Package Size", size=256),
    }


StockPickingModel()

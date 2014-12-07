## Imports
from openerp.osv import fields, osv
import logging


## Get the logger:
_logger = logging.getLogger(__name__)


class SubpartModel(osv.osv):
    _name = "product.subpartline"

    _columns = {
        "product_id": fields.many2one("product.template", "Product", select=True, readonly=True),
        "subpart_id": fields.many2one("product.template", "Subpart", select=True),
        "unit_id": fields.many2one("product.uom", "Unit of Measure", select=True),
        "quantity": fields.float("Quantity"),
    }


SubpartModel()


class ProductTemplateModel(osv.osv):
    _inherit = "product.template"

    def get_related_oems(self, cr, uid, ids, field_names=None, arg=None, context=None):
        """
        Returns related OEMs for the product template:
        """
        ## Copy the context:
        context = context.copy()

        ## Declare the return value:
        result = {}

        ## If no IDs supplied, just return as is:
        if not ids:
            return result

        ## Iterate over IDs and populate the result value:
        for id in ids:
            ## Prepare the context:
            context["product_id"] = id

            ## Get the product template instance:
            product = self.pool.get("product.template")

            ## Declare a temporary container:
            tmpL = []

            ## Iterate get the product's reverse OEM ids:
            tmpL += self.read(cr, uid, id, ["reverse_oem_ids"], context=context).get("reverse_oem_ids")

            ## If no reverse OEM's then, attempt to get the reverses of the OEM (if set):
            if not tmpL:
                ## Get the OEM
                oem = self.read(cr, uid, id, ["oem"], context=context).get("oem")

                ## If set, get it's related oems:
                if oem:
                    tmpL += self.read(cr, uid, oem[0], ["related_oems"], context=context).get("related_oems")

            ## If tmpL is populated, we can safely add it's own:
            if tmpL:
                tmpL.append(id)

            ## Get the set and assign to the result value:
            result[id] = list(set(tmpL))

        ## Done, return with a smiley face:
        return result

    def get_stock_locations(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        context["only_with_stock"] = False
        for id in ids:
            context["product_id"] = id
            location_obj = self.pool.get("stock.location")
            result[id] = location_obj.search(cr, uid, [("usage", "=", "internal")], context=context)
        return result

    _columns = {
        ## Core price data:
        "special_sales_price": fields.float("Special Sales Price"),
        "minimum_sales_price": fields.float("Minimum Sales Price"),
        "export_sales_price": fields.float("Export Sales Price"),
        "minimum_cash_sales_price": fields.float("Minimum Cash Sales Price"),

        ## Core cost data:
        "manual_cost_price": fields.float("Manual Cost Price"),

        ## Auxiliary price data:
        "previous_local_deal_cost_price": fields.float("Previous Month Local Dealership Cost Price"),
        "current_local_deal_cost_price": fields.float("Current Month Local Dealership Cost Price"),
        "etk_cost_price": fields.float("ETK Cost Price"),
        "core_charges": fields.float("Core Charges"),
        "local_deal_discount_rate": fields.char("Local Dealership Discount Rate", size=128),
        "etk_discount_rate": fields.char("ETK Discount Rate", size=128),
        "application_code": fields.char("Application Code", size=256),

        ## Relations:
        "brand": fields.many2one("product.brand", "Brand", select=True),
        "oem": fields.many2one("product.template", "OEM", select=True),
        "reverse_oem_ids": fields.one2many("product.template", "oem", "OEMs", readonly=True),
        "subparts": fields.one2many("product.subpartline", "product_id", "Subparts"),

        ## Auxiliary data:
        "manufactured_in": fields.char("Manufactured In", size=128),
        "old_system_data": fields.text("Old System Data"),
        "weight_migrate": fields.char("Weight (Migrated)", size=256),

        ## Computed relational data:
        "related_oems": fields.function(get_related_oems, type="one2many", relation="product.template", string="Related OEMs"),
        "stock_locations": fields.function(get_stock_locations, type="one2many", relation="stock.location", string="Stock by Location"),

        ## Computed stock data:
        #"stock_A_real": fields.function(get_stock_A_real, type="double", string="Stock A (Real)"),
        #"stock_A_virtual": fields.function(get_stock_A_virtual, type="double", string="Stock A (Virtual)"),
        #"stock_B_real": fields.function(get_stock_B_real, type="double", string="Stock B (Real)"),
        #"stock_B_virtual": fields.function(get_stock_B_virtual, type="double", string="Stock B (Virtual)"),
        #"stock_C_real": fields.function(get_stock_C_real, type="double", string="Stock C (Real)"),
        #"stock_C_virtual": fields.function(get_stock_C_virtual, type="double", string="Stock C (Virtual)"),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Fixes the copy functionality.
        """
        ## If no default data is provided, set it to empty dict:
        if not default:
            default = {}

        ## Get the product:
        product = self.browse(cr, uid, id, context=context)

        ## Set the default code of the default dictionary:
        default["default_code"] = (product.default_code and product.default_code + " (copy)") or False

        ## Done, return with super method's result:
        return super(ExtendedModelProduct, self).copy(cr, uid, id, default=default, context=context)

    def browse_product_id_oem(self, cr, uid, ids, context):
        ## Check the argument type and make sure that it is a list:
        if isinstance(ids, (int, long)):
            ids = [ids]

        ## Get the product:
        product = self.browse(cr, uid, ids, context=context)[0]

        ## Return the view:
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.product',
            'res_id': product.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
            'nodestroy': False
        }


ProductTemplateModel()


class ProductVariantModel(osv.osv):
    _inherit = "product.product"

    _sql_constraints = [
        ("default_code_uniq", "unique(default_code)", "Product Reference (Part Number) must be unique!"),
    ]


ProductVariantModel()

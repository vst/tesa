## Imports
from StringIO import StringIO
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
import base64
import csv
import logging
import re


## Get the logger:
_logger = logging.getLogger(__name__)


class SubpartModel(osv.osv):
    _name = "product.subpartline"

    _columns = {
        "product_id": fields.many2one("product.product", "Product", select=True, readonly=True),
        "subpart_id": fields.many2one("product.product", "Subpart", select=True),
        "unit_id": fields.many2one("product.uom", "Unit of Measure", select=True),
        "quantity": fields.float("Quantity"),
    }


SubpartModel()


class ProductTemplateModel(osv.osv):
    _inherit = "product.template"

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

        ## Auxiliary data:
        "manufactured_in": fields.char("Manufactured In", size=128),
        "old_system_data": fields.text("Old System Data"),
        "weight_migrate": fields.char("Weight (Migrated)", size=256),

        ## Relations:
        "brand": fields.many2one("product.brand", "Brand", select=True),
    }


ProductTemplateModel()


class ProductVariantModel(osv.osv):
    _inherit = "product.product"

    _sql_constraints = [
        ("default_code_uniq", "unique(default_code)", "Product Reference (Part Number) must be unique!"),
    ]

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if len(name) < 3:
            return []
        print "Deneme", name, args, operator, context
        if not args:
            args = []

        ## Search for the default code:
        ids = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            if operator in positive_operators:
                ids = self.search(cr, user, [("default_code", "ilike", name.strip())] + args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)

        ## Exclude from the previous search and return the combination:
        super_result = []
        if limit is not None:
            super_result = super(ProductVariantModel, self).name_search(cr, user, name, args, operator, context, limit - len(result))
        else:
            super_result = super(ProductVariantModel, self).name_search(cr, user, name, args, operator, context)
        return result + [(i[0], "!" + i[1]) for i in super_result if not (i[0] in set(ids))]

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        ctx = dict(context or {}, create_product_product=True)
        return super(ProductVariantModel, self).create(cr, uid, vals, context=ctx)


    def _func_search_releated_oems(self, cr, uid, obj, name, criterion, context):
        ## Get the value, ignore field and op:
        field, op, value = criterion[0]

        ## First get items with default code:

        return [
            '|',
            ('oem.reverse_oem_ids.default_code','ilike', value),
            '|',
            ('reverse_oem_ids.default_code','ilike', value),
            '|',
            ('oem.default_code','ilike',value),
            ('default_code','ilike',value),
        ]

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
            product = self.pool.get("product.product")

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

    def get_stock_for_location(self, location, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            location_obj = self.pool.get("stock.location")\
                                    .search(cr, uid, [("complete_name", "=", "Physical Locations / " + location + " / Stock")],  context=context)
            if len(location_obj) == 0:
                result[id] = 0
                continue
            result[id] = sum([i["qty"] for i in
                              self.pool.get("stock.quant").search_read(cr,
                                                                       uid,
                                                                       [("product_id", "=", id), ("location_id", "=", location_obj[0])],
                                                                       fields=["qty"],
                                                                       context=context)])
        return result

    def get_stock_for_location_A(self, *args, **kwargs):
        return self.get_stock_for_location("A", *args, **kwargs)

    def get_stock_for_location_B(self, *args, **kwargs):
        return self.get_stock_for_location("B", *args, **kwargs)

    def get_stock_for_location_C(self, *args, **kwargs):
        return self.get_stock_for_location("C", *args, **kwargs)

    def get_stock_locations(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            location_obj = self.pool.get("stock.location")
            result[id] = location_obj.search(cr, uid, [("usage", "=", "internal")], context=context)
        return result


    _columns = {
        ## Relations:
        "oem": fields.many2one("product.product", "OEM", select=True),
        "reverse_oem_ids": fields.one2many("product.product", "oem", "OEMs", readonly=True),
        "subparts": fields.one2many("product.subpartline", "product_id", "Subparts"),

        ## Computed relational data:
        "related_oems": fields.function(get_related_oems, type="one2many", relation="product.product", string="Related OEMs", fnct_search=_func_search_releated_oems),
        "stock_locations": fields.function(get_stock_locations, type="one2many", relation="stock.location", string="Stock by Location"),

        ## Computed stock data:
        "stock_A_real": fields.function(get_stock_for_location_A, type="float", string="Stock A (Real)"),
        #"stock_A_virtual": fields.function(get_stock_A_virtual, type="float", string="Stock A (Virtual)"),
        "stock_B_real": fields.function(get_stock_for_location_B, type="float", string="Stock B (Real)"),
        #"stock_B_virtual": fields.function(get_stock_B_virtual, type="float", string="Stock B (Virtual)"),
        "stock_C_real": fields.function(get_stock_for_location_C, type="float", string="Stock C (Real)"),
        #"stock_C_virtual": fields.function(get_stock_C_virtual, type="float", string="Stock C (Virtual)"),
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
        return super(ProductVariantModel, self).copy(cr, uid, id, default=default, context=context)

    def browse_product_id_oem(self, cr, uid, ids, context):
        ## Check the argument type and make sure that it is a list:
        if isinstance(ids, (int, long)):
            ids = [ids]

        ## Get the product:
        product = self.browse(cr, uid, ids, context=context)[0]

        ## Return the view:
        ## TODO: Check the return value, should it be a list?
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

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            code = context.get('display_default_code', True) and d.get('default_code',False) or False
            if code:
                name = '%s' % (code,)
            else:
                name = d.get('name','')
            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and "%s (%s)" % (s.product_name, variant) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          }
                result.append(_name_get(mydict))
        return result


ProductVariantModel()


class SupplierInfoModel(osv.osv):
    _inherit = "product.supplierinfo"

    _columns = {
        "rep_price": fields.float("Rep Price"),
    }


SupplierInfoModel()


class ConfigProductUpload(osv.osv_memory):
    _name="config.product.upload"

    _columns = {
        "data": fields.binary("File"),
        "createp": fields.boolean("Create if it doesn't exist"),
    }

    _defaults = {
        "createp": False,
    }

    defaults = {
        "type": "product",
    }

    @classmethod
    def get_product(cls, product, wizard, cr, uid, context):
        ## Get the product model:
        product_model = wizard.pool.get("product.product")

        ## Get the product:
        product = product_model.search(cr, uid, [("default_code", "=", product.strip())], limit=1, context=context)

        ## Check result:
        if len(product) == 0:
            raise osv.except_osv(_("Error!"), _("Product could not be found: %s." % (product.strip(),)))

        ## Done, return:
        return product[0]

    @classmethod
    def get_brand(cls, brand, wizard, cr, uid, context):
        ## Get the brand model:
        brand_model = wizard.pool.get("product.brand")

        ## Get the brand:
        brand = brand_model.search(cr, uid, [("code", "=", brand.strip())], limit=1, context=context)

        ## Check result:
        if len(brand) == 0:
            raise osv.except_osv(_("Error!"), _("Brand could not be found: %s." % (brand.strip(),)))

        ## Done, return:
        return brand[0]

    @classmethod
    def get_uom(cls, uom, wizard, cr, uid, context):
        ## Get the uom model:
        uom_model = wizard.pool.get("product.uom")

        ## Get the uom:
        uom = uom_model.search(cr, uid, [("name", "=", uom.strip())], limit=1, context=context)

        ## Check result:
        if len(uom) == 0:
            raise osv.except_osv(_("Error!"), _("Unit of measure could not be found: %s." % (uom.strip(),)))

        ## Done, return:
        return uom[0]

    def clean_data(self, data, cr, uid, context):
        new_data = self.defaults.copy()
        for key in data:
            if key in self.mapper:
                new_data[key] = self.mapper[key](data[key], self, cr, uid, context)
            else:
                new_data[key] = data[key]
            if key == "uom_id":
                new_data["uom_po_id"] = new_data["uom_id"]
        return new_data

    def _update_or_create_product(self, data, cr, uid, context):
        _logger.info("Creating product %s" % (data["default_code"],))

        ## Get the product model:
        product_model = self.pool.get("product.product")

        ## Create the product:
        product = product_model.create(cr, uid, self.clean_data(data, cr, uid, context))

        ## Done, return product:
        return product

    def _update_product(self, data, cr, uid, context, createp=False):
        _logger.info("Updating product %s" % (data["default_code"],))

        ## Get the product model:
        product_model = self.pool.get("product.product")

        ## Get the product:
        product = product_model.search(cr, uid, [("default_code", "=", data["default_code"].strip())], limit=1, context=context)

        ## Check result:
        if len(product) == 0:
            if createp:
                return self._update_or_create_product(data, cr, uid, context)
            else:
                raise osv.except_osv(_("Error!"), _("Product could not be found: %s." % (data["default_code"].strip(),)))

        ## Create the product:
        product = product_model.write(cr, uid, product, self.clean_data(data, cr, uid, context))

        ## Done, return product:
        return product

    def upload_product(self, cr, uid, ids, context=None):
        ## Get the wizard:
        wizard = self.read(cr, uid, ids[0], ["data", "createp"], context=context)

        ## Get the data:
        data = base64.decodestring(wizard.get("data"))

        ## Get flag:
        create_flag = wizard.get("createp")

        ## Get the specs:
        specs = []
        try:
            specs = csv.DictReader(StringIO(data))
        except Exception, e:
            print e
            raise osv.except_osv(_("Error!"), _("Can not read the CSV file. Please check the format."))

        ## Iterate over lines and act accordingly:
        for line in specs:
            ## Check the default code:
            if (not "default_code" in line) or (line["default_code"].strip() == ""):
                raise osv.except_osv(_("Error!"), _("Required field 'default_code' cannot be found."))

            ## Update the product:
            self._update_product(line, cr, uid, context, create_flag)

        return {
            "type": "ir.actions.act_window_close",
         }


ConfigProductUpload.mapper = {
    "default_code": lambda x, y, a, b, c: x.strip(),
    "name": lambda x, y, a, b, c: x.strip(),
    "description": lambda x, y, a, b, c: x.strip(),
    "ean13": lambda x, y, a, b, c: x.strip(),
    "manufactured_in": lambda x, y, a, b, c: x.strip(),
    "application_code": lambda x, y, a, b, c: x.strip(),
    "weight_migrate": lambda x, y, a, b, c: x.strip(),
    "lst_price": lambda x, y, a, b, c: float(x.strip()),
    "minimum_cash_sales_price": lambda x, y, a, b, c: float(x.strip()),
    "export_sales_price": lambda x, y, a, b, c: float(x.strip()),
    "minimum_sales_price": lambda x, y, a, b, c: float(x.strip()),
    "special_sales_price": lambda x, y, a, b, c: float(x.strip()),
    "manual_cost_price": lambda x, y, a, b, c: float(x.strip()),
    "previous_local_deal_cost_price": lambda x, y, a, b, c: float(x.strip()),
    "current_local_deal_cost_price": lambda x, y, a, b, c: float(x.strip()),
    "etk_cost_price": lambda x, y, a, b, c: float(x.strip()),
    "core_charges": lambda x, y, a, b, c: float(x.strip()),
    "local_deal_discount_rate": lambda x, y, a, b, c: x.strip(),
    "etk_discount_rate": lambda x, y, a, b, c: x.strip(),
    "application_code": lambda x, y, a, b, c: x.strip(),
    "brand": ConfigProductUpload.get_brand,
    "oem": ConfigProductUpload.get_product,
    "uom_id": ConfigProductUpload.get_uom,
}

ConfigProductUpload()


class ConfigProductSupplierPriceUpload(osv.osv_memory):
    _name="config.product.supplierpriceupload"

    _columns = {
        "data": fields.binary("File"),
    }

    @classmethod
    def get_product(cls, product, wizard, cr, uid, context):
        ## Get the product model:
        product_model = wizard.pool.get("product.product")

        ## Get the product:
        product = product_model.search(cr, uid, [("default_code", "=", product.strip())], limit=1, context=context)

        ## Check result:
        if len(product) == 0:
            raise osv.except_osv(_("Error!"), _("Product could not be found: %s." % (product.strip(),)))

        ## Done, return:
        return product[0]

    @classmethod
    def update_supplierinfo(cls, cr, uid, context, model, product, supplier, price):
        ## Search for the item:
        item = model.search(cr, uid, [("product_tmpl_id", "=", product), ("name", "=", supplier)], limit=1, context=context)
        print product, supplier, price, item

        ## Update if it exists:
        if len(item) > 0:
            ## Yes, update:
            model.write(cr, uid, item[0], dict(rep_price=price))
        else:
            model.create(cr, uid, dict(rep_price=price, product_tmpl_id=product, name=supplier))


    def _update(self, data, cr, uid, context):
        _logger.info("Updating product price %s" % (data["default_code"],))

        ## Get the product model:
        product_model = self.pool.get("product.product")

        ## Get the product:
        product = product_model.search_read(cr, uid, [("default_code", "=", data["default_code"].strip())], fields=["product_tmpl_id"], limit=1, context=context)

        ## Check result:
        if len(product) == 0:
            _logger.info("Product not found %s." % (data["default_code"],))
            return

        ## Get the object:
        product = product[0]["product_tmpl_id"][0]

        ## Get the partner:
        partner_model = self.pool.get("res.partner")

        ## Get the partner:
        partner = partner_model.search(cr, uid, [("ref", "=", data["supplier"].strip())], limit=1, context=context)

        ## Check result:
        if len(partner) == 0:
            raise osv.except_osv(_("Error!"), _("Partner could not be found: %s." % (partner.strip(),)))

        ## Get the object:
        partner = partner[0]

        ## Get the product supplier info:
        self.update_supplierinfo(cr, uid, context, self.pool.get("product.supplierinfo"), product, partner, data["price"].strip())

        ## Done, return product:
        return product

    def upload_supplier_price_list(self, cr, uid, ids, context=None):
        ## Get the wizard:
        wizard = self.read(cr, uid, ids[0], ["data"], context=context)

        ## Get the data:
        data = base64.decodestring(wizard.get("data"))

        ## Get the specs:
        specs = []
        try:
            specs = csv.DictReader(StringIO(data))
        except Exception, e:
            print e
            raise osv.except_osv(_("Error!"), _("Can not read the CSV file. Please check the format."))

        ## Iterate over lines and act accordingly:
        for line in specs:
            ## Check the default code:
            if (not "default_code" in line) or (line["default_code"].strip() == "") or \
               (not "supplier" in line) or (line["supplier"].strip() == "") or \
               (not "price" in line) or (line["price"].strip() == ""):
                raise osv.except_osv(_("Error!"), _("Required fields 'default_code', 'supplier', 'price' could not be found."))

            ## Update the product:
            self._update(line, cr, uid, context)

        return {
            "type": "ir.actions.act_window_close",
         }


ConfigProductSupplierPriceUpload()

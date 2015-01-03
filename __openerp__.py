{
    "name": "tesa",
    "version": "0.0.5dev",
    "author": "Telosoft",
    "category": "Tools",
    "website": "http://www.telosoft.com",
    "description": """Provides an ERP Implementation and Customization Addon (Version 0.0.5dev)""",
    "depends": [
        "base",
        "account_accountant",
        "sale",
        "stock",
        "purchase",
        "hr",
        "contacts",
        "account_asset",
        "account_cancel",
        "stock_reserve_sale",
        "partner_credit_limit",
    ],
    "init_xml": [
    ],
    "update_xml": [
    ],
    "data": [
        "views/base.xml",
        "views/product.xml",
        "views/brand.xml",
        "views/partner.xml",
        "views/stock.xml",
        "views/sale.xml",
        "views/purchase.xml",
        "views/flowchart.xml",
        "views/_menu.xml",
    ],
    "qweb" : [
        "static/src/xml/base.xml",
        "static/src/xml/flowchart.xml",
    ],
    "js": [
        "static/src/js/tesa.js"
    ],
    "css": [
        "static/src/css/tesa.css"
    ],
    "installable": True,
    "auto_install": False,
}

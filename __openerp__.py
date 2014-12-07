{
    "name": "tesa",
    "version": "0.0.1",
    "author": "Telosoft",
    "category": "Tools",
    "website": "http://www.telosoft.com",
    "description": """Provides an ERP Implementation and Customization Addon""",
    "depends": [
        "base",
        "web",
        "product",
        "account_accountant",
        "hr",
        "contacts",
        "stock",
        "sale",
        "purchase",
        "account_asset",
        "account_cancel",
    ],
    "init_xml": [
    ],
    "update_xml": [
    ],
    "data": [
        "views/product.xml",
        "views/brand.xml",
        "views/partner.xml",
        "views/stock.xml",
        "views/sale.xml",
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

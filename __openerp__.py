{
    "name": "TESA",
    "version": "0.0.1",
    "author": "Telosoft",
    "category": "Tools",
    "website": "http://www.telosoft.com",
    "description": """Provides an ERP Implementation and Customization Addon for ESA""",
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
        "views/product.xml"
    ],
    "qweb" : [
    ],
    "js": [
    ],
    "css": [
    ],
    "installable": True,
    "auto_install": False,
}

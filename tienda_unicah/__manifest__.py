{
    "name": "Tienda UNICAH",
    "version": "20.0.1.0.0",
    "summary": "Datos universitarios, convenios y ahorro para Ventas UNICAH",
    "category": "Sales/Sales",
    "author": "UNICAH",
    "depends": ["sale_management", "ventas_unicah"],
    "data": [
        "security/ir.access.csv",
        "data/tienda_convenio_data.xml",
        "views/res_partner_views.xml",
        "views/tienda_convenio_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}

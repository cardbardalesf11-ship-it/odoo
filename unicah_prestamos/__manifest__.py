{
    "name": "Préstamos UNICAH",
    "version": "20.0.1.0.0",
    "summary": "Control de préstamo de equipos universitarios",
    "category": "Sales/Sales",
    "author": "UNICAH",
    "depends": ["sale_management"],
    "data": [
        "security/ir.access.csv",
        "data/ir_sequence_data.xml",
        "views/unicah_prestamo_views.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}

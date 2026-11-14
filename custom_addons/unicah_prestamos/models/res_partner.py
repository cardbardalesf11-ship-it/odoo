from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    prestamo_ids = fields.One2many(
        "unicah.prestamo",
        "solicitante_id",
        string="Préstamos de equipo",
    )

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


TIPOS_CLIENTE = [
    ("estudiante", "Estudiante"),
    ("docente", "Docente"),
    ("administrativo", "Administrativo"),
    ("externo", "Externo"),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    tipo_cliente = fields.Selection(
        TIPOS_CLIENTE,
        string="Tipo de cliente",
    )
    numero_cuenta = fields.Char(
        string="Número de cuenta",
    )
    carrera = fields.Char(
        string="Carrera",
    )

    @api.constrains("tipo_cliente", "numero_cuenta")
    def _check_numero_cuenta_estudiante(self):
        for partner in self:
            if partner.tipo_cliente != "estudiante":
                continue
            if not partner.numero_cuenta:
                raise ValidationError(
                    "El número de cuenta es obligatorio para los estudiantes."
                )
            if not re.fullmatch(r"\d{10}", partner.numero_cuenta):
                raise ValidationError(
                    "El número de cuenta del estudiante debe contener "
                    "exactamente 10 dígitos numéricos."
                )

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .res_partner import TIPOS_CLIENTE


class TiendaConvenio(models.Model):
    _name = "tienda.convenio"
    _description = "Convenio UNICAH"
    _order = "name"

    name = fields.Char(
        string="Nombre",
        required=True,
    )
    tipo_cliente = fields.Selection(
        TIPOS_CLIENTE,
        string="Tipo de cliente",
        required=True,
    )
    porcentaje = fields.Float(
        string="Porcentaje de descuento",
        required=True,
        digits=(5, 2),
    )
    fecha_inicio = fields.Date(
        string="Fecha de inicio",
        required=True,
        default=fields.Date.context_today,
    )
    fecha_fin = fields.Date(
        string="Fecha de finalización",
        required=True,
    )
    active = fields.Boolean(
        string="Activo",
        default=True,
    )

    @api.constrains("porcentaje")
    def _check_porcentaje(self):
        for convenio in self:
            if convenio.porcentaje <= 0:
                raise ValidationError(
                    "El porcentaje del convenio debe ser mayor que 0."
                )
            if convenio.porcentaje > 40:
                raise ValidationError(
                    "El porcentaje del convenio no puede superar el 40 %."
                )

    @api.constrains("fecha_inicio", "fecha_fin")
    def _check_fechas(self):
        for convenio in self:
            if (
                convenio.fecha_inicio
                and convenio.fecha_fin
                and convenio.fecha_fin < convenio.fecha_inicio
            ):
                raise ValidationError(
                    "La fecha de finalización no puede ser anterior "
                    "a la fecha de inicio."
                )

    def _esta_vigente(self, fecha=None):
        self.ensure_one()
        fecha = fecha or fields.Date.context_today(self)
        return (
            (not self.fecha_inicio or self.fecha_inicio <= fecha)
            and (not self.fecha_fin or self.fecha_fin >= fecha)
        )

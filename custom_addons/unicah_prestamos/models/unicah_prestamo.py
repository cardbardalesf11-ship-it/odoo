from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class UnicahPrestamo(models.Model):
    _name = "unicah.prestamo"
    _description = "Préstamo de equipo universitario"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "fecha_prestamo desc, id desc"

    name = fields.Char(
        string="Referencia",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "unicah.prestamo"
        )
        or "Nuevo",
    )
    solicitante_id = fields.Many2one(
        "res.partner",
        string="Solicitante",
        required=True,
        tracking=True,
    )
    equipo = fields.Char(
        string="Equipo",
        required=True,
        tracking=True,
    )
    fecha_prestamo = fields.Date(
        string="Fecha de préstamo",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    fecha_devolucion = fields.Date(
        string="Fecha de devolución",
        required=True,
        tracking=True,
    )
    estado = fields.Selection(
        [
            ("solicitado", "Solicitado"),
            ("entregado", "Entregado"),
            ("devuelto", "Devuelto"),
            ("vencido", "Vencido"),
        ],
        string="Estado",
        default="solicitado",
        required=True,
        tracking=True,
    )
    dias_prestamo = fields.Integer(
        string="Días de préstamo",
        compute="_compute_dias_prestamo",
        store=True,
    )

    @api.depends("fecha_prestamo", "fecha_devolucion")
    def _compute_dias_prestamo(self):
        for prestamo in self:
            if prestamo.fecha_prestamo and prestamo.fecha_devolucion:
                prestamo.dias_prestamo = (
                    prestamo.fecha_devolucion - prestamo.fecha_prestamo
                ).days
            else:
                prestamo.dias_prestamo = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("solicitante_id") or not vals.get("equipo"):
                raise ValidationError(
                    "Todo préstamo debe tener un solicitante y un equipo."
                )
        return super().create(vals_list)

    @api.constrains("fecha_prestamo", "fecha_devolucion")
    def _check_fechas(self):
        for prestamo in self:
            if (
                prestamo.fecha_prestamo
                and prestamo.fecha_devolucion
                and prestamo.fecha_devolucion < prestamo.fecha_prestamo
            ):
                raise ValidationError(
                    "La fecha de devolución no puede ser anterior "
                    "a la fecha del préstamo."
                )

    @api.constrains("solicitante_id", "equipo")
    def _check_solicitante_equipo(self):
        for prestamo in self:
            if not prestamo.solicitante_id or not prestamo.equipo:
                raise ValidationError(
                    "Todo préstamo debe tener un solicitante y un equipo."
                )

    def action_entregar(self):
        for prestamo in self:
            if prestamo.estado == "devuelto":
                raise UserError(
                    "No se puede entregar un préstamo que ya fue devuelto."
                )
            if prestamo.estado != "solicitado":
                raise UserError(
                    "Solo se pueden entregar préstamos en estado Solicitado."
                )
            prestamo.estado = "entregado"
        return True

    def action_devolver(self):
        for prestamo in self:
            if prestamo.estado == "solicitado":
                raise UserError(
                    "No se puede devolver un préstamo que todavía "
                    "no ha sido entregado."
                )
            if prestamo.estado == "devuelto":
                raise UserError("Este préstamo ya fue devuelto.")
            prestamo.estado = "devuelto"
        return True

    def action_marcar_vencido(self):
        for prestamo in self:
            if prestamo.estado != "entregado":
                raise UserError(
                    "Solo se pueden marcar como vencidos los préstamos "
                    "que están entregados."
                )
            if (
                not prestamo.fecha_devolucion
                or prestamo.fecha_devolucion >= fields.Date.context_today(prestamo)
            ):
                raise UserError(
                    "La fecha de devolución todavía no ha pasado."
                )
            prestamo.estado = "vencido"
        return True

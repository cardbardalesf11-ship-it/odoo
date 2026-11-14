from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .res_partner import CANALES_VENTA


class SaleOrder(models.Model):
    _inherit = "sale.order"

    canal_venta = fields.Selection(
        CANALES_VENTA,
        string="Canal de venta",
        compute="_compute_canal_venta",
        store=True,
        readonly=False,
    )

    total_unidades = fields.Float(
        string="Total de unidades",
        compute="_compute_total_unidades",
        store=True,
    )

    requiere_aprobacion = fields.Boolean(
        string="Requiere aprobación",
        compute="_compute_requiere_aprobacion",
        store=True,
    )

    aprobado_por = fields.Many2one(
        "res.users",
        string="Aprobado por",
        readonly=True,
        copy=False,
    )

    pendiente_aprobacion = fields.Boolean(
        string="Pendiente de aprobación",
        compute="_compute_pendiente_aprobacion",
    )

    @api.depends("partner_id", "partner_id.canal_preferido")
    def _compute_canal_venta(self):
        for order in self:
            order.canal_venta = order.partner_id.canal_preferido

    @api.depends("order_line.product_uom_qty")
    def _compute_total_unidades(self):
        for order in self:
            order.total_unidades = sum(
                order.order_line.mapped("product_uom_qty")
            )

    @api.depends("amount_total")
    def _compute_requiere_aprobacion(self):
        for order in self:
            order.requiere_aprobacion = order.amount_total > 50000

    @api.depends("requiere_aprobacion", "aprobado_por", "state")
    def _compute_pendiente_aprobacion(self):
        for order in self:
            order.pendiente_aprobacion = (
                order.requiere_aprobacion
                and not order.aprobado_por
                and order.state in ("draft", "sent")
            )

    def action_aprobar(self):
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            raise AccessError(
                "Solo un administrador de ventas puede aprobar pedidos."
            )

        for order in self:
            order.write({"aprobado_por": self.env.user.id})

    def action_confirm(self):
        for order in self:
            if order.requiere_aprobacion and not order.aprobado_por:
                raise UserError(
                    "Este pedido supera los 50,000 y necesita "
                    "la aprobación de un administrador de ventas."
                )

        return super().action_confirm()

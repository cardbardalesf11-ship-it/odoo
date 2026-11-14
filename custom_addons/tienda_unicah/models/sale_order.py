from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tipo_cliente = fields.Selection(
        related="partner_id.tipo_cliente",
        string="Tipo de cliente",
        store=True,
        readonly=True,
    )
    convenio_id = fields.Many2one(
        "tienda.convenio",
        string="Convenio UNICAH",
        domain="[('tipo_cliente', '=', tipo_cliente), ('active', '=', True)]",
        copy=False,
    )
    convenio_aplicado = fields.Boolean(
        string="Convenio aplicado",
        default=False,
        copy=False,
        readonly=True,
    )
    monto_ahorro = fields.Monetary(
        string="Ahorro por convenio",
        compute="_compute_monto_ahorro",
        store=True,
        currency_field="currency_id",
    )

    @api.depends(
        "convenio_aplicado",
        "order_line.price_unit",
        "order_line.product_uom_qty",
        "order_line.discount",
        "order_line.display_type",
        "order_line.product_id",
        "currency_id",
    )
    def _compute_monto_ahorro(self):
        for order in self:
            ahorro = 0.0
            if order.convenio_aplicado:
                for line in order.order_line:
                    if line.display_type or not line.product_id:
                        continue
                    ahorro += (
                        line.price_unit
                        * line.product_uom_qty
                        * line.discount
                        / 100.0
                    )
            order.monto_ahorro = ahorro

    @api.onchange("partner_id")
    def _onchange_partner_id_convenio(self):
        self.convenio_id = False
        self.convenio_aplicado = False
        if not self.partner_id or not self.partner_id.tipo_cliente:
            return
        hoy = fields.Date.context_today(self)
        convenio = self.env["tienda.convenio"].search(
            [
                ("tipo_cliente", "=", self.partner_id.tipo_cliente),
                ("active", "=", True),
                ("fecha_inicio", "<=", hoy),
                ("fecha_fin", ">=", hoy),
            ],
            order="porcentaje desc",
            limit=1,
        )
        if convenio:
            self.convenio_id = convenio

    @api.onchange("convenio_id")
    def _onchange_convenio_id(self):
        self.convenio_aplicado = False

    def action_aplicar_convenio(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError(
                    "Solo se puede aplicar un convenio a una cotización."
                )
            if not order.convenio_id:
                raise UserError(
                    "Seleccione un convenio antes de aplicarlo."
                )
            if order.convenio_aplicado:
                raise UserError(
                    "El convenio ya fue aplicado a este pedido. "
                    "Seleccione otro convenio si desea cambiarlo."
                )

            lineas_producto = order.order_line.filtered(
                lambda line: not line.display_type and line.product_id
            )
            if not lineas_producto:
                raise UserError(
                    "El pedido no tiene líneas de producto a las que "
                    "aplicar el convenio."
                )

            porcentaje = order.convenio_id.porcentaje
            lineas_producto.write({"discount": porcentaje})
            order.convenio_aplicado = True
            order.message_post(
                body=(
                    "Se aplicó el convenio <b>%s</b> con un descuento "
                    "del %s %% a %s línea(s) de producto."
                )
                % (
                    order.convenio_id.name,
                    porcentaje,
                    len(lineas_producto),
                )
            )
        return True

    def action_confirm(self):
        for order in self:
            if order.tipo_cliente == "estudiante":
                unidades = sum(
                    order.order_line.filtered(
                        lambda line: not line.display_type and line.product_id
                    ).mapped("product_uom_qty")
                )
                if unidades > 10:
                    raise UserError(
                        "Los pedidos de estudiantes no pueden superar "
                        "las 10 unidades de productos. "
                        "Este pedido tiene %s unidades." % unidades
                    )
        return super().action_confirm()

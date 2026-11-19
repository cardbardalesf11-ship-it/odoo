from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVentasUnicah(TransactionCase):
    """Pruebas funcionales del módulo ventas_unicah.

    Se ejecutan dentro de una transacción que Odoo revierte al terminar,
    por lo que no dejan datos en la base de práctica.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                mail_create_nolog=True,
                no_reset_password=True,
            )
        )

        cls.partner_tienda = cls.env["res.partner"].create({
            "name": "Cliente Tienda (prueba)",
            "canal_preferido": "tienda",
        })
        cls.partner_telefono = cls.env["res.partner"].create({
            "name": "Cliente Teléfono (prueba)",
            "canal_preferido": "telefono",
        })

        cls.producto = cls.env["product.product"].create({
            "name": "Laptop (prueba)",
            "list_price": 30000.0,
            "taxes_id": [(5, 0, 0)],
        })

        group_user = cls.env.ref("base.group_user")
        group_manager = cls.env.ref("sales_team.group_sale_manager")
        group_salesman = cls.env.ref("sales_team.group_sale_salesman")

        cls.gerente = cls.env["res.users"].create({
            "name": "Gerente de Ventas (prueba)",
            "login": "gerente_ventas_prueba",
            "email": "gerente_prueba@example.com",
            "group_ids": [(6, 0, [group_user.id, group_manager.id])],
        })
        cls.vendedor = cls.env["res.users"].create({
            "name": "Vendedor (prueba)",
            "login": "vendedor_prueba",
            "email": "vendedor_prueba@example.com",
            "group_ids": [(6, 0, [group_user.id, group_salesman.id])],
        })

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _crear_pedido(self, partner=None, cantidad=1.0, precio=30000.0, user=None):
        """Crea una cotización con una línea del producto de prueba."""
        model = self.env["sale.order"]
        if user:
            model = model.with_user(user)
        return model.create({
            "partner_id": (partner or self.partner_tienda).id,
            "order_line": [
                (0, 0, {
                    "product_id": self.producto.id,
                    "product_uom_qty": cantidad,
                    "price_unit": precio,
                }),
            ],
        })

    # ------------------------------------------------------------------
    # Contactos
    # ------------------------------------------------------------------
    def test_01_canal_preferido_cuatro_opciones(self):
        """El cliente tiene el canal preferido con las cuatro opciones."""
        seleccion = self.env["res.partner"]._fields["canal_preferido"].selection
        valores = [clave for clave, _etiqueta in seleccion]
        self.assertEqual(
            valores, ["tienda", "telefono", "web", "distribuidor"]
        )
        self.assertEqual(self.partner_tienda.canal_preferido, "tienda")
        # Las cuatro opciones se pueden guardar.
        for clave in valores:
            self.partner_tienda.canal_preferido = clave
        self.assertEqual(self.partner_tienda.canal_preferido, "distribuidor")

    # ------------------------------------------------------------------
    # Canal de venta y total de unidades
    # ------------------------------------------------------------------
    def test_02_canal_venta_se_toma_del_cliente(self):
        """El canal del pedido se calcula desde el cliente y se puede cambiar."""
        pedido = self._crear_pedido(self.partner_telefono)
        self.assertEqual(pedido.canal_venta, "telefono")

        # Al cambiar el cliente se vuelve a calcular.
        pedido.partner_id = self.partner_tienda
        self.assertEqual(pedido.canal_venta, "tienda")

        # El usuario puede sobrescribirlo en el pedido concreto.
        pedido.canal_venta = "distribuidor"
        pedido.flush_recordset()
        self.assertEqual(pedido.canal_venta, "distribuidor")

        # Y se conserva al recargar desde la base de datos.
        pedido.invalidate_recordset()
        self.assertEqual(pedido.canal_venta, "distribuidor")

    def test_03_total_unidades_suma_lineas(self):
        """Total de unidades suma las cantidades de todas las líneas."""
        pedido = self._crear_pedido(cantidad=3.0)
        self.assertEqual(pedido.total_unidades, 3.0)

        pedido.write({
            "order_line": [
                (0, 0, {
                    "product_id": self.producto.id,
                    "product_uom_qty": 2.0,
                    "price_unit": 30000.0,
                }),
            ],
        })
        self.assertEqual(pedido.total_unidades, 5.0)

        # Al modificar la cantidad de una línea se recalcula.
        pedido.order_line[0].product_uom_qty = 10.0
        self.assertEqual(pedido.total_unidades, 12.0)

        # Al eliminar una línea también se recalcula.
        pedido.order_line[1].unlink()
        pedido.invalidate_recordset()
        self.assertEqual(pedido.total_unidades, 10.0)

    # ------------------------------------------------------------------
    # Requiere aprobación
    # ------------------------------------------------------------------
    def test_04_requiere_aprobacion_limite(self):
        """El límite es estricto: 50,000 no requiere, más de 50,000 sí."""
        justo = self._crear_pedido(cantidad=1.0, precio=50000.0)
        self.assertEqual(justo.amount_total, 50000.0)
        self.assertFalse(justo.requiere_aprobacion)

        arriba = self._crear_pedido(cantidad=1.0, precio=50000.01)
        self.assertTrue(arriba.requiere_aprobacion)

        grande = self._crear_pedido(cantidad=3.0)
        self.assertEqual(grande.amount_total, 90000.0)
        self.assertTrue(grande.requiere_aprobacion)

    def test_05_pendiente_aprobacion(self):
        """Pendiente solo mientras no haya aprobación y siga en cotización."""
        pedido = self._crear_pedido(cantidad=3.0)
        self.assertTrue(pedido.pendiente_aprobacion)

        self.env["sale.order"].with_user(self.gerente).browse(
            pedido.id
        ).action_aprobar()
        self.assertFalse(pedido.pendiente_aprobacion)

    # ------------------------------------------------------------------
    # Flujo de confirmación
    # ------------------------------------------------------------------
    def test_06_pedido_pequeno_confirma_sin_aprobacion(self):
        """Un pedido que no supera el límite sigue su flujo normal."""
        pedido = self._crear_pedido(cantidad=1.0)
        self.assertFalse(pedido.requiere_aprobacion)
        pedido.action_confirm()
        self.assertEqual(pedido.state, "sale")

    def test_07_pedido_grande_bloqueado_sin_aprobacion(self):
        """Un pedido grande no se confirma mientras no esté aprobado."""
        pedido = self._crear_pedido(cantidad=3.0)
        with self.assertRaises(UserError):
            pedido.action_confirm()
        self.assertEqual(pedido.state, "draft")
        self.assertFalse(pedido.aprobado_por)

    def test_08_gerente_aprueba_y_luego_confirma(self):
        """El administrador de ventas aprueba y el pedido se confirma."""
        pedido = self._crear_pedido(cantidad=3.0)
        pedido.with_user(self.gerente).action_aprobar()

        self.assertEqual(pedido.aprobado_por, self.gerente)
        self.assertFalse(pedido.pendiente_aprobacion)

        pedido.action_confirm()
        self.assertEqual(pedido.state, "sale")

    def test_09_vendedor_no_puede_aprobar(self):
        """Un vendedor sin rol de administrador no puede aprobar."""
        pedido = self._crear_pedido(cantidad=3.0, user=self.vendedor)
        self.assertFalse(
            self.vendedor.has_group("sales_team.group_sale_manager")
        )
        with self.assertRaises(AccessError):
            pedido.with_user(self.vendedor).action_aprobar()
        self.assertFalse(pedido.aprobado_por)

        # Y tampoco puede confirmarlo saltándose la aprobación.
        with self.assertRaises(UserError):
            pedido.with_user(self.vendedor).action_confirm()

    def test_10_duplicado_no_copia_aprobacion(self):
        """Al duplicar un pedido aprobado, la copia no queda aprobada."""
        pedido = self._crear_pedido(cantidad=3.0)
        pedido.with_user(self.gerente).action_aprobar()
        self.assertEqual(pedido.aprobado_por, self.gerente)

        copia = pedido.copy()
        self.assertFalse(copia.aprobado_por)
        self.assertTrue(copia.pendiente_aprobacion)

    # ------------------------------------------------------------------
    # Vistas, filtros y agrupaciones
    # ------------------------------------------------------------------
    def test_11_vistas_heredadas_instaladas(self):
        """Las vistas heredadas existen y contienen los elementos pedidos."""
        form = self.env.ref("ventas_unicah.view_order_form_ventas_unicah")
        self.assertIn("action_aprobar", form.arch)
        self.assertIn("canal_venta", form.arch)
        self.assertIn("total_unidades", form.arch)

        lista = self.env.ref("ventas_unicah.sale_order_tree_ventas_unicah")
        self.assertIn('sum="Total"', lista.arch)

        busqueda = self.env.ref(
            "ventas_unicah.view_sales_order_filter_ventas_unicah"
        )
        self.assertIn("requiere_aprobacion", busqueda.arch)
        self.assertIn("agrupar_canal", busqueda.arch)
        self.assertIn("group_by", busqueda.arch)

        partner_form = self.env.ref(
            "ventas_unicah.view_partner_form_canal_preferido"
        )
        self.assertIn("canal_preferido", partner_form.arch)

    def test_12_busqueda_por_canal_y_aprobacion(self):
        """Los campos calculados se pueden buscar y filtrar."""
        grande = self._crear_pedido(cantidad=3.0)
        pequeno = self._crear_pedido(cantidad=1.0)
        self.env["sale.order"].flush_model()

        pendientes = self.env["sale.order"].search([
            ("id", "in", (grande | pequeno).ids),
            ("requiere_aprobacion", "=", True),
        ])
        self.assertIn(grande, pendientes)
        self.assertNotIn(pequeno, pendientes)

        del_telefono = self.env["sale.order"].search([
            ("id", "in", (grande | pequeno).ids),
            ("canal_venta", "=", "tienda"),
        ])
        self.assertIn(grande, del_telefono)

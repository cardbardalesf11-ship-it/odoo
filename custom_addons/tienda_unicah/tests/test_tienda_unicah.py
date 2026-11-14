from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestTiendaUnicah(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.convenio_model = cls.env["tienda.convenio"]
        cls.order_model = cls.env["sale.order"]
        cls.product_model = cls.env["product.product"]

        cls.producto_a = cls.product_model.create(
            {
                "name": "Producto de prueba A",
                "list_price": 100.0,
                "sale_ok": True,
            }
        )
        cls.producto_b = cls.product_model.create(
            {
                "name": "Producto de prueba B",
                "list_price": 50.0,
                "sale_ok": True,
            }
        )
        cls.estudiante = cls.partner_model.create(
            {
                "name": "Estudiante de prueba",
                "tipo_cliente": "estudiante",
                "numero_cuenta": "2026123456",
                "carrera": "Ingeniería en Sistemas",
            }
        )
        cls.docente = cls.partner_model.create(
            {
                "name": "Docente de prueba",
                "tipo_cliente": "docente",
            }
        )

    def _crear_pedido(self, partner, cantidades):
        lineas = []
        for producto, cantidad in cantidades:
            lineas.append(
                (
                    0,
                    0,
                    {
                        "product_id": producto.id,
                        "product_uom_qty": cantidad,
                    },
                )
            )
        return self.order_model.create(
            {"partner_id": partner.id, "order_line": lineas}
        )

    def test_parte_1_estudiante_y_docente(self):
        self.assertEqual(self.estudiante.tipo_cliente, "estudiante")
        self.assertEqual(self.estudiante.numero_cuenta, "2026123456")
        self.assertEqual(self.estudiante.carrera, "Ingeniería en Sistemas")
        self.assertEqual(self.docente.tipo_cliente, "docente")
        self.assertFalse(self.docente.numero_cuenta)

    def test_parte_1_cuenta_invalida(self):
        with self.assertRaises(ValidationError):
            self.partner_model.create(
                {
                    "name": "Estudiante con cuenta corta",
                    "tipo_cliente": "estudiante",
                    "numero_cuenta": "12345678",
                }
            )

    def test_parte_1_cuenta_obligatoria(self):
        with self.assertRaises(ValidationError):
            self.partner_model.create(
                {
                    "name": "Estudiante sin cuenta",
                    "tipo_cliente": "estudiante",
                }
            )

    def test_parte_2_convenios_iniciales(self):
        estudiantil = self.env.ref("tienda_unicah.convenio_estudiantil")
        docente = self.env.ref("tienda_unicah.convenio_docente")
        self.assertEqual(estudiantil.porcentaje, 15)
        self.assertEqual(estudiantil.tipo_cliente, "estudiante")
        self.assertEqual(docente.porcentaje, 10)
        self.assertEqual(docente.tipo_cliente, "docente")

    def test_parte_2_convenio_administrativo(self):
        convenio = self.convenio_model.create(
            {
                "name": "Convenio administrativo",
                "tipo_cliente": "administrativo",
                "porcentaje": 5,
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-12-31",
            }
        )
        self.assertEqual(convenio.porcentaje, 5)
        self.assertTrue(convenio.active)

    def test_parte_2_permisos_convenios(self):
        salesman_group = self.env.ref("sales_team.group_sale_salesman")
        manager_group = self.env.ref("sales_team.group_sale_manager")

        vendedor = self.env["res.users"].create(
            {
                "name": "Vendedor de prueba",
                "login": "vendedor_prueba_tienda_unicah",
                "email": "vendedor_prueba@example.com",
                "group_ids": [(6, 0, [salesman_group.id])],
            }
        )
        administrador = self.env["res.users"].create(
            {
                "name": "Administrador de prueba",
                "login": "admin_prueba_tienda_unicah",
                "email": "admin_prueba@example.com",
                "group_ids": [(6, 0, [manager_group.id])],
            }
        )

        convenios_vendedor = self.convenio_model.with_user(vendedor)
        self.assertTrue(convenios_vendedor.has_access("read"))
        self.assertFalse(convenios_vendedor.has_access("write"))
        self.assertFalse(convenios_vendedor.has_access("create"))
        self.assertFalse(convenios_vendedor.has_access("unlink"))

        convenios_admin = self.convenio_model.with_user(administrador)
        self.assertTrue(convenios_admin.has_access("read"))
        self.assertTrue(convenios_admin.has_access("write"))
        self.assertTrue(convenios_admin.has_access("create"))
        self.assertTrue(convenios_admin.has_access("unlink"))

    def test_parte_4_porcentaje_convenio(self):
        with self.assertRaises(ValidationError):
            self.convenio_model.create(
                {
                    "name": "Convenio cero",
                    "tipo_cliente": "externo",
                    "porcentaje": 0,
                    "fecha_inicio": "2026-01-01",
                    "fecha_fin": "2026-12-31",
                }
            )
        with self.assertRaises(ValidationError):
            self.convenio_model.create(
                {
                    "name": "Convenio excedido",
                    "tipo_cliente": "externo",
                    "porcentaje": 50,
                    "fecha_inicio": "2026-01-01",
                    "fecha_fin": "2026-12-31",
                }
            )

    def test_parte_4_fechas_convenio(self):
        with self.assertRaises(ValidationError):
            self.convenio_model.create(
                {
                    "name": "Convenio con fechas invertidas",
                    "tipo_cliente": "externo",
                    "porcentaje": 10,
                    "fecha_inicio": "2026-12-31",
                    "fecha_fin": "2026-01-01",
                }
            )

    def test_parte_3_propuesta_y_aplicacion_convenio(self):
        pedido = self._crear_pedido(
            self.estudiante,
            [(self.producto_a, 2), (self.producto_b, 3)],
        )
        pedido.order_line.create(
            {
                "order_id": pedido.id,
                "display_type": "line_section",
                "name": "Sección de prueba",
            }
        )

        pedido._onchange_partner_id_convenio()
        self.assertEqual(
            pedido.convenio_id,
            self.env.ref("tienda_unicah.convenio_estudiantil"),
        )

        pedido.action_aplicar_convenio()
        self.assertTrue(pedido.convenio_aplicado)

        lineas_producto = pedido.order_line.filtered(
            lambda line: not line.display_type and line.product_id
        )
        self.assertEqual(len(lineas_producto), 2)
        for linea in lineas_producto:
            self.assertEqual(linea.discount, 15)

        seccion = pedido.order_line.filtered(
            lambda line: line.display_type == "line_section"
        )
        self.assertEqual(seccion.discount, 0)

        self.assertIn(
            "Se aplicó el convenio",
            pedido.message_ids[0].body,
        )

        with self.assertRaises(UserError):
            pedido.action_aplicar_convenio()

    def test_parte_5_monto_ahorro(self):
        pedido = self._crear_pedido(
            self.estudiante,
            [(self.producto_a, 2), (self.producto_b, 3)],
        )
        pedido.order_line.create(
            {
                "order_id": pedido.id,
                "display_type": "line_note",
                "name": "Nota de prueba",
            }
        )
        pedido.convenio_id = self.env.ref("tienda_unicah.convenio_estudiantil")
        pedido.action_aplicar_convenio()

        # 2 x 100 x 15 % = 30 y 3 x 50 x 15 % = 22.5
        self.assertEqual(pedido.monto_ahorro, 52.5)
        self.assertEqual(pedido.currency_id, pedido.company_id.currency_id)

    def test_parte_4_limite_estudiantes(self):
        pedido = self._crear_pedido(self.estudiante, [(self.producto_a, 12)])
        pedido.order_line.create(
            {
                "order_id": pedido.id,
                "display_type": "line_section",
                "name": "Sección que no debe sumar",
            }
        )
        with self.assertRaises(UserError):
            pedido.action_confirm()

    def test_parte_4_docente_sin_limite(self):
        pedido = self._crear_pedido(self.docente, [(self.producto_a, 12)])
        resultado = pedido.action_confirm()
        self.assertTrue(resultado)
        self.assertEqual(pedido.state, "sale")

    def test_ventas_unicah_conserva_canal_y_aprobacion(self):
        self.docente.canal_preferido = "web"
        pedido = self._crear_pedido(self.docente, [(self.producto_a, 600)])

        self.assertEqual(pedido.canal_venta, "web")
        self.assertTrue(pedido.requiere_aprobacion)
        self.assertFalse(pedido.aprobado_por)

        with self.assertRaises(UserError):
            pedido.action_confirm()

        pedido.action_aprobar()
        self.assertTrue(pedido.aprobado_por)
        pedido.action_confirm()
        self.assertEqual(pedido.state, "sale")

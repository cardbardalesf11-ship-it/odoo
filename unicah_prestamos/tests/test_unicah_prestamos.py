from datetime import date, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestUnicahPrestamos(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.prestamo_model = cls.env["unicah.prestamo"]
        cls.solicitante = cls.env["res.partner"].create(
            {
                "name": "Solicitante de prueba",
                "tipo_cliente": "estudiante",
                "numero_cuenta": "2026654321",
                "carrera": "Ingeniería en Sistemas",
            }
        )

    def _crear_prestamo(self, **valores):
        datos = {
            "solicitante_id": self.solicitante.id,
            "equipo": "Laptop Dell Latitude",
            "fecha_prestamo": "2026-11-13",
            "fecha_devolucion": "2026-11-20",
        }
        datos.update(valores)
        return self.prestamo_model.create(datos)

    def test_prestamo_y_dias_calculados(self):
        prestamo = self._crear_prestamo()
        self.assertEqual(prestamo.estado, "solicitado")
        self.assertEqual(prestamo.dias_prestamo, 7)
        self.assertTrue(prestamo.name.startswith("PRE/"))

    def test_fecha_devolucion_anterior(self):
        with self.assertRaises(ValidationError):
            self._crear_prestamo(
                fecha_prestamo="2026-11-20",
                fecha_devolucion="2026-11-13",
            )

    def test_sin_solicitante_o_equipo(self):
        with self.assertRaises(ValidationError):
            self.prestamo_model.create({"equipo": "Proyector Epson"})
        with self.assertRaises(ValidationError):
            self.prestamo_model.create({"solicitante_id": self.solicitante.id})

    def test_flujo_entregar_devolver(self):
        prestamo = self._crear_prestamo()
        prestamo.action_entregar()
        self.assertEqual(prestamo.estado, "entregado")

        with self.assertRaises(UserError):
            prestamo.action_entregar()

        prestamo.action_devolver()
        self.assertEqual(prestamo.estado, "devuelto")

        with self.assertRaises(UserError):
            prestamo.action_entregar()

    def test_marcar_vencido(self):
        ayer = date.today() - timedelta(days=1)
        prestamo = self._crear_prestamo(
            fecha_prestamo=(ayer - timedelta(days=5)).strftime("%Y-%m-%d"),
            fecha_devolucion=ayer.strftime("%Y-%m-%d"),
        )
        prestamo.action_entregar()
        prestamo.action_marcar_vencido()
        self.assertEqual(prestamo.estado, "vencido")

        prestamo.action_devolver()
        self.assertEqual(prestamo.estado, "devuelto")

    def test_menu_accion_y_vistas(self):
        self.env.ref("unicah_prestamos.menu_unicah_prestamos_root")
        self.env.ref("unicah_prestamos.menu_unicah_prestamo")
        self.env.ref("unicah_prestamos.action_unicah_prestamo")
        self.env.ref("unicah_prestamos.view_unicah_prestamo_list")
        self.env.ref("unicah_prestamos.view_unicah_prestamo_form")
        self.env.ref("unicah_prestamos.view_partner_form_unicah_prestamos")
        self.assertIn("prestamo_ids", self.env["res.partner"]._fields)

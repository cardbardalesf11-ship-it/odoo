# Ventas UNICAH — personalización del módulo de Ventas (Odoo 20)

Módulo propio para Odoo 20 que amplía la aplicación de Ventas **sin modificar el
código fuente de Odoo**: agrega el canal de venta preferido a los clientes, el
canal y el total de unidades a los pedidos, y exige la aprobación de un
administrador de ventas para confirmar pedidos que superen los 50,000.

- **Autor:** UNICAH
- **Versión:** 1.0 (serie 20.0)
- **Dependencias:** `sale_management`
- **Licencia:** LGPL-3

## Funcionalidades

### Contactos (`res.partner`)

| Campo | Tipo | Detalle |
|---|---|---|
| `canal_preferido` | Selection | Tienda, Teléfono, Sitio web, Distribuidor |

Se muestra en el formulario del contacto, justo después del campo de etiquetas
(`category_id`).

### Pedidos de venta (`sale.order`)

| Campo | Tipo | Detalle |
|---|---|---|
| `canal_venta` | Selection, calculado y almacenado | Toma el canal del cliente; se puede cambiar en el pedido |
| `total_unidades` | Float, calculado y almacenado | Suma de las cantidades de todas las líneas |
| `requiere_aprobacion` | Boolean, calculado y almacenado | Verdadero si el total supera 50,000 |
| `aprobado_por` | Many2one a `res.users` | Usuario que aprobó el pedido (`copy=False`) |
| `pendiente_aprobacion` | Boolean, calculado (no almacenado) | Requiere aprobación, no está aprobado y sigue en cotización |

- Los campos nuevos se muestran en el formulario del pedido.
- La lista de cotizaciones agrega las columnas **Canal de venta** y **Total de
  unidades** (con suma al pie).
- El buscador permite filtrar por **Requiere aprobación** y agrupar por
  **Canal de venta**.

### Regla de aprobación

1. Si `amount_total` supera `MONTO_APROBACION` (50,000), el pedido queda
   pendiente de aprobación.
2. El botón **Aprobar** solo lo ven los usuarios con el grupo
   `sales_team.group_sale_manager` (Administrador de ventas) y solo mientras el
   pedido esté pendiente.
3. `action_aprobar()` valida el grupo en el servidor (no solo en la vista) y
   registra el usuario en `aprobado_por`.
4. `action_confirm()` bloquea la confirmación con un `UserError` si el pedido
   requiere aprobación y todavía no la tiene. Si está aprobado (o no supera el
   límite), llama al `super()` y el pedido sigue su flujo normal.

## Estructura

```
ventas_unicah/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── res_partner.py
│   └── sale_order.py
├── views/
│   ├── res_partner_views.xml
│   └── sale_order_views.xml
├── tests/
│   ├── __init__.py
│   └── test_ventas_unicah.py
└── README.md
```

## Instalación y actualización

Con la base de práctica `odoo20_practica` y `custom_addons` dentro de
`addons_path`:

```bash
cd ~/Documents/odoo
source .venv/bin/activate

# Primera instalación
python odoo-bin server -c odoo.conf -d odoo20_practica -i ventas_unicah

# Actualización después de un cambio
python odoo-bin server -c odoo.conf -d odoo20_practica -u ventas_unicah
```

Después de actualizar, reiniciar el servidor de Odoo para que cargue el código
Python nuevo y recargar el navegador (con `?debug=1` si se quiere ver el nombre
técnico de los campos).

## Pruebas

Las pruebas están en `tests/test_ventas_unicah.py`, usan `TransactionCase` (Odoo
revierte la transacción al terminar, así que no dejan datos) y se ejecutan con:

```bash
python odoo-bin server -c odoo.conf -d odoo20_practica \
  -u ventas_unicah --test-enable --test-tags=/ventas_unicah \
  --no-http --stop-after-init
```

Resultado obtenido en la base `odoo20_practica`:

```
0 failed, 0 error(s) of 12 tests when loading database 'odoo20_practica'
ventas_unicah: 14 tests 0.56s 664 queries
```

| Prueba | Qué comprueba | Resultado |
|---|---|---|
| `test_01_canal_preferido_cuatro_opciones` | Las cuatro opciones existen y se guardan | OK |
| `test_02_canal_venta_se_toma_del_cliente` | Canal desde el cliente, recálculo y cambio manual | OK |
| `test_03_total_unidades_suma_lineas` | Suma al crear, agregar, modificar y borrar líneas | OK |
| `test_04_requiere_aprobacion_limite` | 50,000 no requiere; 50,000.01 y 90,000 sí | OK |
| `test_05_pendiente_aprobacion` | Pendiente antes de aprobar, falso después | OK |
| `test_06_pedido_pequeno_confirma_sin_aprobacion` | Flujo normal sin aprobación | OK |
| `test_07_pedido_grande_bloqueado_sin_aprobacion` | `UserError` y el pedido sigue en cotización | OK |
| `test_08_gerente_aprueba_y_luego_confirma` | Registro de `aprobado_por` y confirmación | OK |
| `test_09_vendedor_no_puede_aprobar` | `AccessError` para vendedor; tampoco confirma | OK |
| `test_10_duplicado_no_copia_aprobacion` | La copia de un pedido aprobado no hereda la aprobación | OK |
| `test_11_vistas_heredadas_instaladas` | Las vistas existen y contienen campo, botón y filtros | OK |
| `test_12_busqueda_por_canal_y_aprobacion` | Los campos calculados se pueden buscar | OK |

Además se validaron manualmente las vistas combinadas (formulario, lista y
buscador) con `get_combined_arch()`, para confirmar que los `xpath` se aplican
sobre las vistas reales de Odoo 20.

### Comprobaciones que requieren revisión visual

Las pruebas anteriores son automáticas. Para la entrega conviene verificar en el
navegador:

1. El campo **Canal preferido** en Contactos → formulario.
2. Una cotización de más de 50,000: aviso amarillo y botón **Aprobar**.
3. Que **Confirmar** muestre el mensaje de error antes de aprobar.
4. Que un vendedor sin rol de administrador no vea el botón **Aprobar**.

## Retos opcionales del documento (no implementados)

El PDF de la práctica propone tres ampliaciones que **no** forman parte del
ejercicio base y que aquí se dejaron fuera para no alterar lo solicitado:

1. Anular la aprobación cuando cambia `amount_total`.
2. Impedir el canal Distribuidor si el cliente no es empresa (`is_company`).
3. Mostrar el canal preferido en la lista de contactos.

## Problemas conocidos

| Síntoma | Causa | Solución |
|---|---|---|
| `Element ... cannot be located in parent view` | El `xpath` no coincide con la vista de Odoo 20 | Revisar el nombre del campo o del grupo en la vista original |
| `Field ... does not exist` | Falta importar el modelo en `models/__init__.py` | Importar el archivo y actualizar el módulo |
| El cambio no se ve en el navegador | El servidor no se reinició o el módulo no se actualizó | Reiniciar Odoo con `-u ventas_unicah` y recargar |

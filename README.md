# Examen Final – Programación de Negocios UNICAH

Proyecto de personalización de Odoo 20 para la Universidad Católica de Honduras
(UNICAH). El entregable reúne la práctica anterior de Ventas y los módulos
desarrollados para el examen final.

## Datos del estudiante

| Campo | Valor |
|---|---|
| Nombre del estudiante | Carlos Daniel Bardales |
| Número de cuenta | 0801200418650 |
| Universidad | Universidad Católica de Honduras (UNICAH) |
| Asignatura | Programación de Negocios |
| Docente | [Completar] |
| Sección | [Completar] |
| Periodo académico | [Completar] |

## Descripción

El proyecto está formado por tres módulos independientes que se complementan:

1. **`ventas_unicah`**: práctica anterior de personalización de Ventas. Se
   conservó sin cambios.
2. **`tienda_unicah`**: partes 1 a 5 del examen final. Agrega los datos
   universitarios del cliente, los convenios, la aplicación del convenio en el
   pedido, las validaciones y el cálculo del ahorro.
3. **`unicah_prestamos`**: parte 6 del examen final. Propuesta propia para
   controlar el préstamo de equipos universitarios.

El repositorio se inicializa dentro de `custom_addons` porque esa carpeta ya
está incluida en el `addons_path` de Odoo y porque allí vive el módulo anterior
`ventas_unicah`. De esta forma no se duplica el módulo, no se modifica el código
fuente de Odoo y no hay que cambiar los puertos ni la base de datos.

## Requisitos

- macOS con procesador Apple Silicon.
- Python 3.12.
- Entorno virtual `.venv`.
- Odoo 20.0.
- PostgreSQL escuchando en `127.0.0.1:5433`.
- Base de datos `odoo20_practica`.
- Odoo publicado en el puerto `8069`.

## Instalación

1. Verificar que Odoo esté detenido y que la ruta de los módulos esté en
   `odoo.conf`:

   ```ini
   addons_path = /Users/carlosdaniel/Documents/odoo/addons,/Users/carlosdaniel/Documents/odoo/custom_addons
   ```

2. Activar el entorno virtual:

   ```bash
   cd /Users/carlosdaniel/Documents/odoo
   source .venv/bin/activate
   ```

3. Instalar los módulos nuevos:

   ```bash
   .venv/bin/python odoo-bin -c odoo.conf -d odoo20_practica \
       -i tienda_unicah,unicah_prestamos --stop-after-init
   ```

4. Actualizar los módulos después de un cambio:

   ```bash
   .venv/bin/python odoo-bin -c odoo.conf -d odoo20_practica \
       -u tienda_unicah,unicah_prestamos --stop-after-init
   ```

5. Iniciar Odoo:

   ```bash
   .venv/bin/python odoo-bin -c odoo.conf -d odoo20_practica
   ```

6. Abrir `http://localhost:8069` e iniciar sesión con el usuario de trabajo.

## Módulos incluidos

| Módulo | Parte | Contenido principal |
|---|---|---|
| `ventas_unicah` | Práctica anterior | Canal preferido, canal de venta, total de unidades, aprobación de pedidos mayores de 50,000 y usuario aprobador. |
| `tienda_unicah` | Partes 1 a 5 | Tipo de cliente, número de cuenta, carrera, convenios, aplicación del convenio, validaciones y ahorro. |
| `unicah_prestamos` | Parte 6 | Préstamo de equipos, estados, días calculados, validaciones, menú y pestaña en el contacto. |

## Funcionalidades

### Parte 1 – Datos universitarios del cliente

- Se hereda `res.partner`.
- Se agregan `tipo_cliente`, `numero_cuenta` y `carrera`.
- Se crea la pestaña **UNICAH** en el formulario de contactos.
- El número de cuenta y la carrera solo se muestran para estudiantes.
- El número de cuenta es obligatorio para estudiantes y debe tener exactamente
  10 dígitos numéricos.

### Parte 2 – Convenios

- Modelo `tienda.convenio` con nombre, tipo de cliente, porcentaje, fechas y
  estado activo.
- Validaciones: porcentaje mayor que 0, máximo 40 % y fecha final no anterior
  a la fecha inicial.
- Los vendedores pueden consultar. Los administradores de ventas pueden crear,
  leer, modificar y eliminar.
- Registros iniciales: Convenio estudiantil (15 %) y Convenio docente (10 %).
- Vistas de lista y formulario, acción y menú **Convenios UNICAH** dentro de
  **Ventas > Configuración**.

### Parte 3 – Convenio en el pedido

- Campos `tipo_cliente`, `convenio_id` y `convenio_aplicado` en `sale.order`.
- Al seleccionar un cliente, Odoo propone el convenio vigente de su tipo.
- Botón **Aplicar convenio** visible solo en cotizaciones y mientras el convenio
  no haya sido aplicado.
- El descuento se aplica únicamente a líneas de producto. Las secciones y notas
  no se modifican.
- El resultado se registra en el chatter.
- No se permite aplicar dos veces el mismo convenio sin cambiar de convenio.

### Parte 4 – Validaciones

- Cuenta de estudiante: exactamente 10 dígitos numéricos.
- Convenio: porcentaje mayor que 0, máximo 40 %, fechas coherentes.
- Pedido de estudiante: no se puede confirmar si supera 10 unidades de
  productos. Las secciones y notas no se cuentan.
- La validación de 10 unidades se integró con `action_confirm` de
  `ventas_unicah`, por lo que también se conserva la aprobación de pedidos
  mayores de 50,000.
- Docentes y otros tipos de cliente no tienen el límite de 10 unidades.

### Parte 5 – Ahorro por convenio

- Campo `monto_ahorro` de tipo `Monetary`, calculado, almacenado y relacionado
  con la moneda del pedido.
- Se calcula con precio unitario × cantidad × porcentaje de descuento / 100,
  sin contar secciones ni notas.
- Se muestra en el formulario y en la lista de pedidos, con total al pie de la
  columna.
- Filtro **Con convenio** y agrupación por convenio.

### Parte 6 – Préstamo de equipo universitario

- Modelo `unicah.prestamo` con referencia, solicitante, equipo, fechas, estado y
  días calculados.
- Estados: Solicitado, Entregado, Devuelto y Vencido.
- Reglas: la devolución no puede ser anterior al préstamo; no se registra un
  préstamo sin solicitante ni equipo; no se entrega un préstamo ya devuelto.
- Vista de lista, formulario con chatter, acción y menú propio.
- Herencia de `res.partner` para mostrar la pestaña **Préstamos UNICAH** en el
  contacto.

### Práctica anterior conservada

`ventas_unicah` conserva:

- Canal preferido del cliente.
- Canal de venta del pedido.
- Total de unidades.
- Requiere aprobación para pedidos mayores de 50,000.
- Aprobación por un administrador de ventas.
- Usuario que aprobó.
- Restricción para confirmar sin aprobación.

No se eliminó ni se reemplazó ningún campo o método de este módulo.

## Pruebas realizadas

### Pruebas automatizadas

Se ejecutó la suite de pruebas de Odoo 20 con la base `odoo20_practica`:

```bash
.venv/bin/python odoo-bin -c odoo.conf -d odoo20_practica \
    -u tienda_unicah,unicah_prestamos \
    --test-enable --test-tags /tienda_unicah,/unicah_prestamos \
    --stop-after-init --log-level=test
```

**Resultado real del 13 de noviembre de 2026:**

- 19 pruebas ejecutadas.
- 0 fallos.
- 0 errores.

Cobertura de las pruebas:

| Parte | Qué se comprobó |
|---|---|
| 1 | Estudiante con cuenta válida, docente, cuenta de 8 dígitos y cuenta obligatoria. |
| 2 | Convenios iniciales, convenio administrativo y permisos de vendedor/administrador. |
| 3 | Propuesta del convenio, aplicación del descuento, sección sin descuento y mensaje en el chatter. |
| 4 | Porcentaje 0, porcentaje 50, fechas invertidas, límite de 10 unidades y docente sin límite. |
| 5 | Cálculo del ahorro con dos productos y una nota. |
| 6 | Préstamo, días calculados, fechas invertidas, campos obligatorios, flujo de estados, menú y vistas. |
| Práctica anterior | Canal de venta y aprobación de pedidos mayores de 50,000. |

### Pruebas visuales en el navegador

Las capturas reales se tomarán en la interfaz de Odoo siguiendo la lista de
`docs/capturas.md`. En este documento no se afirma que esas capturas ya existan.

## Estructura del repositorio

```text
custom_addons/
├── README.md
├── .gitignore
├── ventas_unicah/
├── tienda_unicah/
├── unicah_prestamos/
└── docs/
    ├── justificacion.md
    ├── justificacion_borrador.pdf
    ├── capturas.md
    └── generar_pdf.py
```

## Permisos de seguridad

Odoo 20 utiliza el archivo `security/ir.access.csv`, el modelo `ir.access` y las
operaciones `c`, `r`, `u` y `d`.

- `tienda.convenio`: vendedores con lectura; administradores de ventas con CRUD.
- `unicah.prestamo`: usuarios internos con lectura; vendedores con creación,
  lectura y actualización; administradores de ventas con CRUD.

## Historial de Git

El entregable se preparó con una secuencia de commits que refleja el desarrollo:

1. Práctica anterior `ventas_unicah`.
2. Partes 1 a 5 en `tienda_unicah`.
3. Parte 6 en `unicah_prestamos`.
4. Documentación, README y guía de capturas.

## Autor

Carlos Daniel Bardales  
Número de cuenta: 0801200418650  
Universidad Católica de Honduras (UNICAH)

## Licencia

LGPL-3.

# Justificación del Examen Final – Programación de Negocios UNICAH

## Portada

| Campo | Valor |
|---|---|
| Nombre del estudiante | Carlos Daniel Bardales |
| Número de cuenta | 0801200418650 |
| Universidad | Universidad Católica de Honduras (UNICAH) |
| Asignatura | Programación de Negocios |
| Docente | [Completar] |
| Sección | [Completar] |
| Periodo académico | [Completar] |

## Introducción

Para el examen final aproveché el módulo `ventas_unicah` que ya había trabajado
en la práctica anterior. En lugar de borrarlo o hacer otro módulo desde cero,
lo conservé y construí dos módulos nuevos: `tienda_unicah` para las partes 1 a 5
y `unicah_prestamos` para la parte 6.

La idea fue mantener el trabajo anterior funcionando y agregar lo que pedía el
examen de forma ordenada. Cada módulo tiene su propio manifiesto, sus modelos,
sus vistas y sus permisos. `ventas_unicah` no se modificó.

> **Espacio para captura de portada:**  
> `[Insertar aquí una captura general de Odoo con los módulos instalados o el menú de Ventas.]`

---

## Parte 1 – Datos universitarios del cliente

Heredé el modelo `res.partner` porque los estudiantes, docentes y
administrativos siguen siendo contactos de Odoo. No tiene sentido crear otro
modelo de personas si Odoo ya tiene uno que funciona bien para clientes,
proveedores y direcciones.

Agregué tres campos:

- `tipo_cliente`: permite escoger entre Estudiante, Docente, Administrativo y
  Externo.
- `numero_cuenta`: guarda la cuenta del estudiante.
- `carrera`: guarda la carrera que cursa.

En el formulario de contactos agregué una pestaña llamada **UNICAH**. El número
de cuenta y la carrera solamente se ven cuando el tipo de cliente es
Estudiante. Además, el número de cuenta es obligatorio para estudiantes.

La validación en Python revisa que la cuenta tenga exactamente 10 dígitos
numéricos. Si alguien escribe una cuenta de 8 dígitos, Odoo muestra un mensaje
de error y no deja guardar el contacto.

> **Espacio para captura 1:**  
> `[Insertar aquí la pestaña UNICAH de un estudiante con tipo de cliente, número de cuenta y carrera.]`

> **Espacio para captura 2:**  
> `[Insertar aquí la pestaña UNICAH de un docente, donde no se ven número de cuenta ni carrera.]`

---

## Parte 2 – Modelo de convenios

Creé el modelo `tienda.convenio` para guardar los descuentos que la universidad
ofrece según el tipo de cliente. Los campos son:

- Nombre.
- Tipo de cliente.
- Porcentaje de descuento.
- Fecha de inicio.
- Fecha de finalización.
- Activo.

El tipo de cliente usa las mismas opciones de la parte 1 para que no haya
diferencias entre el contacto y el convenio.

También agregué validaciones: el porcentaje debe ser mayor que 0, no puede pasar
del 40 % y la fecha final no puede ser anterior a la fecha inicial. Estas
validaciones se hicieron en Python con `ValidationError`.

Los permisos quedaron así:

- Los vendedores pueden consultar los convenios.
- Los administradores de ventas pueden crear, leer, modificar y eliminar.

Dejé dos registros iniciales:

- Convenio estudiantil: 15 %.
- Convenio docente: 10 %.

El menú **Convenios UNICAH** aparece dentro de **Ventas > Configuración**.

> **Espacio para captura 3:**  
> `[Insertar aquí la lista de convenios con el convenio estudiantil y el docente.]`

> **Espacio para captura 4:**  
> `[Insertar aquí el formulario de un convenio administrativo creado durante la prueba.]`

---

## Parte 3 – Convenio en el pedido

Heredé `sale.order` para no separar el convenio del pedido de venta. Agregué:

- `tipo_cliente`: se toma del cliente.
- `convenio_id`: el convenio que se va a aplicar.
- `convenio_aplicado`: indica si el descuento ya fue aplicado.

Cuando se selecciona el cliente, Odoo busca un convenio activo que corresponda
al tipo de cliente y que esté vigente según las fechas. Si lo encuentra, lo
propone automáticamente en el pedido.

El botón **Aplicar convenio** hace lo siguiente:

1. Revisa que el pedido todavía sea una cotización.
2. Revisa que haya un convenio seleccionado.
3. Aplica el porcentaje a las líneas de producto.
4. No toca las secciones ni las notas.
5. Escribe un mensaje en el chatter.
6. Marca el pedido como que ya tiene el convenio aplicado.

El campo `convenio_aplicado` controla la visibilidad del botón y también evita
que el mismo convenio se aplique dos veces. Si el usuario cambia de convenio,
el campo se reinicia para que pueda tomar una nueva decisión.

> **Espacio para captura 5:**  
> `[Insertar aquí una cotización de un estudiante con el convenio propuesto.]`

> **Espacio para captura 6:**  
> `[Insertar aquí el pedido con dos productos y una sección, después de aplicar el convenio, mostrando el descuento y el mensaje del chatter.]`

---

## Parte 4 – Validaciones

### A. Número de cuenta

Si el cliente es estudiante, la cuenta debe tener exactamente 10 dígitos
numéricos. Si no cumple, se lanza un `ValidationError`. También se valida que la
cuenta no quede vacía cuando el tipo de cliente es Estudiante.

### B. Convenios

- El porcentaje debe ser mayor que 0.
- No puede superar el 40 %.
- La fecha final no puede ser anterior a la fecha inicial.

Estas reglas están en el modelo `tienda.convenio` y se ejecutan al guardar.

### C. Pedidos de estudiantes

Los estudiantes no pueden confirmar pedidos que superen 10 unidades de
productos. La cantidad se calcula sumando solamente las líneas de producto, sin
contar secciones ni notas.

Para no dañar la práctica anterior, no reemplacé el `action_confirm` de
`ventas_unicah`. En `tienda_unicah` agregué mi validación y luego llamé a
`super().action_confirm()`. De esa forma se ejecuta primero la validación de
unidades y después la validación de aprobación de pedidos mayores de 50,000 que
ya existía.

Los pedidos de docentes y de otros tipos de cliente no tienen el límite de 10
unidades.

> **Espacio para captura 7:**  
> `[Insertar aquí el error al guardar un estudiante con una cuenta de 8 dígitos.]`

> **Espacio para captura 8:**  
> `[Insertar aquí el error al crear un convenio de 50 %.]`

> **Espacio para captura 9:**  
> `[Insertar aquí el error al crear un convenio con fechas invertidas.]`

> **Espacio para captura 10:**  
> `[Insertar aquí el error al confirmar un pedido de estudiante con 12 unidades.]`

> **Espacio para captura 11:**  
> `[Insertar aquí un pedido de docente con 12 unidades ya confirmado.]`

---

## Parte 5 – Ahorro por convenio

Agregué el campo `monto_ahorro` al pedido de venta. Es un campo `Monetary`,
calculado y almacenado, y usa la moneda del pedido.

El cálculo suma, para cada línea de producto:

```text
precio unitario × cantidad × porcentaje de descuento / 100
```

Las secciones y las notas se excluyen porque no son productos. El campo se
actualiza cuando cambian el precio, la cantidad, el descuento o el estado del
convenio.

En el formulario se ve el ahorro y en la lista de pedidos agregué la columna con
su total al pie. También agregué el filtro **Con convenio** y la agrupación por
convenio.

> **Espacio para captura 12:**  
> `[Insertar aquí el formulario del pedido mostrando el monto de ahorro.]`

> **Espacio para captura 13:**  
> `[Insertar aquí la lista de pedidos con la columna de ahorro y su total.]`

> **Espacio para captura 14:**  
> `[Insertar aquí el filtro Con convenio y la agrupación por convenio.]`

---

## Parte 6 – Propuesta propia: préstamo de equipo universitario

La propuesta consiste en un módulo llamado `unicah_prestamos` para controlar el
préstamo de laptops, proyectores y otros equipos de la universidad.

El modelo `unicah.prestamo` tiene estos campos:

- `name`: referencia del préstamo, generada con una secuencia.
- `solicitante_id`: contacto que pide el equipo.
- `equipo`: nombre o descripción del equipo.
- `fecha_prestamo`: fecha de entrega.
- `fecha_devolucion`: fecha prevista de devolución.
- `estado`: Solicitado, Entregado, Devuelto o Vencido.
- `dias_prestamo`: campo calculado con los días entre las fechas.

Las reglas de negocio son:

- La fecha de devolución no puede ser anterior a la fecha del préstamo.
- No se puede registrar un préstamo sin solicitante ni equipo.
- No se puede entregar un préstamo que ya fue devuelto.
- El estado cambia según el proceso: se entrega, se devuelve o se marca como
  vencido cuando la fecha de devolución ya pasó.

También heredé `res.partner` para agregar la pestaña **Préstamos UNICAH** en el
contacto. Allí se ven los préstamos de esa persona. El módulo tiene su propia
vista de lista, vista de formulario, acción, menú y permisos.

Elegí este tema porque en la universidad es común que se presten equipos y no
siempre queda claro quién los tiene, cuándo deben devolverse y en qué estado
están. Con este módulo se puede consultar esa información sin usar una hoja de
cálculo aparte.

> **Espacio para captura 15:**  
> `[Insertar aquí el formulario de un préstamo con las fechas y los días calculados.]`

> **Espacio para captura 16:**  
> `[Insertar aquí el error cuando la fecha de devolución es anterior a la fecha del préstamo.]`

> **Espacio para captura 17:**  
> `[Insertar aquí la lista de préstamos con los estados.]`

> **Espacio para captura 18:**  
> `[Insertar aquí el menú Préstamos UNICAH y la pestaña de préstamos en un contacto.]`

---

## Conservación de `ventas_unicah`

Una parte importante del examen era no perder la práctica anterior. El módulo
`ventas_unicah` sigue funcionando con:

- Canal preferido del cliente.
- Canal de venta del pedido.
- Total de unidades.
- Requiere aprobación para pedidos mayores de 50,000.
- Usuario que aprobó.
- Restricción para confirmar sin aprobación.

La prueba automatizada `test_ventas_unicah_conserva_canal_y_aprobacion`
comprobó que el canal de venta se sigue calculando y que un pedido mayor de
50,000 sigue necesitando aprobación antes de confirmarse.

> **Espacio para captura 19:**  
> `[Insertar aquí un pedido mayor de 50,000 con el aviso de aprobación y el botón Aprobar.]`

> **Espacio para captura 20:**  
> `[Insertar aquí el pedido aprobado y confirmado.]`

---

## Respuestas a las preguntas del examen

Estas son las preguntas que normalmente se relacionan con el desarrollo y las
respuestas que puedo dar con el trabajo realizado.

### ¿Por qué se hereda `res.partner` y `sale.order` en lugar de crear modelos nuevos?

Porque Odoo ya tiene esos modelos con toda la lógica de contactos y ventas.
Heredarlos permite agregar campos y validaciones sin perder lo que ya funciona.
Crear modelos nuevos obligaría a repetir direcciones, clientes, pedidos,
impuestos y muchas otras cosas que Odoo ya resuelve.

### ¿Cómo se evita aplicar dos veces el mismo convenio?

Con el campo `convenio_aplicado`. El botón se oculta cuando el valor es
verdadero y el método también revisa ese campo antes de aplicar el descuento.
Si el usuario cambia de convenio, el campo se reinicia para que pueda tomar una
nueva decisión.

### ¿Por qué se usa `ValidationError` y `UserError`?

`ValidationError` se usa para datos que no cumplen una regla del modelo, como
una cuenta de 8 dígitos, un porcentaje de 50 % o una fecha invertida.
`UserError` se usa para acciones que el usuario intenta hacer y que no están
permitidas en ese momento, como aplicar un convenio a un pedido ya confirmado o
confirmar un pedido de estudiante con más de 10 unidades.

### ¿Cómo se conserva la aprobación de pedidos mayores de 50,000?

`tienda_unicah` depende de `ventas_unicah` y su `action_confirm` llama a
`super().action_confirm()`. Así se ejecuta primero la validación de unidades y
después la validación de aprobación que ya existía. No se eliminó ni se copió el
método anterior.

### ¿Por qué el ahorro no cuenta secciones ni notas?

Porque las secciones y las notas son líneas de texto que sirven para organizar
el pedido, no son productos. Si se contaran, el ahorro estaría mal calculado.
Por eso el cálculo revisa que la línea no tenga `display_type` y que tenga un
producto.

### ¿Por qué se creó un módulo aparte para los préstamos?

Porque el control de préstamos de equipo es una necesidad distinta a la venta
de productos. Mantenerlo en un módulo independiente hace que el código sea más
fácil de entender, de instalar y de quitar si la universidad no lo necesita.

### ¿Qué diferencia hay entre un campo calculado almacenado y uno no almacenado?

Un campo calculado almacenado guarda el resultado en la base de datos y se
puede usar para filtrar, agrupar o mostrar en listas. `monto_ahorro` y
`dias_prestamo` son almacenados porque necesito consultarlos y ordenarlos. Un
campo no almacenado se calcula cada vez que se muestra y no ocupa un lugar
permanente en la base.

### ¿Cómo se controlan los permisos en Odoo 20?

En Odoo 20 los permisos se declaran en `security/ir.access.csv`, usando el
modelo `ir.access` y las operaciones `c`, `r`, `u` y `d`. Los vendedores tienen
lectura de convenios y los administradores de ventas tienen CRUD. En préstamos,
los usuarios internos tienen lectura, los vendedores pueden crear y actualizar,
y los administradores pueden hacer todo.

---

## Pruebas realizadas

Se ejecutaron las pruebas automatizadas de Odoo 20 sobre la base
`odoo20_practica`. El resultado fue:

- 19 pruebas ejecutadas.
- 0 fallos.
- 0 errores.

Las pruebas revisaron los datos del estudiante y del docente, la cuenta de 8
dígitos, la cuenta obligatoria, los convenios iniciales, el convenio
administrativo, los permisos, la propuesta y aplicación del convenio, el
descuento de las líneas, el mensaje del chatter, las validaciones de porcentaje
y fechas, el límite de 10 unidades, el pedido de docente sin límite, el cálculo
del ahorro, el préstamo, los días calculados y el flujo de estados.

Las capturas de la interfaz se agregarán después de tomarlas en Odoo. En este
documento no se afirma que ya existan.

> **Espacio para captura 21:**  
> `[Insertar aquí una captura de la terminal con el resultado de las pruebas automatizadas, si el docente lo solicita.]`

---

## Conclusión

El examen quedó organizado en tres módulos. La práctica anterior se conservó,
las partes 1 a 5 se agregaron en `tienda_unicah` y la propuesta de préstamos se
trabajó en `unicah_prestamos`. Lo más importante fue integrar las validaciones
nuevas sin romper la aprobación de pedidos mayores de 50,000 y sin modificar el
código fuente de Odoo.

Las pruebas automatizadas pasaron, y las capturas de la interfaz se tomarán en
el navegador para completar la justificación visual del entregable.

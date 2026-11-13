# Lista de capturas para el entregable

Esta lista sirve para tomar las capturas reales dentro de Odoo. No se deben
inventar ni reutilizar imágenes de otros proyectos.

## Recomendaciones generales

- Iniciar Odoo con la base `odoo20_practica` y abrir
  `http://localhost:8069`.
- Usar preferiblemente el usuario administrador para las capturas de
  configuración y un usuario vendedor para la prueba de permisos.
- Tomar la captura completa de la ventana, sin recortar los botones ni los
  mensajes importantes.
- Guardar las imágenes en una carpeta llamada `capturas/` dentro de `docs/`.
- Usar los nombres sugeridos para que sea fácil insertarlas en el PDF.
- No mostrar datos personales de otras personas que no sean necesarios.

## Parte 1 – Datos universitarios del cliente

### Captura 01 – Estudiante

**Archivo sugerido:** `01_estudiante_unicah.png`

Mostrar el formulario de un contacto con:

- Tipo de cliente: Estudiante.
- Número de cuenta de 10 dígitos.
- Carrera.
- Pestaña **UNICAH** abierta.

### Captura 02 – Docente

**Archivo sugerido:** `02_docente_unicah.png`

Mostrar el formulario de un contacto con:

- Tipo de cliente: Docente.
- Pestaña **UNICAH** abierta.
- Número de cuenta y carrera ocultos.

## Parte 2 – Convenios

### Captura 03 – Convenios iniciales

**Archivo sugerido:** `03_lista_convenios.png`

Mostrar **Ventas > Configuración > Convenios UNICAH** con:

- Convenio estudiantil, 15 %.
- Convenio docente, 10 %.

### Captura 04 – Convenio administrativo

**Archivo sugerido:** `04_convenio_administrativo.png`

Mostrar el formulario de un convenio nuevo para el tipo de cliente
Administrativo, con su porcentaje y sus fechas.

### Captura 05 – Permisos (opcional)

**Archivo sugerido:** `05_permisos_convenios.png`

Mostrar la lista de convenios abierta con un usuario vendedor, donde no
aparezcan las opciones de crear, editar o eliminar. También puede servir una
captura de la configuración de grupos de usuarios.

## Parte 3 – Convenio en el pedido

### Captura 06 – Convenio propuesto

**Archivo sugerido:** `06_convenio_propuesto.png`

Mostrar una cotización de un estudiante con el campo **Convenio UNICAH**
propuesto automáticamente y el botón **Aplicar convenio** visible.

### Captura 07 – Antes de aplicar

**Archivo sugerido:** `07_pedido_antes_convenio.png`

Mostrar el pedido con:

- Dos productos.
- Una sección.
- El botón **Aplicar convenio** disponible.

### Captura 08 – Después de aplicar

**Archivo sugerido:** `08_pedido_convenio_aplicado.png`

Mostrar el mismo pedido con:

- Descuento del 15 % en las líneas de producto.
- La sección sin descuento.
- El campo **Convenio aplicado** marcado.
- El botón **Aplicar convenio** oculto.
- El mensaje del chatter.

## Parte 4 – Validaciones

### Captura 09 – Cuenta de 8 dígitos

**Archivo sugerido:** `09_error_cuenta_8_digitos.png`

Intentar guardar un estudiante con una cuenta de 8 dígitos y capturar el mensaje
de error de Odoo.

### Captura 10 – Convenio de 50 %

**Archivo sugerido:** `10_error_convenio_50.png`

Intentar crear un convenio con 50 % y capturar el mensaje de error.

### Captura 11 – Fechas invertidas

**Archivo sugerido:** `11_error_fechas_convenio.png`

Intentar crear un convenio con fecha final anterior a la fecha inicial y
capturar el mensaje de error.

### Captura 12 – Estudiante con 12 unidades

**Archivo sugerido:** `12_error_limite_estudiante.png`

Intentar confirmar un pedido de estudiante con 12 unidades de producto y
capturar el mensaje que indica que no puede superar las 10 unidades.

### Captura 13 – Docente con 12 unidades

**Archivo sugerido:** `13_docente_12_unidades.png`

Mostrar un pedido de docente con 12 unidades ya confirmado, para comprobar que
el límite no aplica a los docentes.

## Parte 5 – Ahorro por convenio

### Captura 14 – Ahorro en el formulario

**Archivo sugerido:** `14_ahorro_formulario.png`

Mostrar el formulario del pedido con el campo **Ahorro por convenio** y su
valor.

### Captura 15 – Ahorro en la lista

**Archivo sugerido:** `15_ahorro_lista.png`

Mostrar la lista de pedidos con la columna **Ahorro por convenio** y el total al
pie de la columna.

### Captura 16 – Filtro Con convenio

**Archivo sugerido:** `16_filtro_con_convenio.png`

Mostrar el filtro **Con convenio** aplicado en la búsqueda de pedidos.

### Captura 17 – Agrupación por convenio

**Archivo sugerido:** `17_agrupacion_convenio.png`

Mostrar la lista de pedidos agrupada por convenio.

## Parte 6 – Préstamo de equipo universitario

### Captura 18 – Formulario del préstamo

**Archivo sugerido:** `18_prestamo_formulario.png`

Mostrar un préstamo con:

- Referencia.
- Solicitante.
- Equipo.
- Fecha de préstamo.
- Fecha de devolución.
- Días de préstamo calculados.
- Estado.

### Captura 19 – Error de fechas

**Archivo sugerido:** `19_error_fechas_prestamo.png`

Intentar guardar un préstamo con fecha de devolución anterior a la fecha de
préstamo y capturar el error.

### Captura 20 – Lista de préstamos

**Archivo sugerido:** `20_lista_prestamos.png`

Mostrar la lista de préstamos con sus estados y los días calculados.

### Captura 21 – Menú propio

**Archivo sugerido:** `21_menu_prestamos.png`

Mostrar el menú **Préstamos UNICAH** dentro de Odoo y la opción
**Préstamos de equipo**.

### Captura 22 – Pestaña en el contacto

**Archivo sugerido:** `22_prestamos_en_contacto.png`

Mostrar un contacto con la pestaña **Préstamos UNICAH** y sus préstamos
relacionados.

### Captura 23 – Cambio de estado

**Archivo sugerido:** `23_estado_prestamo.png`

Mostrar un préstamo en estado **Entregado** o **Devuelto**, con los botones que
correspondan.

## Práctica anterior `ventas_unicah`

### Captura 24 – Canal preferido

**Archivo sugerido:** `24_canal_preferido.png`

Mostrar un contacto con el campo **Canal preferido** de `ventas_unicah`.

### Captura 25 – Aprobación de pedido grande

**Archivo sugerido:** `25_aprobacion_pedido.png`

Mostrar un pedido mayor de 50,000 con el aviso de aprobación y el botón
**Aprobar**.

### Captura 26 – Pedido aprobado

**Archivo sugerido:** `26_pedido_aprobado.png`

Mostrar el mismo pedido después de aprobarlo y confirmarlo, con el usuario que
aprobó.

### Captura 27 – Resultado de pruebas automatizadas (opcional)

**Archivo sugerido:** `27_pruebas_automatizadas.png`

Si el docente pide evidencia de las pruebas, tomar una captura de la terminal
donde se vea el resultado:

```text
0 failed, 0 error(s) of 19 tests
```

## Orden sugerido para el PDF

1. Portada.
2. Introducción.
3. Parte 1: capturas 01 y 02.
4. Parte 2: capturas 03, 04 y 05.
5. Parte 3: capturas 06, 07 y 08.
6. Parte 4: capturas 09 a 13.
7. Parte 5: capturas 14 a 17.
8. Parte 6: capturas 18 a 23.
9. Práctica anterior: capturas 24 a 26.
10. Pruebas y conclusión: captura 27 si se solicita.

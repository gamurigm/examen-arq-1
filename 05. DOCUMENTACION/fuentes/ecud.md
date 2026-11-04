# ECUD — fuente canonica en revision

## Metadatos de la entrega

- Autores: Gabriel Omar Murillo Medina; Julio Enrique Viche Castillo.
- Grupo: 09.
- NRC: 36884.
- Tutor: Ing. Eduardo Mauricio Campaña Ortega.
- Proyecto: Comercializadora de celulares y módulo de crédito BanQuito.
- Arquitectura: .NET REST; aplicaciones y bases independientes.


[REVISION PENDIENTE: importacion inicial; contrastar con codigo y evidencia actual antes de generar finales]

          TemaESPECIFICACIÓN DE CASOS DE USO DETALLADA PARA CELULARES CON REST EN .NETAutoresGRUPO 09 NRC 36884TutorDocente de la asignatura Fecha27/10/2026TemaESPECIFICACIÓN DE CASOS DE USO DETALLADA PARA CELULARES CON REST EN .NETAutoresGRUPO 09 NRC 36884TutorDocente de la asignatura Fecha27/10/2026

     

     

Tema

ESPECIFICACIÓN DE CASOS DE USO DETALLADA PARA CELULARES CON REST EN .NET

Autores

GRUPO 09 NRC 36884

Tutor

Docente de la asignatura

 

Fecha

27/10/2026

Tema

ESPECIFICACIÓN DE CASOS DE USO DETALLADA PARA CELULARES CON REST EN .NET

Autores

GRUPO 09 NRC 36884

Tutor

Docente de la asignatura

 

Fecha

27/10/2026

ESPECIFICACIÓN DE CASOS DE USO DETALLADO · CELULAR BDDLOCAL RESTFUL .NET

ÍNDICE DE CONTENIDOS

ESPECIFICACIÓN DE CASOS DE USO DETALLADO · CELULAR BDDLOCAL RESTFUL .NET1

ESPECIFICACIÓN DE CASOS DE USO DETALLADO3

ECUD1 — ADMINISTRAR CATÁLOGO E IMÁGENES3

ECUD2 — CONSULTAR ELEGIBILIDAD Y MONTO MÁXIMO6

ECUD3 — REGISTRAR VENTA EN EFECTIVO9

ECUD4 — REGISTRAR VENTA A CRÉDITO12

ECUD5 — CONSULTAR FACTURA Y AMORTIZACIÓN15

ÍNDICE DE ILUSTRACIONES

Ilustración 1. Caso de uso Administrar catálogo e imágenes4

Ilustración 2. Actividad Administrar catálogo e imágenes5

Ilustración 3. Secuencia Administrar catálogo e imágenes6

Ilustración 4. Caso de uso Consultar elegibilidad y monto máximo7

Ilustración 5. Actividad Consultar elegibilidad y monto máximo8

Ilustración 6. Secuencia Consultar elegibilidad y monto máximo9

Ilustración 7. Caso de uso Registrar venta en efectivo10

Ilustración 8. Actividad Registrar venta en efectivo11

Ilustración 9. Secuencia Registrar venta en efectivo12

Ilustración 10. Caso de uso Registrar venta a crédito13

Ilustración 11. Actividad Registrar venta a crédito14

Ilustración 12. Secuencia Registrar venta a crédito14

Ilustración 13. Caso de uso Consultar factura y amortización16

Ilustración 14. Actividad Consultar factura y amortización17

Ilustración 15. Secuencia Consultar factura y amortización18

ÍNDICE DE TABLAS

Tabla 1. ECUD Administrar catálogo e imágenes4

Tabla 2. ECUD Consultar elegibilidad y monto máximo7

Tabla 3. ECUD Registrar venta en efectivo10

Tabla 4. ECUD Registrar venta a crédito13

Tabla 5. ECUD Consultar factura y amortización16

ESPECIFICACIÓN DE CASOS DE USO DETALLADO

Este documento detalla cinco casos de uso del sistema comercializador de celulares para .NET 10: administrar catálogo e imágenes, consultar elegibilidad, registrar ventas en efectivo y crédito, y consultar facturas y amortización. El servidor ASP.NET Core REST usa SQL Server 2025 Express y ADO.NET. BanQuito permanece como servicio bancario remoto e independiente. Los cuatro clientes son consola, WPF, web MVC y MAUI Android.

ECUD1 — ADMINISTRAR CATÁLOGO E IMÁGENES

A continuación, se presenta ECUD1 para mantener celulares y sus fotos opcionales.

Tabla 1. ECUD Administrar catálogo e imágenes.

Nombre Caso de Uso:

Administrar catálogo e imágenes

Identificador:

ECUD1

Descripción:

Permite mantener celulares del catálogo y administrar una imagen opcional por producto.

Meta:

Guardar altas, cambios, desactivaciones y fotos solo después de confirmación del API.

Estado:

Aprobado

Versión:

1.0

Autores:

Grupo 09 · NRC 36884

Fecha creación:

27/10/2026

Fecha modificación:

27/10/2026

Precondiciones:

El servicio .NET y SQL Server están disponibles; el operador puede acceder a la aplicación.

Post condiciones:

El catálogo refleja el cambio confirmado. La foto JPEG, PNG o WebP se guarda, reemplaza o elimina en SQL Server.

Gráfico:

Ilustración 1. Caso de uso Administrar catálogo e imágenes

Ilustración 2. Actividad Administrar catálogo e imágenes

Ilustración 3. Secuencia Administrar catálogo e imágenes

Flujo Básico

Administrar catálogo e imágenes

Actor

Sistema

1. Elige administrar catálogo.

2. Presenta productos y formulario.

3. Ingresa marca, modelo y precio.

4. Valida campos y solicita alta o cambio.

5. Elige una foto o conserva la actual.

6. Verifica formato y límite de 5 MiB.

7. Confirma y envía la solicitud.

8. Guarda catálogo e imagen y confirma.

Flujo Alternativo

A1. Datos inválidos: señalar campos y no enviar. A2. Archivo vacío, tipo no permitido, firma falsa o mayor de 5 MiB: rechazar y conservar la foto anterior. A3. Elimina foto: confirmar y llamar DELETE. A4. Celular vendido: conservarlo y desactivarlo, no borrar factura. A5. API no disponible: conservar formulario y mostrar error.

Casos de uso incluidos: Ninguno.

Casos de uso extendidos: Ninguno.

ECUD2 — CONSULTAR ELEGIBILIDAD Y MONTO MÁXIMO

A continuación, se presenta ECUD2 para verificar los requisitos del crédito en BanQuito.

Tabla 2. ECUD Consultar elegibilidad y monto máximo.

Nombre Caso de Uso:

Consultar elegibilidad y monto máximo

Identificador:

ECUD2

Descripción:

Consulta BanQuito para determinar si el cliente puede financiar la compra y cuál es su monto máximo.

Meta:

Mostrar requisitos y límite antes de elegir la venta a crédito.

Estado:

Aprobado

Versión:

1.0

Autores:

Grupo 09 · NRC 36884

Fecha creación:

27/10/2026

Fecha modificación:

27/10/2026

Precondiciones:

El servicio BanQuito está accesible y el operador tiene cédula del cliente.

Post condiciones:

Se muestran elegibilidad, motivos y monto devueltos por BanQuito; la tienda no modifica la base bancaria.

Gráfico:

Ilustración 4. Caso de uso Consultar elegibilidad y monto máximo

Ilustración 5. Actividad Consultar elegibilidad y monto máximo

Ilustración 6. Secuencia Consultar elegibilidad y monto máximo

Flujo Básico

Consultar elegibilidad y monto máximo

Actor

Sistema

1. Elige consultar elegibilidad.

2. Solicita cédula del cliente.

3. Ingresa y confirma la cédula.

4. Valida formato y envía al servicio BanQuito.

5. Consulta existencia, depósito, crédito activo y edad requerida.

6. Calcula límite según la regla bancaria vigente.

7. Recibe resultado y motivos.

8. Muestra monto máximo y condiciones.

Flujo Alternativo

A1. Cédula inválida: no enviar. A2. Cliente no existe, carece de depósito reciente o mantiene crédito activo: informar no elegible. A3. Para hombres se exige edad mínima de 25 años. A4. BanQuito no responde: informar indisponibilidad, no inventar elegibilidad ni monto. Regla implementada: max(0,(promedio depósitos − promedio retiros) × 0,35 × 6); el enunciado menciona 35%, aunque su fórmula impresa usa 30%.

Casos de uso incluidos: Ninguno.

Casos de uso extendidos: Ninguno.

ECUD3 — REGISTRAR VENTA EN EFECTIVO

A continuación, se presenta ECUD3 para registrar una venta con descuento del 42%.

Tabla 3. ECUD Registrar venta en efectivo.

Nombre Caso de Uso:

Registrar venta en efectivo

Identificador:

ECUD3

Descripción:

Registra la compra de un celular con descuento del 42% sobre el precio de lista.

Meta:

Emitir factura por un solo celular con precio calculado en el servidor.

Estado:

Aprobado

Versión:

1.0

Autores:

Grupo 09 · NRC 36884

Fecha creación:

27/10/2026

Fecha modificación:

27/10/2026

Precondiciones:

Existe un celular activo, el cliente y la cédula están identificados, y la API está disponible.

Post condiciones:

La factura confirmada conserva precio de lista, descuento del 42% y total pagado. No hay control de inventario.

Gráfico:

Ilustración 7. Caso de uso Registrar venta en efectivo

Ilustración 8. Actividad Registrar venta en efectivo

Ilustración 9. Secuencia Registrar venta en efectivo

Flujo Básico

Registrar venta en efectivo

Actor

Sistema

1. Elige venta en efectivo.

2. Presenta catálogo de celulares activos.

3. Selecciona celular e ingresa datos del cliente.

4. Valida campos requeridos y precio vigente.

5. Calcula precio con descuento del 42%.

6. Muestra resumen y solicita confirmación.

7. Envía solicitud de venta.

8. Persiste y devuelve la factura.

Flujo Alternativo

A1. Celular inactivo o inexistente: no emitir factura. A2. Datos incompletos: marcar campos. A3. Precio alterado por el cliente: usar precio vigente del servidor. A4. Error de persistencia: no confirmar la venta. Cada factura incluye un celular; el sistema no descuenta inventario.

Casos de uso incluidos: Ninguno.

Casos de uso extendidos: Ninguno.

ECUD4 — REGISTRAR VENTA A CRÉDITO

A continuación, se presenta ECUD4 para solicitar aprobación de BanQuito y emitir factura.

Tabla 4. ECUD Registrar venta a crédito.

Nombre Caso de Uso:

Registrar venta a crédito

Identificador:

ECUD4

Descripción:

Gestiona una venta financiada mediante aprobación remota y registro del crédito en BanQuito.

Meta:

Emitir factura solo cuando el banco confirme crédito y amortización.

Estado:

Aprobado

Versión:

1.0

Autores:

Grupo 09 · NRC 36884

Fecha creación:

27/10/2026

Fecha modificación:

27/10/2026

Precondiciones:

El cliente cumple elegibilidad; existe celular activo; BanQuito y la API están disponibles.

Post condiciones:

BanQuito registra crédito y amortización. La tienda emite una factura por el celular solo tras recibir aprobación; ante rechazo o error no confirma la venta.

Gráfico:

Ilustración 10. Caso de uso Registrar venta a crédito

Ilustración 11. Actividad Registrar venta a crédito

Ilustración 12. Secuencia Registrar venta a crédito

Flujo Básico

Registrar venta a crédito

Actor

Sistema

1. Elige venta a crédito.

2. Selecciona un celular y proporciona la cédula.

3. Consulta o valida elegibilidad en BanQuito.

4. Elige plazo de 3 a 18 meses.

5. Valida capacidad y presenta cuota estimada.

6. Confirma la solicitud de crédito.

7. BanQuito autoriza y registra el crédito.

8. Tienda emite factura tras aprobación.

Flujo Alternativo

A1. Cliente no elegible o monto insuficiente: informar y no emitir factura. A2. Plazo fuera de 3–18 meses: rechazar. A3. BanQuito rechaza: mostrar motivo y conservar sin venta. A4. Timeout o error remoto: no informar éxito ni emitir factura. A5. Tasa anual fija de 16,5%; se aplica la fórmula de cuota definida por el servicio bancario.. Incluye consultar elegibilidad (ECUD2).

Casos de uso incluidos: Ninguno.

Casos de uso extendidos: Ninguno.

ECUD5 — CONSULTAR FACTURA Y AMORTIZACIÓN

A continuación, se presenta ECUD5 para revisar una factura y su plan de pagos.

Tabla 5. ECUD Consultar factura y amortización.

Nombre Caso de Uso:

Consultar factura y amortización

Identificador:

ECUD5

Descripción:

Permite localizar facturas por cédula y consultar detalle del celular y, en compras financiadas, la amortización.

Meta:

Mostrar una factura persistida y sus pagos sin alterar datos.

Estado:

Aprobado

Versión:

1.0

Autores:

Grupo 09 · NRC 36884

Fecha creación:

27/10/2026

Fecha modificación:

27/10/2026

Precondiciones:

La API está disponible y el operador tiene la cédula de la compra.

Post condiciones:

Se muestra factura por un celular y, si fue financiado, plan de amortización consultado en BanQuito.

Gráfico:

Ilustración 13. Caso de uso Consultar factura y amortización

Ilustración 14. Actividad Consultar factura y amortización

Ilustración 15. Secuencia Consultar factura y amortización

Flujo Básico

Consultar factura y amortización

Actor

Sistema

1. Elige consultar factura.

2. Solicita cédula del cliente.

3. Ingresa la cédula y envía la consulta.

4. Valida formato antes de consultar.

5. Recupera facturas recientes.

6. Selecciona una factura.

7. Consulta detalle y estado del crédito.

8. Muestra precio, forma de pago y celular.

9. Si es crédito, solicita amortización a BanQuito.

10. Muestra cuotas, intereses y saldo recibido.

Flujo Alternativo

A1. Sin facturas: mostrar lista vacía. A2. Cédula inválida: no enviar. A3. Factura de contado: no solicitar amortización. A4. BanQuito no responde: conservar detalle y señalar que amortización no pudo cargarse. A5. No modificar ni duplicar facturas.

Casos de uso incluidos: Ninguno.

Casos de uso extendidos: Ninguno.

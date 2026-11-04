# Revisión del examen de celulares — 4 de noviembre de 2026

## Seguimiento: puntos 1 y 2 resueltos

Después de la revisión inicial, se aplicó `03. BDD/03_MigrarImagenes.sql` a `ComercializadoraCelulares` y se repitió sin errores. Los recuentos y CHECKSUM_AGG de los campos originales permanecieron iguales: CELULAR, 3 filas y huella 1004711225; FACTURA, 2 filas y huella 636696342. Se añadieron IMAGEN e IMAGEN_TIPO como columnas opcionales. Las versiones anteriores pueden seguir usando la base ampliada, sin eliminar columnas.

Se incorporaron a `04. SERVIDOR` los cinco proyectos BanQuito: API, dominio, contratos, administración y pruebas. Sus 14 archivos fuente/configuración se compararon por SHA-256 con el origen al copiarlos. Los dos scripts SQL están en `03. BDD/BanQuito` y la descripción bancaria en `01. UML/02. ECUD/CasosUsoCreditoBanQuito.md`. El proyecto de origen permanece sin editar. Las aplicaciones conservan bases y ensamblados separados; la integración sigue siendo HTTP.

Se corrigieron el manual y los README para ejecutar todo desde esta raíz. El generador MER utiliza este repositorio por defecto, sin escribir en el proyecto vecino; no se regeneraron ni alteraron los modelos existentes.

Validación posterior: 20/20 pruebas bancarias y 19/19 pruebas de tienda aprobadas; API e inicializador bancarios compilan sin errores ni advertencias. Usando los servidores de este repositorio: catálogo HTTP 200 con 3 celulares, elegibilidad vía tienda HTTP 200, monto máximo por código consistente, amortización HTTP 200 con saldo final cero, web HTTP 200 con catálogo y factura web HTTP 200 con amortización. Los servicios temporales se detuvieron al terminar. No se repitieron ventas nuevas en las cuatro interfaces.

Los apartados siguientes documentan la situación inicial; los hallazgos 1, 2 y las rutas del hallazgo 3 quedan superados por este seguimiento. El diagrama UML bancario terminado, la decisión 35%/30%, la actualización de modelos y la demostración completa en cuatro clientes siguen pendientes.

## Revisión inicial

Fuente: `ExamenComplexivoPractivo_CELULARES.docx`. Revisión de código, documentos, modelos, compilación, pruebas, consultas SQL de solo lectura y solicitudes HTTP GET. No se modificaron datos ni se aplicaron migraciones. No se repitió una venta nueva en las cuatro interfaces.

## Dictamen

El proyecto tiene implementada gran parte de la solución, pero **no está listo para acreditar cumplimiento integral de la rúbrica con la entrega actual**. El repositorio contiene la comercializadora; el banco requerido se encuentra fuera de él. Además, la base principal está desactualizada: el catálogo falla al ejecutarse con la configuración predeterminada.

Se distingue entre implementación disponible en esta computadora y contenido entregado en este repositorio. Compilar y pasar pruebas unitarias no demuestra por sí solo que todos los flujos funcionan en los cuatro clientes.

## Hallazgos prioritarios

1. **Bloqueo de ejecución: catálogo HTTP 503.** `GET http://127.0.0.1:19102/api/celulares` falla con SQL Server error 207: `Invalid column name 'IMAGEN'`. La base `ComercializadoraCelulares` solo tiene ID_CELULAR, NOMBRE, PRECIO y ACTIVO. `ServicioCatalogo.Listar` necesita IMAGEN. La migración `03. BDD/03_MigrarImagenes.sql` existe y agrega IMAGEN e IMAGEN_TIPO, pero no está aplicada en esa base. La base QA sí tiene ambas columnas. Esto bloquea la selección normal de celulares y la demostración del catálogo y ventas en los cuatro clientes con la configuración predeterminada. La ruta `/api/salud` devuelve 200 porque solo abre la conexión; no detecta la incompatibilidad del esquema.
2. **Entrega incompleta de BanQuito.** No están en este repositorio sus fuentes, contratos, pruebas ni scripts de creación y carga del Core. Se encontraron y revisaron como referencia, sin editar, en `../../U1/TG.1/1.4. PAO202651_RESTFUL_DOTNET_CONBDD_NRC36884_GR09`. Separar las aplicaciones es correcto; la entrega debe permitir obtener y ejecutar ambas. Un clon de este repositorio, por sí solo, no permite reproducir el examen completo.
3. **Instrucciones de ejecución con ruta incorrecta.** `05. DOCUMENTACION/ManualTecnico.md`, líneas 21 y 33, usa `../../TG.1/...`. Esa ruta no existe desde esta carpeta; la ubicación local encontrada es `../../U1/TG.1/...`. En un clon independiente tampoco existirá necesariamente esta última ubicación. Hace falta una instrucción reproducible para obtener y configurar el banco.
4. **Diagrama bancario insuficientemente entregado.** Los casos de uso renderizados aquí representan la comercializadora. El proyecto vecino tiene `01. UML/CasosUsoCreditoBanQuito.md`, con descripción y un flowchart Mermaid de las funciones bancarias; no se encontró allí una exportación específica BanQuito dentro de su carpeta UML. Un script generador presente aquí no equivale al diagrama UML terminado y entregado. La rúbrica asigna 2 puntos específicamente al diagrama del módulo de crédito.
5. **Ambigüedad del propio enunciado.** El texto establece 35%, pero la fórmula impresa dice 30%. El banco implementa `max(0, (promedio depósitos - promedio retiros) * 0.35 * 6)` y lo prueba explícitamente. El ECUD de este proyecto documenta esa decisión. Conviene obtener el criterio del docente; no corresponde afirmar que 35% sea un error inequívoco.
6. **Evidencias y modelos por actualizar.** README dice que no se comprobó ejecución en emulador; VERIFICACION_EXAMEN afirma que sí se hizo. En esta revisión se confirmó un emulador conectado y el paquete instalado, pero no se repitió el flujo móvil completo ni se verificó que el APK instalado corresponda al código actual. El modelo físico `GR09_Celular_Physical_SQLServer.pdm` y su PNG no incluyen las columnas de imagen del esquema actual. Una exportación de arquitectura está recortada; existe otra legible, `GR09_Arquitectura_Arquitectura cliente-servidor.png`, que muestra ambos servicios y ambas bases.

## Matriz de rúbrica

Los puntos son los máximos del documento, no una calificación otorgada. La fila de facturación contiene dos valores, 2 y 3; se interpreta como 5 puntos en conjunto porque así la suma llega a los 20 declarados.

| Requisito | Puntos | Estado y evidencia |
|---|---:|---|
| Diagrama de casos de uso del módulo de crédito BanQuito | 2 | Parcial. Diagrama específico no entregado aquí; flowchart y descripción en proyecto externo. |
| Descripción del caso de uso de sujeto de crédito | 1 | Cubierto documentalmente por ECUD2; la descripción bancaria más precisa está en el proyecto externo. Incorporar la evidencia bancaria a la entrega. |
| Core: 5 clientes, 5 cuentas, 50 movimientos y entidades de crédito | 2 | Verificado en SQL local: 5/5/50, más CREDITO y AMORTIZACION. Scripts disponibles fuera del repositorio. |
| Diagrama entidad–relación de comercializadora | 1 | Presente: modelos conceptual, lógico y físico editables y PNG. Sin inventario. Actualizar las columnas de imagen. |
| Servicio de elegibilidad por cédula | 1,5 | Implementado en banco externo. HTTP verificado para cliente inexistente, hombre menor de 25, falta de depósito, crédito activo y cliente elegible. |
| Servicio de monto máximo por código de cliente | 1,5 | Implementado en banco externo. GET del cliente 3: HTTP 200 y 2142,00. Usa 35%; enunciado ambiguo. |
| Otorgar crédito y crear amortización por cliente, precio y cuotas | 2 | Código bancario revisado: valida elegibilidad, monto y plazo; guarda crédito y cuotas en transacción. 20 pruebas bancarias pasan. Existe crédito persistido con amortización; no se ejecutó un otorgamiento nuevo en esta revisión. Fuentes externas. |
| Mantenimiento del catálogo | 1 | CRUD implementado y compartido por clientes, pero ejecución actual bloqueada por IMAGEN ausente en la base principal. |
| Facturación en efectivo y crédito en cuatro clientes | 5 | Código presente en consola, WPF, web y MAUI. Descuento del 42% correcto; facturas persistidas de ambos tipos. No acreditado de extremo a extremo hoy: catálogo bloqueado y ventas nuevas no repetidas en cada interfaz. |
| Servicio SOAP/REST que retorna amortización y consumo en cuatro clientes | 1 | REST bancario y pasarela de tienda implementados; cuatro clientes tienen consumo. Consulta HTTP de factura 2 devuelve tabla completa con saldo final cero. Demostración visual de los cuatro clientes pendiente. |
| Consulta de amortización desde comercializadora | 1 | Verificado: GET de amortización HTTP 200 y página web de factura 2 HTTP 200 con tabla. |
| Diagrama de arquitectura completo | 1 | Presente y revisado visualmente: cuatro clientes, API comercializadora, API BanQuito y dos bases. Usar exportación legible. |

## Verificación realizada hoy

- Pruebas comercializadora: **19 aprobadas, 0 fallidas, 0 omitidas**.
- Pruebas BanQuito externo: **20 aprobadas, 0 fallidas, 0 omitidas**.
- API comercializadora compilada al ejecutar pruebas; API BanQuito compilada explícitamente. Clientes consola, WPF, ASP.NET Core MVC y MAUI Android compilados: **0 errores y 0 advertencias**.
- SDK: `D:/tools/dotnet10/dotnet.exe`. Compilación Android con SDK en `D:/tools/android-sdk`. Paquetes y salidas en D:.
- SQL Server SQLEXPRESS activo. Base principal bancaria: 5 clientes, 5 cuentas, 50 movimientos y 1 crédito. Base principal tienda: 3 celulares y 2 facturas.
- Factura 1: efectivo; precio 450,00, descuento 189,00, total 261,00, APROBADA.
- Factura 2: crédito; precio y total 450,00, APROBADA, crédito 1, tres cuotas. Tabla: saldo inicial 450,00; pagos 154,14 / 154,14 / 154,15; saldo final 0,00; capital amortizado total 450,00. El último pago absorbe un centavo de redondeo; documentar este ajuste al defender la cuota fija.
- Elegibilidad bancaria: cliente inexistente rechazado, cliente 2 rechazado por edad, cliente 3 elegible, cliente 4 rechazado por falta de depósito y cliente 5 rechazado por crédito activo.
- Ambos servicios `/api/salud`: HTTP 200. Catálogo: HTTP 503 por esquema. Web principal: HTTP 200 con aviso de error del catálogo; no implica funcionamiento del catálogo. Web de factura 2: HTTP 200 con amortización.
- La primera ejecución web con salidas existentes falló por manifiesto de dependencias desactualizado tras compilar sin restauración. Una compilación normal con restauración regeneró ese manifiesto y permitió iniciar. No se considera un defecto confirmado del código fuente.
- Se inspeccionaron ER físico, casos de uso de tienda y dos exportaciones de arquitectura. No se certificó fidelidad visual completa de todos los Word/PPT ni de todas sus páginas.
- Se iniciaron servicios temporalmente para consultas de lectura; se detuvieron al terminar. No se aplicó la migración ni se alteraron bases.

## Condiciones para cerrar la revisión

1. Aplicar la migración de imágenes en el entorno de demostración y comprobar catálogo y mantenimiento.
2. Completar la entrega reproducible de BanQuito y corregir las instrucciones para obtenerlo y ejecutarlo.
3. Entregar el diagrama UML bancario con su fuente editable y exportación, y su caso de uso detallado.
4. Acordar/documentar el porcentaje del monto máximo frente a la contradicción 35%/30%.
5. Repetir en cada cliente una venta en efectivo, una a crédito y la consulta de amortización; conservar evidencia actual. Probar también rechazos y plazos fuera de 3–18.
6. Actualizar evidencias contradictorias, modelo físico y exportaciones usadas en la defensa.

No se asigna una nota exacta: hay implementación externa y evidencia parcial, y la rúbrica exige mostrar y defender los puntos ante el tribunal. Las funciones adicionales de fotos y temas no suman puntos según el propio enunciado.

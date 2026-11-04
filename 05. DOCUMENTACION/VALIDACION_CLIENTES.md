# Paso 3: clientes consola y web

Fecha: 4 de noviembre de 2026.

## Resultado

14 comprobaciones aprobadas usando `python scripts/VerificarClientesQA.py`. El script crea bases QA únicas, levanta API temporales y conserva los datos para inspección. No modifica bases principales y detiene únicamente sus procesos.

Consola ejecutada con entradas del menú real: catálogo, alta, edición, desactivación, venta en efectivo, crédito nuevo a tres meses y búsqueda/consulta con amortización a saldo cero. Transcripción: `EVIDENCIA_CONSOLA.txt`.

Web ejecutada por HTTP contra MVC: catálogo, alta, edición, desactivación, venta en efectivo, crédito nuevo y búsqueda. Se utilizan cookies y el token antiforgery real; la redirección entrega factura aprobada y amortización renderizada. HTML: `EVIDENCIA_WEB_FACTURA.html`. No se probó JavaScript ni apariencia mediante navegador.

Detalle de casos y bases: `EVIDENCIA_CLIENTES_QA.json`.

## Compilación

- Consola y WPF: cero errores y advertencias.
- Web: cero errores y advertencias usando salida aislada `D:/tools/CelularGR09_WebQA`; la salida habitual está bloqueada por una instancia externa, que no se interrumpió.
- MAUI Android: cero errores, una advertencia MSB3026 por reintento de copia de un ensamblado compartido durante compilaciones concurrentes. No es evidencia de ejecución móvil.
- Emulador `emulator-5554` conectado.

## Pendiente

WPF y Android ya se ejecutaron sobre QA: mantenimiento, efectivo, crédito nuevo, búsqueda y consulta de amortización aprobados. Ver VALIDACION_VISUAL_QA.md y las evidencias correspondientes. La inspección visual y JavaScript de la web se completó en VALIDACION_WEB_DOCUMENTACION.md, después de corregir el parseo decimal MVC. Documentación y diagramas siguen en cierre.

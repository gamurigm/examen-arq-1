# Verificación web en navegador y documentación

Fecha: 4 de noviembre de 2026.

## Web: aprobado con corrección

Chrome headless, viewport de escritorio 1440 px y estrecho 390 px: 13 comprobaciones aprobadas. Se probaron JavaScript, temas, catálogo, alta/edición/desactivación, efectivo, crédito nuevo, elegibilidad por fetch, búsqueda y reapertura. No hubo excepciones JavaScript ni desbordamiento horizontal a 390 px. Se inspeccionaron visualmente las capturas responsive y de factura de crédito.

La prueba reprodujo un defecto real: el navegador envía PrecioEsperado=450.00 y el proveedor MVC con cultura local lo interpretaba incorrectamente, provocando conflicto de precio. Se corrigió únicamente la interpretación de valores de formularios MVC con cultura invariante. El idioma y formato de presentación se conservan. Ambas ventas completaron después de recompilar; cero errores y advertencias de compilación.

Evidencia: EVIDENCIA_WEB_NAVEGADOR.json y evidencias/web_*.png. Reproducción: activar API QA con IniciarQAVisual.py, iniciar web en 19203 con CelularesApiUrl=http://127.0.0.1:19202/, ejecutar VerificarWebNavegador.py con las dependencias documentales instaladas. Usar bases QA nuevas para repetir crédito.

## Documentación: borradores generados

Se preservaron las fuentes importadas y entregas anteriores. Las fuentes *_verificado.md y documentation-profile.json alimentan GenerarDocumentacion.py. Se conserva el diseño de estilos/tablas y tema de las plantillas, reemplazando su contenido por los requisitos actuales.

Borradores externos: D:/tools/CelularGR09-documentacion/borradores. Se generan ERS, ECUD, manual y presentación; manifest.json registra hashes de plantilla, fuente y borrador. ValidarDocumentacion.py pasó sin errores en modo de entradas.

Renderizados: D:/tools/CelularGR09-documentacion/renderizados. ERS: 3 páginas; ECUD: 8; manual: 3; presentación: 12 diapositivas. Se revisaron las hojas de contacto de todas las páginas; se corrigieron contraste de títulos y estilos heredados. No están promovidos a entregables finales: faltan figuras actualizadas, trazabilidad completa y revisión final del paquete.

Comandos, desde un entorno con scripts/requirements-documentacion.txt instalado:

```powershell
python scripts/ValidarDocumentacion.py
python scripts/GenerarDocumentacion.py
python scripts/RenderizarDocumentacion.py --soffice D:/tools/LibreOffice/program/soffice.exe
```

## Diagramas: bloqueo comprobado

El intento de ejecutar el VBS abrió PowerDesigner - Licensing con el mensaje "The trial period has expired" (16.1.0.3637). No se generó el diagrama bancario ni se reemplazaron modelos existentes. Se detuvo el generador bloqueado. Hace falta una licencia válida para cerrar la regeneración mediante COM/VBS. Las fuentes existentes pueden seguir inspeccionándose sin declarar regeneración exitosa.

Siguiente etapa: contrastar modelos existentes con SQL y arquitectura Docker, completar las figuras y cerrar documentos/matriz de rúbrica. La aplicación funcional y las evidencias actuales no equivalen todavía a entrega documental completa.

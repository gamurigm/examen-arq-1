# Revisión de diagramas y documentos

Fecha: 4 de noviembre de 2026.

## Diagramas incluidos

El manual y la presentación comparten `05. DOCUMENTACION/fuentes/manual_verificado.md` y contienen seis exportaciones PNG de PowerDesigner: casos de uso, actividad, secuencia, clases, arquitectura y MER físico. Los hashes de las imágenes fuente están registrados en `05. DOCUMENTACION/EVIDENCIA_DIAGRAMAS.json`; se confirmó que ambos paquetes Office contienen esos mismos PNG.

Los modelos nativos se conservaron. No se regeneraron durante esta revisión porque la licencia de evaluación de PowerDesigner venció. La exportación PowerDesigner existente de arquitectura tiene rótulos recortados en sus bordes; se mantuvo por su procedencia. Corregirla requiere ajustar y exportar el modelo desde PowerDesigner con licencia válida. No se usó la figura SVG alternativa en los manuales.

## Entregables promovidos

| Artefacto | Páginas/diapositivas | Revisión |
| --- | ---: | --- |
| Manual técnico DOCX | 39 páginas | Índices de contenido e ilustraciones actualizados; diagramas PowerDesigner en páginas propias; render revisado. |
| Presentación PPTX | 72 diapositivas | Misma fuente y cobertura del manual; seis diagramas en diapositivas propias; render revisado. |

Se mantuvieron las plantillas Office y se retiró el texto heredado de la portada. No quedan referencias heredadas EurekaBank, SOAP o Java. Las diapositivas y páginas se revisaron en sus renderizados; no se forzó la cantidad del ejemplo.

La fuente canónica tiene SHA-256 `d190ee3bd4f30b25363dbb4e64909c1038834a80ed5c91b58f415e6dba52fea3`. Los hashes de documentos y PDF están en `05. DOCUMENTACION/REVISION_RENDERIZADOS.json`. Respaldo previo local: `05. DOCUMENTACION/.trabajo/respaldo-previo-promocion/`.

La revisión cubre contenido y renderizado documental; no recompila ni vuelve a ejecutar las API o los cuatro clientes.

# Revisión de portada, títulos y diagramas

Fecha: 4 de noviembre de 2026.

## Portada y títulos

La portada del manual conserva el máster oficial `examples/05.Documentacion/04.WS_EXAMEN_GRUPO_1.docx`, incluida su imagen original de Sulley de Monsters, Inc., el marco y los elementos gráficos. El generador ya no sustituye ni redimensiona esa imagen. El SHA-256 de la imagen del DOCX coincide con el del máster: `f117d1949a15ffe64febbc9f0782e2f52169ffcb52cedeb518167eef3a2c0ae4`.

Se revisó `examples/03. PAO202651_CONJUNTAUNO_RESTFUL_JAVA.docx` como referencia de lectura. Los resultados aparecen en español claro, sin títulos con la sigla QA; en Word se muestran como rótulos en negrita dentro del contenido y no llenan el índice. Los registros detallados se referencian en una sola sección.

## Diagramas incluidos

El manual y la presentación comparten `05. DOCUMENTACION/fuentes/manual_verificado.md` y contienen las seis exportaciones PNG originales de PowerDesigner: casos de uso, actividad, secuencia, clases, arquitectura y MER físico. Se confirmó que ambos paquetes Office contienen los mismos seis PNG.

Los modelos nativos se conservaron. No se regeneraron durante esta revisión porque la licencia de evaluación de PowerDesigner venció. El PNG existente de arquitectura conserva rótulos recortados en los bordes; no se reemplazó por una figura de otro origen.

## Tamaño y distribución de imágenes

Se revisaron las 30 páginas renderizadas del DOCX y las 65 diapositivas del PPTX. Las figuras de Word quedan limitadas a 5,25 pulgadas de alto. En PowerPoint, las 25 imágenes permanecen dentro del lienzo, ninguna mide menos de 1,5 pulgadas de ancho y no se detectó cruce entre imágenes y cuadros de texto.

La captura web adaptable original de 390 × 2912 píxeles se conserva en evidencias. En ambos documentos aparece dividida en seis tramos consecutivos: en Word se organiza en dos columnas y en PowerPoint se distribuye en tres diapositivas con dos tramos cada una. La secuencia cubre la captura completa, sin deformar ni omitir contenido.

## Entregables revisados

| Artefacto | Páginas/diapositivas | Revisión |
| --- | ---: | --- |
| Manual técnico DOCX | 30 páginas | Portada original e índice conservados; diagramas PowerDesigner presentes; imágenes de altura moderada; render completo revisado. |
| Presentación PPTX | 65 diapositivas | Misma fuente canónica; seis diagramas PowerDesigner; tamaños corregidos y render completo revisado. |

La fuente canónica tiene SHA-256 `0dfc01b8ce3e3ca9135dc81cdfa22a6f6198096ca73f046c8e6e28206f3fc6e0`. Los hashes de documentos y PDF están en `05. DOCUMENTACION/REVISION_RENDERIZADOS.json`. Respaldo previo a este ajuste: `05. DOCUMENTACION/.trabajo/respaldo-antes-ajuste-imagenes-20261104/`.

La revisión cubre contenido y renderizado documental; no recompila ni vuelve a ejecutar las API o los cuatro clientes. Los cambios de presentación no alteran sus ejecuciones.

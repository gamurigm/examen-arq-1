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

## Seguimiento documental — 5 de noviembre de 2026

Se generaron y renderizaron nuevos borradores del manual y la presentación desde la misma fuente `05. DOCUMENTACION/fuentes/manual_verificado.md` (90 secciones; SHA-256 `e827122062f6f3030da21a99b950274cc110ffeaa8953180abbf2ec03458277a`; hash de contenido canónico `e7fb72616c9b44c065b80a55d52ec990e654af1429319c87b5dfb68da013b977`). Word y PowerPoint COM exportaron 39 páginas y 96 diapositivas. Se revisaron las hojas de contacto de todos los renderizados y páginas representativas en tamaño completo.

| Borrador | Render | Revisión actual |
| --- | ---: | --- |
| Manual técnico DOCX | 39 páginas | La portada conserva la imagen original de Monster y el marco del ejemplo; están las seis figuras PowerDesigner y el anexo SQL. Los bloques de código son monoespaciados y las capturas del cliente no invaden los encabezados. |
| Presentación PPTX | 96 diapositivas | Conserva la plantilla aprobada y sus seis figuras PowerDesigner. La explicación acompaña a una o dos capturas; las capturas verticales de catálogo y amortización tienen una diapositiva propia cuando el texto reduciría su tamaño. La captura web adaptable se reparte en tres diapositivas con dos tramos cada una. Las imágenes miden al menos 1,56 pulgadas de ancho; no se detectaron imágenes sobrepuestas ni fuera del lienzo. |

Los borradores están en `05. DOCUMENTACION/.trabajo/borradores/`; aún no sustituyen los entregables oficiales. Las imágenes `IDE_SolutionExplorer.png`, `IDE_BDDSqlServer.png` e `IDE_ApiEjecucion.png` son placas con texto, no capturas de Visual Studio, y no se usaron como evidencia. Visual Studio Community 2026 sí está instalado. El primer inicio quedó en la pantalla inicial de cuenta; el modo seguro mostró además un error al cargar el menú. No se abrió el proyecto ni se capturó su configuración. Se pidió omitir manualmente la pantalla inicial para continuar; no se ingresaron credenciales. Las capturas auténticas solicitadas siguen pendientes; cuando el proyecto esté abierto se deben añadir a la fuente canónica, regenerar ambos archivos y volver a revisar los renderizados.

La licencia de evaluación de PowerDesigner sigue vencida. Se conservaron las exportaciones existentes y no se modificaron los modelos nativos. Esta revisión no volvió a ejecutar las API ni a compilar clientes.

## Publicación de la ampliación — 5 de noviembre de 2026

Se sustituyeron el manual técnico y la presentación oficiales por los borradores revisados de 39 páginas y 96 diapositivas. Se guardó una copia previa en 05. DOCUMENTACION/.trabajo/respaldo-antes-ampliacion-20261105/. Los hashes oficiales coinciden con los borradores revisados y constan en REVISION_RENDERIZADOS.json.

Visual Studio superó la pantalla de cuenta, pero mostró errores internos de inicialización. ActivityLog.xml registra E_ACCESSDENIED (0x80070005) en EditorPackage, GlobalHubClientPackage y Roslyn/ServiceHub. Las capturas auténticas de configuración continúan pendientes por ese fallo; los archivos de configuración y scripts documentados proceden del repositorio. La entrega publicada no incluye placas de texto presentadas como capturas.

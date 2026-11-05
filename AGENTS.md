# Reglas del proyecto GR09

- Implementar únicamente .NET REST. BanQuito y comercializadora son API separadas; comunicación HTTP sin compartir bases ni ensamblados de dominio.
- Docker ejecuta solo SQL Server. Las API, consola, WPF, MVC y MAUI se ejecutan en el host. No agregar inventario.
- Preparación: copiar `.env.example` a `.env`, configurar contraseña y ejecutar `./PrepararEntorno.ps1 -IniciarApis`. Nunca publicar `.env` ni borrar volúmenes o bases sin instrucción explícita.
- La rúbrica fuente es `ExamenComplexivoPractivo_CELULARES.docx`. Exige cuatro clientes, efectivo con 42% de descuento, crédito de 3–18 cuotas y tasa anual 16,5%. Se conserva 35% para máximo; documentar contradicción con fórmula al 30%.
- Usar `examples` como plantillas de ERS, ECUD, manual y presentación. Referencia de aprendizaje: `../../U1/TG.1`, scripts GenerarDocumentacionEurekaBank.ps1, GenerarDocumentacionTecnicaEurekaBankGR09.ps1 y GenerarPresentacionesEurekaBankGR09.py. No depender de esa ruta al ejecutar la entrega.
- Generar documentos desde copias de las plantillas, preservar estilos y tablas; reemplazar texto heredado y verificar visualmente todas las páginas antes de sustituir resultados. No afirmar que se regeneraron documentos sin ejecutar y revisar el proceso.
- Diagramas: todos los diagramas del proyecto se elaboran en PowerDesigner. Sus modelos nativos y exportaciones PNG son la fuente oficial; está prohibido sustituirlos en los manuales DOCX/PPTX por SVG, Mermaid, figuras dibujadas con scripts u otros diagramas recreados fuera de PowerDesigner. Usar las exportaciones existentes en `01. UML/03. DIAGRAMAS UML` y `02. MER`; si hace falta regenerar, ejecutar `cscript //nologo "01. UML/GenerarDiagramasCelulares.vbs" <raiz> <raiz>` y los generadores de casos específicos con sus argumentos. Revisar destinos antes de ejecutar y conservar modelos completos. Si la licencia bloquea la exportación, mantener las imágenes PowerDesigner existentes y documentar el bloqueo; nunca reemplazarlas con figuras de otra procedencia. Fuente editable y PNG legible son obligatorios. Revisar casos de uso, actividad, secuencia, clases, arquitectura y MER.
- MER: ejecutar `02. MER/GenerarModelosCelulares.ps1` indicando ambas raíces locales. Comparar columnas, claves y relaciones con scripts SQL; no sobrescribir modelos manuales sin respaldo.
- Cierre: pruebas de ambas API, compilación de cuatro clientes y evidencia por interfaz de catálogo, efectivo, crédito nuevo y amortización. Usar QA para ventas; nunca reiniciar datos principales para pruebas. Distinguir probado, implementado y pendiente.

## Formato obligatorio de los ejemplos Office

- Los archivos de `examples` son los masters aprobados y la referencia de formato. Adaptar su contenido al proyecto GR09 y conservar al pie de la letra sus portadas, logos, paleta, tipografías, jerarquía y numeración de títulos, tablas, márgenes, secciones, encabezados, pies, índices, layouts, masters y distribución de figuras.
- Partir siempre de una copia del archivo Office correspondiente. Sustituir el texto, las capturas y las referencias heredadas del proyecto de ejemplo; no reconstruir el documento con un estilo genérico, borrar sus masters o dejar contenido EurekaBank/Java/SOAP.
- Una figura solo se inserta en la sección que describe y debe apuntar a una captura real o diagrama del proyecto. No asignar imágenes por orden alfabético ni estirar capturas para llenar marcos.
- Mantener todos los capítulos y pasos que estén respaldados por el proyecto. El número de páginas/diapositivas sigue el contenido: no añadir relleno para imitar una cantidad si no hay información, y no comprimir el manual eliminando pasos que sí están documentados.

## Fuente compartida del manual DOCX y PPTX

- `05. DOCUMENTACION/fuentes/manual_verificado.md` es la única fuente canónica tanto del manual DOCX como del PPTX. Ambos deben contener los mismos capítulos, procedimientos, resultados, restricciones, diagramas, capturas y metadatos; el perfil debe apuntar ambos artefactos a ese mismo archivo.
- La equivalencia se valida por contenido y evidencia, no por cantidad de páginas. Word puede distribuir varios capítulos en una página y PowerPoint puede dividir un capítulo entre diapositivas para mantener texto legible; no se fuerza una página por capítulo ni un total fijo de diapositivas.
- Usar los layouts del ejemplo que mejor acomoden cada capítulo, manteniendo sus masters, fondo, paleta, tipografía, navegación, títulos, numeración y proporción de imágenes. Si un bloque no cabe legiblemente, redistribuirlo o dividirlo; nunca dejar que invada el encabezado ni reducirlo hasta volverlo ilegible.
- `presentacion_verificado.md` no es una fuente de generación independiente. No editar una narración paralela; actualizar `manual_verificado.md` para regenerar los dos formatos.
- La generación debe fallar si manual y PPTX apuntan a fuentes distintas, falta una figura, se omite contenido canónico o quedan textos/imágenes heredados.

## Generación documental reproducible

Instalar `scripts/requirements-documentacion.txt` en un entorno virtual. Ejecutar, desde la raíz, `python scripts/ValidarDocumentacion.py`, `python scripts/GenerarDocumentacion.py` y `python scripts/RenderizarDocumentacion.py --soffice <ruta-soffice>`. `documentation-profile.json` define fuentes, plantillas y carpetas de borradores/renderizados; `manifest.json` registra hashes y correspondencia de capítulos. No borrar las fuentes importadas como parte de una regeneración.

Revisar los renderizados de todas las páginas y diapositivas antes de sustituir entregables; los borradores no sustituyen automáticamente los Word/PPT oficiales. PowerDesigner 16.1 está instalado, pero la licencia de evaluación está vencida: no afirmar que los VBS terminaron ni modificar la licencia. Reutilizar las exportaciones PNG PowerDesigner existentes y conservar los modelos. Si falta una exportación y la licencia impide generarla, registrar el bloqueo en el informe de rúbrica; no sustituirla por una imagen recreada.

## Figuras PowerDesigner obligatorias en documentos

El DOCX y el PPTX deben incluir las exportaciones PNG originales de PowerDesigner para casos de uso, actividad, secuencia, clases, arquitectura y MER, en los capítulos que las explican. La fuente canónica `05. DOCUMENTACION/fuentes/manual_verificado.md` debe apuntar directamente a esos PNG; la generación debe fallar si falta una imagen, si una figura del manual no proviene de PowerDesigner o si DOCX y PPTX no tienen la misma cobertura.

`01. UML/GenerarFigurasEntrega.vbs` genera SVG sin PowerDesigner y `scripts/VerificarDiagramas.py` las renderiza a PNG para comprobaciones auxiliares del modelo SQL. Esos SVG/PNG no son exportaciones PowerDesigner y no se deben insertar en el DOCX ni en el PPTX.

El generador documental permite seleccionar artefactos con `--artifacts`. No declarar un Word o una presentación revisados mientras sus fuentes, plantillas, índices y renderizados no hayan sido comprobados. Las 83 diapositivas del ejemplo son una referencia de diseño, no una meta de cantidad.

## Manual técnico DOCX y PPTX: misma información obligatoria

- El manual técnico DOCX y su versión PPTX son dos formatos del mismo manual. Deben contener la misma información: alcance, arquitectura, requisitos del entorno, configuración, base de datos, compilación, ejecución, procedimientos, pruebas, resultados, errores, limitaciones, diagramas y capturas correspondientes.
- Usar una única fuente canónica de contenido del manual para generar ambos formatos. El perfil puede definir su distribución visual; no mantener dos narraciones independientes que diverjan.
- Escribir los títulos del manual en español directo. Usar «Pruebas» o «Resultados de pruebas»; no poner la sigla «QA» en encabezados destinados al lector. Conservar nombres reales de scripts y archivos de evidencia cuando se documenten comandos.
- Adaptar únicamente la distribución y presentación: párrafos, tablas y figuras en Word; bloques legibles distribuidos entre diapositivas en PowerPoint. No resumir eliminando información del PPTX ni incorporar pruebas, pasos o explicaciones que falten en el DOCX.
- Mantener correspondencia verificable entre cada sección, procedimiento, figura y evidencia del DOCX y sus diapositivas. Los mismos metadatos, valores y resultados deben coincidir en ambos; registrar el hash de la fuente compartida.
- No rellenar la presentación para alcanzar el número de diapositivas de la plantilla ni comprimir el manual para obtener pocas páginas. Conservar la identidad visual de las plantillas y dimensionar ambos entregables según el contenido real.
- Páginas y diapositivas no tienen que coincidir numéricamente. Una diferencia amplia obliga a verificar cobertura, legibilidad e integridad de contenido; no aprobar mientras haya información presente en un formato y ausente en el otro.
- Validar la equivalencia de contenido y revisar todos los renderizados antes de sustituir los documentos oficiales. La generación de dos archivos que abren correctamente no acredita esta equivalencia.

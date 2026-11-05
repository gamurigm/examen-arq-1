# Registro de implementación del manual práctico

## Alcance
Fuente canónica única para Word y PowerPoint; 75 archivos propios documentados con listados completos, incluidos recursos, configuración y pruebas. No se utiliza un objetivo de páginas.

## Decisiones
- Trabajar en checkout aislado para conservar el repositorio principal.
- Mantener las imágenes PowerDesigner originales y las capturas web/Android existentes.
- Excluir las placas IDE_* y Cliente_Consola/Cliente_WPF: la revisión visual confirmó que contienen texto de marcador.
- Corregir únicamente el import System.IO del controlador WPF, necesario para que Stream compile. El listado del manual incluye el código corregido.
- Usar bases nuevas en el contenedor manualgr09; no alterar las bases del proyecto EurekaBank que ya estaban activas.
- No presentar los casos de comprobación como pruebas ejecutadas; registrar las ejecuciones nuevas y sus limitaciones aparte.

## Seguimiento
Contenido por archivo y recorridos escritos; ambos formatos generados y código completo contrastado. Se añadieron siete capturas reales y registros de compilación, pruebas unitarias y operaciones HTTP. La revisión visual está documentada en REVISION_RENDERIZADOS.json. Permanecen pendientes las pantallas gráficas de instalación, proyecto cargado en Visual Studio y SSMS, y la repetición completa de mantenimiento y ventas desde cada interfaz.

## Matriz de discrepancias y estado

| Discrepancia | Acción realizada | Límite o pendiente |
|---|---|---|
| Documentación resumida | 75 archivos propios con explicación, relaciones y código completo; 48 capítulos | La explicación de cada método se complementa con su listado; no se copian dependencias externas |
| Instalación poco detallada | Pasos de cargas, SDK, Docker, SQL Server y Android; captura real del entorno instalado | Pantallas del instalador no capturadas |
| Persistencia sin evidencia visual | Captura real de sqlcmd con ambas bases y contenedor healthy | Secuencia gráfica de SSMS pendiente |
| Servidor sin respuesta observable | Salud y catálogo HTTP200; facturas HTTP201; amortización HTTP200; rechazo HTTP400 | Carga de proyecto en Visual Studio bloqueada por E_ABORT |
| Consola y WPF sin imágenes auténticas | Capturas reales del catálogo de ambos clientes; placas descartadas | Recorridos completos de mantenimiento y venta por interfaz pendientes |
| Capturas web y Android | Conservadas e identificadas como históricas; Android compilado de nuevo | No se repitió todo el recorrido Android |
| Código demasiado compacto | Texto normal11pt, tablas10pt, código9pt; secciones horizontales y nombres repetidos | PDFs de LibreOffice tienen diferencias respecto a Word |
| PPT pierde líneas largas | División de líneas minificadas con reconstrucción exacta; nombre del archivo en cada fragmento | La extensión aumenta al conservar todos los listados |
| Imágenes lejos del procedimiento | Agrupación solo de imágenes consecutivas en Word y PowerPoint | Capturas anchas reciben una diapositiva individual |
| Falta de comprobación reproducible | ValidarManualPractico.py contrasta75hashes, listados, fragmentos, imágenes y ambos formatos | La revisión visual no equivale a ejecutar todos los casos funcionales |

## Ejecuciones comprobadas
- Seis compilaciones completadas; WPF tras añadir System.IO.
- BanQuito:20 pruebas; comercializadora:19 pruebas; cero fallos y cero omisiones.
- Factura de efectivo:precio450, descuento189, total261.
- Factura a crédito:capital450, tres cuotas, saldo final0.
- Catálogo consultado desde consola y ventana WPF.
- El fallo de restauración inicial de una ruta D: se resolvió usando caché temporal local. Las credenciales de prueba no forman parte de la documentación.

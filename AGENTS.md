# Reglas del proyecto GR09

- Implementar únicamente .NET REST. BanQuito y comercializadora son API separadas; comunicación HTTP sin compartir bases ni ensamblados de dominio.
- Docker ejecuta solo SQL Server. Las API, consola, WPF, MVC y MAUI se ejecutan en el host. No agregar inventario.
- Preparación: copiar `.env.example` a `.env`, configurar contraseña y ejecutar `./PrepararEntorno.ps1 -IniciarApis`. Nunca publicar `.env` ni borrar volúmenes o bases sin instrucción explícita.
- La rúbrica fuente es `ExamenComplexivoPractivo_CELULARES.docx`. Exige cuatro clientes, efectivo con 42% de descuento, crédito de 3–18 cuotas y tasa anual 16,5%. Se conserva 35% para máximo; documentar contradicción con fórmula al 30%.
- Usar `examples` como plantillas de ERS, ECUD, manual y presentación. Referencia de aprendizaje: `../../U1/TG.1`, scripts GenerarDocumentacionEurekaBank.ps1, GenerarDocumentacionTecnicaEurekaBankGR09.ps1 y GenerarPresentacionesEurekaBankGR09.py. No depender de esa ruta al ejecutar la entrega.
- Generar documentos desde copias de las plantillas, preservar estilos y tablas; reemplazar texto heredado y verificar visualmente todas las páginas antes de sustituir resultados. No afirmar que se regeneraron documentos sin ejecutar y revisar el proceso.
- Diagramas: PowerDesigner COM instalado en Windows, ejecutar `cscript //nologo "01. UML/GenerarDiagramasCelulares.vbs" <raiz> <raiz>` y el generador de casos específicos según sus argumentos. Revisar destinos antes de ejecutar; conservar modelos existentes completos. Fuente editable y PNG legible son obligatorios. Revisar casos bancarios, actividad, secuencia, clases y arquitectura.
- MER: ejecutar `02. MER/GenerarModelosCelulares.ps1` indicando ambas raíces locales. Comparar columnas, claves y relaciones con scripts SQL; no sobrescribir modelos manuales sin respaldo.
- Cierre: pruebas de ambas API, compilación de cuatro clientes y evidencia por interfaz de catálogo, efectivo, crédito nuevo y amortización. Usar QA para ventas; nunca reiniciar datos principales para pruebas. Distinguir probado, implementado y pendiente.

## Generación documental reproducible

Instalar `scripts/requirements-documentacion.txt` en un entorno virtual. Ejecutar, desde la raíz, `python scripts/ValidarDocumentacion.py`, `python scripts/GenerarDocumentacion.py` y `python scripts/RenderizarDocumentacion.py --soffice <ruta-soffice>`. `documentation-profile.json` define fuentes, plantillas y carpetas de borradores/renderizados; `manifest.json` registra hashes. Las fuentes `*_verificado.md` conservan requisitos y evidencias actuales; no borrar las importadas como parte de una regeneración.

Revisar PDFs/PNG antes de sustituir entregables; los borradores actuales no sustituyen automáticamente los Word/PPT previos. PowerDesigner 16.1 está instalado, pero la licencia de evaluación está vencida: no afirmar que los VBS terminaron ni modificar la licencia. Conservar modelos y documentar este bloqueo en el informe de rúbrica.

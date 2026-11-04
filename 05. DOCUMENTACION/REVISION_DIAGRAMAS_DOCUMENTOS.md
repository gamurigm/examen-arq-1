# Diagramas y documentación: revisión actual

Fecha: 4 de noviembre de 2026.

## Figuras entregadas

- Casos de uso UML bancarios: comercializadora como actor, elegibilidad, máximo, otorgamiento y consulta; relaciones include hacia validaciones y registro de amortización.
- Arquitectura: cuatro clientes, dos API REST .NET en host y solo SQL Server en Docker; dos bases y conexiones separadas.
- Modelo físico de tienda: 21 atributos entre CELULAR y FACTURA, imágenes incluidas, referencia remota bancaria y relación 1 a 0..N. Sin inventario.

Cada figura tiene SVG editable y PNG junto al archivo fuente. Se generaron realmente con GenerarFigurasEntrega.vbs y se revisaron las tres exportaciones. EVIDENCIA_DIAGRAMAS.json registra huellas de los archivos y comparación con los atributos y FK de SQL Docker. Se verificaron nombres de atributos y relación; los tipos y restricciones se contrastaron también con 01_CrearBases.sql durante la revisión.

No se regeneraron modelos PowerDesigner: su licencia está vencida. El generador VBS alternativo no modifica licencia ni archivos nativos existentes. SVG es el formato editable de las figuras nuevas.

## Word integrado

Los borradores ERS, ECUD y manual contienen las tres figuras y conservan las portadas gráficas de las plantillas. Se actualizaron títulos, autores desde documentation-profile.json, tutor y fecha. Se eliminaron páginas vacías introducidas por los saltos heredados y no quedan los marcadores XXXX/YYYY/ZZZZ ni títulos Java/SOAP/EurekaBank del ejemplo.

PDF revisados: ERS 6 páginas, ECUD 12 páginas, manual 7 páginas. Se revisaron hojas de contacto y portadas; son versiones de revisión, no sustituyen todavía el paquete final completo.

Reproducción:

```powershell
cscript //nologo "01. UML/GenerarFigurasEntrega.vbs" (Get-Location).Path
python scripts/VerificarDiagramas.py
python scripts/GenerarDocumentacion.py --artifacts ers ecud manual
python scripts/RenderizarDocumentacion.py
```

Dependencias Python: scripts/requirements-documentacion.txt. Carpetas de borrador y renderizado configuradas en documentation-profile.json; en este equipo bajo D:/tools/CelularGR09-documentacion. manifest.json conserva hashes y distingue los tres artefactos generados de la presentación anterior.

## Pendiente concreto

La presentación fuente tiene 15 secciones, pero la plantilla tiene 83 diapositivas. El generador rechaza esa discrepancia para conservar la estructura existente. Falta completar la correspondencia, integrar sus figuras, renderizar y revisar todas las diapositivas. Después se podrá cerrar trazabilidad y publicar el paquete Word/PPT final con respaldo de las versiones anteriores.

# Revisión de diagramas y documentos

Fecha: 4 de noviembre de 2026.

## Figuras

- Casos de uso bancarios: cliente comercializadora, elegibilidad, máximo, crédito y amortización.
- Arquitectura: cuatro clientes, dos API REST .NET en el host, SQL Server en Docker y bases separadas.
- MER físico: tablas CELULAR y FACTURA, imágenes, referencia bancaria remota y relación 1:N; sin inventario.

Las tres figuras se generaron con `01. UML/GenerarFigurasEntrega.vbs`. Cada una tiene fuente SVG editable y PNG. `05. DOCUMENTACION/EVIDENCIA_DIAGRAMAS.json` registra hashes y comparación de columnas y claves foráneas con SQL Server.

No se regeneraron modelos nativos de PowerDesigner porque la licencia de evaluación venció. Se conservaron los modelos existentes; las figuras actuales no dependen de esa licencia.

## Entregables revisados

| Artefacto | Render | Revisión |
| --- | ---: | --- |
| ERS | 6 páginas | Portada, requisitos, tablas y tres figuras; todas las páginas revisadas. |
| ECUD | 12 páginas | Portada, ocho casos, reglas comunes y tres figuras; todas las páginas revisadas. |
| Manual técnico | 34 páginas | Índices actualizados, tablas, diagramas, capturas QA/clientes, resultados, límites y bibliografía; las 34 páginas revisadas. |
| Presentación | 69 diapositivas | 81 secciones de la fuente canónica; todas las diapositivas revisadas. |

El manual DOCX y la presentación usan `05. DOCUMENTACION/fuentes/manual_verificado.md`, SHA-256 `6cf1b168c2bc5d1b28942a85fbc56bcd7305a14ec872deac319a3cf0c2629070`. La generación conserva cada sección canónica una vez; las diapositivas agrupan pruebas breves y separan capturas cuando hace falta espacio. La cantidad de diapositivas sigue el contenido, no las 83 diapositivas de la plantilla.

Las cuatro versiones oficiales se reemplazaron desde borradores revisados. Respaldo previo: `D:\tools\CelularGR09-documentacion\respaldo\20261104-181500`. `REVISION_RENDERIZADOS.json` contiene hashes, conteos y estado de revisión.

## Reproducción

```powershell
python scripts/ValidarDocumentacion.py
python scripts/GenerarDocumentacion.py
python scripts/RenderizarDocumentacion.py --soffice <ruta-soffice>
```

Las API y los cuatro clientes no se compilaron ni se probaron en esta revisión documental. Las figuras nativas de PowerDesigner tampoco se regeneraron por la licencia vencida.

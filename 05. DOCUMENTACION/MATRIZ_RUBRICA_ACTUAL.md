# Matriz actual de rúbrica y evidencia

Fuente: ExamenComplexivoPractivo_CELULARES.docx. Los puntos indican máximos de rúbrica; no son una nota asignada. La fila de facturación se interpreta 2 + 3 para sumar el total declarado de 20.

| Ítem | Máximo | Evidencia actual |
|---|---:|---|
| Casos de uso del módulo bancario | 2 | SVG editable y PNG GR09_BanQuito_CasosUso; fuente VBS ejecutada y figura revisada |
| Descripción de verificar sujeto | 1 | CU02 en ecud_verificado.md y Word de revisión; reglas y alternativas explícitas |
| Core 5 clientes, 5 cuentas, 50 movimientos y entidades de crédito | 2 | Inicialización Docker y datos QA verificados; CREDITO y AMORTIZACION en esquema dbo del Core |
| MER comercializadora | 1 | GR09_Celulares_SQL_Actual SVG/PNG, 21 atributos y relación contrastados con SQL; modelos nativos conservados |
| Elegibilidad por cédula | 1,5 | EVIDENCIA_API_QA.json: existente, inexistente, edad, depósito y crédito activo |
| Máximo por código de cliente | 1,5 | Cliente 3: 2142,00; 35% documentado frente a contradicción del 30% impreso |
| Otorgamiento y amortización | 2 | Monto igual al máximo aprobado; superior rechazado; 3 y 18 cuotas, interés y saldo cero; persistencia y reintentos |
| Mantenimiento catálogo | 1 | Recorridos reales en consola, MVC/Chrome, WPF y Android sobre QA |
| Facturación efectivo y crédito en cuatro clientes | 5 | EVIDENCIA_CONSOLA.txt, EVIDENCIA_CLIENTES_QA.json, EVIDENCIA_WEB_NAVEGADOR.json, EVIDENCIA_WPF_QA.json, EVIDENCIA_ANDROID_QA.json |
| Servicio de amortización y consumo en cuatro clientes | 1 | Servicio bancario y pasarela verificados; recorridos de consulta en los cuatro clientes |
| Consulta amortización desde comercializadora | 1 | Tabla y saldo cero comprobados por HTTP y clientes; capturas Android y web |
| Arquitectura completa | 1 | GR09_Arquitectura_Docker SVG/PNG: cuatro clientes, dos API, Docker solo SQL y dos bases |

Las funciones cuentan con evidencia QA; el tribunal debe observar y defender cada ítem. La validación de una copia limpia en otra máquina y la presentación de defensa no se certifican por estas pruebas. El cierre documental del paquete sigue pendiente según REVISION_DIAGRAMAS_DOCUMENTOS.md. Se conservan los informes anteriores como historial; sus pendientes pueden estar superados por estas verificaciones más recientes.

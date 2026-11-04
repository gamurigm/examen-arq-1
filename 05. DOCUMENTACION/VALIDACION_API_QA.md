# Paso 2: flujos REST sobre bases QA

Verificación ejecutada el 4 de noviembre de 2026: **53 comprobaciones aprobadas**.

## Reproducción

Con SQL Server Docker inicializado y .NET/Python disponibles en PATH:

```powershell
python scripts/VerificarApiQA.py
```

El script compila ambas API, comprueba disponibilidad de puertos 19201/19202, crea dos bases QA con nombres únicos y ejecuta las API temporales contra ellas. Termina únicamente los procesos que inició. No elimina las bases QA ni modifica las bases principales. Requiere `.env` configurado; no guarda credenciales en la evidencia.

## Resultados

- Catálogo: consulta inicial, alta, edición y desactivación.
- Elegibilidad: inexistente, masculino menor de 25, ausencia de depósito reciente y cliente elegible.
- Monto máximo: cliente 3 obtiene 2142,00 con la regla del 35%.
- Rechazo por plazo 2/19 tanto en banco como en facturación; rechazo por monto superior y edad.
- Efectivo: precio 450, descuento 189, total 261 y factura aprobada.
- Crédito desde comercializadora: 450, sin descuento, aprobado con referencia bancaria.
- Repetir efectivo o crédito conserva el identificador; cambiar datos de una operación existente produce 409.
- Crédito activo: elegibilidad negativa y nuevo otorgamiento rechazado.
- Monto exactamente igual al máximo: aprobado a 18 meses.
- Amortizaciones de 3 y 18 meses: fechas mensuales, interés inicial al 16,5% anual/12, balance de cada cuota, capital completo y saldo final cero. Cuota fija salvo ajuste final de redondeo.
- Consulta bancaria de amortización coincide con la pasarela de comercializadora.
- Consulta de factura y búsqueda por cédula correctas.

Detalle verificable: `EVIDENCIA_API_QA.json`, con nombres de bases, casos aprobados y conteos SQL. Última ejecución: dos créditos bancarios y dos facturas de tienda.

## Pendiente

Esto acredita flujos HTTP, no interacción con consola, WPF, web o Android. Continúan pendientes la demostración en cada interfaz y la generación/revisión documental y de diagramas.

# Comercializadora de celulares y BanQuito
.NET REST · Grupo 09 · NRC 36884
Dos API independientes, cuatro clientes y SQL Server en Docker.
## Problema y alcance
Catálogo sin inventario y facturación de un celular por compra.
Pago en efectivo o crédito directo autorizado por BanQuito.
No se implementa la programación del Core bancario completo.
## Arquitectura
Consola, WPF, web MVC y Android MAUI consumen la API comercializadora.
Comercializadora y BanQuito se comunican por REST/JSON.
Dos bases independientes en SQL Server Docker; las aplicaciones corren en host.
## Modelo de datos
Tienda: CELULAR y FACTURA; fotos opcionales y referencia remota del crédito.
Banco: CLIENTE, CUENTA, MOVIMIENTO, CREDITO y AMORTIZACION.
Semillas verificadas: 5 clientes, 5 cuentas, 50 movimientos.
## Elegibilidad bancaria
Ser cliente, tener depósito en último mes y no tener crédito activo.
Hombres con 25 años cumplidos.
La consulta no garantiza aprobación posterior: el otorgamiento revalida.
## Monto máximo
Promedios de depósitos y retiros de los últimos tres meses.
Máximo = max(0, diferencia × 35% × 6).
Enunciado contradictorio: texto 35%, fórmula 30%; decisión explícita al 35%.
## Otorgamiento y amortización
Código de cliente, precio del teléfono y número de cuotas.
Plazo 3–18 meses; interés anual 16,5%, pagos mensuales.
Transacción bancaria y referencia idempotente; última cuota ajusta centavos.
## Efectivo y crédito
Efectivo: precio 450, descuento 189, total 261.
Crédito: factura aprobada solo después de autorización bancaria.
No duplicar operaciones al reintentar; resolver estados pendientes.
## Cuatro clientes comprobados
Consola: entradas del menú real y transcripción.
Web: formularios MVC y Chrome con JavaScript; decimales corregidos.
WPF: eventos de controles reales; Android: emulador y capturas ADB.
## Evidencia de pruebas
39 pruebas unitarias y 53 comprobaciones HTTP QA.
14 comprobaciones consola/MVC; 10 WPF; 9 recorridos Android.
13 comprobaciones posteriores de navegador; consultar registros para alcance.
## Entrega y diagramas
Plantillas locales, fuentes revisadas y generación por scripts.
Conservar modelos y exportaciones; comparar MER con SQL.
PowerDesigner: licencia de evaluación vencida; regeneración editable bloqueada.
## Defensa y pendientes
Demostrar servicios bancarios y ventas en los cuatro clientes sobre QA.
Explicar máximo 35%/30% y ajuste de la última cuota.
Cerrar diagramas bancarios y revisión visual documental antes de afirmar cumplimiento integral.

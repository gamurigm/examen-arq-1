# Paso 1: entorno Docker y API

Verificado: 4 de noviembre de 2026.

Comando: `./PrepararEntorno.ps1 -IniciarApis`.

- SQL Server Docker saludable; inicialización repetida sin duplicar semillas: 5 clientes, 5 cuentas, 50 movimientos.
- API BanQuito `/api/salud`: HTTP 200.
- API comercializadora `/api/salud`: HTTP 200.
- Catálogo `/api/celulares`: HTTP 200, tres celulares activos.
- Elegibilidad de 0304050607: HTTP 200, sujeto de crédito, cliente 3, máximo 2142,00.
- Máximo del cliente 3: HTTP 200, 2142,00.
- Pruebas comercializadora: 19/19 aprobadas.
- Pruebas bancarias: 20/20 aprobadas.

Ambas API iniciadas por el script con conexiones al puerto Docker 19433. No se emitieron ventas ni créditos para esta comprobación. Se conservaron las bases SQLEXPRESS.

Pendiente: verificación funcional en bases QA de ventas, amortización y cuatro interfaces; generación documental y revisión visual de diagramas. Este paso no acredita la rúbrica completa.

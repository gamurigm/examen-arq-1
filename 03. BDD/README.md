# Base de datos de la tienda

`01_CrearBases.sql`, `03_MigrarImagenes.sql` y `02_DatosPrueba.sql`, ejecutados en ese orden, crean o actualizan y siembran `ComercializadoraCelulares`. La migración agrega las columnas de imagen que necesita el catálogo actual, también sobre bases existentes.

`BanQuito/BanQuito_01_CrearBase.sql` y `BanQuito/BanQuito_02_DatosPrueba.sql` crean y siembran la base independiente `BanQuitoCore`: 5 clientes, 5 cuentas y 50 movimientos, además de las tablas de crédito y amortización. Siga el manual técnico para ejecutar los inicializadores incluidos en `04. SERVIDOR` sobre SQLEXPRESS.

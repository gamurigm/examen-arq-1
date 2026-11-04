# Comercializadora de celulares · GR09

Sistema .NET 10 para catálogo y facturación de celulares. SQL Server 2025 Express almacena celulares, fotos y facturas. La tienda no maneja inventario.

## Límites

- La comercializadora expone REST en `http://127.0.0.1:19102/`.
- BanQuito está incluido en `04. SERVIDOR/BanQuito.Api`; es una aplicación independiente que atiende elegibilidad y crédito por HTTP en `http://127.0.0.1:19101/`.
- La web MVC usa `http://127.0.0.1:19103/`.
- La tienda guarda la referencia remota del crédito; no comparte base ni ensamblados con BanQuito.

## Ejecutar

1. Instale .NET 10 y SQL Server 2025 Express con instancia `SQLEXPRESS`.
2. Aplique los scripts de creación y datos de `03. BDD/BanQuito`, y los scripts `03. BDD/01_CrearBases.sql`, `03_MigrarImagenes.sql` y `02_DatosPrueba.sql`, en ese orden. La migración también se puede ejecutar en una instalación nueva.
3. Inicie `04. SERVIDOR/BanQuito.Api/BanQuito.Api.csproj` si probará compras a crédito.
4. Inicie `04. SERVIDOR/Comercializadora.Api/Comercializadora.Api.csproj`.
5. Inicie uno o más clientes: consola, WPF, MAUI Android o web MVC.

`05. DOCUMENTACION/ManualTecnico.md` explica configuración y comandos. Android compila sin dispositivo con `dotnet build`; instalar requiere un emulador o dispositivo conectado.

## Funciones

- Catálogo con alta, edición, desactivación y fotos opcionales.
- Fotos JPEG, PNG o WebP de hasta 5 MiB; se pueden cargar, reemplazar y quitar desde los cuatro clientes.
- Venta en efectivo con 42% de descuento.
- Venta a crédito aprobada por BanQuito, consulta de facturas y amortización.
- Tema claro y oscuro en las interfaces compatibles.

## Decisiones técnicas

La web usa ASP.NET Core MVC. El servidor separa controladores, servicios y reglas de dominio; usa inyección de dependencias. SQL Server se accede con ADO.NET y comandos parametrizados; no usa Entity Framework Core. El enunciado permite elegir framework y motor de base de datos.

## Actualización verificada · 4 de noviembre de 2026

- BanQuito incluido con API, dominio, contratos, inicializador, scripts SQL y 20 pruebas aprobadas; las 19 pruebas de tienda también pasan.
- Migración de imágenes aplicada a la base principal sin alterar los 3 celulares ni las 2 facturas existentes. La migración se ejecutó dos veces para comprobar idempotencia.
- Catálogo, elegibilidad y amortización responden HTTP 200. La web muestra el catálogo y la amortización usando ambos servicios compilados desde este repositorio.
- Manual actualizado para inicializar y ejecutar ambas aplicaciones sin depender del proyecto vecino. Esta comprobación no repitió ventas nuevas en las cuatro interfaces.

## Evidencia anterior · 27 de octubre de 2026

- 19/19 pruebas automatizadas aprobadas.
- API, consola, WPF, web MVC, MAUI Android y herramienta de administración compilaron sin errores ni advertencias.
- Flujo de imagen comprobado en una base QA aislada: carga y reemplazo `204`, descarga con bytes esperados, eliminación `204` y consulta posterior `404`.
- No se comprobó instalación ni ejecución en emulador o teléfono en esta revisión.

Consulta `05. DOCUMENTACION/AVANCE.md` y `05. DOCUMENTACION/VERIFICACION_EXAMEN.md` para alcance y evidencias.

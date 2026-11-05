# Manual técnico: comercializadora de celulares y BanQuito

## Introducción y objetivos
El sistema permite administrar un catálogo de celulares, emitir facturas y solicitar financiamiento a BanQuito mediante servicios HTTP. Ofrece cuatro aplicaciones cliente: consola, escritorio WPF, web ASP.NET Core MVC y móvil .NET MAUI para Android. Este manual explica la preparación del entorno, la organización del código, la persistencia, los contratos de comunicación y los procedimientos necesarios para ejecutar y mantener la solución.

El objetivo general es proporcionar una guía técnica reproducible para instalar, configurar y comprender la comercializadora y el servicio bancario. Los objetivos específicos son describir las responsabilidades de cada componente, documentar las estructuras de datos y reglas de negocio, detallar la ejecución de los cuatro clientes y establecer criterios para comprobar su funcionamiento.

El documento está dirigido a desarrolladores, responsables de instalación y estudiantes que necesiten continuar el proyecto. Los comandos se ejecutan desde la raíz de `examen-arq-1`, en PowerShell, salvo que se indique otra ubicación. Grupo 09 · NRC 36884. Autores: Gabriel Omar Murillo Medina y Julio Enrique Viche Castillo. Tutor: Ing. Eduardo Mauricio Campaña Ortega.

## Alcance y reglas del sistema
La comercializadora registra nombre, precio, estado e imagen opcional de cada celular. Cada factura corresponde a un comprador y un celular. La desactivación retira el producto del catálogo de venta y conserva sus referencias históricas. El sistema no administra cantidades, bodegas ni movimientos de inventario.

Existen dos modalidades de pago. En efectivo, el servidor aplica un descuento del 42 % sobre el precio de lista. En crédito directo, BanQuito evalúa al cliente y financia el precio de lista en un plazo de 3 a 18 meses, con una tasa anual del 16,5 %. La tabla de amortización corresponde al crédito y se consulta desde la factura.

BanQuito mantiene clientes, cuentas, movimientos, créditos y cuotas en su propia base de datos. La implementación cubre la evaluación y el otorgamiento requeridos por el ejercicio; no incorpora un sistema bancario completo, pagos posteriores de cuotas, transferencias ni autenticación de usuarios. Los nombres `APROBADA`, `PENDIENTE` y `RECHAZADA` que aparecen en los contratos representan estados de una factura.

## Fundamentos de arquitectura y persistencia
REST describe restricciones para organizar interacciones entre componentes distribuidos a través de recursos e interfaces uniformes (Fielding, 2000; Fielding y Taylor, 2002). En este proyecto, los recursos comerciales se identifican mediante rutas HTTP, los intercambios de datos utilizan JSON y los clientes delegan la lógica de negocio a las API. La referencia teórica orienta el diseño; el comportamiento concreto se define en los controladores y servicios del repositorio.

La separación entre presentación, lógica de aplicación y acceso a datos facilita identificar responsabilidades y modificar una capa sin trasladar reglas a las interfaces (Fowler, 2002). Los controladores HTTP reciben solicitudes; los servicios coordinan consultas, transacciones y llamadas remotas; las clases de dominio calculan descuentos, elegibilidad y amortización.

El modelo relacional organiza los datos en relaciones y permite expresar restricciones de integridad (Codd, 1970). En la implementación, las claves primarias, foráneas, restricciones e índices de SQL Server protegen las relaciones entre entidades. Las transacciones delimitan cambios que deben conservar coherencia dentro de cada base; el aislamiento y la concurrencia son aspectos centrales de los sistemas de bases de datos (Silberschatz et al., 2019).

## Estructura del proyecto
La distribución de carpetas separa análisis, modelos de datos, código y documentación. Abrir la carpeta completa permite conservar las referencias relativas de los proyectos. El repositorio no incluye un archivo de solución `.sln`; Visual Studio puede abrir cada `.csproj` y cargar sus referencias.

| Carpeta | Contenido y finalidad |
|---|---|
| `01. UML` | ERS, especificaciones de casos de uso y modelos UML de PowerDesigner. |
| `02. MER` | Modelos de datos y exportaciones del esquema relacional. |
| `03. BDD` | Creación de bases, tablas, migración de imágenes y datos iniciales. |
| `04. SERVIDOR` | API de tienda, API bancaria, dominios, contratos, inicializadores y pruebas. |
| `04. COMPARTIDO` | Cliente HTTP y controlador común de las cuatro interfaces. |
| `04. CLICON` | Aplicación de consola. |
| `04. CLIESC` | Aplicación WPF para Windows. |
| `04. CLIWEB` | Aplicación ASP.NET Core MVC. |
| `04. CLIMOV` | Aplicación .NET MAUI para Android. |
| `05. DOCUMENTACION` | Manual, presentación, fuentes y registros de pruebas. |
| `scripts` | Herramientas de comprobación y generación documental. |

## Arquitectura y comunicación
Los cuatro clientes consumen exclusivamente Comercializadora.Api. Esta API resuelve catálogo y facturación en `ComercializadoraCelulares`; para las operaciones de crédito llama por HTTP a BanQuito.Api. El banco consulta y modifica `BanQuitoCore`. Las API son procesos independientes y no comparten ensamblados de dominio ni acceden directamente a la base de la otra aplicación.

En el entorno local, Docker ejecuta únicamente SQL Server. Las dos API y los clientes se ejecutan en Windows. Ambas bases residen en el mismo motor, pero conservan esquemas y responsabilidades independientes. La referencia de crédito guardada en una factura es un identificador remoto; no es una clave foránea entre bases.

| Componente | Dirección local | Consumidor |
|---|---|---|
| BanQuito.Api | `http://127.0.0.1:19101/` | API comercializadora. |
| Comercializadora.Api | `http://127.0.0.1:19102/` | Consola, WPF, web MVC y móvil. |
| Web MVC | `http://127.0.0.1:19103/` | Navegador. |
| SQL Server | `127.0.0.1,19433` | Las API en el host. |
| Tienda desde Android Emulator | `http://10.0.2.2:19102/` | Aplicación MAUI en el emulador. |

La exportación siguiente representa la separación entre clientes, servicios y persistencia. Para interpretar su despliegue, considerar que el contenedor aloja el motor y los demás procesos se ejecutan en el host.

![PowerDesigner: arquitectura cliente-servidor](../../01. UML/03. DIAGRAMAS UML/05_ARQUITECTURA/GR09_Arquitectura_Arquitectura cliente-servidor.png)

## Instalación y configuración de herramientas
### SDK .NET y entorno de desarrollo
Instalar el SDK .NET compatible con `global.json`, que solicita la versión `10.0.401` con avance a parches de la misma banda. Comprobar que `dotnet` está disponible en la terminal. Un runtime por sí solo no permite compilar los proyectos.

```powershell
dotnet --info
dotnet --list-sdks
```

Para trabajar desde Visual Studio, disponer de las cargas de ASP.NET y desarrollo web, escritorio .NET y .NET MAUI. Abrir Archivo > Abrir > Proyecto o solución y seleccionar el `.csproj` correspondiente. La compilación por terminal permite trabajar sin depender de las pantallas del IDE.

### Docker Desktop y SQL Server
Instalar Docker Desktop, iniciar su motor y seleccionar contenedores Linux. El archivo `compose.yaml` utiliza SQL Server 2022 Developer. No se necesita instalar una instancia SQL Server nativa para el procedimiento de este manual. SQL Server Management Studio es una herramienta opcional para consultar el motor; no sustituye al contenedor.

```powershell
docker version
docker compose version
```

### Android y herramientas auxiliares
Para compilar y ejecutar el móvil, instalar la carga MAUI y las herramientas Android, incluidas las herramientas de plataforma y un emulador. El proyecto declara `net10.0-android`, Microsoft.Maui.Controls `10.0.110` y versión mínima de Android API 23. Revisar las cargas instaladas con `dotnet workload list` y, si falta la correspondiente, instalarla con `dotnet workload install maui`.

Las herramientas documentales se instalan con `python -m pip install -r scripts/requirements-documentacion.txt` dentro de un entorno virtual. Los recorridos de navegador requieren además Playwright y su navegador instalado. Estas dependencias son auxiliares y no son requisitos de ejecución de las API.

## Configuración local del repositorio
### Rutas de compilación y dependencias
`Directory.Build.props` configura C# 14, nulabilidad y rutas de salida. En este repositorio, las salidas predeterminadas se dirigen a `D:\tools\CelularGR09` y los paquetes a `D:\NuGet\packages`. Si el equipo no dispone de esa unidad, pasar rutas locales a MSBuild. El siguiente ejemplo prepara argumentos reutilizables en la sesión de PowerShell:

```powershell
$buildArgs = @(
  "-p:CelularBuildRoot=$env:LOCALAPPDATA\CelularesGR09\build",
  "-p:CelularPackagesRoot=$env:LOCALAPPDATA\CelularesGR09\packages"
)
```

Usar esos mismos argumentos en las compilaciones, pruebas y ejecuciones del equipo. `NuGet.Config` contiene la ruta de caché original; `CelularPackagesRoot` se transmite como `RestorePackagesPath` desde `Directory.Build.props`. Las referencias a proyectos se resuelven dentro del repositorio, por lo que debe conservarse su estructura.

### Archivo de entorno
Crear `.env` a partir de `.env.example` solo si todavía no existe. Abrirlo en un editor y asignar localmente `MSSQL_SA_PASSWORD`. Mantener una contraseña válida para SQL Server. `.env` no forma parte de los entregables ni debe mostrarse en capturas.

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

### Orden de arranque
Iniciar primero SQL Server y sus bases; después BanQuito.Api, Comercializadora.Api y finalmente el cliente seleccionado. Ejecutar `./PrepararEntorno.ps1 -IniciarApis` automatiza el contenedor, los cinco scripts SQL y el arranque de las API cuando `dotnet` y las rutas predeterminadas están disponibles. Para controlar los procesos en terminales separadas o usar rutas de compilación distintas, seguir el procedimiento manual de los capítulos siguientes.

## Instalación y configuración de SQL Server
El servicio `sqlserver` publica el puerto interno `1433` en `127.0.0.1:19433`. El volumen `celulares_sql` conserva las bases entre reinicios. La edición Developer está destinada al entorno académico de desarrollo. El archivo de composición incorpora una comprobación de salud mediante `sqlcmd`.

| Parámetro | Configuración |
|---|---|
| Imagen del motor | `mcr.microsoft.com/mssql/server:2022-latest` |
| Servicio de Compose | `sqlserver` |
| Puerto desde Windows | `127.0.0.1,19433` |
| Puerto del motor en el contenedor | `1433` |
| Volumen persistente | `celulares_sql:/var/opt/mssql` |
| Contraseña | Variable local `MSSQL_SA_PASSWORD` |
| Bases de aplicación | `ComercializadoraCelulares` y `BanQuitoCore` |

### Preparar e inicializar
Desde la raíz ejecutar el script sin modificadores para crear o completar las bases y cargar los datos semilla:

```powershell
./PrepararEntorno.ps1
docker compose ps
docker compose logs --tail 80 sqlserver
```

El script ejecuta `docker compose up -d --wait` y detiene el proceso si el contenedor no queda disponible o un script SQL produce un error. Si el puerto `19433` está ocupado, revisar su uso antes de iniciar. El cambio de puerto exige ajustar tanto `compose.yaml` como las cadenas de conexión de las dos API.

### Consultar con SQL Server Management Studio
En SSMS seleccionar Motor de base de datos e introducir `127.0.0.1,19433`. Para esta configuración local, usar autenticación SQL Server con usuario `sa` y la contraseña definida en `.env`. La conexión del proyecto cifra el transporte y confía en el certificado del contenedor mediante `TrustServerCertificate=True`. Revisar en el Explorador de objetos las dos bases y las tablas de `dbo`.

Para detener el entorno conservando su información, utilizar `docker compose stop`. Para reanudarlo, utilizar `docker compose up -d --wait`. No eliminar el volumen persistente como procedimiento de reinicio.

## Creación y carga de las bases de datos
Los scripts contienen instrucciones condicionales para crear objetos que falten y evitar duplicar los datos semilla identificados por sus claves. Ejecutarlos en el orden siguiente. La migración de imágenes también forma parte de una instalación nueva y debe aplicarse sobre una base existente antes de usar fotografías.

| Orden | Script | Responsabilidad |
|---|---|---|
| 1 | `03. BDD/01_CrearBases.sql` | Crear ComercializadoraCelulares, CELULAR y FACTURA. |
| 2 | `03. BDD/03_MigrarImagenes.sql` | Incorporar columnas opcionales de imagen si faltan. |
| 3 | `03. BDD/02_DatosPrueba.sql` | Insertar el catálogo inicial de tres celulares. |
| 4 | `03. BDD/BanQuito/BanQuito_01_CrearBase.sql` | Crear BanQuitoCore, tablas, claves e índices bancarios. |
| 5 | `03. BDD/BanQuito/BanQuito_02_DatosPrueba.sql` | Insertar cinco clientes, cinco cuentas y cincuenta movimientos. |

La fecha de los movimientos semilla se calcula con respecto al día de ejecución. Como las inserciones no reemplazan movimientos existentes, ejecutar nuevamente la carga días después no actualiza sus fechas. Esto afecta los criterios de último mes y últimos tres meses; para repetir escenarios, utilizar una base de pruebas nueva.

La consulta siguiente permite revisar las cantidades existentes desde SSMS. Los valores iniciales solo corresponden a una instalación limpia; una base utilizada puede contener más registros.

```sql
SELECT COUNT(*) AS Celulares
FROM ComercializadoraCelulares.dbo.CELULAR;
SELECT COUNT(*) AS Clientes FROM BanQuitoCore.dbo.CLIENTE;
SELECT COUNT(*) AS Cuentas FROM BanQuitoCore.dbo.CUENTA;
SELECT COUNT(*) AS Movimientos FROM BanQuitoCore.dbo.MOVIMIENTO;
```

Los cinco scripts completos se incluyen en el anexo. Su ejecución automatizada utiliza las herramientas SQL del contenedor; los inicializadores de administración del repositorio conservan configuraciones de instalaciones anteriores y no son necesarios para el flujo Docker descrito aquí.

## Modelo de datos de la comercializadora
`CELULAR` contiene los productos del catálogo. `FACTURA` referencia al celular y conserva una copia del nombre y precio utilizados en la operación. Esta copia permite consultar el contenido de la venta aunque el catálogo cambie después. Las restricciones SQL y las validaciones de dominio controlan los valores comerciales.

| Tabla | Identificación y datos | Reglas principales |
|---|---|---|
| CELULAR | ID_CELULAR, NOMBRE, PRECIO, ACTIVO, IMAGEN y tipo MIME. | Identificador identity; precio positivo; foto opcional. |
| FACTURA | ID_FACTURA, ID_OPERACION, FECHA, comprador, producto, pago, precio, descuento y total. | ID_OPERACION único; referencia al celular; valores monetarios persistidos. |
| FACTURA: crédito | COD_CLIENTE_BANCO, COD_CREDITO, NUMERO_CUOTAS y ESTADO. | Referencias remotas; cuotas entre 3 y 18 para crédito; control del estado de la operación. |

Los importes se almacenan como valores decimales; el servidor utiliza `decimal` y parámetros SQL con precisión y escala explícitas para los montos. La API valida fotografías JPEG, PNG o WebP de hasta 5 MiB y almacena los bytes y el tipo MIME en la misma base. No se utiliza un directorio público para guardar archivos subidos.

![PowerDesigner: modelo físico comercializadora](../../02. MER/03. FISICO/GR09_Celulares_Physical_DotNet_SQLServer.png)

## Modelo de datos de BanQuito
BanQuito mantiene la relación de clientes con sus cuentas y movimientos. Un crédito pertenece a un cliente y contiene su tabla de amortización. Las relaciones bancarias se resuelven dentro de `BanQuitoCore`; la API comercial no consulta estas tablas.

| Tabla | Claves y contenido |
|---|---|
| CLIENTE | COD_CLIENTE como clave; cédula única, nombre, género y nacimiento. |
| CUENTA | NUM_CUENTA como clave; referencia a CLIENTE y saldo. |
| MOVIMIENTO | COD_MOVIMIENTO como clave; referencia a CUENTA, tipo DEP/RET, valor y fecha. |
| CREDITO | COD_CREDITO como clave; referencia a CLIENTE, referencia de venta, monto, plazo, tasa, fecha y estado. |
| AMORTIZACION | Clave compuesta COD_CREDITO y NUMERO_CUOTA; fecha, cuota, interés, capital y saldo. |

El índice único filtrado de crédito por cliente con estado `ACTIVO` impide registrar dos créditos activos simultáneos. La referencia de venta también es única para identificar reintentos. El índice de movimientos por cuenta y fecha apoya las consultas de períodos. Una fila de amortización con número cero representa el saldo inicial y no una cuota cobrada.

## Aplicación servidor: organización y configuración
### Proyectos y responsabilidades
`Comercializadora.Api` publica los controladores de celulares, crédito y facturas. `ServicioCatalogo` realiza las operaciones del catálogo; `ServicioFacturas` coordina la venta; `ServicioBanQuito` encapsula las llamadas bancarias. `Comercializadora.Dominio` contiene las reglas de facturación e imágenes y `Celulares.Contratos` define solicitudes y respuestas comerciales.

`BanQuito.Api` publica la evaluación y el otorgamiento. `ServicioCredito` coordina la persistencia y `BanQuito.Dominio/ReglasCredito.cs` implementa la elegibilidad, el máximo y la amortización. Sus contratos pertenecen a `BanQuito.Contratos`. La comunicación entre API utiliza HTTP, sin referencias de proyecto hacia el dominio contrario.

### Registro de servicios y acceso a datos
En `Program.cs` se registran controladores y servicios mediante inyección de dependencias. Los servicios comerciales y bancarios se crean con alcance de solicitud. El cliente HTTP hacia BanQuito obtiene la URL de `Servicios:BanQuitoUrl` y establece un tiempo máximo de 10 segundos. Las interfaces usan un cliente HTTP compartido con tiempo máximo de 30 segundos.

El acceso a SQL Server usa ADO.NET y `Microsoft.Data.SqlClient`, no Entity Framework Core. Los servicios abren conexiones asíncronas, ejecutan comandos parametrizados y liberan conexiones, lectores y transacciones con `await using`. La separación entre operaciones HTTP y reglas de dominio permite probar los cálculos sin ejecutar una interfaz.

### Configuración de conexión
`appsettings.json` declara direcciones y bases, pero no incluye la contraseña. El valor completo de `ConnectionStrings:BaseDatos` debe llegar por configuración local, por ejemplo con la variable `ConnectionStrings__BaseDatos`. `Servicios__BanQuitoUrl` permite sobrescribir la dirección bancaria. El doble guion bajo representa los niveles de configuración en variables de entorno.

Los proyectos web tienen marco `net10.0` y declaran `Microsoft.Data.SqlClient` `7.1.1`. Los archivos de configuración y las referencias reales de las API se reproducen en el anexo.

![PowerDesigner: clases del servicio y cliente](../../01. UML/03. DIAGRAMAS UML/04_CLASES/GR09_Clases_Clases del servicio y cliente.png)

## Compilación y ejecución de las API
### Compilar
En una terminal PowerShell situada en la raíz, definir `$buildArgs` como se explicó en la configuración local. `dotnet build` restaura los paquetes necesarios y compila las referencias de cada proyecto.

```powershell
dotnet build "04. SERVIDOR/BanQuito.Api/BanQuito.Api.csproj" @buildArgs
dotnet build "04. SERVIDOR/Comercializadora.Api/Comercializadora.Api.csproj" @buildArgs
```

### Iniciar BanQuito en una terminal
Leer únicamente la variable requerida del archivo local. La contraseña se incorpora a la configuración del proceso, sin escribirla en el comando como un valor literal. Mantener la terminal abierta mientras se utiliza la aplicación.

```powershell
$linea = Get-Content .env |
  Where-Object { $_ -match '^MSSQL_SA_PASSWORD=' } |
  Select-Object -First 1
if (!$linea) { throw 'Falta MSSQL_SA_PASSWORD en .env' }
$claveSql = $linea.Substring('MSSQL_SA_PASSWORD='.Length)
$env:ConnectionStrings__BaseDatos =
  "Server=127.0.0.1,19433;Database=BanQuitoCore;User Id=sa;Password=$claveSql;Encrypt=True;TrustServerCertificate=True"
dotnet run --project "04. SERVIDOR/BanQuito.Api/BanQuito.Api.csproj" @buildArgs
```

### Iniciar la comercializadora en otra terminal
En la nueva terminal, volver a definir `$buildArgs` y cargar `$linea` y `$claveSql` con las instrucciones anteriores. Elegir la base de tienda antes de ejecutar su proyecto; cada proceso hereda la configuración de su propia terminal.

```powershell
$env:ConnectionStrings__BaseDatos =
  "Server=127.0.0.1,19433;Database=ComercializadoraCelulares;User Id=sa;Password=$claveSql;Encrypt=True;TrustServerCertificate=True"
$env:Servicios__BanQuitoUrl = 'http://127.0.0.1:19101/'
dotnet run --project "04. SERVIDOR/Comercializadora.Api/Comercializadora.Api.csproj" @buildArgs
```

### Comprobar disponibilidad
En una tercera terminal ejecutar las consultas de salud. Cada ruta comprueba la conexión con la base de su API. La salud de la tienda no comprueba por sí sola la integración bancaria.

```powershell
Invoke-RestMethod 'http://127.0.0.1:19101/api/salud'
Invoke-RestMethod 'http://127.0.0.1:19102/api/salud'
Invoke-RestMethod 'http://127.0.0.1:19102/api/celulares'
```

Para detener una API ejecutada en primer plano, usar Ctrl+C en su terminal. Al finalizar, cerrar la sesión o retirar las variables locales con `Remove-Item Env:ConnectionStrings__BaseDatos -ErrorAction SilentlyContinue`. Evitar iniciar varias instancias sobre el mismo puerto.

## Contratos REST de la comercializadora
Las solicitudes con cuerpo JSON usan `Content-Type: application/json`. Las fotos usan `multipart/form-data` con el campo `archivo`. El identificador `{id}` de las rutas siguientes corresponde al recurso indicado; una factura y un crédito poseen identificadores diferentes.

| Método | Recurso | Función |
|---|---|---|
| GET | `/api/celulares` | Listar el catálogo activo. |
| GET | `/api/celulares/{id}` | Consultar un celular. |
| POST | `/api/celulares` | Crear un celular con nombre, precio y estado. |
| PUT | `/api/celulares/{id}` | Actualizar sus datos. |
| DELETE | `/api/celulares/{id}` | Desactivar el celular. |
| GET / PUT / DELETE | `/api/celulares/{id}/imagen` | Descargar, cargar o retirar la foto. |
| GET | `/api/credito/elegibilidad?cedula=...` | Consultar al banco a través de la tienda. |
| POST | `/api/facturas` | Registrar la venta con su identificador de operación. |
| GET | `/api/facturas?cedula=...` | Consultar hasta 50 facturas de la cédula. |
| GET | `/api/facturas/{id}` | Recuperar una factura. |
| GET | `/api/facturas/{id}/amortizacion` | Consultar las cuotas de su crédito. |

`SolicitudFactura` incluye `IdOperacion`, `Cedula`, `NombreCliente`, `IdCelular`, `FormaPago`, `NumeroCuotas` y `PrecioEsperado`. Los valores de `FormaPago` son `EFECTIVO` y `CREDITO_DIRECTO`. Una venta en efectivo no admite cuotas; una venta a crédito requiere un número entre 3 y 18. El servidor valida el precio del catálogo frente al precio informado por el cliente para evitar confirmar una venta con un precio desactualizado.

Las altas de catálogo y factura devuelven HTTP 201 con la ubicación del recurso. La desactivación y los cambios de imagen responden 204. Las consultas devuelven datos JSON, excepto la descarga de imagen, que devuelve sus bytes con el MIME correspondiente.

## Contratos REST de BanQuito
El servicio bancario expone la evaluación y las operaciones de crédito. Los cuatro clientes realizan su actividad comercial por la API de tienda; las rutas bancarias permiten documentar y comprobar la integración entre servidores.

| Método | Recurso bancario | Datos y finalidad |
|---|---|---|
| GET | `/api/credito/elegibilidad?cedula=...` | Cédula; devuelve condición, código de cliente, nombre, motivo y máximo. |
| GET | `/api/credito/clientes/{codigoCliente}/monto-maximo` | Código de cliente; devuelve monto máximo. |
| POST | `/api/creditos` | Código, precio del teléfono, cuotas y referencia de venta. |
| GET | `/api/creditos/{id}` | Recupera el crédito y sus cuotas. |
| GET | `/api/creditos/{id}/amortizacion` | Recupera únicamente el plan de pagos. |
| GET | `/api/salud` | Comprueba la conexión con BanQuitoCore. |

`SolicitudCredito` recibe `CodigoCliente`, `PrecioTelefono`, `NumeroCuotas` y `ReferenciaVenta`. La referencia conserva la relación con la solicitud comercial y permite recuperar el mismo crédito ante un reintento. La respuesta contiene identificador, cliente, monto, cuotas, fecha, estado y tabla de amortización.

## Reglas de elegibilidad y monto máximo
### Evaluación del solicitante
`ReglasCredito.Evaluar` comprueba que la persona exista como cliente bancario, que tenga al menos un depósito entre la fecha actual y un mes atrás y que no posea un crédito activo. Para clientes de género masculino exige 25 años cumplidos, calculados con la fecha de nacimiento. Las fechas futuras no participan en la evaluación ni en el cálculo del máximo.

El resultado de la consulta informa la situación al momento de consultar. El otorgamiento vuelve a evaluar las condiciones, ya que otro proceso pudo registrar un crédito entre ambas solicitudes. La restricción de unicidad del crédito activo respalda esta regla en la base de datos.

### Cálculo del monto
El código selecciona los movimientos comprendidos entre la fecha actual y tres meses atrás. Calcula por separado el promedio de los valores de los depósitos y el promedio de los valores de los retiros; si no hay movimientos de un tipo, su promedio se toma como cero. Son promedios por movimiento, no un promedio de totales mensuales.

```text
D = promedio de valores de depósitos del período
R = promedio de valores de retiros del período
Monto máximo = redondear(max(0, (D - R) × 0,35 × 6), 2)
```

Por ejemplo, con D = 1 000,00 y R = 200,00, la diferencia es 800,00 y el máximo resulta 1 680,00. Si los retiros promedios superan a los depósitos, el máximo es cero.

El enunciado presenta una discrepancia: el texto indica 35 % y su fórmula impresa utiliza 30 %. `ReglasCredito.MontoMaximo` implementa `0.35m`. El manual documenta ese valor como decisión del proyecto; un cambio de criterio requiere modificar la regla y sus pruebas, no solo la descripción.

## Facturación, transacciones y reintentos
### Venta en efectivo
El servidor consulta un celular activo, comprueba `PrecioEsperado` si se envió y calcula el total como precio multiplicado por `0.58`. Para un precio de 450,00, el descuento es 189,00 y el total es 261,00. La factura conserva nombre, precio, descuento y total de esa operación. No se solicita un crédito al banco para este pago.

### Venta a crédito
`ServicioFacturas` registra inicialmente la factura con estado `PENDIENTE` dentro de una transacción local. Después solicita el crédito a BanQuito. Al recibir la respuesta, guarda la referencia bancaria y cambia la factura a `APROBADA`. Un rechazo de negocio del banco cambia el estado a `RECHAZADA`; un fallo de comunicación puede dejar la operación pendiente para resolverla con un reintento.

Las transacciones de cada aplicación son locales. La solicitud HTTP al banco y la actualización de la factura no forman una única transacción distribuida. Por ello, perder la respuesta de red no permite concluir que el banco no creó el crédito.

### Idempotencia y concurrencia
El cliente genera un `IdOperacion` por venta y debe conservarlo durante sus reintentos. Una solicitud con el mismo identificador y los mismos datos recupera o completa la operación existente. Si el identificador ya pertenece a datos distintos, el servidor devuelve un conflicto. BanQuito aplica el mismo criterio mediante `ReferenciaVenta`.

La creación comercial utiliza aislamiento Serializable y bloqueos al consultar la operación y el precio. El banco combina transacciones con restricciones de unicidad. Después de una interrupción, consultar las facturas y reintentar con el mismo identificador; crear otro identificador puede registrar otra venta.

![PowerDesigner: secuencia de venta a crédito](../../01. UML/03. DIAGRAMAS UML/03_SECUENCIA/GR09_Secuencia_Venta a crédito.png)

## Cálculo y consulta de amortización
`ReglasCredito.Amortizar` calcula pagos mensuales mediante cuota de anualidad. El capital es el precio financiado y el plazo permitido es de 3 a 18 meses. La implementación interpreta la tasa anual del 16,5 % como nominal y la divide entre 12; la tasa mensual utilizada es `0.01375`, equivalente al 1,375 %.

```text
P = capital; n = meses; i = 0,165 / 12
A = P × i × (1 + i)^n / ((1 + i)^n - 1)
Interés del mes = saldo anterior × i
Capital del mes = cuota - interés
Saldo del mes = saldo anterior - capital del mes
```

Los importes se redondean a dos decimales con `MidpointRounding.AwayFromZero`. La última cuota absorbe la diferencia de centavos para cancelar el capital. La fila cero muestra el monto inicial y los vencimientos posteriores se calculan sumando meses a la fecha del crédito.

Ejemplo calculado para capital de 450,00, plazo de tres meses y la tasa del proyecto. Las fechas dependen del día de otorgamiento; se muestran los períodos para explicar el cálculo.

| Período | Cuota | Interés | Capital | Saldo |
|---|---|---|---|---|
| 0 | 0,00 | 0,00 | 0,00 | 450,00 |
| 1 | 154,14 | 6,19 | 147,95 | 302,05 |
| 2 | 154,14 | 4,15 | 149,99 | 152,06 |
| 3 | 154,15 | 2,09 | 152,06 | 0,00 |

La suma de capital debe ser 450,00 y el saldo final cero. El total de la factura a crédito conserva el precio de lista; los intereses se reflejan en las cuotas, cuya suma puede superar ese total. La API comercial obtiene la amortización del banco utilizando el crédito relacionado con la factura.

## Modelado de casos de uso y actividad
Los casos de uso representan la administración del catálogo, la emisión y consulta de facturas y la participación del banco en el financiamiento. El actor de la aplicación interactúa con una interfaz cliente; la evaluación bancaria se integra mediante el servicio remoto.

![PowerDesigner: casos de uso de ventas](../../01. UML/03. DIAGRAMAS UML/01_CASOS_DE_USO/GR09_CasosUso_Sistema de ventas de celulares.png)

## Flujo de actividad de venta a crédito
El flujo inicia con la selección del celular y los datos del comprador. La consulta de elegibilidad y monto orienta la solicitud; el banco revalida al otorgar el crédito. El recorrido distingue la autorización de negocio, el rechazo y los pasos necesarios para obtener la factura y su tabla de amortización.

Los modelos editables y las exportaciones PNG se conservan en las carpetas UML y MER. Las figuras incorporadas son exportaciones existentes de PowerDesigner; esta revisión documental no modifica sus modelos.

![PowerDesigner: actividad de venta a crédito](../../01. UML/03. DIAGRAMAS UML/02_ACTIVIDAD/GR09_Actividad_Venta a crédito.png)

## Capa compartida de los clientes
`Celulares.Cliente/Servicios/ClienteComercializadora.cs` concentra las solicitudes HTTP, la serialización JSON, la descarga de imágenes y la lectura de errores. `Controladores/ControladorTienda.cs` ofrece las operaciones que utilizan las cuatro interfaces: catálogo, guardado, imágenes, desactivación, facturación, elegibilidad y consultas.

`InterpretarPrecio` acepta punto o coma decimal y rechaza separadores mezclados, precios no positivos o valores con más de dos decimales. El cálculo preliminar en la interfaz facilita mostrar el total; el servidor vuelve a validar y calcular antes de persistir. Los errores HTTP se presentan con el mensaje de negocio recibido, cuando está disponible.

| Cliente | Ubicación de su dirección de API |
|---|---|
| Consola | Variable de entorno `CELULARES_API_URL`; valor predeterminado local. |
| WPF | Configuración de su código de inicio; admite `CELULARES_API_URL`. |
| Web MVC | Clave `CelularesApiUrl` de `appsettings.json` o variable equivalente. |
| Android | `MauiProgram.DireccionServidor`; predeterminado `10.0.2.2:19102`, reemplazable por propiedad de compilación `CelularesApiUrl`. |

La separación evita repetir el contrato HTTP en cada pantalla. Las interfaces no reciben contraseñas SQL ni crean conexiones directas con las bases de datos.

## Cliente de consola: compilación y operación
### Estructura y ejecución
`Program.cs` configura `HttpClient` y crea `ControladorConsola`; `VistaConsola` gestiona la lectura de datos y los colores de terminal. Compilar y ejecutar después de iniciar las API. Definir `$buildArgs` si se utilizan rutas locales distintas de las predeterminadas.

```powershell
$env:CELULARES_API_URL = 'http://127.0.0.1:19102/'
dotnet build "04. CLICON/Celulares.Consola/Celulares.Consola.csproj" @buildArgs
dotnet run --project "04. CLICON/Celulares.Consola/Celulares.Consola.csproj" @buildArgs
```

### Opciones del menú
| Opción | Procedimiento |
|---|---|
| 1: Catálogo | Consultar identificador, nombre, precio y disponibilidad de foto. |
| 2: Guardar celular | Dejar ID vacío para crear; ingresar un ID existente para editar; escribir nombre y precio. |
| 3: Desactivar | Elegir un celular y confirmar la desactivación. |
| 4: Nueva venta | Seleccionar celular, comprador y pago; indicar cuotas para crédito; revisar y confirmar. |
| 5: Elegibilidad | Ingresar cédula y consultar condición, motivo y monto máximo. |
| 6 y 7: Facturas | Buscar por cédula o abrir por número; consultar amortización cuando corresponda. |
| 8 y 9: Pendiente | Reintentar la solicitud conservada o descartarla después de consultar su situación. |
| 10 y 11: Fotos | Indicar ID y ruta JPEG, PNG o WebP para cargar; confirmar para retirar la foto. |
| 12 y 0 | Cambiar tema de terminal o finalizar. |

Si falla una venta, la sesión conserva la solicitud pendiente. La opción 8 reutiliza su identificador. Antes de descartarla con la opción 9, consultar las facturas: la interrupción pudo ocurrir después del registro en el servidor.

## Cliente de escritorio WPF: compilación y operación
### Estructura y ejecución
La aplicación de escritorio requiere Windows. `MainWindow.xaml` declara la interfaz, su archivo asociado atiende los eventos y `ControladorEscritorio` conecta las acciones con la capa compartida. La presentación utiliza controles WPF y llamadas asíncronas al servicio comercial.

```powershell
$env:CELULARES_API_URL = 'http://127.0.0.1:19102/'
dotnet build "04. CLIESC/Celulares.Escritorio/Celulares.Escritorio.csproj" @buildArgs
dotnet run --project "04. CLIESC/Celulares.Escritorio/Celulares.Escritorio.csproj" @buildArgs
```

### Recorrido de uso
Al abrir la ventana, consultar el catálogo y seleccionar el celular. Para crear o editar, completar nombre y precio y utilizar la acción de guardar. La selección identifica el registro que se modifica. La administración de fotos permite cargar, reemplazar o quitar la imagen del producto.

En la operación de venta, ingresar los datos del comprador, seleccionar efectivo o crédito y revisar el total. Para crédito, consultar la condición bancaria e indicar el número de cuotas permitido. Confirmar una sola vez y esperar la respuesta. En consultas, buscar las facturas del comprador y seleccionar la operación cuyo detalle o amortización se necesita.

Si aparece un mensaje de conexión, verificar primero la salud de la API de tienda. Si el problema solo afecta crédito, comprobar BanQuito. No modificar datos e iniciar otra venta para resolver un tiempo de espera; consultar el registro y conservar la solicitud pendiente.

## Cliente web MVC: compilación y funcionamiento
### Creación lógica y estructura
`Program.cs` registra MVC, el cliente HTTP y `ControladorTienda`. `TiendaController` procesa catálogo, imágenes, venta, elegibilidad y consultas. `Views/Tienda/Index.cshtml` presenta el catálogo y formularios; `Factura.cshtml` muestra el detalle y las cuotas. `_Layout.cshtml`, `site.css` y `tema.js` definen estructura visual y cambio de tema.

El controlador utiliza tokens antifalsificación en las acciones de formulario que modifican información. Los campos numéricos se procesan con `FormularioInvariante` para mantener el punto decimal que envía HTML. El navegador se comunica con MVC; la aplicación web ejecuta las llamadas a la API comercial.

### Compilación y ejecución
Verificar en `appsettings.json` que `CelularesApiUrl` apunte a la tienda. Iniciar la web en otra terminal y abrir `http://127.0.0.1:19103/`.

```powershell
dotnet build "04. CLIWEB/Celulares.Web/Celulares.Web.csproj" @buildArgs
dotnet run --project "04. CLIWEB/Celulares.Web/Celulares.Web.csproj" @buildArgs
```

### Catálogo y mantenimiento
Usar el formulario de catálogo para registrar un nombre y un precio positivo. Seleccionar la edición de un producto para modificar sus datos. La desactivación retira el celular de las opciones de venta. La carga de foto envía el archivo al servidor, que valida tamaño, MIME y firma; retirar una foto no elimina el celular.

Las capturas muestran la distribución existente en los temas claro y oscuro. Se incluyen como referencia de interfaz y no como una certificación de pruebas.

![Navegador: catálogo en tema claro](../evidencias/web_catalogo_claro.png)
![Navegador: catálogo en tema oscuro](../evidencias/web_catalogo_oscuro.png)

## Cliente web: facturación y consultas
Para vender en efectivo, seleccionar un celular, ingresar cédula y nombre, elegir efectivo y revisar el descuento. Al confirmar, la web abre el detalle de factura. Verificar que el precio base, descuento y total correspondan al producto elegido.

Para crédito, consultar la elegibilidad del comprador, revisar el monto máximo y establecer entre 3 y 18 cuotas. La confirmación solicita la operación al banco mediante la tienda. La vista de factura muestra la referencia de crédito y la amortización cuando el financiamiento está registrado.

La búsqueda por cédula recupera las operaciones del comprador; abrir una factura permite revisar sus datos históricos. Si se interrumpe la solicitud de venta, conservar los datos y el identificador del formulario al reintentar. La consulta bancaria previa no sustituye la validación al otorgar.

![Navegador: detalle de venta en efectivo](../evidencias/web_efectivo.png)
![Navegador: detalle y amortización de crédito](../evidencias/web_credito_directo.png)

## Cliente web: distribución adaptable
La hoja de estilos reorganiza los paneles de catálogo y venta para pantallas estrechas. Los campos de precio y cuotas deben mantenerse legibles, y la tabla de amortización debe poder consultarse sin perder sus columnas. Los temas claro y oscuro cambian la presentación de la interfaz.

La captura existente de 390 píxeles de ancho se presenta en seis tramos consecutivos para que puedan leerse los formularios y el detalle. Los tramos pertenecen al mismo recorrido vertical; no representan seis aplicaciones ni seis resultados de prueba.

![Navegador: vista adaptable, tramo 1 de 6](../evidencias/web_responsive_panel_01.png)
![Navegador: vista adaptable, tramo 2 de 6](../evidencias/web_responsive_panel_02.png)
![Navegador: vista adaptable, tramo 3 de 6](../evidencias/web_responsive_panel_03.png)
![Navegador: vista adaptable, tramo 4 de 6](../evidencias/web_responsive_panel_04.png)
![Navegador: vista adaptable, tramo 5 de 6](../evidencias/web_responsive_panel_05.png)
![Navegador: vista adaptable, tramo 6 de 6](../evidencias/web_responsive_panel_06.png)

## Cliente móvil Android: configuración y compilación
### Organización
`MauiProgram.cs` establece el destino HTTP; `App.cs` inicia la aplicación; `MainPage.cs` organiza la interfaz y `ControladorMovil` utiliza la capa compartida. El proyecto declara el identificador `ec.edu.monster.celulares.gr09`. El manifiesto Android contiene la configuración de la aplicación.

### Dirección del servidor
El emulador accede al host mediante `http://10.0.2.2:19102/`. Su dirección `127.0.0.1` apunta al propio Android. `MauiProgram.DireccionServidor` usa esa URL de forma predeterminada y permite reemplazarla mediante el metadato de compilación `CelularesApiUrl`. En un dispositivo físico, establecer una dirección accesible del equipo y habilitar la escucha y el acceso local del servicio para ese entorno.

### Compilar sin instalar
Definir `$sdkAndroid` con la ruta real del Android SDK del equipo. El ejemplo usa su ubicación habitual en el perfil de Windows; verificar que existe. La compilación sin instalación no necesita un dispositivo conectado.

```powershell
$sdkAndroid = "$env:LOCALAPPDATA\Android\Sdk"
dotnet build "04. CLIMOV/Celulares.Movil/Celulares.Movil.csproj" `
  -f net10.0-android @buildArgs "-p:AndroidSdkDirectory=$sdkAndroid"
```

### Instalar y abrir
Iniciar un emulador o conectar un dispositivo con depuración habilitada. Comprobar que ADB enumera un destino autorizado antes de ejecutar el objetivo `Run`. Un archivo APK instalado manualmente desde una compilación Debug puede depender de ensamblados de despliegue rápido; utilizar el objetivo de ejecución para ese recorrido.

```powershell
& "$sdkAndroid\platform-tools\adb.exe" devices
dotnet build "04. CLIMOV/Celulares.Movil/Celulares.Movil.csproj" `
  -t:Run -f net10.0-android @buildArgs "-p:AndroidSdkDirectory=$sdkAndroid"
```

## Cliente móvil: catálogo y mantenimiento
Abrir la aplicación con la API de tienda disponible. En el catálogo se muestran nombre, precio y foto cuando existe. Seleccionar un producto permite trabajar con su identificador; para guardar, completar un nombre y precio válidos. La edición actualiza el catálogo, mientras que la desactivación conserva las facturas anteriores.

Las imágenes son opcionales. Seleccionar un archivo JPEG, PNG o WebP dentro del límite de 5 MiB; el servicio comercial valida y almacena su contenido. Si una imagen no aparece, revisar primero que exista y que su ruta HTTP sea alcanzable desde Android.

Las capturas existentes permiten identificar el catálogo inicial y la vista posterior a una edición.

![Android: catálogo inicial](../evidencias/android_catalogo.png)
![Android: producto editado](../evidencias/android_catalogo_editado.png)

## Cliente móvil: venta en efectivo y crédito
Seleccionar un celular y completar los datos del comprador. Para efectivo, revisar la reducción del 42 % y confirmar. El detalle debe conservar el precio, el descuento y el total del momento de compra. No se genera una tabla bancaria para efectivo.

Para crédito, consultar la elegibilidad, comprobar que el precio no supere el máximo y elegir entre 3 y 18 cuotas. Confirmar la solicitud y esperar la respuesta del servicio. El descuento de efectivo no se aplica al capital financiado. Ante una interrupción, consultar las facturas antes de crear otra operación.

Las pantallas siguientes ilustran ambas modalidades con los registros existentes de la aplicación.

![Android: detalle de venta en efectivo](../evidencias/android_efectivo.png)
![Android: detalle de compra a crédito](../evidencias/android_credito.png)

## Cliente móvil: facturas y amortización
Buscar las facturas por la cédula del comprador y abrir el detalle de la operación. Para una factura de crédito con referencia bancaria disponible, consultar su amortización. La vista debe mostrar número de cuota, fecha, cuota, interés, capital y saldo; la fila inicial conserva el monto financiado.

La consulta usa el identificador de factura en la API comercial. El servidor obtiene internamente el identificador del crédito y consulta BanQuito, por lo que el usuario no necesita introducir la dirección bancaria ni conectarse a SQL Server.

![Android: amortización a tres cuotas](../evidencias/android_amortizacion.png)
![Android: consulta de amortización desde factura](../evidencias/android_consulta_amortizacion.png)

## Cliente móvil: búsqueda de operaciones
Ingresar la cédula con la que se registró la compra y consultar la lista de facturas. Seleccionar una operación para revisar celular, modalidad, total y estado. La consulta también ayuda a resolver una venta cuyo resultado no se recibió por una interrupción de red.

La aplicación consulta como máximo las 50 operaciones más recientes que devuelve el servicio para esa cédula. Si se necesita información fuera de ese alcance, revisar los procedimientos de consulta del servidor; no interpretar una lista parcial como ausencia definitiva de registros.

![Android: búsqueda y reapertura de factura](../evidencias/android_busqueda.png)

## Pruebas de los servicios y criterios de comprobación
Las pruebas deben vincular una entrada y una condición inicial con una respuesta verificable. La tabla define criterios para ejecutar una revisión funcional; no declara que los casos se hayan ejecutado durante esta edición del manual. Los registros históricos se conservan separados de los resultados esperados.

| Caso | Entrada o condición | Resultado que se debe comprobar |
|---|---|---|
| Catálogo | Crear, editar y desactivar un celular de prueba. | Datos persistidos; producto desactivado fuera del catálogo de venta. |
| Imágenes | Cargar y retirar una foto válida. | Carga 204; descarga con el contenido correcto; consulta sin foto 404. |
| Archivo inválido | Firma, MIME o tamaño fuera de lo permitido. | Rechazo del archivo sin reemplazar una foto válida. |
| Efectivo | Precio 450,00, sin cuotas. | Descuento 189,00 y total 261,00. |
| Elegibilidad | Cliente inexistente, varón menor de 25 o sin depósito reciente. | Condición no elegible con motivo correspondiente. |
| Máximo | Promedios de depósitos y retiros conocidos. | Aplicación de diferencia × 0,35 × 6 y límite inferior cero. |
| Plazo | Solicitud con 2 o 19 cuotas. | Rechazo por estar fuera del intervalo permitido. |
| Límite de crédito | Monto mayor al máximo y monto igual al máximo. | Rechazo del primero; admisión del segundo si cumple las demás reglas. |
| Crédito activo | Intento de segundo crédito para el mismo cliente. | Rechazo sin registrar otro crédito activo. |
| Reintento | Mismo identificador y mismos datos. | Una sola factura y un solo crédito relacionados. |
| Conflicto | Mismo identificador con datos distintos. | Respuesta de conflicto sin modificar la operación original. |
| Amortización | Capital 450,00 a 3 y a 18 meses. | Fila inicial y n cuotas; fechas mensuales; capital total; saldo final cero. |
| Consultas | Búsqueda por cédula y apertura por ID. | Datos de factura y amortización coherentes con la operación guardada. |
| Interfaces | Ejecutar los recorridos en los cuatro clientes. | Mismas reglas y datos del contrato comercial. |

Los datos semilla bancarios incluyen diferentes condiciones: `0102030405` es el cliente masculino adulto del conjunto; `0203040506` representa al masculino de 24 años; `0405060708` posee movimientos más antiguos. La elegibilidad depende del día de la carga, de los movimientos y de los créditos ya registrados; revisar esas condiciones antes de usar cualquier cédula como caso de prueba.

## Ejecución reproducible de pruebas
### Pruebas unitarias
Ejecutar los proyectos de prueba de ambos dominios. El comando devuelve el resultado de la ejecución del equipo; registrar su fecha y salida antes de informar cantidades o estados.

```powershell
dotnet test "04. SERVIDOR/Pruebas/Comercializadora.Pruebas.csproj" @buildArgs
dotnet test "04. SERVIDOR/BanQuito.Pruebas/BanQuito.Pruebas.csproj" @buildArgs
```

### Integración e interfaces
Los scripts de integración y los recorridos visuales generan sus propios registros. Antes de ejecutarlos, revisar las rutas de herramientas y su configuración local: varios arneses conservan rutas del equipo de desarrollo. Utilizar bases aisladas para las ventas de prueba; no reinicializar las bases principales.

```powershell
python scripts/VerificarApiQA.py
python scripts/VerificarClientesQA.py
python scripts/IniciarQAVisual.py
python scripts/VerificarWebNavegador.py
```

`VerificarApiQA.py` cubre contratos y reglas integradas. `VerificarClientesQA.py` recorre consola y MVC. `IniciarQAVisual.py` prepara el entorno para pruebas de interfaz; los arneses WPF y `AndroidQA.py` utilizan controles y un emulador reales. La comprobación web usa Playwright y requiere su navegador instalado.

Los archivos `EVIDENCIA_API_QA.json`, `EVIDENCIA_CLIENTES_QA.json`, `EVIDENCIA_WPF_QA.json`, `EVIDENCIA_ANDROID_QA.json` y `EVIDENCIA_WEB_NAVEGADOR.json` pertenecen a ejecuciones registradas en el proyecto. Para interpretar un resultado, consultar fecha, escenario, entradas y captura asociada. La presencia de una imagen o un registro anterior no demuestra por sí sola el funcionamiento de una ejecución nueva.

## Manejo de errores y solución de problemas
Las API convierten errores conocidos en respuestas HTTP y presentan un cuerpo de problema con campos como `status` y `title`. Los clientes leen el mensaje y lo muestran en su interfaz. Los detalles internos se consultan en la salida del servidor; no deben sustituirse por mensajes genéricos de éxito.

| Síntoma o código | Causa a revisar | Acción técnica |
|---|---|---|
| SQL Server no disponible | Docker detenido, contenedor sin salud o puerto ocupado. | Revisar `docker compose ps` y registros; iniciar el motor y comprobar `19433`. |
| Error de acceso a SQL | Contraseña ausente o distinta de la instancia persistida. | Revisar `.env` localmente y la variable de conexión del proceso; conservar el volumen. |
| API falla desde el IDE | No heredó `ConnectionStrings__BaseDatos`. | Iniciar con el script o cargar la variable antes de ejecutar. |
| Base u objeto ausente | Preparación incompleta o migración pendiente. | Aplicar los scripts en orden y revisar el error SQL. |
| HTTP 400 | Campos, precio, cuotas o archivo inválidos. | Corregir la entrada según el contrato. |
| HTTP 404 | Recurso inexistente o producto sin imagen. | Comprobar ID y disponibilidad de foto. |
| HTTP 409 | Reintento con datos distintos, crédito activo o condición de negocio incompatible. | Leer `title` y consultar la operación existente. |
| HTTP 503 | SQL Server o servicio remoto no disponible. | Comprobar salud de ambas API y conexiones; reintentar con el mismo identificador. |
| HTTP 500 | Error interno no clasificado. | Consultar el registro del servidor y reproducir la entrada en un entorno aislado. |
| Android no conecta | Uso de loopback del emulador o API detenida. | Verificar `10.0.2.2:19102` y salud de la tienda en el host. |
| MAUI no instala | No hay dispositivo autorizado o faltan herramientas. | Revisar ADB, SDK y carga MAUI antes de usar `-t:Run`. |
| Error de unidad D: | Rutas de compilación originales no existen en el equipo. | Pasar `CelularBuildRoot` y `CelularPackagesRoot` con rutas válidas. |

La API utiliza HTTP local y no incorpora autenticación ni autorización de usuarios. Si se cambia el despliegue para permitir acceso desde otros equipos, deben definirse controles de acceso y transporte adecuados antes de tratar ese entorno como un servicio de producción.

## Mantenimiento y limitaciones
Mantener las credenciales fuera del código y actualizar su configuración por entorno. Antes de modificar esquema o reglas de negocio, conservar una copia de seguridad y ejecutar las pruebas en una base independiente. Una migración de imágenes agrega columnas opcionales; no requiere borrar el catálogo ni las facturas para actualizar una instalación existente.

Los movimientos semilla envejecen con el calendario, por lo que las pruebas de elegibilidad necesitan fechas controladas. El banco recibe la fecha a través de `TimeProvider`; la lógica de dominio permite evaluar períodos concretos. Conservar las referencias idempotentes al investigar interrupciones de crédito.

La discrepancia entre 35 % y 30 % debe resolverse con el criterio académico del enunciado y reflejarse en código, pruebas y documentación. La tasa de 16,5 % y el descuento de 42 % son parámetros del ejercicio. Los modelos PowerDesigner y sus exportaciones existentes se conservan como fuente de las figuras; la regeneración depende de disponer de una licencia utilizable.

## Conclusiones
La solución concentra las reglas comerciales en una API de tienda y delega la evaluación y el financiamiento a una API bancaria independiente. La separación permite utilizar cuatro interfaces sobre el mismo contrato y mantener el acceso a las bases dentro de los servicios responsables.

La operación a crédito requiere coordinar persistencia local y comunicación HTTP. Los estados de factura, las referencias únicas y los reintentos con el mismo identificador permiten manejar interrupciones sin interpretar una pérdida de conexión como una venta nueva. El cálculo decimal y el ajuste de la cuota final mantienen la coherencia del capital amortizado.

La instalación se realiza con SQL Server en Docker y aplicaciones .NET en el host. La reproducibilidad depende de conservar la estructura del repositorio, configurar las rutas y credenciales del equipo y distinguir los criterios esperados de los resultados obtenidos al ejecutar las pruebas.

## Recomendaciones
Utilizar el orden de arranque SQL Server, BanQuito, comercializadora y cliente. Registrar la fecha y condiciones de cada comprobación y utilizar datos aislados para las ventas de prueba. Al cambiar el destino Android o la dirección bancaria, actualizar la configuración correspondiente y repetir la consulta de salud y el recorrido afectado.

Mantener el manual y su presentación a partir de la misma fuente documental. Actualizar contratos, ejemplos y pruebas cuando cambie una regla. Conservar las capturas reales junto con los registros de su escenario y evitar sustituirlas por imágenes que solo anuncien una pantalla o un resultado.

## Referencias bibliográficas
Codd, E. F. (1970). A relational model of data for large shared data banks. Communications of the ACM, 13(6), 377–387. https://doi.org/10.1145/362384.362685

Fielding, R. T. (2000). Architectural styles and the design of network-based software architectures [Tesis doctoral, University of California, Irvine]. https://ics.uci.edu/~fielding/pubs/dissertation/top.htm

Fielding, R. T., y Taylor, R. N. (2002). Principled design of the modern Web architecture. ACM Transactions on Internet Technology, 2(2), 115–150. https://doi.org/10.1145/514183.514185

Fowler, M. (2002). Patterns of enterprise application architecture. Addison-Wesley. https://martinfowler.com/books/eaa.html

Silberschatz, A., Korth, H. F., y Sudarshan, S. (2019). Database system concepts (7.ª ed.). McGraw-Hill Education. https://www.db-book.com/

## Anexo A. Archivos de configuración
Los siguientes listados reproducen los archivos del repositorio que definen el motor, las direcciones de las API y las referencias de sus proyectos. La contraseña se proporciona mediante configuración de entorno y no se incorpora a estos listados.

### Docker Compose
Ruta: `compose.yaml`.

```yaml
services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_PID: Developer
      MSSQL_SA_PASSWORD: ${MSSQL_SA_PASSWORD:?Configure .env desde .env.example}
    ports:
      - "127.0.0.1:19433:1433"
    volumes:
      - celulares_sql:/var/opt/mssql
    healthcheck:
      test: ["CMD-SHELL", '/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$$MSSQL_SA_PASSWORD" -C -Q "SELECT 1" -b -o /dev/null']
      interval: 5s
      timeout: 5s
      retries: 30
volumes:
  celulares_sql:
```

### Configuración de Comercializadora.Api
Ruta: `04. SERVIDOR/Comercializadora.Api/appsettings.json`.

```json
{
  "Urls": "http://127.0.0.1:19102",
  "ConnectionStrings": {
    "BaseDatos": "Server=127.0.0.1,19433;Database=ComercializadoraCelulares;User Id=sa;Encrypt=True;TrustServerCertificate=True;Connect Timeout=8"
  },
  "Servicios": {
    "BanQuitoUrl": "http://127.0.0.1:19101/"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

### Configuración de BanQuito.Api
Ruta: `04. SERVIDOR/BanQuito.Api/appsettings.json`.

```json
{
  "Urls": "http://127.0.0.1:19101",
  "ConnectionStrings": {
    "BaseDatos": "Server=127.0.0.1,19433;Database=BanQuitoCore;User Id=sa;Encrypt=True;TrustServerCertificate=True;Connect Timeout=8"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

### Proyecto Comercializadora.Api
Ruta: `04. SERVIDOR/Comercializadora.Api/Comercializadora.Api.csproj`.

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.Data.SqlClient" Version="7.1.1" />
    <PackageReference Include="System.Security.Cryptography.Pkcs" Version="10.0.13" />
    <ProjectReference Include="..\Comercializadora.Dominio\Comercializadora.Dominio.csproj" />
    <ProjectReference Include="..\Contratos\Celulares.Contratos.csproj" />
  </ItemGroup>
</Project>
```

### Proyecto BanQuito.Api
Ruta: `04. SERVIDOR/BanQuito.Api/BanQuito.Api.csproj`.

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
<PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup>
<ItemGroup><PackageReference Include="Microsoft.Data.SqlClient" Version="7.1.1" /><PackageReference Include="System.Security.Cryptography.Pkcs" Version="10.0.13" />
<ProjectReference Include="..\BanQuito.Dominio\BanQuito.Dominio.csproj" />
<ProjectReference Include="..\BanQuito.Contratos\BanQuito.Contratos.csproj" /></ItemGroup>
</Project>
```

## Anexo B. Scripts SQL del proyecto
Los listados siguientes conservan la definición y los datos semilla del repositorio. Ejecutar con una herramienta que interprete los separadores `GO`, en el orden de preparación descrito en el manual.

Los listados corresponden a los cinco archivos que ejecuta `PrepararEntorno.ps1`, en el mismo orden documentado. Se incluyen para consultar las definiciones reales de tablas, restricciones, migración y semillas. No se modifican bases al leer este anexo.

### 03. BDD/01_CrearBases.sql

```sql
SET QUOTED_IDENTIFIER ON;
GO
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;
GO
USE master;
GO
IF DB_ID(N'ComercializadoraCelulares') IS NULL CREATE DATABASE ComercializadoraCelulares;
GO
USE ComercializadoraCelulares;
GO
IF OBJECT_ID(N'dbo.CELULAR') IS NULL
CREATE TABLE dbo.CELULAR (
 ID_CELULAR int IDENTITY PRIMARY KEY, NOMBRE nvarchar(100) NOT NULL,
 PRECIO numeric(10,2) NOT NULL CHECK(PRECIO>0), ACTIVO bit NOT NULL DEFAULT 1,
 IMAGEN varbinary(max) NULL, IMAGEN_TIPO varchar(40) NULL
);
IF OBJECT_ID(N'dbo.FACTURA') IS NULL
CREATE TABLE dbo.FACTURA (
 ID_FACTURA int IDENTITY PRIMARY KEY, ID_OPERACION uniqueidentifier NOT NULL UNIQUE,
 FECHA datetime2 NOT NULL DEFAULT SYSDATETIME(), CEDULA nvarchar(100) NOT NULL, NOMBRE_CLIENTE nvarchar(100) NOT NULL,
 ID_CELULAR int NOT NULL REFERENCES dbo.CELULAR(ID_CELULAR), NOMBRE_CELULAR nvarchar(100) NOT NULL,
 FORMA_PAGO varchar(20) NOT NULL CHECK(FORMA_PAGO IN ('EFECTIVO','CREDITO_DIRECTO')),
 PRECIO numeric(10,2) NOT NULL CHECK(PRECIO>0), DESCUENTO numeric(10,2) NOT NULL, TOTAL numeric(10,2) NOT NULL CHECK(TOTAL>0),
 COD_CLIENTE_BANCO int NULL, COD_CREDITO int NULL,
 NUMERO_CUOTAS int NULL CHECK(NUMERO_CUOTAS BETWEEN 3 AND 18),
 ESTADO varchar(12) NOT NULL CHECK(ESTADO IN ('PENDIENTE','APROBADA','RECHAZADA')),
 CONSTRAINT CK_FACTURA_PAGO CHECK(
  (FORMA_PAGO='EFECTIVO' AND COD_CREDITO IS NULL AND NUMERO_CUOTAS IS NULL) OR
  (FORMA_PAGO='CREDITO_DIRECTO' AND NUMERO_CUOTAS IS NOT NULL))
);
GO
```

### 03. BDD/03_MigrarImagenes.sql

```sql
USE ComercializadoraCelulares;
GO
IF COL_LENGTH(N'dbo.CELULAR', N'IMAGEN') IS NULL
    ALTER TABLE dbo.CELULAR ADD IMAGEN varbinary(max) NULL;
IF COL_LENGTH(N'dbo.CELULAR', N'IMAGEN_TIPO') IS NULL
    ALTER TABLE dbo.CELULAR ADD IMAGEN_TIPO varchar(40) NULL;
GO
```

### 03. BDD/02_DatosPrueba.sql

```sql
USE ComercializadoraCelulares;
GO
IF NOT EXISTS(SELECT 1 FROM dbo.CELULAR WHERE NOMBRE=N'Celular Aurora 128 GB')
 INSERT dbo.CELULAR(NOMBRE,PRECIO) VALUES(N'Celular Aurora 128 GB',450.00);
IF NOT EXISTS(SELECT 1 FROM dbo.CELULAR WHERE NOMBRE=N'Celular Nova 256 GB')
 INSERT dbo.CELULAR(NOMBRE,PRECIO) VALUES(N'Celular Nova 256 GB',750.00);
IF NOT EXISTS(SELECT 1 FROM dbo.CELULAR WHERE NOMBRE=N'Celular Prisma 64 GB')
 INSERT dbo.CELULAR(NOMBRE,PRECIO) VALUES(N'Celular Prisma 64 GB',250.00);
GO
```

### 03. BDD/BanQuito/BanQuito_01_CrearBase.sql

```sql
SET QUOTED_IDENTIFIER ON;
GO
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;
GO
USE master;
GO
IF DB_ID(N'BanQuitoCore') IS NULL CREATE DATABASE BanQuitoCore;
GO
USE BanQuitoCore;
GO
IF OBJECT_ID(N'dbo.CLIENTE') IS NULL
CREATE TABLE dbo.CLIENTE (
 COD_CLIENTE int NOT NULL PRIMARY KEY, CEDULA varchar(100) NOT NULL UNIQUE,
 NOMBRE varchar(100) NOT NULL, GENERO varchar(1) NOT NULL CHECK (GENERO IN ('M','F')),
 FECHA_NACIMIENTO date NOT NULL
);
IF OBJECT_ID(N'dbo.CUENTA') IS NULL
CREATE TABLE dbo.CUENTA (
 NUM_CUENTA varchar(8) NOT NULL PRIMARY KEY,
 COD_CLIENTE int NOT NULL REFERENCES dbo.CLIENTE(COD_CLIENTE), SALDO numeric(10,2) NOT NULL
);
IF OBJECT_ID(N'dbo.MOVIMIENTO') IS NULL
CREATE TABLE dbo.MOVIMIENTO (
 COD_MOVIMIENTO int NOT NULL PRIMARY KEY, NUM_CUENTA varchar(8) NOT NULL REFERENCES dbo.CUENTA(NUM_CUENTA),
 TIPO varchar(3) NOT NULL CHECK (TIPO IN ('DEP','RET')), VALOR numeric(10,2) NOT NULL CHECK (VALOR>0), FECHA date NOT NULL
);
IF OBJECT_ID(N'dbo.CREDITO') IS NULL
CREATE TABLE dbo.CREDITO (
 COD_CREDITO int IDENTITY PRIMARY KEY, COD_CLIENTE int NOT NULL REFERENCES dbo.CLIENTE(COD_CLIENTE),
 REFERENCIA_VENTA uniqueidentifier NOT NULL UNIQUE, MONTO numeric(10,2) NOT NULL CHECK (MONTO>0),
 NUMERO_CUOTAS int NOT NULL CHECK (NUMERO_CUOTAS BETWEEN 3 AND 18),
 TASA_ANUAL decimal(7,5) NOT NULL DEFAULT 0.165, FECHA date NOT NULL,
 ESTADO varchar(10) NOT NULL CHECK (ESTADO IN ('ACTIVO','CANCELADO'))
);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='UX_CREDITO_ACTIVO' AND object_id=OBJECT_ID('dbo.CREDITO'))
CREATE UNIQUE INDEX UX_CREDITO_ACTIVO ON dbo.CREDITO(COD_CLIENTE) WHERE ESTADO='ACTIVO';
IF OBJECT_ID(N'dbo.AMORTIZACION') IS NULL
CREATE TABLE dbo.AMORTIZACION (
 COD_CREDITO int NOT NULL REFERENCES dbo.CREDITO(COD_CREDITO),
 NUMERO_CUOTA int NOT NULL CHECK (NUMERO_CUOTA BETWEEN 0 AND 18), FECHA_PAGO date NOT NULL,
 VALOR_CUOTA numeric(10,2) NOT NULL, INTERES_PAGADO numeric(10,2) NOT NULL,
 CAPITAL_PAGADO numeric(10,2) NOT NULL, SALDO numeric(10,2) NOT NULL CHECK (SALDO>=0),
 CONSTRAINT PK_AMORTIZACION PRIMARY KEY(COD_CREDITO,NUMERO_CUOTA)
);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name='IX_MOVIMIENTO_CUENTA_FECHA' AND object_id=OBJECT_ID('dbo.MOVIMIENTO'))
CREATE INDEX IX_MOVIMIENTO_CUENTA_FECHA ON dbo.MOVIMIENTO(NUM_CUENTA,FECHA) INCLUDE(TIPO,VALOR);
GO
```

### 03. BDD/BanQuito/BanQuito_02_DatosPrueba.sql

```sql
USE BanQuitoCore;
GO
SET XACT_ABORT ON;
BEGIN TRANSACTION;
DECLARE @hoy date=CAST(GETDATE() AS date);
IF NOT EXISTS(SELECT 1 FROM dbo.CLIENTE WHERE COD_CLIENTE=1)
 INSERT dbo.CLIENTE VALUES(1,'0102030405','Juan Perez','M',DATEADD(YEAR,-35,@hoy));
IF NOT EXISTS(SELECT 1 FROM dbo.CLIENTE WHERE COD_CLIENTE=2)
 INSERT dbo.CLIENTE VALUES(2,'0203040506','Carlos Gomez','M',DATEADD(YEAR,-24,@hoy));
IF NOT EXISTS(SELECT 1 FROM dbo.CLIENTE WHERE COD_CLIENTE=3)
 INSERT dbo.CLIENTE VALUES(3,'0304050607','Ana Lopez','F',DATEADD(YEAR,-23,@hoy));
IF NOT EXISTS(SELECT 1 FROM dbo.CLIENTE WHERE COD_CLIENTE=4)
 INSERT dbo.CLIENTE VALUES(4,'0405060708','Maria Torres','F',DATEADD(YEAR,-32,@hoy));
IF NOT EXISTS(SELECT 1 FROM dbo.CLIENTE WHERE COD_CLIENTE=5)
 INSERT dbo.CLIENTE VALUES(5,'0506070809','Luis Sanchez','M',DATEADD(YEAR,-30,@hoy));
DECLARE @cliente int=1;
WHILE @cliente<=5
BEGIN
 DECLARE @cuenta varchar(8)=CAST(10000000+@cliente AS varchar(8));
 IF NOT EXISTS(SELECT 1 FROM dbo.CUENTA WHERE NUM_CUENTA=@cuenta) INSERT dbo.CUENTA VALUES(@cuenta,@cliente,2000.00);
 DECLARE @numero int=1;
 WHILE @numero<=10
 BEGIN
  DECLARE @id int=(@cliente-1)*10+@numero;
  DECLARE @tipo varchar(3)=CASE WHEN @numero%2=1 THEN 'DEP' ELSE 'RET' END;
  DECLARE @dias int=@numero*6+CASE WHEN @cliente=4 THEN 40 ELSE 0 END;
  DECLARE @valor numeric(10,2)=CASE WHEN @tipo='DEP' THEN 1000+@cliente*50 ELSE 100+@cliente*10 END;
  IF NOT EXISTS(SELECT 1 FROM dbo.MOVIMIENTO WHERE COD_MOVIMIENTO=@id)
   INSERT dbo.MOVIMIENTO VALUES(@id,@cuenta,@tipo,@valor,DATEADD(DAY,-@dias,@hoy));
  SET @numero+=1;
 END
 SET @cliente+=1;
END
COMMIT;
SELECT 'CLIENTES' AS ENTIDAD,COUNT(*) AS TOTAL FROM dbo.CLIENTE
UNION ALL SELECT 'CUENTAS',COUNT(*) FROM dbo.CUENTA
UNION ALL SELECT 'MOVIMIENTOS',COUNT(*) FROM dbo.MOVIMIENTO;
GO
```

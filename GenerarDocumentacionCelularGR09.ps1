[CmdletBinding()]
param([string]$Raiz = $PSScriptRoot)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Raiz = [System.IO.Path]::GetFullPath($Raiz)

# ── rutas del proyecto ────────────────────────────────────────────────────────
$ProyectoNombre = 'TI.1.1. PAO202651_CELULAR_BDDLOCAL_RESTFUL_NRC36884_GR09'
$Root   = Join-Path $Raiz "TI.1.1 $ProyectoNombre" 2>$null
# Intenta también sin espacio
if (-not (Test-Path -LiteralPath $Root)) {
    $Root = Join-Path $Raiz $ProyectoNombre
}
if (-not (Test-Path -LiteralPath $Root)) {
    # buscar carpeta que coincida
    $found = Get-ChildItem -Path $Raiz -Directory | Where-Object { $_.Name -like '*CELULAR*RESTFUL*' } | Select-Object -First 1
    if ($null -eq $found) { throw "No se encontro el proyecto CELULAR en $Raiz" }
    $Root = $found.FullName
}
Write-Output "Proyecto: $Root"

$UmlDir   = Join-Path $Root '01. UML'
$ErsDir   = Join-Path $UmlDir  '01. ERS'
$MerDir   = Join-Path $Root '02. MER'
$Docs     = Join-Path $Root '05. DOCUMENTACION'
$ManualDir= Join-Path $Docs '01. MANUAL TECNICO'
$PptDir   = Join-Path $Docs '02. PRESENTACION'
$CaptDir  = Join-Path $ManualDir 'Capturas'

foreach ($d in @($ErsDir, $ManualDir, $PptDir, $CaptDir)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

# ── helpers Word ──────────────────────────────────────────────────────────────
function P($doc, [string]$text, [int]$style = -1, [int]$align = 0, [int]$size = 10, [bool]$bold = $false) {
    $start = [int]$doc.Content.End - 1
    $r = $doc.Range($start, $start); $r.InsertAfter($text + [char]13)
    $p = $doc.Range($start, $start + $text.Length + 1).Paragraphs.Item(1)
    $p.Style = $style; $p.Alignment = $align
    $p.Format.SpaceAfter = 6; $p.Format.KeepTogether = -1
    $p.Range.Font.Name = 'Arial'; $p.Range.Font.Size = $size
    if ($bold) { $p.Range.Font.Bold = -1 }
    return $p
}

function T($doc, [string[]]$headers, [object[]]$rows, [int[]]$widths = @()) {
    $data = [Collections.Generic.List[object]]::new()
    $data.Add($headers)
    foreach ($row in $rows) { $data.Add($row) }
    $at = [int]$doc.Content.End - 1
    $table = $doc.Tables.Add($doc.Range($at, $at), $data.Count, $headers.Count)
    $table.Borders.Enable = 1; $table.AllowAutoFit = $true; $table.AutoFitBehavior(2)
    for ($r = 0; $r -lt $data.Count; $r++) {
        for ($c = 0; $c -lt $headers.Count; $c++) {
            $rowData = $data[$r]
            $cell = $table.Cell($r + 1, $c + 1)
            $cell.Range.Text = [string]$rowData[$c]
            $cell.Range.Font.Name = 'Arial'
            $fs = if ($headers.Count -ge 5) { [double]7.5 } else { [double]9 }
            $cell.Range.Font.Size = $fs; $cell.VerticalAlignment = 1
            if ($r -eq 0) { $cell.Range.Bold = -1; $cell.Shading.BackgroundPatternColor = 15132390 }
        }
    }
    if ($widths.Count -eq $headers.Count) {
        for ($c = 0; $c -lt $widths.Count; $c++) {
            try { $table.Columns.Item($c + 1).Width = $widths[$c] } catch {}
        }
    }
    try { $table.Rows.Item(1).HeadingFormat = -1 } catch {}
    $tail = $doc.Range([int]$doc.Content.End - 1, [int]$doc.Content.End - 1)
    $tail.InsertAfter([char]13)
    return $table
}

function Pic($doc, [string]$path, [float]$max = 450) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Write-Warning "Imagen no encontrada (se omite): $path"
        return
    }
    $at  = [int]$doc.Content.End - 1
    $pic = $doc.Range($at, $at).InlineShapes.AddPicture($path, $false, $true)
    $pic.LockAspectRatio = -1
    if ($pic.Width -gt $max) { $pic.Width = $max }
    $pic.Range.ParagraphFormat.Alignment = 1
    $tail = $doc.Range([int]$doc.Content.End - 1, [int]$doc.Content.End - 1)
    $tail.InsertAfter([char]13)
}

function Setup-Word($doc) {
    $doc.PageSetup.TopMargin    = 56
    $doc.PageSetup.BottomMargin = 52
    $doc.PageSetup.LeftMargin   = 54
    $doc.PageSetup.RightMargin  = 54
    $f = $doc.Sections.Item(1).Footers.Item(1).Range
    $f.Text = 'COMERCIALIZADORA CELULARES  |  GRUPO 09  |  NRC 36884'
    $f.Font.Name = 'Arial'; $f.Font.Size = 8
    $f.ParagraphFormat.Alignment = 2
}

function Cover($doc, [string]$title, [string]$subtitle) {
    [void](P $doc 'COMERCIALIZADORA DE CELULARES' -63 1 26 $true)
    [void](P $doc 'GRUPO 09 · NRC 36884' -1 1 13 $true)
    [void](P $doc '' -1 1 12)
    [void](P $doc $title -2 1 20 $true)
    [void](P $doc $subtitle -1 1 13)
    [void](P $doc '' -1 1 10)
    [void](P $doc 'Protocolo: REST' -1 1 11)
    [void](P $doc 'Tecnologia: .NET 10 · C# 14' -1 1 11)
    [void](P $doc 'Base de datos: SQL Server 2025 Express' -1 1 11)
    [void](P $doc '26 de octubre de 2026' -1 1 10)
    $n = [int]$doc.Content.End - 1
    $doc.Range($n, $n).InsertBreak(7)
}

function New-Doc($word, [string]$path, [string]$title, [scriptblock]$build) {
    $doc = $word.Documents.Add()
    Setup-Word $doc
    try {
        & $build $doc
        try {
            $doc.BuiltInDocumentProperties.Item('Title').Value  = $title
            $doc.BuiltInDocumentProperties.Item('Author').Value = 'Grupo 09'
        } catch {}
        $doc.SaveAs2($path, 16)
    } finally {
        $doc.Close($false)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)
    }
}

# ── captura placeholder ───────────────────────────────────────────────────────
# Si no hay capturas reales, crea imagenes placeholder de texto
function Ensure-Capture([string]$path, [string]$label) {
    if (Test-Path -LiteralPath $path -PathType Leaf) { return }
    # Crea un placeholder PNG minimo usando .NET Drawing
    Add-Type -AssemblyName System.Drawing -ErrorAction SilentlyContinue
    try {
        $bmp  = [System.Drawing.Bitmap]::new(900, 500)
        $g    = [System.Drawing.Graphics]::FromImage($bmp)
        $g.Clear([System.Drawing.Color]::FromArgb(30, 30, 40))
        $font = [System.Drawing.Font]::new('Arial', 18, [System.Drawing.FontStyle]::Bold)
        $brush= [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(180, 210, 255))
        $g.DrawString("[CAPTURA: $label]", $font, $brush, [System.Drawing.PointF]::new(40, 200))
        $g.DrawString('Grupo 09 · NRC 36884 · Comercializadora Celulares', $font, $brush, [System.Drawing.PointF]::new(40, 260))
        $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        $g.Dispose(); $font.Dispose(); $brush.Dispose(); $bmp.Dispose()
        Write-Warning "Placeholder creado: $path"
    } catch {
        Write-Warning "No se pudo crear placeholder para $label; continua sin imagen."
    }
}

# ── ERS ───────────────────────────────────────────────────────────────────────
function Build-ERS($doc) {
    Cover $doc 'ESPECIFICACION DE REQUISITOS DE SOFTWARE' 'Comercializadora de Celulares · REST · .NET'

    [void](P $doc '1. Introduccion' -2 0 15 $true)
    [void](P $doc 'El presente documento especifica los requisitos funcionales y no funcionales del sistema de Comercializadora de Celulares, desarrollado con arquitectura REST sobre .NET 10 y base de datos SQL Server 2025 Express. El sistema permite gestionar el catalogo de celulares, registrar ventas en efectivo y a credito directo mediante integracion con BanQuito, y consultar facturas y tablas de amortizacion.')

    [void](P $doc '2. Alcance' -2 0 15 $true)
    [void](P $doc 'La comercializadora expone una API REST consumida por cuatro clientes: consola (.NET), escritorio (WPF), movil (MAUI Android) y web (ASP.NET Core MVC). La evaluacion de credito y amortizacion se delega al servicio externo BanQuito (puerto 19101). La comercializadora utiliza SQL Server Express con la base ComercializadoraCelulares y no replica datos bancarios.')

    [void](P $doc '3. Definiciones y abreviaturas' -2 0 15 $true)
    [void](T $doc @('Termino','Definicion') @(
        @('REST','Estilo arquitectonico HTTP para intercambio de recursos JSON.'),
        @('API','Interfaz de programacion de aplicaciones expuesta en http://127.0.0.1:19102.'),
        @('BanQuito','Servicio bancario externo en http://127.0.0.1:19101 que evalua credito.'),
        @('CELULAR','Entidad de catalogo con precio lista y estado activo/inactivo.'),
        @('FACTURA','Registro de venta en efectivo o credito directo de un celular.'),
        @('ID_OPERACION','UUID idempotente que evita duplicacion de facturas.'),
        @('MVC','Patron vista–controlador–modelo aplicado en los cuatro clientes.'),
        @('MAUI','Multi-platform App UI de .NET para el cliente movil Android.')
    ) @(130, 347))

    [void](P $doc '4. Requisitos funcionales' -2 0 15 $true)
    [void](T $doc @('ID','Requisito','Descripcion','Prioridad') @(
        @('RF-01','Consultar catalogo','GET /api/celulares devuelve celulares activos con nombre y precio lista.','Alta'),
        @('RF-02','Crear celular','POST /api/celulares registra nuevo celular con nombre y precio.','Alta'),
        @('RF-03','Editar celular','PUT /api/celulares/{id} actualiza nombre y precio de un celular existente.','Alta'),
        @('RF-04','Desactivar celular','DELETE /api/celulares/{id} pone ACTIVO = 0 sin eliminar el registro.','Alta'),
        @('RF-05','Venta en efectivo','POST /api/facturas con FORMA_PAGO=EFECTIVO aplica 42% de descuento al precio lista.','Alta'),
        @('RF-06','Venta a credito','POST /api/facturas con FORMA_PAGO=CREDITO_DIRECTO consulta elegibilidad y solicita credito a BanQuito.','Alta'),
        @('RF-07','Consultar factura','GET /api/facturas/{id} retorna datos de la factura y estado de credito.','Media'),
        @('RF-08','Consultar amortizacion','GET /api/facturas/{id}/amortizacion retorna cuotas del credito aprobado.','Media'),
        @('RF-09','Idempotencia','Reintentar la misma ID_OPERACION devuelve la factura existente sin duplicar.','Alta'),
        @('RF-10','Separacion MVC','Cada cliente implementa vistas, controladores y servicios independientes.','Alta')
    ) @(40, 110, 245, 60))

    [void](P $doc '5. Requisitos no funcionales' -2 0 15 $true)
    [void](T $doc @('ID','Requisito','Descripcion') @(
        @('RNF-01','Disponibilidad','La API debe responder en menos de 500 ms bajo carga normal.'),
        @('RNF-02','Seguridad','No se exponen contrasenas ni cadenas de conexion en respuestas ni capturas.'),
        @('RNF-03','Mantenibilidad','El codigo sigue MVC con carpetas definidas; los contratos se centralizan en Celulares.Contratos.'),
        @('RNF-04','Portabilidad','Los clientes consola y web son multiplataforma; escritorio requiere Windows; movil requiere Android 12+.'),
        @('RNF-05','Trazabilidad','Cada factura conserva ID_OPERACION para auditoria e idempotencia.')
    ) @(50, 120, 307))

    [void](P $doc '6. Casos de uso' -2 0 15 $true)
    [void](P $doc 'El actor principal es el Usuario (administrador o vendedor). Interactua con: Gestionar catalogo (RF-01 a RF-04), Registrar venta (RF-05 y RF-06), Consultar factura (RF-07) y Consultar amortizacion (RF-08). La venta a credito incluye la interaccion con el sistema externo BanQuito.')
    $cuImg = Join-Path $UmlDir 'PowerDesigner\GR09_Celular_CasosUso.png'
    if (-not (Test-Path -LiteralPath $cuImg -PathType Leaf)) {
        $cuImg = Join-Path $CaptDir 'CasosUso.png'
        Ensure-Capture $cuImg 'Diagrama de Casos de Uso'
    }
    [void](P $doc 'Figura 1. Diagrama de casos de uso.' -1 1 9)
    Pic $doc $cuImg

    [void](P $doc '7. Diagrama de secuencia: venta' -2 0 15 $true)
    [void](P $doc 'La secuencia de venta inicia en el cliente; el controlador envia HTTP JSON a la API; la API delega al servicio de facturas; si es credito se consulta BanQuito; se persiste la factura en SQL Server y se retorna el resultado al cliente.')
    $seqImg = Join-Path $UmlDir 'PowerDesigner\GR09_Celular_Secuencia_Venta.png'
    if (-not (Test-Path -LiteralPath $seqImg -PathType Leaf)) {
        $seqImg = Join-Path $CaptDir 'Secuencia_Venta.png'
        Ensure-Capture $seqImg 'Diagrama de Secuencia - Venta'
    }
    [void](P $doc 'Figura 2. Diagrama de secuencia de venta.' -1 1 9)
    Pic $doc $seqImg

    [void](P $doc '8. Diagrama de clases' -2 0 15 $true)
    [void](P $doc 'Las clases principales son Celular, Factura, ServicioCatalogo, ServicioFacturas y ServicioBanQuito. Los controladores REST delegan en los servicios. La libreria Celulares.Contratos define los DTOs compartidos por cliente y servidor.')
    $clsImg = Join-Path $UmlDir 'PowerDesigner\GR09_Celular_Clases.png'
    if (-not (Test-Path -LiteralPath $clsImg -PathType Leaf)) {
        $clsImg = Join-Path $CaptDir 'Clases.png'
        Ensure-Capture $clsImg 'Diagrama de Clases'
    }
    [void](P $doc 'Figura 3. Diagrama de clases.' -1 1 9)
    Pic $doc $clsImg

    [void](P $doc '9. Modelo entidad-relacion' -2 0 15 $true)
    [void](P $doc 'La base ComercializadoraCelulares tiene dos tablas: CELULAR (catalogo) y FACTURA (ventas). La relacion es uno a muchos. COD_CLIENTE_BANCO y COD_CREDITO son referencias remotas al sistema BanQuito; no son claves foraneas locales.')
    $merImg = Join-Path $MerDir 'PowerDesigner\GR09_Celular_MER_Fisico.png'
    if (-not (Test-Path -LiteralPath $merImg -PathType Leaf)) {
        $merImg = Join-Path $CaptDir 'MER_Fisico.png'
        Ensure-Capture $merImg 'MER Fisico SQL Server'
    }
    [void](P $doc 'Figura 4. Modelo entidad-relacion fisico.' -1 1 9)
    Pic $doc $merImg

    [void](P $doc '10. Glosario de atributos clave' -2 0 15 $true)
    [void](T $doc @('Tabla','Columna','Tipo','Descripcion') @(
        @('CELULAR','ID_CELULAR','int identity','Clave primaria autoincremental.'),
        @('CELULAR','NOMBRE','nvarchar(100)','Nombre del modelo de celular.'),
        @('CELULAR','PRECIO','numeric(10,2)','Precio de lista mayor que cero.'),
        @('CELULAR','ACTIVO','bit','Estado: 1 activo, 0 inactivo.'),
        @('FACTURA','ID_FACTURA','int identity','Clave primaria autoincremental.'),
        @('FACTURA','ID_OPERACION','uniqueidentifier','UUID unico para idempotencia.'),
        @('FACTURA','ID_CELULAR','int FK','Referencia a CELULAR.'),
        @('FACTURA','FORMA_PAGO','varchar(20)','EFECTIVO o CREDITO_DIRECTO.'),
        @('FACTURA','TOTAL','numeric(10,2)','Monto cobrado al cliente.'),
        @('FACTURA','ESTADO','varchar(12)','PENDIENTE, APROBADA o RECHAZADA.')
    ) @(65, 110, 120, 182))
}

# ── MANUAL TECNICO ────────────────────────────────────────────────────────────
function Build-Manual($doc) {
    Cover $doc 'MANUAL TECNICO' 'Comercializadora de Celulares · REST · .NET 10'

    [void](P $doc '1. Proposito y alcance' -2 0 15 $true)
    [void](P $doc 'Describe la arquitectura, configuracion, ejecucion y mantenimiento del sistema de Comercializadora de Celulares. Permite gestionar el catalogo de celulares, registrar ventas en efectivo y a credito, consultar facturas y tablas de amortizacion. Los cuatro clientes consumen la API REST y no abren conexiones directas a la base de datos.')

    [void](P $doc '2. Arquitectura y tecnologias' -2 0 15 $true)
    [void](P $doc 'Servidor: .NET 10, ASP.NET Core REST. Persistencia: SQL Server 2025 Express (SQLEXPRESS). Clientes .NET: consola (Celulares.Consola), escritorio WPF (Celulares.Escritorio), movil MAUI Android (Celulares.Movil) y web MVC (Celulares.Web). La libreria compartida Celulares.Cliente contiene los servicios HTTP y los DTOs de transporte.')
    [void](T $doc @('Capa','Responsabilidad') @(
        @('Vista','Captura datos de usuario y muestra resultados y errores.'),
        @('Controlador','Valida interaccion, administra navegacion y coordina servicios.'),
        @('Modelo','Representa celulares, facturas, operaciones y credito.'),
        @('Cliente de servicio','Serializa solicitudes y procesa respuestas HTTP/JSON.'),
        @('Servicio y repositorio','Aplica reglas de negocio y accede a SQL Server.')
    ) @(112, 365))
    [void](P $doc 'Los cuatro clientes comparten Celulares.Cliente (servicios y contratos HTTP). La comercializadora no comparte ensamblados con BanQuito; la comunicacion es unicamente HTTP.')

    [void](P $doc '3. Contrato REST de la comercializadora' -2 0 15 $true)
    [void](P $doc 'La API REST intercambia JSON. La transferencia de credito envia ID_OPERACION como identificador idempotente. Las respuestas distinguen exito, error de validacion y error del servicio externo.')
    [void](T $doc @('Metodo y recurso','Descripcion') @(
        @('GET /api/celulares','Retorna catalogo activo con nombre y precio lista.'),
        @('POST /api/celulares','Registra nuevo celular (nombre, precio).'),
        @('PUT /api/celulares/{id}','Actualiza nombre y precio de un celular existente.'),
        @('DELETE /api/celulares/{id}','Desactiva un celular (ACTIVO=0).'),
        @('POST /api/facturas','Registra venta en efectivo o a credito directo.'),
        @('GET /api/facturas/{id}','Consulta datos de una factura.'),
        @('GET /api/facturas/{id}/amortizacion','Retorna tabla de cuotas del credito aprobado.')
    ) @(245, 232))
    [void](P $doc 'API de tienda: http://127.0.0.1:19102. API BanQuito (externo): http://127.0.0.1:19101. Para emulador Android se usa http://10.0.2.2:19102.')

    [void](P $doc '4. Reglas de negocio' -2 0 15 $true)
    foreach ($line in @(
        '• Venta en efectivo: descuento del 42 % sobre el precio de lista.',
        '• Venta a credito: precio neto entre 1 y monto maximo autorizado por BanQuito; plazo entre 3 y 18 meses; tasa anual 16,5 % con cuota fija y ajuste a saldo cero en ultima cuota.',
        '• El banco exige cliente existente, deposito en el ultimo mes y ausencia de credito activo.',
        '• Si el genero es masculino, debe tener al menos 25 anos cumplidos al momento de la evaluacion.',
        '• Un rechazo o indisponibilidad de BanQuito no confirma la venta a credito.',
        '• ID_OPERACION unico: reintentar la misma operacion devuelve la factura existente sin duplicar.'
    )) { [void](P $doc $line) }

    [void](P $doc '5. Persistencia y MER' -2 0 15 $true)
    [void](P $doc 'Base de datos local: ComercializadoraCelulares en SQL Server 2025 Express (SQLEXPRESS). Dos tablas: CELULAR y FACTURA. Los datos bancarios (COD_CLIENTE_BANCO, COD_CREDITO) son referencias remotas y no claves foraneas locales. BanQuitoCore pertenece al proyecto bancario.')
    $merImg = Join-Path $MerDir 'PowerDesigner\GR09_Celular_MER_Fisico.png'
    if (-not (Test-Path -LiteralPath $merImg -PathType Leaf)) { $merImg = Join-Path $CaptDir 'MER_Fisico.png'; Ensure-Capture $merImg 'MER Fisico SQL Server' }
    [void](P $doc 'Figura 1. MER fisico de ComercializadoraCelulares en SQL Server.' -1 1 9)
    Pic $doc $merImg 400

    $merCImg = Join-Path $MerDir 'PowerDesigner\GR09_Celular_MER_Conceptual.png'
    if (-not (Test-Path -LiteralPath $merCImg -PathType Leaf)) { $merCImg = Join-Path $CaptDir 'MER_Conceptual.png'; Ensure-Capture $merCImg 'MER Conceptual' }
    [void](P $doc 'Figura 2. MER conceptual.' -1 1 9)
    Pic $doc $merCImg 400

    [void](P $doc '6. Configuracion e inicializacion' -2 0 15 $true)
    [void](P $doc 'Requisitos: .NET 10 SDK, SQL Server 2025 Express (SQLEXPRESS) y Android SDK 36 (para cliente movil). Los paquetes NuGet se almacenan en D:\NuGet\packages.')
    [void](P $doc 'Pasos de configuracion:')
    foreach ($step in @(
        '1. Instalar SQL Server 2025 Express ejecutando: & ".\03. BDD\InstalarSQL2025.ps1" -Media "D:\Downloads\sqlserver2025\engine\SETUP.EXE"',
        '2. Inicializar la base de la comercializadora: dotnet run --project "04. SERVIDOR\Administracion\Administracion.csproj" -- --aplicar "03. BDD\01_CrearBases.sql" "03. BDD\02_DatosPrueba.sql"',
        '3. Inicializar BanQuitoCore (proyecto bancario): dotnet run --project "..\TG.1\1.4. PAO...\01. SERVIDOR\BanQuito.Administracion\BanQuito.Administracion.csproj" -- --aplicar ...',
        '4. Iniciar API de tienda (puerto 19102): dotnet run --project "04. SERVIDOR\Comercializadora.Api\Comercializadora.Api.csproj"',
        '5. Iniciar API BanQuito (puerto 19101): dotnet run --project "..\TG.1\1.4...\BanQuito.Api\BanQuito.Api.csproj"',
        '6. Iniciar clientes segun se necesite (ver seccion 7).'
    )) { [void](P $doc $step) }

    [void](P $doc '7. Captura del entorno de desarrollo (NetBeans / Visual Studio)' -2 0 15 $true)
    [void](P $doc 'La solucion se abre en Visual Studio 2022 o Rider. La estructura de proyectos en el Solution Explorer muestra Comercializadora.Api, Celulares.Contratos, Comercializadora.Dominio, Celulares.Cliente, Celulares.Consola, Celulares.Escritorio, Celulares.Movil y Celulares.Web.')

    $vs1 = Join-Path $CaptDir 'IDE_SolutionExplorer.png'
    Ensure-Capture $vs1 'Visual Studio - Solution Explorer'
    [void](P $doc 'Figura 3. Solucion en Visual Studio / IDE.' -1 1 9)
    Pic $doc $vs1 430

    $vs2 = Join-Path $CaptDir 'IDE_ApiEjecucion.png'
    Ensure-Capture $vs2 'API Comercializadora ejecutandose'
    [void](P $doc 'Figura 4. API Comercializadora ejecutandose en el puerto 19102.' -1 1 9)
    Pic $doc $vs2 430

    $vs3 = Join-Path $CaptDir 'IDE_BDDSqlServer.png'
    Ensure-Capture $vs3 'SQL Server - Base ComercializadoraCelulares'
    [void](P $doc 'Figura 5. Base de datos ComercializadoraCelulares en SQL Server 2025 Express.' -1 1 9)
    Pic $doc $vs3 430

    [void](P $doc '8. Iniciar los cuatro clientes' -2 0 15 $true)
    [void](T $doc @('Cliente','Comando dotnet run','URL / Notas') @(
        @('Consola','dotnet run --project "04. CLICON\Celulares.Consola\Celulares.Consola.csproj"','Terminal interactiva.'),
        @('Escritorio WPF','dotnet run --project "04. CLIESC\Celulares.Escritorio\Celulares.Escritorio.csproj"','Requiere Windows.'),
        @('Web MVC','dotnet run --project "04. CLIWEB\Celulares.Web\Celulares.Web.csproj"','http://127.0.0.1:19103'),
        @('Movil MAUI','dotnet build ... -t:Run -p:AndroidSdkDirectory="D:\tools\android-sdk"','Emulador GR10_Pixel_35.')
    ) @(95, 245, 137))
    [void](P $doc 'El emulador Android usa 10.0.2.2:19102. Para telefono fisico, iniciar la API con --urls http://0.0.0.0:19102 y permitir el puerto en la red local.')

    $cli1 = Join-Path $CaptDir 'Cliente_Consola.png'
    Ensure-Capture $cli1 'Cliente Consola - Menu principal'
    [void](P $doc 'Figura 6. Cliente consola: menu principal.' -1 1 9)
    Pic $doc $cli1 430

    $cli2 = Join-Path $CaptDir 'Cliente_WPF.png'
    Ensure-Capture $cli2 'Cliente WPF - Pantalla principal'
    [void](P $doc 'Figura 7. Cliente escritorio WPF: pantalla principal.' -1 1 9)
    Pic $doc $cli2 430

    $cli3 = Join-Path $CaptDir 'Cliente_Web.png'
    Ensure-Capture $cli3 'Cliente Web MVC - Catalogo'
    [void](P $doc 'Figura 8. Cliente web MVC: catalogo de celulares.' -1 1 9)
    Pic $doc $cli3 430

    $cli4 = Join-Path $CaptDir 'Cliente_MAUI.png'
    Ensure-Capture $cli4 'Cliente MAUI Android - Catalogo'
    [void](P $doc 'Figura 9. Cliente MAUI Android: catalogo en emulador.' -1 1 9)
    Pic $doc $cli4 430

    [void](P $doc '9. Diagrama de componentes y arquitectura' -2 0 15 $true)
    $archImg = Join-Path $UmlDir 'PowerDesigner\GR09_Celular_Arquitectura.png'
    if (-not (Test-Path -LiteralPath $archImg -PathType Leaf)) { $archImg = Join-Path $CaptDir 'Arquitectura.png'; Ensure-Capture $archImg 'Diagrama de Arquitectura' }
    [void](P $doc 'Figura 10. Arquitectura del sistema.' -1 1 9)
    Pic $doc $archImg 430

    [void](P $doc '10. Diagnostico' -2 0 15 $true)
    [void](T $doc @('Sintoma','Verificacion') @(
        @('Conexion rechazada (tienda)','Compruebe que la API escucha en 127.0.0.1:19102 y que no hay firewall bloqueando.'),
        @('Conexion rechazada (BanQuito)','Compruebe que la API bancaria escucha en 127.0.0.1:19101.'),
        @('Error de credito rechazado','Revise elegibilidad del cliente: deposito reciente, sin credito activo, edad si es masculino.'),
        @('Factura duplicada','Usar la misma ID_OPERACION devuelve la factura existente; no es un error.'),
        @('Error de base de datos','Revise cadena de conexion, esquema creado y permisos en SQLEXPRESS.'),
        @('Emulador no conecta','Usar 10.0.2.2 en lugar de localhost desde el emulador Android.')
    ) @(150, 327))
    [void](P $doc 'No registre contrasenas, tokens ni cadenas de conexion. Registre hora, codigo de respuesta e identificador de operacion.')
}

# ── eliminar .md sobrantes ────────────────────────────────────────────────────
function Remove-MdSurplus {
    $mdToDelete = @(
        (Join-Path $Docs 'ManualTecnico.md'),
        (Join-Path $Docs 'Arquitectura.md'),
        (Join-Path $Docs 'AVANCE.md'),
        (Join-Path $Docs 'PLAN.md'),
        (Join-Path $Docs 'VERIFICACION_EXAMEN.md'),
        (Join-Path $Docs 'README.md'),
        (Join-Path $Docs 'Diagramas.md'),
        (Join-Path $Docs 'Requisitos.md'),
        (Join-Path $UmlDir 'Diagramas.md'),
        (Join-Path $MerDir 'Diagramas.md'),
        (Join-Path $MerDir 'ModeloDatos.md')
    )
    foreach ($f in $mdToDelete) {
        if (Test-Path -LiteralPath $f -PathType Leaf) {
            Remove-Item -LiteralPath $f -Force
            Write-Output "Eliminado: $f"
        }
    }
    # Eliminar README.md de subcarpetas de 01. UML y 02. MER (solo los sueltos)
    foreach ($dir in @($UmlDir, $MerDir,
        (Join-Path $UmlDir 'PowerDesigner'),
        (Join-Path $MerDir 'PowerDesigner'),
        (Join-Path $MerDir '01. CONCEPTUAL'),
        (Join-Path $MerDir '02. LOGICO'),
        (Join-Path $MerDir '03. FISICO'))) {
        $readme = Join-Path $dir 'README.md'
        if (Test-Path -LiteralPath $readme -PathType Leaf) {
            Remove-Item -LiteralPath $readme -Force
            Write-Output "Eliminado: $readme"
        }
    }
}

# ── crear estructura faltante de UML (subcarpetas del 01 al 05) ───────────────
function Ensure-UmlStructure {
    $subs = @('01. ERS', '02. ECUD', '03. DIAGRAMAS UML')
    foreach ($s in $subs) {
        New-Item -ItemType Directory -Force -Path (Join-Path $UmlDir $s) | Out-Null
    }
    $diagSubs = @('01_CASOS_DE_USO','02_ACTIVIDAD','03_SECUENCIA','04_CLASES','05_ARQUITECTURA')
    foreach ($ds in $diagSubs) {
        New-Item -ItemType Directory -Force -Path (Join-Path $UmlDir "03. DIAGRAMAS UML\$ds") | Out-Null
    }
    $merSubs = @('01. CONCEPTUAL','02. LOGICO','03. FISICO','PowerDesigner')
    foreach ($ms in $merSubs) {
        New-Item -ItemType Directory -Force -Path (Join-Path $MerDir $ms) | Out-Null
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $UmlDir 'PowerDesigner') | Out-Null
}

# ── ejecucion ─────────────────────────────────────────────────────────────────
Write-Output '-- Asegurando estructura de carpetas --'
Ensure-UmlStructure

Write-Output '-- Eliminando archivos .md sobrantes --'
Remove-MdSurplus

$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false; $word.DisplayAlerts = 0

    # ERS Completo formato IEEE 830 (identico a GR05, GR69 y plantilla oficial ESPE)
    $ersScript = Join-Path $Raiz "GenerarErsCompletoCelularGR09.ps1"
    if (Test-Path -LiteralPath $ersScript) {
        Write-Output "Generando ERS completo IEEE 830 desde plantilla oficial..."
        & powershell -ExecutionPolicy Bypass -File $ersScript -Raiz $Raiz
    } else {
        $ersPath = Join-Path $ErsDir 'ERS_CELULAR_RESTFUL_DOTNET_GR09.docx'
        Write-Output "Generando ERS: $ersPath"
        New-Doc $word $ersPath 'ERS Comercializadora de Celulares GR09' { param($d) Build-ERS $d }
        Write-Output 'ERS generado.'
    }

    # MANUAL TECNICO
    $manualPath = Join-Path $ManualDir 'MANUAL_TECNICO_CELULAR_RESTFUL_DOTNET_GR09.docx'
    Write-Output "Generando Manual Tecnico: $manualPath"
    New-Doc $word $manualPath 'Manual Tecnico Comercializadora de Celulares GR09' { param($d) Build-Manual $d }
    Write-Output 'Manual tecnico generado.'

} finally {
    if ($word) {
        try { $word.Quit() } catch {}
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}

Write-Output ''
Write-Output '=== Documentos Word generados. ==='
Write-Output 'Para la PRESENTACION (.pptx) ejecute:'
Write-Output "  python GenerarPresentacionCelularGR09.py --root `"$Raiz`""
Write-Output ''
Write-Output 'Para los diagramas Power Designer, consulte AGENTS.md en esta carpeta.'

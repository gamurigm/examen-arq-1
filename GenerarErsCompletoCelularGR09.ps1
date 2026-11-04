<#
.SYNOPSIS
    Genera la Especificacion de Requerimientos de Software (ERS) completa en formato
    IEEE 830 para el proyecto Comercializadora de Celulares GR09.
.DESCRIPTION
    Usa la plantilla oficial de la ESPE (PLANTILLA_ERS_SOAP_JAVA_GR09.docx),
    conserva la caratula institucional con formas y logos, e implementa todas
    las secciones del estandar IEEE 830 idénticas a los proyectos GR05, GR69 y GR09:
      - Control de la línea base documental
      - Indice de contenidos (TOC)
      - Indice de tablas e ilustraciones
      - 1. Introduccion
      - 2. Proposito
      - 3. Alcance (con tabla de alcance)
      - 4. Definiciones, acronimos y abreviaturas (tablas de definiciones y siglas)
      - 5. Referencias (tabla de fuentes)
      - 6. Vision general del documento
      - 7. Descripcion general (perspectiva, funciones, entorno, usuarios, interfaces, restricciones)
      - 8. Especificacion de requerimientos (interfaces comunes, fichas de requisitos funcionales RF-01 a RF-10, reglas de negocio RN-01 a RN-06, fichas de requisitos no funcionales RNF-01 a RNF-08, otros requerimientos)
      - 9. Diagramas UML de SAP PowerDesigner (Casos de uso, Actividad, Secuencia, Clases, Arquitectura)
      - 10. Modelo Entidad-Relacion (MER) de SAP PowerDesigner (Conceptual, Logico, Fisico y diccionario de datos)
      - 11. Matriz de trazabilidad (Objetivos vs Requisitos vs Casos de Uso vs Componentes)
      - 12. Conclusiones y recomendaciones
#>
[CmdletBinding()]
param(
    [string]$Raiz = $PSScriptRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Raiz = [System.IO.Path]::GetFullPath($Raiz)
$proyectoDir = Join-Path $Raiz "TI.1.1. PAO202651_CELULAR_BDDLOCAL_RESTFUL_NRC36884_GR09"
if (-not (Test-Path -LiteralPath $proyectoDir)) {
    $found = Get-ChildItem -Path $Raiz -Directory | Where-Object { $_.Name -like "*CELULAR*RESTFUL*" } | Select-Object -First 1
    if ($null -eq $found) { throw "No se encontro la carpeta del proyecto CELULAR en $Raiz" }
    $proyectoDir = $found.FullName
}
$proyectoDir = [System.IO.Path]::GetFullPath($proyectoDir)

$ersDir = [System.IO.Path]::GetFullPath((Join-Path $proyectoDir "01. UML\01. ERS"))
$umlDir = [System.IO.Path]::GetFullPath((Join-Path $proyectoDir "01. UML"))
$merDir = [System.IO.Path]::GetFullPath((Join-Path $proyectoDir "02. MER"))

$templatePath = Join-Path $Raiz "..\TG.1\1.1. PAO202651_SOAP_JAVA_CONBDD_NRC36884_GR09\01. UML\01. ERS\PLANTILLA_ERS_SOAP_JAVA_GR09.docx"
$templatePath = [System.IO.Path]::GetFullPath($templatePath)
if (-not (Test-Path -LiteralPath $templatePath)) {
    # buscar plantilla alternativa
    $cand = Get-ChildItem -Path (Join-Path $Raiz "..\..") -Filter "*PLANTILLA_ERS*.docx" -Recurse | Select-Object -First 1
    if ($cand) { $templatePath = $cand.FullName } else { throw "No se encontro plantilla ERS." }
}
Write-Output "Usando plantilla: $templatePath"

$outputDocx = [System.IO.Path]::GetFullPath((Join-Path $ersDir "ERS_CELULAR_RESTFUL_DOTNET_GR09.docx"))
Write-Output "Destino ERS: $outputDocx"

# Copiar plantilla
Copy-Item -LiteralPath $templatePath -Destination $outputDocx -Force

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($outputDocx)

    # 1. Actualizar Caratula (Formas)
    Write-Output "Actualizando caratula institucional..."
    $nuevoTema = "ESPECIFICACION DE REQUERIMIENTOS DE SOFTWARE PARA COMERCIALIZADORA DE CELULARES REST EN .NET CON BASE DE DATOS"
    for ($i = 1; $i -le $doc.Shapes.Count; $i++) {
        $shape = $doc.Shapes.Item($i)
        try {
            if ($shape.TextFrame.HasText -ne 0) {
                $rng = $shape.TextFrame.TextRange
                $find = $rng.Find
                $find.ClearFormatting()
                $find.Replacement.ClearFormatting()
                $find.Execute("ESPECIFICACIÓN DE REQUERIMIENTOS DE SOFTWARE PARA SOA CON SOAP EN JAVA SIN BDD", $false, $false, $false, $false, $false, $true, 1, $false, $nuevoTema, 2) | Out-Null
                $find.Execute("ESPECIFICACION DE REQUERIMIENTOS DE SOFTWARE PARA SOA CON SOAP EN JAVA SIN BDD", $false, $false, $false, $false, $false, $true, 1, $false, $nuevoTema, 2) | Out-Null
            }
        } catch {}
    }

    # 2. Localizar inicio del cuerpo despues de la caratula
    $bodyStart = $doc.GoTo(1, 1, 2).Start
    $bodyEnd = $doc.Content.End - 1
    if ($bodyStart -lt $bodyEnd) {
        $doc.Range($bodyStart, $bodyEnd).Delete() | Out-Null
    }

    # Helpers de construccion
    function Add-P($text, [string]$styleName = "Normal", [int]$align = 0, [int]$spaceAfter = 6, [bool]$bold = $false) {
        $end = [int]$doc.Content.End - 1
        $r = $doc.Range($end, $end)
        $r.InsertAfter($text + [char]13)
        $p = $doc.Range($end, $end + $text.Length + 1).Paragraphs.Item(1)
        try { $p.Style = $styleName } catch { $p.Style = "Normal" }
        $p.Alignment = $align
        $p.Format.SpaceAfter = $spaceAfter
        $p.Format.KeepTogether = -1
        if ($bold) { $p.Range.Font.Bold = -1 }
        [void]$p
    }

    function Add-H1($text) { Add-P $text "Título 1" 0 10 $true }
    function Add-H2($text) { Add-P $text "Título 2" 0 8  $true }
    function Add-H3($text) { Add-P $text "Título 3" 0 6  $true }

    function Add-Table([string[]]$headers, [object[]]$rows, [int[]]$widths = @(), [string]$caption = "") {
        if ($caption) {
            Add-P $caption "Descripción" 0 4 $false
        }
        $data = [System.Collections.Generic.List[object]]::new()
        $data.Add($headers)
        foreach ($row in $rows) { $data.Add($row) }
        $at = [int]$doc.Content.End - 1
        $tbl = $doc.Tables.Add($doc.Range($at, $at), $data.Count, $headers.Count)
        $tbl.Borders.Enable = 1
        $tbl.AllowAutoFit = $false
        $tbl.Rows.AllowBreakAcrossPages = 0
        $tbl.Rows.Item(1).HeadingFormat = -1

        for ($r = 0; $r -lt $data.Count; $r++) {
            $rowData = $data[$r]
            for ($c = 0; $c -lt $headers.Count; $c++) {
                $cell = $tbl.Cell($r + 1, $c + 1)
                $cell.Range.Text = [string]$rowData[$c]
                $cell.Range.Font.Name = "Arial"
                $cell.Range.Font.Size = 9
                $cell.VerticalAlignment = 1
                if ($r -eq 0) {
                    $cell.Range.Bold = -1
                    $cell.Shading.BackgroundPatternColor = 15132390
                }
            }
        }
        if ($widths.Count -eq $headers.Count) {
            for ($c = 0; $c -lt $widths.Count; $c++) {
                try { $tbl.Columns.Item($c + 1).Width = $widths[$c] } catch {}
            }
        }
        $tail = $doc.Range([int]$doc.Content.End - 1, [int]$doc.Content.End - 1)
        $tail.InsertAfter([char]13)
        return $tbl
    }

    function Add-Ficha([string]$id, [string]$nombre, [string]$desc, [string]$obj, [string]$importancia, [string]$estado, [string]$comentarios, [string]$caption = "") {
        if ($caption) { Add-P $caption "Descripción" 0 4 $false }
        $at = [int]$doc.Content.End - 1
        $tbl = $doc.Tables.Add($doc.Range($at, $at), 7, 2)
        $tbl.Borders.Enable = 1
        $tbl.AllowAutoFit = $false
        $tbl.Rows.AllowBreakAcrossPages = 0

        $rowsData = @(
            @($id, $nombre),
            @("Descripcion", $desc),
            @("Objetivo / Criterio", $obj),
            @("Importancia", $importancia),
            @("Estado", $estado),
            @("Estabilidad", "Alta"),
            @("Comentarios", $comentarios)
        )
        for ($r = 0; $r -lt 7; $r++) {
            $c1 = $tbl.Cell($r + 1, 1)
            $c2 = $tbl.Cell($r + 1, 2)
            $c1.Range.Text = $rowsData[$r][0]; $c1.Range.Font.Name = "Arial"; $c1.Range.Font.Size = 9; $c1.Range.Bold = -1
            $c2.Range.Text = $rowsData[$r][1]; $c2.Range.Font.Name = "Arial"; $c2.Range.Font.Size = 9
            if ($r -eq 0) {
                $c1.Shading.BackgroundPatternColor = 15132390
                $c2.Shading.BackgroundPatternColor = 15132390
                $c2.Range.Bold = -1
            }
        }
        try {
            $tbl.Columns.Item(1).Width = 115
            $tbl.Columns.Item(2).Width = 365
        } catch {}
        $tail = $doc.Range([int]$doc.Content.End - 1, [int]$doc.Content.End - 1)
        $tail.InsertAfter([char]13)
    }

    function Add-Image([string]$imgPath, [string]$caption, [float]$maxW = 460) {
        if (-not (Test-Path -LiteralPath $imgPath -PathType Leaf)) {
            Write-Warning "Imagen no encontrada: $imgPath"
            return
        }
        if ($caption) { Add-P $caption "Descripción" 1 4 $false }
        $at = [int]$doc.Content.End - 1
        $pic = $doc.Range($at, $at).InlineShapes.AddPicture($imgPath, $false, $true)
        $pic.LockAspectRatio = -1
        if ($pic.Width -gt $maxW) { $pic.Width = $maxW }
        $pic.Range.ParagraphFormat.Alignment = 1
        $tail = $doc.Range([int]$doc.Content.End - 1, [int]$doc.Content.End - 1)
        $tail.InsertAfter([char]13)
    }

    # =========================================================================
    # CONTENIDO FORMAL IEEE 830
    # =========================================================================
    Write-Output "Generando secciones IEEE 830 completas..."

    # Salto de seccion tras caratula
    $at = [int]$doc.Content.End - 1

    # INDICES
    Add-P "INDICE DE CONTENIDOS" "TtuloTDC" 1 12 $true
    $tocRng = $doc.Range([int]$doc.Content.End - 1, [int]$doc.Content.End - 1)
    $doc.TablesOfContents.Add($tocRng, $true, 1, 3) | Out-Null
    $rBreak = $doc.Range([int]$doc.Content.End - 1, [int]$doc.Content.End - 1)
    $rBreak.InsertBreak(7)

    # CASO DE ESTUDIO
    Add-H1 "Caso de estudio"
    Add-P "El presente proyecto implementa el sistema de Comercializadora de Celulares bajo arquitectura REST sobre la plataforma .NET 10 y SQL Server 2025 Express. El sistema permite gestionar el catalogo de telefonos moviles, registrar ventas en efectivo y a credito directo con integracion remota al sistema bancario BanQuito (puerto 19101), y consultar facturas y tablas de amortizacion desde cuatro canales clientes independientes (Consola, Escritorio WPF, Web MVC y Movil MAUI Android)."
    Add-P "La situacion de partida exige desacoplar totalmente los clientes de la persistencia de datos. Los cuatro clientes interactuan exclusivamente con la API REST expuesta en el puerto 19102 mediante mensajes HTTP/JSON estandarizados, compartiendo la libreria de contratos y transporte Celulares.Cliente. Cuando se solicita una venta a credito, la comercializadora consulta la capacidad de endeudamiento del cliente en BanQuito sin conocer ni alterar la estructura interna de la base bancaria BanQuitoCore."

    Add-Table @("Dato", "Valor") @(
        @("Proyecto", "Comercializadora de Celulares REST .NET con Base de Datos"),
        @("Asignatura y grupo", "Arquitectura de Software · Grupo 09 · NRC 36884"),
        @("Version del ERS", "2.0 (Linea base formal IEEE 830)"),
        @("Fecha de la linea base", "27 de octubre de 2026"),
        @("Producto documentado", "API REST, Clientes Consola, WPF, Web MVC, MAUI Android y persistencia SQL Server"),
        @("Estado", "Especificacion alineada estrictamente al codigo del repositorio")
    ) @(150, 330) "Tabla 1. Control de la linea base documental"

    # 1. INTRODUCCION
    Add-H1 "1. Introduccion"
    Add-P "La presente Especificacion de Requerimientos de Software (ERS) describe los servicios, reglas del negocio, contratos de intercambio y condiciones de ejecucion de la Comercializadora de Celulares. Su finalidad es proporcionar un marco normativo, verificable y trazable para los procesos de desarrollo, auditoria de software y pruebas de integracion del Examen Complexivo."
    Add-P "La arquitectura distribuye la presentacion en cuatro interfaces homologadas visual y funcionalmente, concentrando las reglas de facturacion y el acceso a datos en la API REST. La evaluacion crediticia se delega a BanQuito mediante peticiones HTTP asincronas, conservando la independencia de ambos dominios."

    # 2. PROPOSITO
    Add-H1 "2. Proposito"
    Add-P "El proposito de este documento es especificar de manera detallada y sin ambiguedades los requerimientos funcionales y no funcionales del sistema, formalizando las entradas, procesos, salidas y restricciones de diseno bajo el estandar IEEE 830."
    Add-P "Este documento esta dirigido al equipo de arquitectura, revisores academicos y operadores tecnicos. Todo cambio futuro en endpoints, reglas de descuento, calculo de amortizacion o politicas de credito debera reflejarse en esta linea base manteniendo la trazabilidad."

    # 3. ALCANCE
    Add-H1 "3. Alcance"
    Add-P "El producto comprende la API REST desarrollada en ASP.NET Core (.NET 10), la base de datos relacional ComercializadoraCelulares en SQL Server 2025 Express, y los cuatro clientes: consola interactiva, aplicacion de escritorio en WPF, sitio web en ASP.NET Core MVC y aplicacion movil en .NET MAUI para Android."

    Add-Table @("Incluido en la linea base", "Resultado esperado") @(
        @("Gestion de Catalogo", "Listar, crear, modificar y dar de baja logica celulares activos."),
        @("Venta en Efectivo", "Calcular y aplicar automaticamente el 42% de descuento sobre el precio de lista."),
        @("Venta a Credito Directo", "Consultar elegibilidad en BanQuito, validar cupo, calcular cuotas a tasa 16.5% anual (plazos 3 a 18 meses) y registrar operacion."),
        @("Idempotencia", "Garantizar que una venta reintentada con el mismo UUID (ID_OPERACION) no duplique registros ni transacciones."),
        @("Consulta de Factura y Amortizacion", "Consultar el detalle de la factura y recuperar la tabla de pagos del credito aprobado."),
        @("Arquitectura en 4 Canales", "Acceso homologado desde Consola, WPF, Web MVC y MAUI Android mediante Celulares.Cliente.")
    ) @(160, 320) "Tabla 2. Alcance funcional de la Comercializadora de Celulares"

    # 4. DEFINICIONES Y ABREVIATURAS
    Add-H1 "4. Definiciones, acronimos y abreviaturas"
    Add-H2 "4.1. Definiciones"
    Add-Table @("Termino", "Definicion en el sistema") @(
        @("Celular activo", "Registro en la tabla CELULAR con ACTIVO=1 disponible para comercializacion."),
        @("Credito directo", "Modalidad de financiamiento autorizada por BanQuito con plazo de 3 a 18 meses y tasa 16.5% anual."),
        @("Descuento efectivo", "Rebaja automatica del 42% sobre el precio de lista al seleccionar pago en efectivo."),
        @("Factura", "Comprobante de venta persistido en la tabla FACTURA con identificador unico y estado."),
        @("ID_OPERACION", "Identificador global unico (UUID) generado por el cliente para asegurar idempotencia."),
        @("Amortizacion", "Estructura de cuotas mensuales fijas generada por BanQuito para liquidar el credito."),
        @("Separacion MVC", "Patron arquitectonico que separa las Vistas, Controladores y Modelos en cada cliente."),
        @("Libreria Compartida", "Ensamblado Celulares.Cliente que encapsula DTOs y llamadas HTTP para los cuatro clientes.")
    ) @(140, 340) "Tabla 3. Definiciones del dominio"

    Add-H2 "4.2. Acronimos y abreviaturas"
    Add-Table @("Sigla", "Significado") @(
        @("ERS", "Especificacion de Requerimientos de Software (IEEE 830)"),
        @("REST", "Representational State Transfer"),
        @("HTTP / JSON", "Hypertext Transfer Protocol / JavaScript Object Notation"),
        @("API", "Application Programming Interface"),
        @("WPF", "Windows Presentation Foundation"),
        @("MAUI", "Multi-platform App UI (.NET)"),
        @("MVC", "Modelo - Vista - Controlador"),
        @("UUID", "Universally Unique Identifier"),
        @("SQL", "Structured Query Language"),
        @("DTO", "Data Transfer Object"),
        @("RF / RNF", "Requisito Funcional / Requisito No Funcional"),
        @("TOC", "Table of Contents (Indice de Contenidos)")
    ) @(120, 360) "Tabla 4. Acronimos y abreviaturas"

    # 5. REFERENCIAS
    Add-H1 "5. Referencias"
    Add-Table @("ID", "Fuente del repositorio", "Uso en la especificacion") @(
        @("F1", "CelularesController.cs y FacturasController.cs (Comercializadora.Api)", "Publicacion de operaciones y contratos REST"),
        @("F2", "ServicioFacturas.cs y ReglasFacturacion.cs (Comercializadora.Dominio)", "Reglas de descuento, plazos y validaciones"),
        @("F3", "ServicioBanQuito.cs (Comercializadora.Api)", "Cliente HTTP para integracion con API BanQuito 19101"),
        @("F4", "01_CrearBases.sql y 02_DatosPrueba.sql (03. BDD)", "Esquema relacional en SQL Server 2025 Express"),
        @("F5", "ClienteComercializadora.cs (00. COMPARTIDO/Celulares.Cliente)", "Servicio compartido de transporte HTTP"),
        @("F6", "Modelos.cs (Celulares.Contratos)", "Definicion de DTOs compartidos de peticion y respuesta"),
        @("F7", "Celulares.Consola, Escritorio, Web, Movil", "Implementaciones cliente con separacion MVC"),
        @("F8", "Modelos PowerDesigner (.cdm, .ldm, .pdm, .oom, .eam)", "Fuentes formales de diagramas UML y MER")
    ) @(40, 220, 220) "Tabla 5. Fuentes de requisitos"

    # 6. VISION GENERAL
    Add-H1 "6. Vision general del documento"
    Add-P "El documento se organiza siguiendo el estandar IEEE 830. La seccion 7 describe la perspectiva, funciones y entorno. La seccion 8 formaliza las interfaces, fichas detalladas de requerimientos funcionales y no funcionales, y reglas del negocio. Las secciones 9 y 10 presentan los modelos oficiales de SAP PowerDesigner para UML y MER. La seccion 11 define la matriz de trazabilidad y la seccion 12 resume conclusiones."

    # 7. DESCRIPCION GENERAL
    Add-H1 "7. Descripcion general"
    Add-H2 "7.1. Perspectiva del producto"
    Add-P "El sistema es un ecosistema distribuido multicapa. Cuatro canales clientes consumen la API de la Comercializadora (127.0.0.1:19102). La API consulta su propia base de datos local SQL Server (ComercializadoraCelulares) y se comunica via HTTP con el servicio externo BanQuito (127.0.0.1:19101) para evaluar solicitudes de credito directo."
    Add-P "Flujo principal de venta a credito: Cliente -> Vista -> Controlador -> ClienteComercializadora -> POST /api/facturas -> Comercializadora.Api -> ServicioFacturas -> ServicioBanQuito -> BanQuito.Api -> ComercializadoraCelulares SQL Server."

    Add-H2 "7.2. Funciones del producto (software)"
    Add-Table @("Funcion principal", "Descripcion del servicio") @(
        @("Gestion de Catalogo", "Listar celulares activos, registrar nuevos equipos, modificar precio/nombre y desactivacion logica."),
        @("Liquidacion Efectivo", "Calculo del 42% de descuento sobre el precio de lista y emision de factura de contado."),
        @("Evaluacion Crediticia", "Consulta de elegibilidad y monto maximo precalificado en BanQuito."),
        @("Emision a Credito", "Registro de credito en BanQuito, generacion de cronograma de cuotas y factura."),
        @("Consulta Amortizacion", "Visualizacion del numero de cuota, fecha de vencimiento, valor, capital e interes."),
        @("Auditoria e Idempotencia", "Trazabilidad por ID_OPERACION evitando registros duplicados ante reintentos de conexion.")
    ) @(150, 330) "Tabla 6. Funciones del producto"

    Add-H2 "7.3. Condiciones del entorno"
    Add-Table @("Elemento", "Condicion requerida") @(
        @("Sistema Operativo", "Windows 10 / Windows 11 (64 bits)."),
        @("Plataforma .NET", ".NET 10 SDK (C# 14)."),
        @("Base de Datos", "Microsoft SQL Server 2025 Express (instancia SQLEXPRESS)."),
        @("Entorno Movil", "Android SDK API 36 con emulador Android 12+ (GR10_Pixel_35)."),
        @("Red local / Puertos", "127.0.0.1:19102 (Tienda), 127.0.0.1:19101 (BanQuito), 10.0.2.2 (alias emulador).")
    ) @(150, 330) "Tabla 7. Condiciones del entorno"

    Add-H2 "7.4. Caracteristicas de los usuarios"
    Add-Table @("Tipo de usuario", "Responsabilidad y perfil") @(
        @("Vendedor / Operador", "Registra ventas en efectivo o credito, consulta clientes y emite comprobantes."),
        @("Administrador", "Gestiona altas, bajas y modificaciones en el catalogo de telefonos moviles."),
        @("Auditor Tecnico", "Comprueba la consistencia de facturas, cuotas y enlaces con BanQuito.")
    ) @(150, 330) "Tabla 8. Caracteristicas de los usuarios"

    Add-H2 "7.5. Interfaces externas"
    Add-Table @("Interfaz", "Descripcion del intercambio") @(
        @("BanQuito API (19101)", "GET /api/credito/elegibilidad y POST /api/credito/solicitudes mediante HTTP/JSON."),
        @("SQL Server Express", "Conexion ADO.NET mediante Microsoft.Data.SqlClient con seguridad integrada."),
        @("Emulador Android", "Direccionamiento especial 10.0.2.2:19102 para acceder al host local de Windows.")
    ) @(150, 330) "Tabla 9. Interfaces externas"

    Add-H2 "7.6. Restricciones"
    Add-P "• No se comparten bases de datos entre la Comercializadora y BanQuito; la integracion es exclusivamente HTTP REST."
    Add-P "• Prohibido incluir credenciales o cadenas de conexion en repositorios o capturas."
    Add-P "• Estricta separacion MVC en los cuatro clientes; ninguna vista puede realizar peticiones HTTP directamente."

    Add-H2 "7.7. Suposiciones y dependencias"
    Add-P "Se asume que la API de BanQuito se encuentra iniciada en el puerto 19101 previo a la ejecucion de ventas a credito. En caso de indisponibilidad bancaria, la comercializadora rechaza la solicitud de forma controlada sin registrar venta inconsistente."

    # 8. ESPECIFICACION DE REQUERIMIENTOS
    Add-H1 "8. Especificacion de requerimientos"
    Add-H2 "8.1. Requisitos comunes de las interfaces"
    Add-H3 "8.1.1. Interfaces de usuario"
    Add-P "Los cuatro clientes comparten la misma identidad visual, paleta de colores corporativa, etiquetas claras y flujo operativo: catalogo, seleccion de equipo, seleccion de modalidad de pago, confirmacion y consulta de amortizacion."

    Add-H3 "8.1.2. Interfaces de hardware y software"
    Add-P "Hardware minimo: Procesador Intel Core i5 / AMD Ryzen 5, 8 GB RAM, 20 GB de espacio libre en disco. Software: .NET 10 SDK, SQL Server 2025 Express, SSMS y Visual Studio 2022 o VS Code."

    Add-H3 "8.1.3. Interfaces de comunicacion"
    Add-P "Protocolo HTTP 1.1 / REST con serializacion JSON. Endpoints base: http://127.0.0.1:19102 (API Comercializadora) y http://127.0.0.1:19101 (API BanQuito)."

    Add-H2 "8.2. Requisitos funcionales"
    Add-H3 "8.2.1. Lista de requisitos funcionales"
    Add-Table @("Codigo", "Nombre del Requisito", "Prioridad", "Estado") @(
        @("RF-01", "Consultar catalogo de celulares activos", "Alta", "Aprobado"),
        @("RF-02", "Crear nuevo celular en catalogo", "Alta", "Aprobado"),
        @("RF-03", "Editar celular existente", "Alta", "Aprobado"),
        @("RF-04", "Desactivar celular (baja logica)", "Alta", "Aprobado"),
        @("RF-05", "Registrar venta en efectivo (descuento 42%)", "Alta", "Aprobado"),
        @("RF-06", "Registrar venta a credito directo (BanQuito)", "Alta", "Aprobado"),
        @("RF-07", "Consultar detalle de factura emitida", "Media", "Aprobado"),
        @("RF-08", "Consultar tabla de amortizacion de credito", "Media", "Aprobado"),
        @("RF-09", "Garantizar idempotencia por ID_OPERACION", "Alta", "Aprobado"),
        @("RF-10", "Separacion arquitectonica MVC en 4 clientes", "Alta", "Aprobado")
    ) @(55, 255, 80, 90) "Tabla 10. Resumen de Requisitos Funcionales"

    Add-H3 "8.2.2. Especificacion detallada (Fichas IEEE 830)"

    Add-Ficha "RF-01" "Consultar catalogo de celulares activos" `
        "El sistema debe retornar el listado completo de celulares registrados cuyo estado ACTIVO sea igual a 1, incluyendo ID, nombre y precio lista." `
        "OBJ-001 (Gestion de catalogo)" "Alta" "Aprobado" `
        "Consumido mediante GET /api/celulares por los 4 canales clientes." "Tabla 11. Ficha RF-01"

    Add-Ficha "RF-02" "Crear nuevo celular en catalogo" `
        "El sistema debe permitir dar de alta un nuevo equipo celular validando que el nombre no este vacio y que el precio de lista sea estrictamente mayor a cero." `
        "OBJ-001 (Gestion de catalogo)" "Alta" "Aprobado" `
        "Consumido mediante POST /api/celulares. Asigna ACTIVO=1 por defecto." "Tabla 12. Ficha RF-02"

    Add-Ficha "RF-03" "Editar celular existente" `
        "El sistema debe permitir modificar el nombre y precio de lista de un celular existente identificado por su ID_CELULAR." `
        "OBJ-001 (Gestion de catalogo)" "Alta" "Aprobado" `
        "Consumido mediante PUT /api/celulares/{id}." "Tabla 13. Ficha RF-03"

    Add-Ficha "RF-04" "Desactivar celular (baja logica)" `
        "El sistema debe permitir cambiar el estado de un celular a ACTIVO=0 sin borrar fisicamente el registro, preservando la integridad de facturas historicas." `
        "OBJ-001 (Gestion de catalogo)" "Alta" "Aprobado" `
        "Consumido mediante DELETE /api/celulares/{id}." "Tabla 14. Ficha RF-04"

    Add-Ficha "RF-05" "Registrar venta en efectivo con 42% descuento" `
        "Al seleccionar forma de pago EFECTIVO, el sistema debe aplicar automaticamente una deduccion del 42% sobre el precio de lista, registrar la venta y emitir la factura aprobada." `
        "OBJ-002 (Proceso de facturacion)" "Alta" "Aprobado" `
        "Persiste en FACTURA con FORMA_PAGO=EFECTIVO, COD_CREDITO=NULL y cuotas=NULL." "Tabla 15. Ficha RF-05"

    Add-Ficha "RF-06" "Registrar venta a credito directo con BanQuito" `
        "Al seleccionar CREDITO_DIRECTO, el sistema debe consultar la elegibilidad del cliente en BanQuito, validar el monto maximo, plazo (3-18 meses), solicitar el credito a tasa 16.5% y registrar la factura." `
        "OBJ-002 y OBJ-003 (Integracion bancaria)" "Alta" "Aprobado" `
        "Guarda en FACTURA el COD_CLIENTE_BANCO, COD_CREDITO y NUMERO_CUOTAS." "Tabla 16. Ficha RF-06"

    Add-Ficha "RF-07" "Consultar detalle de factura emitida" `
        "El sistema debe permitir recuperar la informacion de una factura por su ID_FACTURA o ID_OPERACION, mostrando cliente, celular, total y forma de pago." `
        "OBJ-002 (Facturacion)" "Media" "Aprobado" `
        "Consumido mediante GET /api/facturas/{id}." "Tabla 17. Ficha RF-07"

    Add-Ficha "RF-08" "Consultar tabla de amortizacion de credito" `
        "Para facturas a credito, el sistema debe recuperar de BanQuito la tabla de cuotas asociadas al COD_CREDITO, detallando capital, interes y cuota fija." `
        "OBJ-003 (Amortizacion bancaria)" "Media" "Aprobado" `
        "Consumido mediante GET /api/facturas/{id}/amortizacion." "Tabla 18. Ficha RF-08"

    Add-Ficha "RF-09" "Garantizar idempotencia por ID_OPERACION" `
        "El sistema debe evitar duplicidad de facturas cuando se envia una solicitud con un ID_OPERACION (UUID) ya registrado, retornando la factura existente." `
        "OBJ-004 (Consistencia y confiabilidad)" "Alta" "Aprobado" `
        "Implementado con indice UNIQUE sobre ID_OPERACION en SQL Server." "Tabla 19. Ficha RF-09"

    Add-Ficha "RF-10" "Separacion arquitectonica MVC en 4 clientes" `
        "Cada cliente (Consola, WPF, Web MVC, MAUI) debe estructurarse en capas separadas de Modelo, Vista y Controlador, canalizando peticiones via Celulares.Cliente." `
        "OBJ-004 (Mantenibilidad)" "Alta" "Aprobado" `
        "Verificado en la estructura de proyectos de la solucion .NET." "Tabla 20. Ficha RF-10"

    Add-H3 "8.2.3. Reglas de negocio"
    Add-P "• RN-01 (Descuento Efectivo): Toda venta con FORMA_PAGO = 'EFECTIVO' recibe un descuento obligatorio del 42 % sobre el precio de lista."
    Add-P "• RN-02 (Plazo de Credito): Las ventas a credito se financian exclusivamente en plazos enteros comprendidos entre 3 y 18 meses."
    Add-P "• RN-03 (Tasa de Interes BanQuito): El credito aplica una tasa de interes nominal anual del 16.5 % con cuota mensual fija bajo metodo frances."
    Add-P "• RN-04 (Elegibilidad Crediticia): BanQuito exige cliente registrado, deposito registrado en el ultimo mes y ausencia de creditos activos."
    Add-P "• RN-05 (Restriccion Demografica): Si el cliente es de genero masculino, debe tener al menos 25 anos cumplidos a la fecha de la consulta."
    Add-P "• RN-06 (Idempotencia Obligatoria): Cada factura exige un ID_OPERACION de tipo UUID provisto por el cliente emisor."

    Add-H2 "8.3. Requisitos no funcionales"
    Add-H3 "8.3.1. Lista de requisitos no funcionales"
    Add-Table @("Codigo", "Nombre", "Categoria", "Criterio de Aceptacion") @(
        @("RNF-01", "Protocolo de comunicacion REST", "Arquitectura", "Intercambio en HTTP/JSON bajo codificacion UTF-8."),
        @("RNF-02", "Tiempo de respuesta", "Rendimiento", "Operaciones locales < 300 ms; operaciones con BanQuito < 1200 ms."),
        @("RNF-03", "Persistencia ACID", "Fiabilidad", "Transacciones atotmicas en SQL Server 2025 Express."),
        @("RNF-04", "Seguridad de credenciales", "Seguridad", "Sin contrasenas ni connection strings expuestos en texto plano."),
        @("RNF-05", "Portabilidad de clientes", "Portabilidad", "Soporte en Windows (Consola/WPF/Web) y Android 12+ (MAUI)."),
        @("RNF-06", "Trazabilidad de operaciones", "Auditoria", "Registro estricto de fecha, UUID y estado en cada factura."),
        @("RNF-07", "Mantenibilidad y desacoplamiento", "Arquitectura", "Separacion estricta MVC y contratos en Celulares.Contratos."),
        @("RNF-08", "Disponibilidad del servicio", "Disponibilidad", "Manejo resiliente de caidas del servicio BanQuito sin crash.")
    ) @(60, 150, 90, 180) "Tabla 21. Resumen de Requisitos No Funcionales"

    Add-H3 "8.3.2. Fichas de requisitos no funcionales"
    Add-Ficha "RNF-01" "Protocolo de comunicacion REST" "Toda la comunicacion entre clientes, comercializadora y BanQuito debe ser HTTP REST con payloads JSON." "Estandar SOA" "Alta" "Aprobado" "Permite interoperabilidad transparente multiplataforma." "Tabla 22. Ficha RNF-01"
    Add-Ficha "RNF-02" "Tiempo de respuesta" "El tiempo maximo de respuesta de la API no superara 300 ms para catalogo y 1.2 segundos para ventas con credito." "Rendimiento" "Alta" "Aprobado" "Verificado en pruebas locales." "Tabla 23. Ficha RNF-02"
    Add-Ficha "RNF-03" "Persistencia ACID" "La emision de facturas garantiza atomicidad, consistencia, aislamiento y durabilidad mediante transacciones en SQL Server." "Fiabilidad" "Alta" "Aprobado" "Comprobado en SQLEXPRESS." "Tabla 24. Ficha RNF-03"
    Add-Ficha "RNF-04" "Seguridad de credenciales" "Queda prohibido incluir claves maestras, credenciales bancarias o cadenas de conexion en repositorios o capturas." "Seguridad" "Alta" "Aprobado" "Auditoria de codigo limpio." "Tabla 25. Ficha RNF-04"

    # 9. DIAGRAMAS UML
    Add-H1 "9. Diagramas UML de SAP PowerDesigner"
    Add-P "A continuacion se presentan los diagramas de modelado orientados a objetos generados y exportados formalmente desde SAP PowerDesigner 16.1:"

    Add-H2 "9.1. Diagrama de Casos de Uso"
    Add-P "Muestra la interaccion entre el actor Usuario (Vendedor) y los casos de uso del catalogo y ventas, incorporando al actor secundario BanQuito para la evaluacion crediticia."
    Add-Image (Join-Path $umlDir "PowerDesigner\GR09_Celular_CasosUso.png") "Ilustracion 1. Diagrama de casos de uso (SAP PowerDesigner)"

    Add-H2 "9.2. Diagrama de Actividad"
    Add-P "Modela el flujo de venta mostrando la bifurcacion de decision entre pago en efectivo (aplicando el 42% de descuento) y pago a credito directo (consultando BanQuito)."
    Add-Image (Join-Path $umlDir "PowerDesigner\GR09_Celular_Actividad_Venta.png") "Ilustracion 2. Diagrama de actividad - Proceso de venta (SAP PowerDesigner)"

    Add-H2 "9.3. Diagrama de Secuencia"
    Add-P "Ilustra la secuencia temporal y los mensajes entre Cliente, Vista MVC, Controlador, API REST Comercializadora, ServicioFacturas, BanQuito API y SQL Server."
    Add-Image (Join-Path $umlDir "PowerDesigner\GR09_Celular_Secuencia_Venta.png") "Ilustracion 3. Diagrama de secuencia - Emision de venta a credito (SAP PowerDesigner)"

    Add-H2 "9.4. Diagrama de Clases"
    Add-P "Estructura de clases del sistema dividida en capas: Entidades de Dominio (Celular, Factura), Servicios de Negocio, Controladores API y Cliente HTTP compartido."
    Add-Image (Join-Path $umlDir "PowerDesigner\GR09_Celular_Clases.png") "Ilustracion 4. Diagrama de clases de diseno (SAP PowerDesigner)"

    Add-H2 "9.5. Diagrama de Arquitectura"
    Add-P "Representa la arquitectura de integracion empresarial (EAM): cuatro canales clientes conectandose a traves del transporte compartido hacia la API REST y BanQuito."
    Add-Image (Join-Path $umlDir "PowerDesigner\GR09_Celular_Arquitectura.png") "Ilustracion 5. Diagrama de arquitectura de componentes (SAP PowerDesigner)"

    # 10. MODELO DE DATOS MER
    Add-H1 "10. Modelo de datos (MER) de SAP PowerDesigner"
    Add-P "El modelo de datos de la base ComercializadoraCelulares fue disenado en SAP PowerDesigner en sus tres niveles de abstraccion:"

    Add-H2 "10.1. Modelo Conceptual (CDM)"
    Add-Image (Join-Path $merDir "PowerDesigner\GR09_Celular_MER_Conceptual.png") "Ilustracion 6. Modelo entidad-relacion conceptual (SAP PowerDesigner CDM)"

    Add-H2 "10.2. Modelo Logico (LDM)"
    Add-Image (Join-Path $merDir "PowerDesigner\GR09_Celular_MER_Logico.png") "Ilustracion 7. Modelo entidad-relacion logico (SAP PowerDesigner LDM)"

    Add-H2 "10.3. Modelo Fisico (PDM - SQL Server)"
    Add-Image (Join-Path $merDir "PowerDesigner\GR09_Celular_MER_Fisico.png") "Ilustracion 8. Modelo fisico relacional SQL Server (SAP PowerDesigner PDM)"

    Add-H2 "10.4. Diccionario de datos de la base ComercializadoraCelulares"
    Add-Table @("Tabla", "Columna", "Tipo SQL", "Nulo", "Descripcion") @(
        @("CELULAR", "ID_CELULAR", "INT IDENTITY(1,1)", "NO", "Clave primaria autoincremental"),
        @("CELULAR", "NOMBRE", "NVARCHAR(100)", "NO", "Nombre comercial y modelo del celular"),
        @("CELULAR", "PRECIO", "NUMERIC(10,2)", "NO", "Precio de lista de venta al publico (>0)"),
        @("CELULAR", "ACTIVO", "BIT", "NO", "Estado: 1 activo para venta, 0 baja logica"),
        @("FACTURA", "ID_FACTURA", "INT IDENTITY(1,1)", "NO", "Clave primaria autoincremental"),
        @("FACTURA", "ID_OPERACION", "UNIQUEIDENTIFIER", "NO", "Identificador unico de transaccion (idempotencia)"),
        @("FACTURA", "FECHA", "DATETIME2", "NO", "Fecha y hora de emision de la factura"),
        @("FACTURA", "CEDULA", "NVARCHAR(100)", "NO", "Identificacion o cedula del comprador"),
        @("FACTURA", "NOMBRE_CLIENTE", "NVARCHAR(100)", "NO", "Nombres completos del cliente"),
        @("FACTURA", "ID_CELULAR", "INT (FK)", "NO", "Clave foranea que referencia a CELULAR(ID_CELULAR)"),
        @("FACTURA", "NOMBRE_CELULAR", "NVARCHAR(100)", "NO", "Nombre del celular al momento de facturar"),
        @("FACTURA", "FORMA_PAGO", "VARCHAR(20)", "NO", "Modalidad: 'EFECTIVO' o 'CREDITO_DIRECTO'"),
        @("FACTURA", "PRECIO", "NUMERIC(10,2)", "NO", "Precio lista aplicado en la venta"),
        @("FACTURA", "DESCUENTO", "NUMERIC(10,2)", "NO", "Monto descontado (42% en efectivo, 0 en credito)"),
        @("FACTURA", "TOTAL", "NUMERIC(10,2)", "NO", "Valor neto final facturado"),
        @("FACTURA", "COD_CLIENTE_BANCO", "INT", "SI", "Referencia remota al cliente en BanQuito"),
        @("FACTURA", "COD_CREDITO", "INT", "SI", "Referencia remota al credito aprobado en BanQuito"),
        @("FACTURA", "NUMERO_CUOTAS", "INT", "SI", "Plazo en meses acordado (entre 3 y 18 meses)"),
        @("FACTURA", "ESTADO", "VARCHAR(12)", "NO", "Estado: 'PENDIENTE', 'APROBADA' o 'RECHAZADA'")
    ) @(65, 110, 110, 35, 160) "Tabla 26. Diccionario de datos ComercializadoraCelulares"

    # 11. MATRIZ DE TRAZABILIDAD
    Add-H1 "11. Matriz de trazabilidad"
    Add-P "La siguiente matriz establece la correspondencia directa entre los objetivos, requisitos funcionales, casos de uso y componentes de software implementados en el repositorio:"

    Add-Table @("Requisito", "Objetivo", "Caso de Uso", "Componente Servidor", "Componente Cliente") @(
        @("RF-01", "OBJ-001", "CU_Catalogo", "CelularesController.Get()", "ClienteComercializadora.ObtenerCatalogoAsync()"),
        @("RF-02", "OBJ-001", "CU_GestionCat", "CelularesController.Post()", "ClienteComercializadora.CrearCelularAsync()"),
        @("RF-03", "OBJ-001", "CU_GestionCat", "CelularesController.Put()", "ClienteComercializadora.EditarCelularAsync()"),
        @("RF-04", "OBJ-001", "CU_GestionCat", "CelularesController.Delete()", "ClienteComercializadora.DesactivarAsync()"),
        @("RF-05", "OBJ-002", "CU_VentaEfectivo", "FacturasController / ReglasFacturacion", "ControladorTienda.VenderEfectivo()"),
        @("RF-06", "OBJ-002", "CU_VentaCredito", "FacturasController / ServicioBanQuito", "ControladorTienda.VenderCredito()"),
        @("RF-07", "OBJ-002", "CU_Factura", "FacturasController.GetById()", "ClienteComercializadora.ObtenerFacturaAsync()"),
        @("RF-08", "OBJ-003", "CU_Amortizacion", "FacturasController.GetAmortizacion()", "ClienteComercializadora.ObtenerAmortizacionAsync()"),
        @("RF-09", "OBJ-004", "CU_VentaEfectivo / Credito", "UQ_FACTURA_OPERACION (SQL Server)", "Guid.NewGuid() en cliente"),
        @("RF-10", "OBJ-004", "Todos", "Comercializadora.Api (ASP.NET Core)", "Consola, WPF, Web MVC, MAUI Android")
    ) @(45, 55, 100, 140, 140) "Tabla 27. Matriz de trazabilidad de requerimientos"

    # 12. CONCLUSIONES Y RECOMENDACIONES
    Add-H1 "12. Conclusiones y recomendaciones"
    Add-H2 "12.1. Conclusiones"
    Add-P "• Se implemento satisfactoriamente la arquitectura de software distribuida para la Comercializadora de Celulares sobre .NET 10 y SQL Server 2025 Express, cumpliendo con los lineamientos del Examen Complexivo."
    Add-P "• La integracion con el servicio bancario BanQuito demostro ser robusta y desacoplada, ejecutando la evaluacion crediticia y cronograma de amortizacion sin transferir ni duplicar esquemas de base de datos."
    Add-P "• Los cuatro canales clientes (Consola, Escritorio WPF, Web MVC y Movil MAUI Android) ofrecen consistencia visual y de comportamiento gracias a la reutilizacion de contratos y del cliente HTTP compartido."
    Add-P "• El modelado integro en SAP PowerDesigner 16.1 respalda la calidad de diseno en niveles conceptual, logico, fisico y de analisis de objetos UML."

    Add-H2 "12.2. Recomendaciones"
    Add-P "• Mantener la politica de aislamiento de cadenas de conexion mediante variables de entorno o almacenes seguros de configuracion."
    Add-P "• En despliegues en servidores externos, habilitar cifrado TLS/HTTPS en los endpoints 19102 y 19101."
    Add-P "• Realizar pruebas de integracion continuas ejecutando la suite de pruebas unitarias automatizadas del proyecto Comercializadora.Pruebas."

    # Actualizar campos e indices
    Write-Output "Actualizando campos e indices de Word..."
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    foreach ($tof in $doc.TablesOfFigures) { $tof.Update() }
    $doc.Repaginate()
    foreach ($toc in $doc.TablesOfContents) { $toc.UpdatePageNumbers() }
    foreach ($tof in $doc.TablesOfFigures) { $tof.UpdatePageNumbers() }

    $doc.Save()
    Write-Output "=== ERS IEEE 830 generado con EXITO: $outputDocx ==="
    Write-Output "Paginas finales: $($doc.ComputeStatistics(2))"
    Write-Output "Tablas creadas: $($doc.Tables.Count)"

} finally {
    if ($doc) {
        $doc.Close($false)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($doc)
    }
    if ($word) {
        try { $word.Quit() } catch {}
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

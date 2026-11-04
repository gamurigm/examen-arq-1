<#
.SYNOPSIS
    Genera los modelos de datos en SAP PowerDesigner (CDM, LDM, PDM)
    y exporta los diagramas PNG para el proyecto CELULARES GR09.
#>
[CmdletBinding()]
param([string]$Raiz = $PSScriptRoot)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Set-MerSymbolPosition($Symbol, [int[]]$Position) {
    $point = $Symbol.GetAttribute('Position')
    $point.X = $Position[0]
    $point.Y = $Position[1]
    $Symbol.SetAttribute('Position', $point) | Out-Null
}

$proyectoDir = Join-Path $Raiz "TI.1.1. PAO202651_CELULAR_BDDLOCAL_RESTFUL_NRC36884_GR09"
if (-not (Test-Path -LiteralPath $proyectoDir)) {
    $found = Get-ChildItem -Path $Raiz -Directory | Where-Object { $_.Name -like "*CELULAR*RESTFUL*" } | Select-Object -First 1
    if ($null -eq $found) { throw "No se encontro la carpeta del proyecto CELULAR en $Raiz" }
    $proyectoDir = $found.FullName
}
Write-Output "Directorio proyecto: $proyectoDir"

$merDir = Join-Path $proyectoDir "02. MER"
$conceptualDir = Join-Path $merDir "01. CONCEPTUAL"
$logicalDir    = Join-Path $merDir "02. LOGICO"
$physicalDir   = Join-Path $merDir "03. FISICO"
$pdDir         = Join-Path $merDir "PowerDesigner"

New-Item -ItemType Directory -Force -Path $conceptualDir, $logicalDir, $physicalDir, $pdDir | Out-Null

$app = $null
try {
    $app = New-Object -ComObject PowerDesigner.Application
    $app.InteractiveMode = 2
    Write-Output "PowerDesigner conectado: $($app.Version)"

    # =========================================================================
    # 1. PDM - Modelo Fisico SQL Server
    # =========================================================================
    Write-Output "Creando PDM (Fisico SQL Server)..."
    $pdmMeta = $app.MetaModel.GetMetaClassByPublicName("PdPDM.Model")
    $pdm = $app.CreateModel($pdmMeta.Kind, "|DBMS=Microsoft SQL Server 2008|Diagram=PhysicalDiagram", 9)
    $pdm.Name = "Comercializadora Celulares Fisico GR09"
    $pdm.Code = "GR09_Celular_PDM"
    $pdm.Comment = "Modelo fisico SQL Server 2025 Express para ComercializadoraCelulares GR09."

    $diagPdm = $pdm.PhysicalDiagrams.Item(0)
    $diagPdm.Name = "MER Fisico Comercializadora"
    $diagPdm.Code = "GR09_MER_Fisico"

    # Tabla CELULAR
    $tblCelular = $pdm.Tables.CreateNew()
    $tblCelular.Name = "CELULAR"; $tblCelular.Code = "CELULAR"
    $tblCelular.Comment = "Catalogo de celulares de la comercializadora."

    $colIdCel = $tblCelular.Columns.CreateNew()
    $colIdCel.Name = "ID_CELULAR"; $colIdCel.Code = "ID_CELULAR"; $colIdCel.DataType = "INT"; $colIdCel.Mandatory = $true; $colIdCel.Identity = $true; $colIdCel.Primary = $true

    $colNomCel = $tblCelular.Columns.CreateNew()
    $colNomCel.Name = "NOMBRE"; $colNomCel.Code = "NOMBRE"; $colNomCel.DataType = "NVARCHAR(100)"; $colNomCel.Mandatory = $true

    $colPrecCel = $tblCelular.Columns.CreateNew()
    $colPrecCel.Name = "PRECIO"; $colPrecCel.Code = "PRECIO"; $colPrecCel.DataType = "NUMERIC(10,2)"; $colPrecCel.Mandatory = $true

    $colActCel = $tblCelular.Columns.CreateNew()
    $colActCel.Name = "ACTIVO"; $colActCel.Code = "ACTIVO"; $colActCel.DataType = "BIT"; $colActCel.Mandatory = $true

    # Tabla FACTURA
    $tblFactura = $pdm.Tables.CreateNew()
    $tblFactura.Name = "FACTURA"; $tblFactura.Code = "FACTURA"
    $tblFactura.Comment = "Facturas de venta de celulares (efectivo o credito directo)."

    $colIdFac = $tblFactura.Columns.CreateNew()
    $colIdFac.Name = "ID_FACTURA"; $colIdFac.Code = "ID_FACTURA"; $colIdFac.DataType = "INT"; $colIdFac.Mandatory = $true; $colIdFac.Identity = $true; $colIdFac.Primary = $true

    $colIdOp = $tblFactura.Columns.CreateNew()
    $colIdOp.Name = "ID_OPERACION"; $colIdOp.Code = "ID_OPERACION"; $colIdOp.DataType = "UNIQUEIDENTIFIER"; $colIdOp.Mandatory = $true

    $colFecha = $tblFactura.Columns.CreateNew()
    $colFecha.Name = "FECHA"; $colFecha.Code = "FECHA"; $colFecha.DataType = "DATETIME2"; $colFecha.Mandatory = $true

    $colCed = $tblFactura.Columns.CreateNew()
    $colCed.Name = "CEDULA"; $colCed.Code = "CEDULA"; $colCed.DataType = "NVARCHAR(100)"; $colCed.Mandatory = $true

    $colNomCli = $tblFactura.Columns.CreateNew()
    $colNomCli.Name = "NOMBRE_CLIENTE"; $colNomCli.Code = "NOMBRE_CLIENTE"; $colNomCli.DataType = "NVARCHAR(100)"; $colNomCli.Mandatory = $true

    $colFkCel = $tblFactura.Columns.CreateNew()
    $colFkCel.Name = "ID_CELULAR"; $colFkCel.Code = "ID_CELULAR"; $colFkCel.DataType = "INT"; $colFkCel.Mandatory = $true

    $colNomCelFac = $tblFactura.Columns.CreateNew()
    $colNomCelFac.Name = "NOMBRE_CELULAR"; $colNomCelFac.Code = "NOMBRE_CELULAR"; $colNomCelFac.DataType = "NVARCHAR(100)"; $colNomCelFac.Mandatory = $true

    $colForma = $tblFactura.Columns.CreateNew()
    $colForma.Name = "FORMA_PAGO"; $colForma.Code = "FORMA_PAGO"; $colForma.DataType = "VARCHAR(20)"; $colForma.Mandatory = $true

    $colPrecio = $tblFactura.Columns.CreateNew()
    $colPrecio.Name = "PRECIO"; $colPrecio.Code = "PRECIO"; $colPrecio.DataType = "NUMERIC(10,2)"; $colPrecio.Mandatory = $true

    $colDesc = $tblFactura.Columns.CreateNew()
    $colDesc.Name = "DESCUENTO"; $colDesc.Code = "DESCUENTO"; $colDesc.DataType = "NUMERIC(10,2)"; $colDesc.Mandatory = $true

    $colTotal = $tblFactura.Columns.CreateNew()
    $colTotal.Name = "TOTAL"; $colTotal.Code = "TOTAL"; $colTotal.DataType = "NUMERIC(10,2)"; $colTotal.Mandatory = $true

    $colCodCli = $tblFactura.Columns.CreateNew()
    $colCodCli.Name = "COD_CLIENTE_BANCO"; $colCodCli.Code = "COD_CLIENTE_BANCO"; $colCodCli.DataType = "INT"; $colCodCli.Mandatory = $false

    $colCodCred = $tblFactura.Columns.CreateNew()
    $colCodCred.Name = "COD_CREDITO"; $colCodCred.Code = "COD_CREDITO"; $colCodCred.DataType = "INT"; $colCodCred.Mandatory = $false

    $colCuotas = $tblFactura.Columns.CreateNew()
    $colCuotas.Name = "NUMERO_CUOTAS"; $colCuotas.Code = "NUMERO_CUOTAS"; $colCuotas.DataType = "INT"; $colCuotas.Mandatory = $false

    $colEstado = $tblFactura.Columns.CreateNew()
    $colEstado.Name = "ESTADO"; $colEstado.Code = "ESTADO"; $colEstado.DataType = "VARCHAR(12)"; $colEstado.Mandatory = $true

    # Clave foranea
    $ref = $pdm.References.CreateNew()
    $ref.Name = "FK_FACTURA_CELULAR"; $ref.Code = "FK_FACTURA_CELULAR"
    $ref.ParentTable = $tblCelular
    $ref.ChildTable = $tblFactura
    $join = $ref.Joins.CreateNew()
    $join.ParentTableColumn = $colIdCel
    $join.ChildTableColumn = $colFkCel

    # Indice unico ID_OPERACION
    $idxOp = $tblFactura.Indexes.CreateNew()
    $idxOp.Name = "UQ_FACTURA_OPERACION"; $idxOp.Code = "UQ_FACTURA_OPERACION"; $idxOp.Unique = $true
    $idxCol = $idxOp.IndexColumns.CreateNew(); $idxCol.Column = $colIdOp

    # Simbolos y posiciones
    $symCel = $diagPdm.AttachObject($tblCelular)
    Set-MerSymbolPosition $symCel @(-22000, 0)

    $symFac = $diagPdm.AttachObject($tblFactura)
    Set-MerSymbolPosition $symFac @(22000, 0)

    $diagPdm.AttachLinkObject($ref) | Out-Null

    $pdmPath = Join-Path $physicalDir "GR09_Celular_Physical_SQLServer.pdm"
    $pdmPng  = Join-Path $physicalDir "GR09_Celular_Physical_SQLServer.png"
    $pdm.Save($pdmPath)
    $diagPdm.ExportImage($pdmPng)
    Write-Output "Exportado PDM: $pdmPath ($pdmPng)"
    Copy-Item -LiteralPath $pdmPath -Destination (Join-Path $pdDir "GR09_Celular_MER.pdm") -Force
    Copy-Item -LiteralPath $pdmPng -Destination (Join-Path $pdDir "GR09_Celular_MER_Fisico.png") -Force
    $pdm.Close()

    # =========================================================================
    # 2. LDM - Modelo Logico
    # =========================================================================
    Write-Output "Creando LDM (Logico)..."
    $ldmMeta = $app.MetaModel.GetMetaClassByPublicName("PdLDM.Model")
    $ldm = $app.CreateModel($ldmMeta.Kind, "|Diagram=LogicalDiagram", 9)
    $ldm.Name = "Comercializadora Celulares Logico GR09"
    $ldm.Code = "GR09_Celular_LDM"
    $diagLdm = $ldm.LogicalDiagrams.Item(0)
    $diagLdm.Name = "MER Logico Comercializadora"
    $diagLdm.Code = "GR09_MER_Logico"

    $entCelL = $ldm.Entities.CreateNew(); $entCelL.Name = "CELULAR"; $entCelL.Code = "CELULAR"
    $la1 = $entCelL.Attributes.CreateNew(); $la1.Name = "Id Celular"; $la1.Code = "ID_CELULAR"; $la1.DataType = "INT"; $la1.Mandatory = $true
    $la2 = $entCelL.Attributes.CreateNew(); $la2.Name = "Nombre"; $la2.Code = "NOMBRE"; $la2.DataType = "VARCHAR(100)"; $la2.Mandatory = $true
    $la3 = $entCelL.Attributes.CreateNew(); $la3.Name = "Precio"; $la3.Code = "PRECIO"; $la3.DataType = "NUMERIC(10,2)"; $la3.Mandatory = $true
    $la4 = $entCelL.Attributes.CreateNew(); $la4.Name = "Activo"; $la4.Code = "ACTIVO"; $la4.DataType = "BOOLEAN"; $la4.Mandatory = $true
    $lidCel = $entCelL.Identifiers.CreateNew(); $lidCel.Name = "PK_CELULAR"; $lidCel.Code = "PK_CELULAR"; $lidCel.PrimaryIdentifier = $true
    $lidCel.Attributes.Add($la1)

    $entFacL = $ldm.Entities.CreateNew(); $entFacL.Name = "FACTURA"; $entFacL.Code = "FACTURA"
    $lb1 = $entFacL.Attributes.CreateNew(); $lb1.Name = "Id Factura"; $lb1.Code = "ID_FACTURA"; $lb1.DataType = "INT"; $lb1.Mandatory = $true
    $lb2 = $entFacL.Attributes.CreateNew(); $lb2.Name = "Id Operacion"; $lb2.Code = "ID_OPERACION"; $lb2.DataType = "GUID"; $lb2.Mandatory = $true
    $lb3 = $entFacL.Attributes.CreateNew(); $lb3.Name = "Fecha"; $lb3.Code = "FECHA"; $lb3.DataType = "DATETIME"; $lb3.Mandatory = $true
    $lb4 = $entFacL.Attributes.CreateNew(); $lb4.Name = "Cedula"; $lb4.Code = "CEDULA"; $lb4.DataType = "VARCHAR(100)"; $lb4.Mandatory = $true
    $lb5 = $entFacL.Attributes.CreateNew(); $lb5.Name = "Nombre Cliente"; $lb5.Code = "NOMBRE_CLIENTE"; $lb5.DataType = "VARCHAR(100)"; $lb5.Mandatory = $true
    $lb6 = $entFacL.Attributes.CreateNew(); $lb6.Name = "Forma Pago"; $lb6.Code = "FORMA_PAGO"; $lb6.DataType = "VARCHAR(20)"; $lb6.Mandatory = $true
    $lb7 = $entFacL.Attributes.CreateNew(); $lb7.Name = "Precio"; $lb7.Code = "PRECIO"; $lb7.DataType = "NUMERIC(10,2)"; $lb7.Mandatory = $true
    $lb8 = $entFacL.Attributes.CreateNew(); $lb8.Name = "Descuento"; $lb8.Code = "DESCUENTO"; $lb8.DataType = "NUMERIC(10,2)"; $lb8.Mandatory = $true
    $lb9 = $entFacL.Attributes.CreateNew(); $lb9.Name = "Total"; $lb9.Code = "TOTAL"; $lb9.DataType = "NUMERIC(10,2)"; $lb9.Mandatory = $true
    $lb10= $entFacL.Attributes.CreateNew(); $lb10.Name= "Cod Cliente Banco"; $lb10.Code="COD_CLIENTE_BANCO"; $lb10.DataType="INT"; $lb10.Mandatory=$false
    $lb11= $entFacL.Attributes.CreateNew(); $lb11.Name= "Cod Credito"; $lb11.Code="COD_CREDITO"; $lb11.DataType="INT"; $lb11.Mandatory=$false
    $lb12= $entFacL.Attributes.CreateNew(); $lb12.Name= "Numero Cuotas"; $lb12.Code="NUMERO_CUOTAS"; $lb12.DataType="INT"; $lb12.Mandatory=$false
    $lb13= $entFacL.Attributes.CreateNew(); $lb13.Name= "Estado"; $lb13.Code="ESTADO"; $lb13.DataType="VARCHAR(12)"; $lb13.Mandatory=$true
    $lidFac = $entFacL.Identifiers.CreateNew(); $lidFac.Name = "PK_FACTURA"; $lidFac.Code = "PK_FACTURA"; $lidFac.PrimaryIdentifier = $true
    $lidFac.Attributes.Add($lb1)

    $relL = $ldm.Relationships.CreateNew()
    $relL.Name = "CELULAR_FACTURA"; $relL.Code = "CELULAR_FACTURA"
    $relL.Entity1 = $entCelL; $relL.Entity2 = $entFacL
    $relL.Entity1ToEntity2RoleMinimumCardinality = "0"
    $relL.Entity1ToEntity2RoleMaximumCardinality = "n"
    $relL.Entity2ToEntity1RoleMinimumCardinality = "1"
    $relL.Entity2ToEntity1RoleMaximumCardinality = "1"

    $symCelL = $diagLdm.AttachObject($entCelL); Set-MerSymbolPosition $symCelL @(-22000, 0)
    $symFacL = $diagLdm.AttachObject($entFacL); Set-MerSymbolPosition $symFacL @(22000, 0)
    $diagLdm.AttachLinkObject($relL) | Out-Null

    $ldmPath = Join-Path $logicalDir "GR09_Celular_Logical.ldm"
    $ldmPng  = Join-Path $logicalDir "GR09_Celular_Logical.png"
    $ldm.Save($ldmPath)
    $diagLdm.ExportImage($ldmPng)
    Write-Output "Exportado LDM: $ldmPath ($ldmPng)"
    Copy-Item -LiteralPath $ldmPath -Destination (Join-Path $pdDir "GR09_Celular_MER.ldm") -Force
    Copy-Item -LiteralPath $ldmPng -Destination (Join-Path $pdDir "GR09_Celular_MER_Logico.png") -Force
    $ldm.Close()

    # =========================================================================
    # 3. CDM - Modelo Conceptual
    # =========================================================================
    Write-Output "Creando CDM (Conceptual)..."
    $cdmMeta = $app.MetaModel.GetMetaClassByPublicName("PdCDM.Model")
    $cdm = $app.CreateModel($cdmMeta.Kind, "|Diagram=ConceptualDiagram", 9)
    $cdm.Name = "Comercializadora Celulares Conceptual GR09"
    $cdm.Code = "GR09_Celular_CDM"
    $diagCdm = $cdm.ConceptualDiagrams.Item(0)
    $diagCdm.Name = "MER Conceptual Comercializadora"
    $diagCdm.Code = "GR09_MER_Conceptual"

    $entCelC = $cdm.Entities.CreateNew(); $entCelC.Name = "CELULAR"; $entCelC.Code = "CELULAR"
    $ca1 = $entCelC.Attributes.CreateNew(); $ca1.Name = "Id Celular"; $ca1.Code = "ID_CELULAR"; $ca1.DataType = "Número"; $ca1.Mandatory = $true
    $ca2 = $entCelC.Attributes.CreateNew(); $ca2.Name = "Nombre"; $ca2.Code = "NOMBRE"; $ca2.DataType = "Texto"; $ca2.Mandatory = $true
    $ca3 = $entCelC.Attributes.CreateNew(); $ca3.Name = "Precio"; $ca3.Code = "PRECIO"; $ca3.DataType = "Importe"; $ca3.Mandatory = $true
    $ca4 = $entCelC.Attributes.CreateNew(); $ca4.Name = "Activo"; $ca4.Code = "ACTIVO"; $ca4.DataType = "Texto"; $ca4.Mandatory = $true
    $cidCel = $entCelC.Identifiers.CreateNew(); $cidCel.Name = "PK_CELULAR"; $cidCel.Code = "PK_CELULAR"; $cidCel.PrimaryIdentifier = $true
    $cidCel.Attributes.Add($ca1)

    $entFacC = $cdm.Entities.CreateNew(); $entFacC.Name = "FACTURA"; $entFacC.Code = "FACTURA"
    $cb1 = $entFacC.Attributes.CreateNew(); $cb1.Name = "Id Factura"; $cb1.Code = "ID_FACTURA"; $cb1.DataType = "Número"; $cb1.Mandatory = $true
    $cb2 = $entFacC.Attributes.CreateNew(); $cb2.Name = "Id Operacion"; $cb2.Code = "ID_OPERACION"; $cb2.DataType = "Identificador"; $cb2.Mandatory = $true
    $cb3 = $entFacC.Attributes.CreateNew(); $cb3.Name = "Fecha"; $cb3.Code = "FECHA"; $cb3.DataType = "Fecha y hora"; $cb3.Mandatory = $true
    $cb4 = $entFacC.Attributes.CreateNew(); $cb4.Name = "Cedula"; $cb4.Code = "CEDULA"; $cb4.DataType = "Texto"; $cb4.Mandatory = $true
    $cb5 = $entFacC.Attributes.CreateNew(); $cb5.Name = "Nombre Cliente"; $cb5.Code = "NOMBRE_CLIENTE"; $cb5.DataType = "Texto"; $cb5.Mandatory = $true
    $cb6 = $entFacC.Attributes.CreateNew(); $cb6.Name = "Forma Pago"; $cb6.Code = "FORMA_PAGO"; $cb6.DataType = "Texto"; $cb6.Mandatory = $true
    $cb7 = $entFacC.Attributes.CreateNew(); $cb7.Name = "Total"; $cb7.Code = "TOTAL"; $cb7.DataType = "Importe"; $cb7.Mandatory = $true
    $cb8 = $entFacC.Attributes.CreateNew(); $cb8.Name = "Estado"; $cb8.Code = "ESTADO"; $cb8.DataType = "Texto"; $cb8.Mandatory = $true
    $cidFac = $entFacC.Identifiers.CreateNew(); $cidFac.Name = "PK_FACTURA"; $cidFac.Code = "PK_FACTURA"; $cidFac.PrimaryIdentifier = $true
    $cidFac.Attributes.Add($cb1)

    $relC = $cdm.Relationships.CreateNew()
    $relC.Name = "Pertenece a"; $relC.Code = "CELULAR_FACTURA"
    $relC.Entity1 = $entCelC; $relC.Entity2 = $entFacC
    $relC.Entity1ToEntity2RoleMinimumCardinality = "0"
    $relC.Entity1ToEntity2RoleMaximumCardinality = "n"
    $relC.Entity2ToEntity1RoleMinimumCardinality = "1"
    $relC.Entity2ToEntity1RoleMaximumCardinality = "1"

    $symCelC = $diagCdm.AttachObject($entCelC); Set-MerSymbolPosition $symCelC @(-22000, 0)
    $symFacC = $diagCdm.AttachObject($entFacC); Set-MerSymbolPosition $symFacC @(22000, 0)
    $diagCdm.AttachLinkObject($relC) | Out-Null

    $cdmPath = Join-Path $conceptualDir "GR09_Celular_Conceptual.cdm"
    $cdmPng  = Join-Path $conceptualDir "GR09_Celular_Conceptual.png"
    $cdm.Save($cdmPath)
    $diagCdm.ExportImage($cdmPng)
    Write-Output "Exportado CDM: $cdmPath ($cdmPng)"
    Copy-Item -LiteralPath $cdmPath -Destination (Join-Path $pdDir "GR09_Celular_MER.cdm") -Force
    Copy-Item -LiteralPath $cdmPng -Destination (Join-Path $pdDir "GR09_Celular_MER_Conceptual.png") -Force
    $cdm.Close()

    Write-Output "=== Modelos MER (Fisico, Logico, Conceptual) generados con EXITO ==="

} finally {
    if ($app) {
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
        [GC]::Collect()
        [GC]::WaitForPendingFinalizers()
    }
}

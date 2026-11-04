[CmdletBinding()]
param(
    [string]$ProfilePath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'documentation-profile.json'),
    [string]$OutputPath,
    [switch]$Force
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$profile = Get-Content -Raw -LiteralPath $ProfilePath | ConvertFrom-Json
$root = Split-Path -Parent (Resolve-Path -LiteralPath $ProfilePath).Path
$artifact = $profile.documentation.artifacts.ers
$templatePath = Join-Path $root $artifact.template
$sourcePath = Join-Path $root $artifact.source
if (-not $OutputPath) {
    $draft = $profile.documentation.draft_directory
    New-Item -ItemType Directory -Force -Path $draft | Out-Null
    $OutputPath = Join-Path $draft ([IO.Path]::GetFileName($artifact.output))
}
$templateFullPath = [IO.Path]::GetFullPath($templatePath)
$outputFullPath = [IO.Path]::GetFullPath($OutputPath)
$outputDirectory = [IO.Path]::GetDirectoryName($outputFullPath)

if (-not (Test-Path -LiteralPath $templateFullPath -PathType Leaf)) {
    throw "No se encontró la plantilla Word: $templateFullPath"
}
if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "No se encontró la fuente Markdown: $sourcePath"
}
$sourceText = [IO.File]::ReadAllText($sourcePath)
if ($sourceText -match '(?i)REVISION PENDIENTE|SCREENSHOT PENDING|\bTODO\b') {
    throw 'El ERS debe documentar Celulares sin referencias a DOCX de otros proyectos.'
}
if ([IO.Path]::GetExtension($outputFullPath) -ine '.docx') {
    throw 'OutputPath debe terminar en .docx.'
}
if ([IO.Directory]::Exists($outputFullPath)) {
    throw 'OutputPath debe ser una ruta de archivo .docx.'
}
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    throw "No existe el directorio de salida: $outputDirectory"
}
if ([string]::Equals($templateFullPath, $outputFullPath, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'OutputPath no puede apuntar al archivo de plantilla.'
}
if ((Test-Path -LiteralPath $outputFullPath -PathType Leaf) -and -not $Force) {
    throw "El archivo de salida ya existe. Usa -Force para reemplazarlo: $outputFullPath"
}

$pandoc = Get-Command pandoc -ErrorAction Stop
$bodyPath = Join-Path $env:TEMP ('Celulares_ERS_body_' + [Guid]::NewGuid().ToString('N') + '.docx')
$word = $null
$document = $null

function Add-CaptionRun {
    param($XmlDocument, $Paragraph, [string]$Kind, [string]$Value)
    $w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    $run = $XmlDocument.CreateElement('w', 'r', $w)
    if ($Kind -eq 'field') {
        $node = $XmlDocument.CreateElement('w', 'fldChar', $w)
        $attribute = $XmlDocument.CreateAttribute('w', 'fldCharType', $w)
        $attribute.Value = $Value
        [void]$node.Attributes.Append($attribute)
    }
    else {
        $localName = if ($Kind -eq 'instruction') { 'instrText' } else { 't' }
        $node = $XmlDocument.CreateElement('w', $localName, $w)
        $attribute = $XmlDocument.CreateAttribute('xml', 'space', 'http://www.w3.org/XML/1998/namespace')
        $attribute.Value = 'preserve'
        [void]$node.Attributes.Append($attribute)
        $node.InnerText = $Value
    }
    [void]$run.AppendChild($node)
    [void]$Paragraph.AppendChild($run)
}

try {
    & $pandoc.Source $sourcePath --from markdown --to docx --standalone --number-sections --toc --toc-depth=3 --resource-path (Split-Path -Parent $sourcePath) --reference-doc $templateFullPath --output $bodyPath
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $bodyPath -PathType Leaf)) {
        throw "Pandoc no pudo generar el cuerpo del ERS (código $LASTEXITCODE)."
    }

    # Add native Word sequence fields to the generated captions for the two automatic indexes.
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::Open($bodyPath, [IO.Compression.ZipArchiveMode]::Update)
    try {
        $entry = $archive.GetEntry('word/document.xml')
        $reader = [IO.StreamReader]::new($entry.Open())
        [xml]$bodyXml = $reader.ReadToEnd()
        $reader.Close()
        $w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        $namespaces = [Xml.XmlNamespaceManager]::new($bodyXml.NameTable)
        $namespaces.AddNamespace('w', $w)
        foreach ($paragraph in $bodyXml.SelectNodes('//w:p', $namespaces)) {
            $style = $paragraph.SelectSingleNode('w:pPr/w:pStyle', $namespaces)
            if ($null -eq $style -or $style.GetAttribute('val', $w) -notin @('TableCaption', 'ImageCaption')) {
                continue
            }
            $caption = ($paragraph.SelectNodes('.//w:t', $namespaces) | ForEach-Object { $_.InnerText }) -join ''
            if ($caption -notmatch '^(Tabla|Ilustración) ([0-9]+)\. (.+)$') { continue }
            $label = $Matches[1]
            $number = $Matches[2]
            $title = $Matches[3]
            [void]$style.SetAttribute('val', $w, 'Descripcin')
            foreach ($child in @($paragraph.ChildNodes)) {
                if ($child.LocalName -ne 'pPr') { [void]$paragraph.RemoveChild($child) }
            }
            Add-CaptionRun $bodyXml $paragraph 'text' ($label + ' ')
            Add-CaptionRun $bodyXml $paragraph 'field' 'begin'
            Add-CaptionRun $bodyXml $paragraph 'instruction' (' SEQ ' + $label + ' \* ARABIC ')
            Add-CaptionRun $bodyXml $paragraph 'field' 'separate'
            Add-CaptionRun $bodyXml $paragraph 'text' $number
            Add-CaptionRun $bodyXml $paragraph 'field' 'end'
            Add-CaptionRun $bodyXml $paragraph 'text' ('. ' + $title)
        }
        $entry.Delete()
        $entry = $archive.CreateEntry('word/document.xml')
        $writer = [IO.StreamWriter]::new($entry.Open(), [Text.UTF8Encoding]::new($false))
        $bodyXml.Save($writer)
        $writer.Close()
    }
    finally { $archive.Dispose() }

    if (Test-Path -LiteralPath $outputFullPath -PathType Leaf) {
        Remove-Item -LiteralPath $outputFullPath -Force
    }
    Copy-Item -LiteralPath $templateFullPath -Destination $outputFullPath

    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.ScreenUpdating = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($outputFullPath, $false, $false)

    $coverTitle = 'ESPECIFICACIÓN DE REQUERIMIENTOS DE SOFTWARE PARA SOA CON SOAP EN JAVA SIN BDD'
    $eurekaTitle = 'ESPECIFICACIÓN DE REQUERIMIENTOS DE SOFTWARE PARA CELULARES Y BANQUITO REST .NET CON BASE DE DATOS'
    $titleUpdated = $false
    for ($i = 1; $i -le $document.Shapes.Count; $i++) {
        $shape = $document.Shapes.Item($i)
        try {
            if ($shape.TextFrame.HasText -ne 0) {
                $find = $shape.TextFrame.TextRange.Find
                $find.ClearFormatting()
                $find.Replacement.ClearFormatting()
                $titleUpdated = $find.Execute($coverTitle, $false, $false, $false, $false, $false, $true, 1, $false, $eurekaTitle, 2) -or $titleUpdated
            }
        }
        catch { }
    }
    if (-not $titleUpdated) {
        throw 'No se encontró el título de la plantilla en la carátula.'
    }

    # Keep the first page from the template and replace its old body with the generated Celulares content.
    $bodyStart = $document.GoTo(1, 1, 2).Start
    $bodyEnd = $document.Content.End - 1
    if ($bodyStart -ge $bodyEnd) {
        throw 'No se pudo determinar el inicio del cuerpo después de la carátula.'
    }
    $document.Range($bodyStart, $bodyEnd).Delete() | Out-Null
    $insertRange = $document.Range($bodyStart, $bodyStart)
    $insertRange.InsertFile($bodyPath) | Out-Null

    foreach ($table in $document.Tables) {
        $table.Range.ParagraphFormat.Alignment = 0
        $table.Rows.AllowBreakAcrossPages = 0
        $table.Rows.Item(1).HeadingFormat = -1
        $table.Rows.Item(1).Range.ParagraphFormat.KeepWithNext = -1
        $table.Rows.Item($table.Rows.Count).Range.ParagraphFormat.KeepWithNext = 0
        if ($table.Columns.Count -eq 2) {
            $setup = $table.Range.Sections.Item(1).PageSetup
            $width = $setup.PageWidth - $setup.LeftMargin - $setup.RightMargin
            $isRequirement = $table.Cell(2, 1).Range.Text -match 'Identificador'
            $firstWidth = if ($isRequirement) { $width * 0.24 } else { $width * 0.30 }
            $table.AllowAutoFit = $false
            $table.PreferredWidthType = 3
            $table.PreferredWidth = $width
            $table.Columns.Item(1).SetWidth($firstWidth, 0)
            $table.Columns.Item(2).SetWidth(($width - $firstWidth), 0)
            if ($isRequirement) {
                $table.Range.ParagraphFormat.KeepWithNext = -1
                $table.Rows.Item($table.Rows.Count).Range.ParagraphFormat.KeepWithNext = 0
            }
        }
    }
    foreach ($paragraph in $document.Paragraphs) {
        $paragraph.Format.KeepTogether = -1
        $styleName = ''
        try { $styleName = [string]$paragraph.Range.Style.NameLocal }
        catch { continue }
        if ($styleName -match 'Heading|Título') {
            $paragraph.Format.KeepWithNext = -1
        }
        if ($styleName -match 'Caption|Leyenda|Descripción') {
            $paragraph.Format.KeepWithNext = if ($paragraph.Range.Text -match '^Tabla ') { -1 } else { 0 }
        }
    }
    foreach ($image in $document.InlineShapes) {
        $image.Range.ParagraphFormat.KeepTogether = -1
        $image.Range.ParagraphFormat.KeepWithNext = -1
    }

    $findHeading = $document.Content.Find
    $findHeading.ClearFormatting()
    $findHeading.Replacement.ClearFormatting()
    $findHeading.Execute('Table of Contents', $false, $false, $false, $false, $false, $true, 1, $false, 'ÍNDICE DE CONTENIDOS', 2) | Out-Null
    $document.Fields.Update() | Out-Null
    foreach ($figures in $document.TablesOfFigures) { $figures.Update() }
    foreach ($toc in $document.TablesOfContents) { $toc.Update() }
    $document.Repaginate()
    foreach ($figures in $document.TablesOfFigures) { $figures.Update() }
    foreach ($toc in $document.TablesOfContents) { $toc.Update() }
    foreach ($figures in $document.TablesOfFigures) {
        $figures.Range.Font.Size = 10
        $figures.Range.ParagraphFormat.SpaceBefore = 0
        $figures.Range.ParagraphFormat.SpaceAfter = 0
        $figures.Range.ParagraphFormat.LineSpacingRule = 0
        $figures.Range.ParagraphFormat.KeepWithNext = 0
        $figures.Range.ParagraphFormat.KeepTogether = -1
    }
    $document.Repaginate()
    foreach ($figures in $document.TablesOfFigures) { $figures.UpdatePageNumbers() }
    foreach ($toc in $document.TablesOfContents) { $toc.UpdatePageNumbers() }
    $document.Save()

    Write-Output ('ERS generado desde la plantilla: ' + $outputFullPath)
    Write-Output ('Páginas: ' + $document.ComputeStatistics(2))
}
finally {
    if ($null -ne $document) {
        $document.Close(0)
        [Runtime.InteropServices.Marshal]::ReleaseComObject($document) | Out-Null
    }
    if ($null -ne $word) {
        $word.Quit()
        [Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    if (Test-Path -LiteralPath $bodyPath -PathType Leaf) {
        Remove-Item -LiteralPath $bodyPath -Force
    }
}

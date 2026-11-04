[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$DraftDirectory,
    [Parameter(Mandatory)][string]$RenderDirectory,
    [string]$FilesJson = '[]',
    [switch]$UpdateFieldsOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$DraftDirectory = [System.IO.Path]::GetFullPath($DraftDirectory)
$RenderDirectory = [System.IO.Path]::GetFullPath($RenderDirectory)
New-Item -ItemType Directory -Force -Path $RenderDirectory | Out-Null

$requestedFiles = @($FilesJson | ConvertFrom-Json)
$selectedFiles = if ($requestedFiles.Count -gt 0) {
    @($requestedFiles | ForEach-Object { [System.IO.Path]::GetFullPath((Join-Path $DraftDirectory ([string]$_))) })
} else {
    @(Get-ChildItem -LiteralPath $DraftDirectory -File | Where-Object { $_.Extension -in '.docx', '.pptx' } | ForEach-Object FullName)
}

$word = $null
$powerPoint = $null
try {
    $documents = @($selectedFiles | Where-Object { [System.IO.Path]::GetExtension($_) -ieq '.docx' })
    if ($documents.Count -gt 0) {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $word.DisplayAlerts = 0
        foreach ($path in $documents) {
            $document = $null
            try {
                $document = $word.Documents.Open($path, $false, $false, $false)
                $document.Fields.Update() | Out-Null
                for ($index = 1; $index -le $document.TablesOfContents.Count; $index++) {
                    $document.TablesOfContents.Item($index).Update()
                }
                for ($index = 1; $index -le $document.TablesOfFigures.Count; $index++) {
                    $document.TablesOfFigures.Item($index).Update()
                }
                $document.Repaginate()
                $document.Save()
                if (-not $UpdateFieldsOnly) {
                    $pdfPath = Join-Path $RenderDirectory ([System.IO.Path]::GetFileNameWithoutExtension($path) + '.pdf')
                    $document.ExportAsFixedFormat($pdfPath, 17)
                    Write-Output ("Word: {0} páginas · {1}" -f $document.ComputeStatistics(2), [System.IO.Path]::GetFileName($path))
                }
            } finally {
                if ($null -ne $document) {
                    $document.Close($false)
                    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
                }
            }
        }
    }

    $presentations = @($selectedFiles | Where-Object { [System.IO.Path]::GetExtension($_) -ieq '.pptx' })
    if ($presentations.Count -gt 0) {
        $powerPoint = New-Object -ComObject PowerPoint.Application
        $powerPoint.Visible = -1
        foreach ($path in $presentations) {
            $presentation = $null
            try {
                $presentation = $powerPoint.Presentations.Open($path, -1, 0, 0)
                $pdfPath = Join-Path $RenderDirectory ([System.IO.Path]::GetFileNameWithoutExtension($path) + '.pdf')
                $presentation.SaveAs($pdfPath, 32)
                Write-Output ("PowerPoint: {0} diapositivas · {1}" -f $presentation.Slides.Count, [System.IO.Path]::GetFileName($path))
            } finally {
                if ($null -ne $presentation) {
                    $presentation.Close()
                    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation)
                }
            }
        }
    }
} finally {
    if ($null -ne $powerPoint) {
        $powerPoint.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint)
    }
    if ($null -ne $word) {
        $word.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
}

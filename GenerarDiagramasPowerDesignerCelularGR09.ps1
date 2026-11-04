<#
.SYNOPSIS
    Script maestro que ejecuta la generacion completa de diagramas PowerDesigner:
    1. GenerarModelosCelularGR09.ps1 (MER: CDM, LDM, PDM y PNGs)
    2. GenerarDiagramasCelularGR09.vbs (UML: Casos de Uso, Actividad, Secuencia, Clases, Arquitectura)
#>
[CmdletBinding()]
param([string]$Raiz = $PSScriptRoot)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Output "=== 1. Generando Modelos MER (CDM, LDM, PDM) ==="
& powershell -ExecutionPolicy Bypass -File (Join-Path $Raiz "GenerarModelosCelularGR09.ps1") -Raiz $Raiz

Write-Output ""
Write-Output "=== 2. Generando Modelos UML (Casos de Uso, Actividad, Secuencia, Clases, Arquitectura) ==="
& "C:\Windows\SysWOW64\cscript.exe" //nologo (Join-Path $Raiz "GenerarDiagramasCelularGR09.vbs")

Write-Output ""
Write-Output "=== Todos los modelos PowerDesigner y diagramas PNG generados con exito ==="

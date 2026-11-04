param([switch]$IniciarApis)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path .env)) { Copy-Item .env.example .env }
$line = Get-Content .env | Where-Object { $_ -match '^MSSQL_SA_PASSWORD=' } | Select-Object -First 1
if (!$line) { throw 'Falta MSSQL_SA_PASSWORD en .env' }
$password = $line.Substring('MSSQL_SA_PASSWORD='.Length)
& docker compose up -d --wait
if ($LASTEXITCODE) { throw 'SQL Server no pudo iniciar' }
$scripts = @('03. BDD/01_CrearBases.sql','03. BDD/03_MigrarImagenes.sql','03. BDD/02_DatosPrueba.sql','03. BDD/BanQuito/BanQuito_01_CrearBase.sql','03. BDD/BanQuito/BanQuito_02_DatosPrueba.sql')
foreach ($script in $scripts) {
    Get-Content -Raw -LiteralPath $script | & docker compose exec -T sqlserver bash -c '/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -b'
    if ($LASTEXITCODE) { throw "Fallo SQL: $script" }
}
if ($IniciarApis) {
    foreach ($entry in @(@('BanQuito.Api','BanQuitoCore'),@('Comercializadora.Api','ComercializadoraCelulares'))) {
        $env:ConnectionStrings__BaseDatos = "Server=127.0.0.1,19433;Database=$($entry[1]);User Id=sa;Password=$password;Encrypt=True;TrustServerCertificate=True"
        Start-Process dotnet -ArgumentList @('run','--project',('"04. SERVIDOR/'+$entry[0]+'/'+$entry[0]+'.csproj"')) -WindowStyle Hidden
    }
    Remove-Item Env:ConnectionStrings__BaseDatos
}

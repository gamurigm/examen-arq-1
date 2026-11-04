[CmdletBinding()]
param(
    [uri]$ApiUrl = 'http://127.0.0.1:19102/',
    [switch]$Reemplazar
)

$ErrorActionPreference = 'Stop'
$assets = Join-Path (Split-Path -Parent $PSScriptRoot) 'assets/celulares'
$imagenes = Get-Content -Raw -LiteralPath (Join-Path $assets 'catalogo.json') | ConvertFrom-Json
$baseUrl = $ApiUrl.AbsoluteUri.TrimEnd('/')
$catalogo = Invoke-RestMethod "$baseUrl/api/celulares"
$http = [System.Net.Http.HttpClient]::new()
try {
    foreach ($imagen in $imagenes) {
        $coincidencias = @($catalogo | Where-Object nombre -EQ $imagen.celular)
        if ($coincidencias.Count -ne 1) {
            throw "Se esperaba un celular activo con nombre: $($imagen.celular)"
        }
        $celular = $coincidencias[0]
        if ($celular.imagenUrl -and -not $Reemplazar) {
            Write-Output "Conservada la imagen existente: $($imagen.celular)"
            continue
        }
        $archivo = Join-Path $assets $imagen.archivo
        if ((Get-FileHash -LiteralPath $archivo -Algorithm SHA256).Hash -ne $imagen.sha256) {
            throw "La imagen no coincide con su SHA-256: $archivo"
        }
        $form = [System.Net.Http.MultipartFormDataContent]::new()
        try {
            $contenido = [System.Net.Http.ByteArrayContent]::new([IO.File]::ReadAllBytes($archivo))
            $contenido.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::new('image/jpeg')
            $form.Add($contenido, 'archivo', $imagen.archivo)
            $url = "$baseUrl/api/celulares/$($celular.id)/imagen"
            $respuesta = $http.PutAsync($url, $form).GetAwaiter().GetResult()
            try { $null = $respuesta.EnsureSuccessStatusCode() }
            finally { $respuesta.Dispose() }
            $datos = $http.GetByteArrayAsync($url).GetAwaiter().GetResult()
            $hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($datos))
            if ($hash -ne $imagen.sha256) { throw "La descarga no coincide: $($imagen.celular)" }
            Write-Output "Imagen guardada y verificada por SHA-256: $($imagen.celular)"
        }
        finally { $form.Dispose() }
    }
}
finally { $http.Dispose() }

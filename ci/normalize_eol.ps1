# Convierte CRLF -> LF en los scripts bash del CI.
# Se ejecuta en el HOST (Windows) porque Docker Desktop no permite
# renombrar/borrar archivos en bind-mounts 9p desde el contenedor.
$ErrorActionPreference = 'Stop'

Get-ChildItem -Path ci -Filter *.sh | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw
    if ($content -match "`r") {
        $content = $content -replace "`r`n", "`n"
        Set-Content -Path $_.FullName -Value $content -NoNewline
        Write-Host "Normalizado: $($_.Name)"
    } else {
        Write-Host "OK (LF): $($_.Name)"
    }
}

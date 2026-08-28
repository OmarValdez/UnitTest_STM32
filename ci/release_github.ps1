param([Parameter(Mandatory = $true)][string]$Version)

$ErrorActionPreference = "Stop"
$token = $env:GHT
if (-not $token) { Write-Error "Falta GITHUB_TOKEN (credential github-token)"; exit 1 }

# --- Repositorio desde el remote origin ---
$remote = git remote get-url origin
if ($remote -match 'github\.com[:/]([^/]+)/(.+?)(\.git)?$') {
    $owner = $Matches[1]
    $repoName = $Matches[2]
} else {
    Write-Error "No se pudo determinar el repo de github desde: $remote"
    exit 1
}
$api = "https://api.github.com/repos/$owner/$repoName"
$headers = @{ Authorization = "Bearer $token"; Accept = "application/vnd.github+json" }
Write-Host "Repo: $owner/$repoName  tag: $Version"

# --- Changelog desde el agente (git disponible en Windows) ---
try { $prev = git describe --tags --abbrev=0 HEAD~1 2>$null } catch { $prev = $null }
if ($prev) { $log = git log --oneline "$prev..HEAD" } else { $log = git log --oneline -10 }
$changelog = ($log -join "`n")
Set-Content -Path build/changelog.md -Value $changelog -Encoding utf8

# --- Release existente? (idempotente: reutiliza y repuebla) ---
$rel = $null
try { $rel = Invoke-RestMethod -Uri "$api/releases/tags/$Version" -Headers $headers } catch { }
if ($rel) {
    Write-Host "Release existente reutilizado: $($rel.html_url)"
    $relId = $rel.id
    $upload = $rel.upload_url -replace '\{\?.*$', ''
    foreach ($a in (Invoke-RestMethod -Uri "$api/releases/$relId/assets" -Headers $headers)) {
        Write-Host "Eliminando asset previo: $($a.name)"
        Invoke-RestMethod -Uri "$api/releases/assets/$($a.id)" -Method Delete -Headers $headers | Out-Null
    }
} else {
    $body = @{
        tag_name   = $Version
        name       = "Release $Version"
        body       = $changelog
        draft      = $false
        prerelease = $false
    } | ConvertTo-Json
    $rel = Invoke-RestMethod -Uri "$api/releases" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    $upload = $rel.upload_url -replace '\{\?.*$', ''
    Write-Host "Release creado: $($rel.html_url)"
}

# --- Assets a subir ---
$files = @(
    "build/DockerDebug/ST_UnitTest.elf",
    "build/DockerDebug/ST_UnitTest.bin",
    "build/DockerDebug/ST_UnitTest.hex",
    "build/DockerDebug/ST_UnitTest.elf.sig",
    "build/DockerDebug/ST_UnitTest.bin.sig",
    "build/DockerDebug/ST_UnitTest.hex.sig",
    "build/signatures.json",
    "build/evidence/sbom.json"
)
$evZip = Get-ChildItem build/evidence/evidencia-*.zip -ErrorAction SilentlyContinue | Select-Object -First 1
if ($evZip) { $files += $evZip.FullName }
$files += "build/changelog.md"
$files += "config/release_pubkey.pem"

foreach ($f in $files) {
    if (-not (Test-Path $f)) { Write-Host "OMITIDO (no existe): $f"; continue }
    $name = Split-Path $f -Leaf
    Write-Host "Subiendo $name ..."
    $out = curl.exe -sS -w "`nHTTP_STATUS:%{http_code}" `
        -H "Authorization: Bearer $token" `
        -H "Content-Type: application/octet-stream" `
        --data-binary "@$f" "$upload`?name=$name"
    Write-Host $out
    if ($out -notmatch 'HTTP_STATUS:2\d\d') { Write-Error "Fallo al subir $name"; exit 1 }
}

Write-Host "Release $Version completo: $($rel.html_url)"

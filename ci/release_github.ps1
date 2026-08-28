param(
    [Parameter(Mandatory = $true)][string]$Version,
    [Parameter(Mandatory = $true)][string]$Token
)

$ErrorActionPreference = "Stop"

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

# --- Changelog desde el agente (git disponible en Windows) ---
try { $prev = git describe --tags --abbrev=0 HEAD~1 2>$null } catch { $prev = $null }
if ($prev) { $log = git log --oneline "$prev..HEAD" } else { $log = git log --oneline -10 }
$changelog = ($log -join "`n")
Set-Content -Path build/changelog.md -Value $changelog -Encoding utf8

# --- Crear release ---
$body = @{
    tag_name   = $Version
    name       = "Release $Version"
    body       = $changelog
    draft      = $false
    prerelease = $false
} | ConvertTo-Json

$headers = @{ Authorization = "Bearer $Token"; Accept = "application/vnd.github+json" }
$rel = Invoke-RestMethod -Uri "$api/releases" -Method Post -Headers $headers -Body $body -ContentType "application/json"
$upload = $rel.upload_url -replace '\{\?.*$', ''

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
    if (Test-Path $f) {
        $name = Split-Path $f -Leaf
        Invoke-RestMethod -Uri "$upload`?name=$name" -Method Post -Headers $headers -ContentType "application/octet-stream" -InFile $f
        Write-Host "Subido: $name"
    } else {
        Write-Host "Omitido (no existe): $f"
    }
}

Write-Host "Release $Version creado: $($rel.html_url)"

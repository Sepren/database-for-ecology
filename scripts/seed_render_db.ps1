param(
    [string]$RenderDatabaseUrl = ""
)

$ErrorActionPreference = "Stop"

Set-Location -LiteralPath (Join-Path $PSScriptRoot "..")

if (-not $RenderDatabaseUrl) {
    $RenderDatabaseUrl = $env:RENDER_DATABASE_URL
}

if (-not $RenderDatabaseUrl) {
    Write-Host "Paste Render External Database URL (postgres://...):"
    $RenderDatabaseUrl = Read-Host
}

if (-not $RenderDatabaseUrl) {
    throw "RENDER_DATABASE_URL is required."
}

if (-not (Test-Path -LiteralPath "data/merged_documents.xlsx")) {
    throw "Missing local file data/merged_documents.xlsx"
}

$env:RENDER_DATABASE_URL = $RenderDatabaseUrl
python scripts/seed_render_db.py

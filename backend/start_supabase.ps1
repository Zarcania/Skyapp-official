#!/usr/bin/env powershell

# Démarre le serveur FastAPI (Supabase) avec diagnostics utiles
Write-Host "==> Démarrage du backend SkyApp (Supabase) ..." -ForegroundColor Cyan

try {
  Set-Location -Path $PSScriptRoot
  Write-Host ("Répertoire courant: {0}" -f (Get-Location)) -ForegroundColor DarkGray

  # Charger les variables d'environnement depuis .env
  if (Test-Path ".env") {
    Write-Host "Chargement du fichier .env..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
      if ($_ -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        if (-not $key.StartsWith('#') -and $key -ne '') {
          [Environment]::SetEnvironmentVariable($key, $value, 'Process')
          Write-Host "  $key = OK" -ForegroundColor DarkGray
        }
      }
    }
  }

  # Afficher la présence des variables d'environnement (sans leurs valeurs)
  if ($env:SUPABASE_URL) { Write-Host "Env SUPABASE_URL: OK" -ForegroundColor Green } else { Write-Host "Env SUPABASE_URL: MISSING" -ForegroundColor Red }
  if ($env:SUPABASE_ANON_KEY) { Write-Host "Env SUPABASE_ANON_KEY: OK" -ForegroundColor Green } else { Write-Host "Env SUPABASE_ANON_KEY: MISSING" -ForegroundColor Red }

  # Autoriser le login dev localement si absent
  if (-not (Test-Path Env:ALLOW_DEV_LOGIN)) { $env:ALLOW_DEV_LOGIN = '1' }
  Write-Host ("ALLOW_DEV_LOGIN=$($env:ALLOW_DEV_LOGIN)") -ForegroundColor DarkGray

  # Logs immédiats
  $env:PYTHONUNBUFFERED = '1'

  # Lancer uvicorn avec logs clairs
  Write-Host "Lancement uvicorn (http://127.0.0.1:8001) ..." -ForegroundColor Yellow
  python -X dev -m uvicorn server_supabase:app --host 127.0.0.1 --port 8001 --log-level info
} catch {
  Write-Host "Échec du démarrage:" -ForegroundColor Red
  Write-Host $_ -ForegroundColor Red
  exit 1
}

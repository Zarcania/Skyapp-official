#!/usr/bin/env powershell

<#
  Démarre SkyApp (backend Supabase + frontend) sous Windows/PowerShell.
  - Backend: uvicorn server_supabase:app (127.0.0.1:8001)
  - Frontend: npm start (port défini dans frontend/.env.local, par défaut 3002)
#>

param(
  [int]$BackendPort = 8001,
  [int]$FrontendPort = 3002,
  [switch]$KillExisting,
  [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg){ Write-Host $msg -ForegroundColor Cyan }
function Write-Ok($msg){ Write-Host $msg -ForegroundColor Green }
function Write-Warn($msg){ Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg){ Write-Host $msg -ForegroundColor Red }

try {
  $root = Split-Path -Parent $MyInvocation.MyCommand.Path
  $backendDir = Join-Path $root 'backend'
  $frontendDir = Join-Path $root 'frontend'

  Write-Info "==> Démarrage SkyApp (backend + frontend)"
  Write-Host "Racine: $root" -ForegroundColor DarkGray

  if ($KillExisting) {
    Write-Warn "Arrêt des processus éventuels (ports $BackendPort / $FrontendPort) ..."
    try {
      $p1 = (Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue).OwningProcess
      if ($p1) { Stop-Process -Id $p1 -Force }
    } catch {}
    try {
      $p2 = (Get-NetTCPConnection -LocalPort $FrontendPort -State Listen -ErrorAction SilentlyContinue).OwningProcess
      if ($p2) { Stop-Process -Id $p2 -Force }
    } catch {}
    Write-Ok "Ports libérés (si des processus existaient)."
  }

  # 1) Backend -----------------------------------------------------------------
  Write-Info "[1/3] Backend: uvicorn @ 127.0.0.1:$BackendPort"
  $env:ALLOW_DEV_LOGIN = '1'
  $env:PYTHONUNBUFFERED = '1'
  $backendArgs = "-m uvicorn server_supabase:app --host 127.0.0.1 --port $BackendPort --log-level info"
  Start-Process -FilePath python -ArgumentList $backendArgs -WorkingDirectory $backendDir -WindowStyle Normal | Out-Null
  Write-Host "Backend en cours de démarrage..." -ForegroundColor DarkGray

  $healthUrl = "http://127.0.0.1:$BackendPort/api/health"
  $maxTries = 30  # Augmenté de 20 à 30 (21 secondes au lieu de 14)
  $ok = $false
  for ($i=1; $i -le $maxTries; $i++) {
    Start-Sleep -Milliseconds 700
    Write-Host "." -NoNewline -ForegroundColor DarkGray
    try {
      $resp = Invoke-WebRequest -UseBasicParsing $healthUrl -TimeoutSec 3 -ErrorAction SilentlyContinue
      if ($resp.StatusCode -eq 200) { $ok = $true; Write-Host ""; break }
    } catch {}
  }
  if ($ok) { 
    Write-Ok "✅ Backend OK: $healthUrl" 
  } else { 
    Write-Err "❌ Backend non joignable à $healthUrl après $maxTries tentatives"
    Write-Warn "Le backend peut prendre plus de temps. Vérifie la fenêtre du backend."
  }

  # 2) Frontend ---------------------------------------------------------------
  Write-Info "[2/3] Frontend: npm start (port attendu $FrontendPort)"
  if (-not (Test-Path (Join-Path $frontendDir 'package.json'))) {
    throw "package.json introuvable dans $frontendDir"
  }

  # S'assurer d'un .env.local cohérent (ne réécrit pas s'il existe déjà)
  $envLocalPath = Join-Path $frontendDir '.env.local'
  # Extraire SUPABASE_URL et SUPABASE_ANON_KEY depuis backend/.env si possible
  $backendEnvPath = Join-Path $backendDir '.env'
  $supUrl = $null; $supAnon = $null
  if (Test-Path $backendEnvPath) {
    $lines = Get-Content $backendEnvPath -ErrorAction SilentlyContinue
    foreach ($l in $lines) {
      if ($l -match '^\s*SUPABASE_URL\s*=\s*(.+)$') { $supUrl = $Matches[1].Trim() }
      if ($l -match '^\s*SUPABASE_ANON_KEY\s*=\s*(.+)$') { $supAnon = $Matches[1].Trim() }
    }
  }

  if (-not (Test-Path $envLocalPath)) {
    $content = @(
      "PORT=$FrontendPort",
      "BROWSER=none",
      "REACT_APP_BACKEND_URL=http://127.0.0.1:$BackendPort"
    )
    if ($supUrl) { $content += "REACT_APP_SUPABASE_URL=$supUrl" }
    if ($supAnon) { $content += "REACT_APP_SUPABASE_ANON_KEY=$supAnon" }
    ($content -join "`n") | Out-File -FilePath $envLocalPath -Encoding UTF8
    Write-Host ".env.local créé avec variables FRONT et SUPABASE." -ForegroundColor DarkGray
  } else {
    # Upsert des variables dans .env.local existant
    $envText = Get-Content $envLocalPath -Raw -ErrorAction SilentlyContinue
    function Upsert-Line($text, $key, $val) {
      if (-not $val) { return $text }
      $pattern = "(?m)^$key=.*$"
      $replacement = "$key=$val"
      if ($text -match $pattern) { return ([regex]::Replace($text, $pattern, $replacement)) }
      else { return ($text.TrimEnd()+"`n"+$replacement) }
    }
    $envText = Upsert-Line $envText 'PORT' $FrontendPort
    $envText = Upsert-Line $envText 'BROWSER' 'none'
    $envText = Upsert-Line $envText 'REACT_APP_BACKEND_URL' "http://127.0.0.1:$BackendPort"
    if ($supUrl) { $envText = Upsert-Line $envText 'REACT_APP_SUPABASE_URL' $supUrl }
    if ($supAnon) { $envText = Upsert-Line $envText 'REACT_APP_SUPABASE_ANON_KEY' $supAnon }
    $envText | Out-File -FilePath $envLocalPath -Encoding UTF8
    Write-Host ".env.local mis à jour (ports + Supabase)." -ForegroundColor DarkGray
  }

  # Lancer npm start dans une nouvelle fenêtre PowerShell (plus stable que cmd.exe)
  Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","cd '$frontendDir'; npm start" -WindowStyle Normal | Out-Null
  Write-Host "Frontend en cours de démarrage (nouvelle fenêtre PowerShell)..." -ForegroundColor DarkGray
  
  # Attendre que le frontend soit prêt
  Write-Host "Vérification du frontend..." -ForegroundColor DarkGray
  $frontendReady = $false
  for ($i=1; $i -le 30; $i++) {
    Start-Sleep -Milliseconds 1000
    try {
      $conn = Get-NetTCPConnection -LocalPort $FrontendPort -State Listen -ErrorAction SilentlyContinue
      if ($conn) { $frontendReady = $true; break }
    } catch {}
  }
  if ($frontendReady) { Write-Ok "Frontend OK: http://localhost:$FrontendPort" } 
  else { Write-Warn "Frontend toujours en démarrage (peut prendre 30-60s)..." }

  # 3) Résumé -----------------------------------------------------------------
  Write-Host ""; Write-Ok "[3/3] Tout est lancé."
  Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
  Write-Host "Backend (API): " -NoNewline -ForegroundColor White
  Write-Host "http://127.0.0.1:$BackendPort/api/health" -ForegroundColor Cyan
  Write-Host "Docs API:      " -NoNewline -ForegroundColor White
  Write-Host "http://127.0.0.1:$BackendPort/docs" -ForegroundColor Cyan
  Write-Host "Frontend:      " -NoNewline -ForegroundColor White
  Write-Host "http://localhost:$FrontendPort" -ForegroundColor Cyan
  Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
  Write-Host ""
  Write-Host "💡 " -NoNewline -ForegroundColor Yellow
  Write-Host "Laisse les fenêtres PowerShell ouvertes pour garder les serveurs actifs." -ForegroundColor White
  Write-Host "⚠️  " -NoNewline -ForegroundColor Red
  Write-Host "Pour arrêter : ferme les fenêtres ou utilise " -NoNewline -ForegroundColor White
  Write-Host ".\stop_skyapp.ps1" -ForegroundColor Cyan
  Write-Host ""

  if ($OpenBrowser) {
    try {
      Start-Sleep -Seconds 2
      Start-Process "http://localhost:$FrontendPort"
      Write-Ok "✅ Navigateur ouvert sur http://localhost:$FrontendPort"
    } catch {
      Write-Warn "⚠️  Impossible d'ouvrir automatiquement le navigateur. Ouvre manuellement: http://localhost:$FrontendPort"
    }
  } else {
    Write-Host "💻 Ouvre ton navigateur sur: " -NoNewline -ForegroundColor Yellow
    Write-Host "http://localhost:$FrontendPort" -ForegroundColor Cyan
  }
  
  Write-Host ""
  Write-Host "🚀 SkyApp est prêt !" -ForegroundColor Green
  Write-Host ""
  Write-Host "Appuie sur une touche pour fermer cette fenêtre (les serveurs resteront actifs)..." -ForegroundColor DarkGray
  $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
  
} catch {
  Write-Err "❌ Échec du démarrage: $_"
  Write-Host ""
  Write-Host "Appuie sur une touche pour fermer..." -ForegroundColor DarkGray
  $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
  exit 1
}

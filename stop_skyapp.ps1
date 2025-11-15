#!/usr/bin/env powershell

<#
  Arrête proprement tous les serveurs SkyApp (backend + frontend)
#>

param(
  [int]$BackendPort = 8001,
  [int]$FrontendPort = 3002
)

$ErrorActionPreference = 'Continue'

function Write-Info($msg){ Write-Host $msg -ForegroundColor Cyan }
function Write-Ok($msg){ Write-Host $msg -ForegroundColor Green }
function Write-Warn($msg){ Write-Host $msg -ForegroundColor Yellow }

Write-Info "🛑 Arrêt de SkyApp..."
Write-Host ""

# Fonction pour arrêter un processus sur un port donné
function Stop-ProcessOnPort($port, $name) {
  try {
    $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($connection) {
      $processId = $connection.OwningProcess
      $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
      if ($process) {
        Write-Info "   Arrêt du $name (PID: $processId, Port: $port)..."
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
        Write-Ok "   ✅ $name arrêté"
        return $true
      }
    }
    Write-Warn "   ⚠️  $name non trouvé sur le port $port"
    return $false
  } catch {
    Write-Warn "   ⚠️  Erreur lors de l'arrêt du $name : $_"
    return $false
  }
}

# Arrêter le backend
$backendStopped = Stop-ProcessOnPort $BackendPort "Backend"

# Arrêter le frontend
$frontendStopped = Stop-ProcessOnPort $FrontendPort "Frontend"

# Arrêter tous les processus Python et Node restants (au cas où)
Write-Info "`n🧹 Nettoyage des processus restants..."
$pythonProcesses = Get-Process | Where-Object { $_.ProcessName -like '*python*' } -ErrorAction SilentlyContinue
$nodeProcesses = Get-Process | Where-Object { $_.ProcessName -like '*node*' } -ErrorAction SilentlyContinue

if ($pythonProcesses) {
  Write-Info "   Arrêt de $($pythonProcesses.Count) processus Python..."
  $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
  Write-Ok "   ✅ Processus Python arrêtés"
}

if ($nodeProcesses) {
  Write-Info "   Arrêt de $($nodeProcesses.Count) processus Node.js..."
  $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
  Write-Ok "   ✅ Processus Node.js arrêtés"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if ($backendStopped -or $frontendStopped -or $pythonProcesses -or $nodeProcesses) {
  Write-Ok "✅ SkyApp arrêté avec succès !"
} else {
  Write-Warn "⚠️  Aucun serveur SkyApp n'était actif"
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""
Write-Host "💡 Pour redémarrer SkyApp, utilise: " -NoNewline -ForegroundColor Yellow
Write-Host ".\start_skyapp.ps1" -ForegroundColor Cyan
Write-Host ""

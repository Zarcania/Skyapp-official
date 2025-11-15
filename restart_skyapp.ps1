#!/usr/bin/env powershell

<#
  Redémarre SkyApp en arrêtant puis relançant backend + frontend
#>

param(
  [int]$BackendPort = 8001,
  [int]$FrontendPort = 3002,
  [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'

Write-Host "🔄 Redémarrage de SkyApp..." -ForegroundColor Cyan
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stop = Join-Path $root 'stop_skyapp.ps1'
$start = Join-Path $root 'start_skyapp.ps1'

if (-not (Test-Path $stop)) { throw "stop_skyapp.ps1 introuvable dans $root" }
if (-not (Test-Path $start)) { throw "start_skyapp.ps1 introuvable dans $root" }

Write-Host "📍 Étape 1/2 : Arrêt des serveurs..." -ForegroundColor Yellow
Write-Host ""
& powershell -NoProfile -ExecutionPolicy Bypass -File $stop -BackendPort $BackendPort -FrontendPort $FrontendPort

Write-Host ""
Write-Host "📍 Étape 2/2 : Démarrage des serveurs..." -ForegroundColor Yellow
Write-Host ""
Start-Sleep -Seconds 2

# Construire proprement les arguments pour le start (les switchs doivent 
# être passés sans valeur, uniquement s'ils sont présents)
$startArgs = @('-BackendPort', $BackendPort, '-FrontendPort', $FrontendPort, '-KillExisting')
if ($OpenBrowser) { $startArgs += '-OpenBrowser' }

& powershell -NoProfile -ExecutionPolicy Bypass -File $start @startArgs

Write-Host "Redémarrage terminé." -ForegroundColor Green

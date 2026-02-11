# ========================================
# SCRIPT DE REDEMARRAGE SKYAPP
# ========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  REDEMARRAGE DE SKYAPP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$root = $PSScriptRoot

# Etape 1: Arreter
Write-Host "[1/2] Arret des serveurs..." -ForegroundColor Yellow
& "$root\stop_skyapp.ps1"

# Attendre que tous les processus se terminent proprement
Write-Host "`nAttente de l'arret complet..." -ForegroundColor DarkGray
Start-Sleep -Seconds 3

# Etape 2: Demarrer
Write-Host "`n[2/2] Demarrage des serveurs..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
& "$root\start_skyapp.ps1"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  REDEMARRAGE TERMINE !" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

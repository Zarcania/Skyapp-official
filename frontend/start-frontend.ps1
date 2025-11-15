#!/usr/bin/env powershell

# Script pour démarrer l'application frontend
Write-Host "Démarrage de l'application frontend..." -ForegroundColor Green

# Changer vers le répertoire frontend
Set-Location -Path $PSScriptRoot
Write-Host "Répertoire courant: $(Get-Location)" -ForegroundColor Yellow

# Vérifier la présence du package.json
if (Test-Path "./package.json") {
    Write-Host "package.json trouvé" -ForegroundColor Green
    
    # Démarrer l'application
    Write-Host "Lancement de npm start..." -ForegroundColor Yellow
    npm start
} else {
    Write-Host "Erreur: package.json non trouvé dans le répertoire courant" -ForegroundColor Red
    Write-Host "Répertoire courant: $(Get-Location)" -ForegroundColor Red
    Get-ChildItem | Select-Object Name, Mode
}
# ========================================
# CONFIGURATION DES ALIAS SKYAPP
# ========================================
# Ce script configure des alias PowerShell pour lancer Skyapp depuis n'importe où

# Obtenir le chemin dynamiquement
$skyappRoot = Split-Path $PSScriptRoot -Parent

# Créer des fonctions globales
function Global:Start-Skyapp {
    & "$skyappRoot\start_skyapp.ps1"
}

function Global:Stop-Skyapp {
    & "$skyappRoot\stop_skyapp.ps1"
}

function Global:Restart-Skyapp {
    & "$skyappRoot\restart_skyapp.ps1"
}

# Créer des alias courts
Set-Alias -Name "start-skyapp" -Value Start-Skyapp -Scope Global
Set-Alias -Name "stop-skyapp" -Value Stop-Skyapp -Scope Global
Set-Alias -Name "restart-skyapp" -Value Restart-Skyapp -Scope Global

Write-Host "`n✅ Alias Skyapp configurés avec succès !" -ForegroundColor Green
Write-Host "`nCommandes disponibles :" -ForegroundColor Cyan
Write-Host "  start-skyapp    - Démarrer Skyapp" -ForegroundColor Yellow
Write-Host "  stop-skyapp     - Arrêter Skyapp" -ForegroundColor Yellow
Write-Host "  restart-skyapp  - Redémarrer Skyapp" -ForegroundColor Yellow
Write-Host "`nTu peux maintenant utiliser ces commandes depuis n'importe quel dossier !`n" -ForegroundColor Green

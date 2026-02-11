# Script PowerShell pour vérifier et créer la table company_settings
# Usage: .\scripts\setup_company_settings.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURATION COMPANY SETTINGS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path ".\backend\server_supabase.py")) {
    Write-Host "❌ Erreur: Ce script doit être exécuté depuis la racine du projet" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Ce script va vous aider à configurer la table company_settings dans Supabase" -ForegroundColor Yellow
Write-Host ""
Write-Host "ÉTAPES À SUIVRE:" -ForegroundColor Green
Write-Host "1. Ouvrez https://app.supabase.com dans votre navigateur" -ForegroundColor White
Write-Host "2. Sélectionnez votre projet SkyApp" -ForegroundColor White
Write-Host "3. Cliquez sur 'SQL Editor' dans le menu de gauche" -ForegroundColor White
Write-Host "4. Cliquez sur '+ New query'" -ForegroundColor White
Write-Host "5. Copiez le SQL ci-dessous et collez-le dans l'éditeur" -ForegroundColor White
Write-Host "6. Cliquez sur 'Run' pour exécuter" -ForegroundColor White
Write-Host ""

# Lire le fichier SQL
$sqlFile = ".\migrations\create_company_settings.sql"

if (-not (Test-Path $sqlFile)) {
    Write-Host "❌ Fichier SQL non trouvé: $sqlFile" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SQL À COPIER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$sqlContent = Get-Content $sqlFile -Raw
Write-Host $sqlContent -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Copier dans le presse-papiers si possible
try {
    Set-Clipboard -Value $sqlContent
    Write-Host "✅ Le SQL a été copié dans votre presse-papiers !" -ForegroundColor Green
    Write-Host "   Vous pouvez maintenant le coller directement dans Supabase (Ctrl+V)" -ForegroundColor Yellow
} catch {
    Write-Host "ℹ️  Copiez manuellement le SQL ci-dessus" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Après avoir exécuté le SQL dans Supabase, redémarrez le backend:" -ForegroundColor Cyan
Write-Host "  .\scripts\restart_skyapp.ps1" -ForegroundColor White
Write-Host ""

# Attendre l'utilisateur
Write-Host "Appuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

#!/usr/bin/env pwsh
# Script pour créer la table mission_reports dans Supabase

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  CREATION TABLE MISSION_REPORTS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$migrationFile = "migrations/create_mission_reports_table.sql"

if (-not (Test-Path $migrationFile)) {
    Write-Host "❌ Fichier de migration introuvable: $migrationFile" -ForegroundColor Red
    exit 1
}

Write-Host "📄 Lecture du fichier de migration..." -ForegroundColor Yellow
$sqlContent = Get-Content $migrationFile -Raw

Write-Host "`n📋 Contenu SQL à exécuter:" -ForegroundColor Yellow
Write-Host $sqlContent -ForegroundColor Gray

Write-Host "`n⚠️  IMPORTANT: Vous devez exécuter ce SQL dans Supabase SQL Editor" -ForegroundColor Yellow
Write-Host "`n📍 Étapes:" -ForegroundColor Cyan
Write-Host "1. Ouvrez https://supabase.com/dashboard" -ForegroundColor White
Write-Host "2. Sélectionnez votre projet" -ForegroundColor White
Write-Host "3. Allez dans 'SQL Editor'" -ForegroundColor White
Write-Host "4. Créez une nouvelle requête" -ForegroundColor White
Write-Host "5. Collez le SQL ci-dessus" -ForegroundColor White
Write-Host "6. Cliquez sur 'RUN' pour exécuter" -ForegroundColor White

Write-Host "`n✅ Le SQL a été copié dans votre presse-papier!" -ForegroundColor Green
Set-Clipboard -Value $sqlContent

Write-Host "`nAppuyez sur une touche pour continuer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

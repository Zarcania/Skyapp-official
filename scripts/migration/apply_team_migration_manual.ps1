# Script pour appliquer manuellement la migration team_leader_collaborators
# À exécuter dans Supabase SQL Editor

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  MIGRATION: team_leader_collaborators" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$migrationFile = "migrations\2025-11-28_team_leader_collaborators.sql"

if (-not (Test-Path $migrationFile)) {
    Write-Host "[ERREUR] Fichier de migration introuvable: $migrationFile" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Lecture du fichier de migration..." -ForegroundColor Yellow
$sqlContent = Get-Content $migrationFile -Raw -Encoding UTF8

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  INSTRUCTIONS" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Ouvrez Supabase Dashboard:" -ForegroundColor White
Write-Host "   https://supabase.com/dashboard/project/wursductnatclwrqvgua/editor" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Allez dans 'SQL Editor'" -ForegroundColor White
Write-Host ""
Write-Host "3. Cliquez sur 'New query'" -ForegroundColor White
Write-Host ""
Write-Host "4. Copiez-collez le SQL ci-dessous:" -ForegroundColor White
Write-Host ""
Write-Host "================================================" -ForegroundColor Yellow
Write-Host "  SQL À EXÉCUTER" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host $sqlContent -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Cliquez sur 'Run' pour exécuter" -ForegroundColor White
Write-Host ""
Write-Host "6. Vérifiez que vous voyez:" -ForegroundColor White
Write-Host "   - Table 'team_leader_collaborators' créée" -ForegroundColor Green
Write-Host "   - Index créés" -ForegroundColor Green
Write-Host "   - RLS Policies activées" -ForegroundColor Green
Write-Host "   - Vue 'team_leader_stats' créée" -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Copier dans le presse-papier si possible
try {
    Set-Clipboard -Value $sqlContent
    Write-Host "[SUCCESS] SQL copié dans le presse-papier !" -ForegroundColor Green
    Write-Host "           Vous pouvez maintenant coller directement dans Supabase" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Copiez manuellement le SQL ci-dessus" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Appuyez sur Entrée pour ouvrir Supabase dans le navigateur..."
Read-Host
Start-Process "https://supabase.com/dashboard/project/wursductnatclwrqvgua/editor"

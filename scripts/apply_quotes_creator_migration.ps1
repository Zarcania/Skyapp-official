# Script pour appliquer la migration add_created_by_to_quotes.sql

Write-Host "Application de la migration add_created_by_to_quotes..." -ForegroundColor Cyan

# Lire le fichier de migration
$migrationFile = ".\migrations\add_created_by_to_quotes.sql"

if (-not (Test-Path $migrationFile)) {
    Write-Host "Erreur: Le fichier de migration $migrationFile n'existe pas" -ForegroundColor Red
    exit 1
}

$sql = Get-Content $migrationFile -Raw

Write-Host "`nContenu de la migration:" -ForegroundColor Yellow
Write-Host $sql -ForegroundColor White

Write-Host "`n==============================================`n" -ForegroundColor Green
Write-Host "Pour appliquer cette migration:" -ForegroundColor Yellow
Write-Host "1. Ouvrez Supabase Studio (http://localhost:54323)" -ForegroundColor Cyan
Write-Host "2. Allez dans 'SQL Editor'" -ForegroundColor Cyan
Write-Host "3. Créez une nouvelle query" -ForegroundColor Cyan
Write-Host "4. Copiez-collez le SQL ci-dessus" -ForegroundColor Cyan
Write-Host "5. Exécutez la query" -ForegroundColor Cyan
Write-Host "`n==============================================`n" -ForegroundColor Green

Write-Host "Voulez-vous ouvrir Supabase Studio maintenant? (O/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq "O" -or $response -eq "o") {
    Start-Process "http://localhost:54323"
    Write-Host "Supabase Studio ouvert dans votre navigateur" -ForegroundColor Green
}

Write-Host "`nMigration préparée avec succès!" -ForegroundColor Green

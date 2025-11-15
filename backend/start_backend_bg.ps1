# Script pour démarrer le backend en arrière-plan
$BackendPath = $PSScriptRoot
Set-Location $BackendPath

Write-Host "🚀 Démarrage du backend SkyApp sur le port 8001..." -ForegroundColor Cyan

# Lancer Python en arrière-plan
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "server_supabase.py" -WorkingDirectory $BackendPath

Start-Sleep -Seconds 3

# Vérifier que le serveur est actif
$connection = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq 8001 }
if ($connection) {
    Write-Host "✅ Backend démarré avec succès sur http://127.0.0.1:8001" -ForegroundColor Green
    Write-Host "📖 Documentation API: http://127.0.0.1:8001/docs" -ForegroundColor Yellow
} else {
    Write-Host "❌ Erreur: Le backend n'a pas pu démarrer" -ForegroundColor Red
}

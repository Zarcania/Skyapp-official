# Script PowerShell de pre-deploiement - Verifications de securite
# A executer AVANT de deployer en production

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "VERIFICATIONS PRE-DEPLOIEMENT" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$ERRORS = 0
$WARNINGS = 0

# 1. Verifier que .env n'est pas commite
Write-Host "1. Verification des fichiers .env..." -ForegroundColor Yellow
$envFiles = git ls-files 2>$null | Select-String -Pattern "\.env$|\.env\.local$"
if ($envFiles) {
    Write-Host "ERREUR: Des fichiers .env sont trackes par git!" -ForegroundColor Red
    Write-Host "   Fichiers trouves:" -ForegroundColor Red
    $envFiles | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
    Write-Host "   -> Executez: git rm --cached .env .env.local" -ForegroundColor Yellow
    $ERRORS++
} else {
    Write-Host "OK: Aucun fichier .env n'est tracke" -ForegroundColor Green
}
Write-Host ""

# 2. Verifier .gitignore
Write-Host "2. Verification du .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -match "\.env") {
        Write-Host "OK: .env est dans .gitignore" -ForegroundColor Green
    } else {
        Write-Host "ERREUR: .env n'est pas dans .gitignore!" -ForegroundColor Red
        $ERRORS++
    }
} else {
    Write-Host "ERREUR: .gitignore manquant!" -ForegroundColor Red
    $ERRORS++
}
Write-Host ""

# 3. Verifier les print() dans le code
Write-Host "3. Verification des print() dans le code..." -ForegroundColor Yellow
if (Test-Path "backend\server_supabase.py") {
    $printCount = (Select-String -Path "backend\server_supabase.py" -Pattern "print\(" | Measure-Object).Count
    if ($printCount -gt 5) {
        Write-Host "WARNING: $printCount print() trouves dans server_supabase.py" -ForegroundColor Yellow
        Write-Host "   -> Recommandation: Remplacer par logging.info() ou logging.error()" -ForegroundColor Yellow
        $WARNINGS++
    } else {
        Write-Host "OK: Peu de print() trouves" -ForegroundColor Green
    }
}
Write-Host ""

# 4. Verifier les secrets hardcodes
Write-Host "4. Recherche de secrets potentiellement hardcodes..." -ForegroundColor Yellow
$secretsFound = Select-String -Path "backend\*.py" -Pattern "sk-" -ErrorAction SilentlyContinue
if ($secretsFound) {
    Write-Host "ERREUR: Cles API potentiellement hardcodees trouvees!" -ForegroundColor Red
    $secretsFound | ForEach-Object { Write-Host "   $($_.Path):$($_.LineNumber)" -ForegroundColor Red }
    $ERRORS++
} else {
    Write-Host "OK: Aucune cle API hardcodee detectee" -ForegroundColor Green
}
Write-Host ""

# 5. Verifier render.yaml
Write-Host "5. Verification du render.yaml..." -ForegroundColor Yellow
if (Test-Path "render.yaml") {
    $renderContent = Get-Content "render.yaml" -Raw
    if ($renderContent -match "ALLOWED_ORIGINS") {
        if ($renderContent -match 'value:\s*"\*"') {
            Write-Host "WARNING: ALLOWED_ORIGINS=* dans render.yaml" -ForegroundColor Yellow
            Write-Host "   -> Remplacer par vos domaines exacts en production" -ForegroundColor Yellow
            $WARNINGS++
        } else {
            Write-Host "OK: ALLOWED_ORIGINS configure" -ForegroundColor Green
        }
    } else {
        Write-Host "WARNING: ALLOWED_ORIGINS non trouve dans render.yaml" -ForegroundColor Yellow
        $WARNINGS++
    }
} else {
    Write-Host "WARNING: render.yaml non trouve" -ForegroundColor Yellow
    $WARNINGS++
}
Write-Host ""

# 6. Verifier les variables d'environnement critiques
Write-Host "6. Verification de render.yaml - Variables critiques..." -ForegroundColor Yellow
if (Test-Path "render.yaml") {
    $renderContent = Get-Content "render.yaml" -Raw
    
    $requiredVars = @(
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "SUPABASE_ANON_KEY",
        "FOUNDER_EMAIL",
        "ALLOWED_ORIGINS"
    )
    
    $missingVars = @()
    foreach ($var in $requiredVars) {
        if ($renderContent -notmatch $var) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Host "WARNING: Variables manquantes dans render.yaml:" -ForegroundColor Yellow
        $missingVars | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
        $WARNINGS++
    } else {
        Write-Host "OK: Toutes les variables critiques presentes" -ForegroundColor Green
    }
}
Write-Host ""

# 7. Verifier que ALLOW_DEV_LOGIN est desactive en prod
Write-Host "7. Verification ALLOW_DEV_LOGIN..." -ForegroundColor Yellow
if (Test-Path "render.yaml") {
    $renderContent = Get-Content "render.yaml" -Raw
    if ($renderContent -match 'ALLOW_DEV_LOGIN.*value:.*["'']1["'']' -or $renderContent -match 'ALLOW_DEV_LOGIN.*value:.*true') {
        Write-Host "ERREUR: ALLOW_DEV_LOGIN est active dans render.yaml!" -ForegroundColor Red
        Write-Host "   -> DOIT etre 0 ou false en production" -ForegroundColor Red
        $ERRORS++
    } else {
        Write-Host "OK: ALLOW_DEV_LOGIN desactive ou absent" -ForegroundColor Green
    }
}
Write-Host ""

# 8. Verifier les migrations SQL
Write-Host "8. Verification des migrations SQL..." -ForegroundColor Yellow
if (Test-Path "migrations") {
    $sqlCount = (Get-ChildItem -Path "migrations" -Filter "*.sql" | Measure-Object).Count
    Write-Host "OK: $sqlCount fichiers de migration trouves" -ForegroundColor Green
    Write-Host "   -> N'oubliez pas de les appliquer sur la base de production!" -ForegroundColor Yellow
    
    # Lister les migrations
    Write-Host "`n   Migrations a appliquer:" -ForegroundColor Cyan
    Get-ChildItem -Path "migrations" -Filter "*.sql" | Sort-Object Name | ForEach-Object {
        Write-Host "   - $($_.Name)" -ForegroundColor Cyan
    }
} else {
    Write-Host "WARNING: Dossier migrations non trouve" -ForegroundColor Yellow
    $WARNINGS++
}
Write-Host ""

# 9. Verifier package.json frontend
Write-Host "9. Verification du package.json frontend..." -ForegroundColor Yellow
if (Test-Path "frontend\package.json") {
    $packageJson = Get-Content "frontend\package.json" -Raw | ConvertFrom-Json
    if ($packageJson.scripts.build) {
        Write-Host "OK: Script de build present" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Script de build manquant dans package.json" -ForegroundColor Yellow
        $WARNINGS++
    }
}
Write-Host ""

# 10. Verifier requirements.txt
Write-Host "10. Verification du requirements.txt..." -ForegroundColor Yellow
if (Test-Path "backend\requirements.txt") {
    Write-Host "OK: requirements.txt present" -ForegroundColor Green
    
    # Verifier les dependances critiques
    $reqContent = Get-Content "backend\requirements.txt" -Raw
    $criticalDeps = @("fastapi", "uvicorn", "supabase", "pydantic")
    $missingDeps = @()
    
    foreach ($dep in $criticalDeps) {
        if ($reqContent -notmatch $dep) {
            $missingDeps += $dep
        }
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Host "WARNING: Dependances critiques manquantes:" -ForegroundColor Yellow
        $missingDeps | ForEach-Object { Write-Host "   - $_" -ForegroundColor Yellow }
        $WARNINGS++
    }
} else {
    Write-Host "ERREUR: requirements.txt manquant!" -ForegroundColor Red
    $ERRORS++
}
Write-Host ""

# Resume
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "RESUME DES VERIFICATIONS" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Erreurs: $ERRORS" -ForegroundColor $(if ($ERRORS -gt 0) { "Red" } else { "Green" })
Write-Host "Avertissements: $WARNINGS" -ForegroundColor $(if ($WARNINGS -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

if ($ERRORS -gt 0) {
    Write-Host "DEPLOIEMENT NON RECOMMANDE" -ForegroundColor Red
    Write-Host "   -> Corrigez les erreurs avant de deployer" -ForegroundColor Red
    Write-Host ""
    Write-Host "Consultez CHECKLIST_PRODUCTION.md pour plus de details" -ForegroundColor Yellow
    exit 1
} elseif ($WARNINGS -gt 0) {
    Write-Host "DEPLOIEMENT POSSIBLE AVEC PRECAUTIONS" -ForegroundColor Yellow
    Write-Host "   -> Verifiez les avertissements" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Consultez CHECKLIST_PRODUCTION.md pour la checklist complete" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "PRET POUR LE DEPLOIEMENT" -ForegroundColor Green
    Write-Host ""
    Write-Host "Suivez maintenant CHECKLIST_PRODUCTION.md etape par etape" -ForegroundColor Cyan
    exit 0
}

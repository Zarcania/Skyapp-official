# 🔧 Corrections de Code pour la Production

Ce document liste les modifications spécifiques à apporter au code avant le déploiement en production.

---

## 1️⃣ Remplacer les print() par logging

### ❌ Problème
Le fichier [server_supabase.py](backend/server_supabase.py) contient de nombreux `print()` qui ne sont pas appropriés pour un environnement de production.

### ✅ Solution

**Ajouter la configuration du logger en début de fichier:**

Chercher la section après les imports (ligne ~130) et s'assurer que le logging est bien configuré:

```python
# Configuration du logging
import logging

logging.basicConfig(
    level=logging.INFO,  # Utiliser WARNING en production stricte
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**Remplacer tous les print() par des appels logging:**

```python
# ❌ AVANT (ligne ~13)
print("=" * 100)
print("CHARGEMENT DU FICHIER server_supabase.py - CODE MIS A JOUR LE 29 JANVIER 2026")
print("=" * 100)

# ✅ APRÈS
logger.info("=" * 100)
logger.info("CHARGEMENT DU FICHIER server_supabase.py - CODE MIS A JOUR LE 29 JANVIER 2026")
logger.info("=" * 100)
```

```python
# ❌ AVANT (ligne ~321)
print(f"🔑 get_user_from_token appelé - credentials présents: {credentials is not None}")

# ✅ APRÈS
logger.debug(f"🔑 get_user_from_token appelé - credentials présents: {credentials is not None}")
```

```python
# ❌ AVANT (ligne ~397)
print(f"❌ ERREUR dans get_user_from_token: {type(e).__name__}: {str(e)}")

# ✅ APRÈS
logger.error(f"❌ ERREUR dans get_user_from_token: {type(e).__name__}: {str(e)}")
```

### Règles de niveau de logging:
- `logger.debug()` - Informations de debug détaillées (désactivées en production si level=INFO)
- `logger.info()` - Événements normaux (startup, requêtes importantes)
- `logger.warning()` - Situations anormales mais gérables
- `logger.error()` - Erreurs qui nécessitent attention
- `logger.critical()` - Erreurs critiques qui peuvent arrêter l'application

### Script de remplacement automatique:

```powershell
# PowerShell - Remplacer tous les print() par logger.info()
$file = "backend\server_supabase.py"
$content = Get-Content $file -Raw

# Remplacements basiques (à adapter selon le contexte)
$content = $content -replace 'print\(f"❌', 'logger.error(f"❌'
$content = $content -replace 'print\(f"⚠️', 'logger.warning(f"⚠️'
$content = $content -replace 'print\(f"✅', 'logger.info(f"✅'
$content = $content -replace 'print\(f"🔑', 'logger.debug(f"🔑'
$content = $content -replace 'print\(f"', 'logger.info(f"'
$content = $content -replace 'print\("', 'logger.info("'

Set-Content $file $content
```

⚠️ **Important:** Vérifier manuellement après le remplacement automatique.

---

## 2️⃣ Sécuriser la configuration CORS

### ❌ Problème actuel (ligne ~8115-8127)

```python
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")  # ⚠️ Dangereux par défaut
if allowed_origins_env.strip() in ("", "*"):
    _allow_origins = ["*"]
else:
    _allow_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,  # ⚠️ Avec origins=["*"] c'est une faille de sécurité
    allow_origins=_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Problème:** `allow_credentials=True` avec `allow_origins=["*"]` est une faille de sécurité.

### ✅ Solution recommandée

```python
# Configuration CORS sécurisée
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")

# En production, EXIGER que ALLOWED_ORIGINS soit défini
if not allowed_origins_env or allowed_origins_env.strip() in ("", "*"):
    # Mode développement uniquement
    if os.getenv("ENVIRONMENT", "production") == "development":
        _allow_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        logger.warning("⚠️ CORS en mode développement - origins locales autorisées")
    else:
        # En production, REFUSER de démarrer si ALLOWED_ORIGINS n'est pas défini
        logger.error("❌ ERREUR: ALLOWED_ORIGINS doit être défini en production!")
        logger.error("   Configurez ALLOWED_ORIGINS=https://votreapp.vercel.app,https://app.votredomaine.com")
        raise ValueError("ALLOWED_ORIGINS requis en production")
else:
    _allow_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    logger.info(f"✅ CORS configuré avec origins: {_allow_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=_allow_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Plus restrictif
    allow_headers=["*"],
    expose_headers=["*"],
)
```

### Variables d'environnement à ajouter:

Dans `render.yaml`:
```yaml
- key: ENVIRONMENT
  value: "production"
- key: ALLOWED_ORIGINS
  value: "https://votreapp.vercel.app"  # ⚠️ Remplacer par votre vraie URL
```

---

## 3️⃣ Sécuriser le mode développement

### ❌ Problème (ligne ~68, ~344)

Le mode dev avec `ALLOW_DEV_LOGIN` permet de bypasser l'authentification:

```python
ALLOW_DEV_LOGIN = os.environ.get('ALLOW_DEV_LOGIN', '0') in ('1', 'true', 'True', 'yes', 'on')

# Plus loin dans le code (ligne ~344)
if credentials.credentials.startswith('dev_token_') and ALLOW_DEV_LOGIN:
    return {
        "id": credentials.credentials.replace('dev_token_', ''),
        # ... bypass complet de l'auth
    }
```

### ✅ Solution

**Option 1: S'assurer que c'est désactivé en production**

Dans `render.yaml`:
```yaml
- key: ALLOW_DEV_LOGIN
  value: "0"  # ✅ TOUJOURS 0 en production
```

**Option 2: Ajouter une double vérification dans le code** (ligne ~344)

```python
# Dev fallback uniquement en environnement de développement
if (credentials.credentials.startswith('dev_token_') and 
    ALLOW_DEV_LOGIN and 
    os.getenv("ENVIRONMENT") == "development"):  # Double vérification
    
    logger.warning(f"⚠️ DEV MODE: Utilisation d'un token de dev")
    return {
        "id": credentials.credentials.replace('dev_token_', ''),
        "email": "dev@example.com",
        "role": "ADMIN"
    }
```

**Option 3: Supprimer complètement le code de dev** (recommandé pour la production)

Commenter ou supprimer les lignes 343-351:

```python
# # Dev fallback: token spécial généré par le mode dev
# if credentials.credentials.startswith('dev_token_') and ALLOW_DEV_LOGIN:
#     return {
#         "id": credentials.credentials.replace('dev_token_', ''),
#         "email": "dev@example.com",
#         "role": "ADMIN"
#     }
```

---

## 4️⃣ Améliorer la gestion des erreurs

### ❌ Problème

Certaines erreurs exposent trop d'informations:

```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # ⚠️ Expose les détails internes
```

### ✅ Solution

```python
except Exception as e:
    # Logger l'erreur complète pour le debug
    logger.error(f"Erreur lors de la création du chantier: {type(e).__name__}: {str(e)}")
    logger.exception(e)  # Log le stack trace complet
    
    # Retourner un message générique à l'utilisateur
    if os.getenv("ENVIRONMENT") == "development":
        # En dev, on peut exposer les détails
        raise HTTPException(status_code=500, detail=str(e))
    else:
        # En production, message générique
        raise HTTPException(
            status_code=500, 
            detail="Une erreur interne est survenue. Veuillez réessayer."
        )
```

---

## 5️⃣ Sécuriser les clés API

### ✅ Vérifier qu'aucune clé n'est hardcodée

Exécuter cette commande pour chercher des clés potentiellement hardcodées:

```powershell
# Chercher des patterns de clés API
Select-String -Path "backend\*.py" -Pattern "sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9]{35}|eyJ[a-zA-Z0-9]{20,}" 
```

Si des clés sont trouvées, les remplacer par:

```python
# ❌ JAMAIS ça
OPENAI_API_KEY = "sk-proj-abc123..."

# ✅ TOUJOURS ça
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("⚠️ OPENAI_API_KEY non configurée - Fonctionnalités IA désactivées")
```

---

## 6️⃣ Optimiser les requêtes Supabase

### ✅ Utiliser des index

S'assurer que les colonnes fréquemment requêtées sont indexées:

```sql
-- À ajouter dans une migration
CREATE INDEX IF NOT EXISTS idx_worksites_client_id ON worksites(client_id);
CREATE INDEX IF NOT EXISTS idx_worksites_company_id ON worksites(company_id);
CREATE INDEX IF NOT EXISTS idx_quotes_company_id ON quotes(company_id);
CREATE INDEX IF NOT EXISTS idx_schedules_worksite_id ON schedules(worksite_id);
CREATE INDEX IF NOT EXISTS idx_schedules_technicien_id ON schedules(technicien_id);
```

### ✅ Limiter les SELECT *

```python
# ❌ AVANT - Récupère toutes les colonnes
response = supabase.table('worksites').select('*').execute()

# ✅ APRÈS - Récupère seulement ce qui est nécessaire
response = supabase.table('worksites').select(
    'id, title, client_id, status, created_at'
).execute()
```

---

## 7️⃣ Ajouter des timeouts

### ✅ Ajouter des timeouts aux requêtes HTTP

Pour éviter que l'API ne reste bloquée:

```python
import httpx

# Pour les appels à des APIs externes (OpenAI, IOPOLE, etc.)
async with httpx.AsyncClient(timeout=30.0) as client:  # Timeout de 30 secondes
    response = await client.post(url, json=data)
```

---

## 8️⃣ Validation des entrées utilisateur

### ✅ Utiliser Pydantic strictement

S'assurer que tous les endpoints valident les données:

```python
from pydantic import BaseModel, Field, validator

class WorksiteCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    address: str = Field(..., min_length=5, max_length=500)
    client_id: str
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Le titre ne peut pas être vide')
        return v.strip()
```

---

## 9️⃣ Mettre en place le rate limiting

### ✅ Ajouter SlowAPI pour limiter les requêtes

```python
# À ajouter dans requirements.txt
slowapi==0.1.9

# Dans server_supabase.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Sur les endpoints sensibles
@app.post("/api/auth/signup")
@limiter.limit("5/minute")  # Max 5 inscriptions par minute par IP
async def signup(request: Request, user: UserSignup):
    # ...
```

---

## 🔟 Checklist de vérification finale

Avant de commiter et déployer:

- [ ] Tous les `print()` remplacés par `logging`
- [ ] CORS configuré avec domaines exacts
- [ ] `ALLOW_DEV_LOGIN=0` en production
- [ ] Aucune clé API hardcodée
- [ ] Variables d'environnement documentées
- [ ] Timeout sur les requêtes HTTP externes
- [ ] Validation Pydantic stricte
- [ ] Messages d'erreur génériques en production
- [ ] Index de base de données optimisés
- [ ] Tests unitaires passent: `pytest backend/tests/`

---

## 📝 Script d'application rapide

```powershell
# Script pour appliquer les corrections essentielles

Write-Host "🔧 Application des corrections de production..." -ForegroundColor Cyan

# 1. Backup du fichier original
Copy-Item "backend\server_supabase.py" "backend\server_supabase.py.backup"

# 2. Remplacer les print() critiques
$file = "backend\server_supabase.py"
$content = Get-Content $file -Raw

$content = $content -replace 'print\(f"❌', 'logger.error(f"❌'
$content = $content -replace 'print\(f"⚠️', 'logger.warning(f"⚠️'

Set-Content $file $content

Write-Host "✅ Corrections appliquées" -ForegroundColor Green
Write-Host "⚠️  IMPORTANT: Vérifiez manuellement les modifications!" -ForegroundColor Yellow
Write-Host "   Backup disponible: backend\server_supabase.py.backup" -ForegroundColor Yellow
```

---

**Prochaine étape:** Une fois ces corrections appliquées, exécuter:
```powershell
.\scripts\pre_deploy_check.ps1
```

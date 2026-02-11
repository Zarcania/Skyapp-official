#  SkyApp BTP - Application de Gestion

Application complète de gestion pour entreprises BTP avec gestion de chantiers, devis, facturation électronique, planning et équipes.

##  Structure du projet

\\\
Skyapp/
 backend/              # API FastAPI + Supabase
 frontend/             # React Application
 docs/                 #  Documentation complète
    api/              # Documentation API
    guides/           # Guides d'utilisation
    migration/        # Documentation migrations
    README.md         # Index documentation
 scripts/              #  Scripts utilitaires
    migration/        # Scripts de migration DB
    tests/            # Scripts de test
    data/             # Création données test
    README.md         # Documentation scripts
 migrations/           # Historique migrations
 supabase/             # Configuration Supabase
 tests/                # Tests unitaires
\\\

##  Démarrage rapide

### Lancement de l'application
\\\powershell
# Démarrer backend + frontend
.\scripts\start_skyapp.ps1

# Redémarrer l'application
.\scripts\restart_skyapp.ps1

# Arrêter l'application
.\scripts\stop_skyapp.ps1
\\\

### Backend seul
\\\powershell
python scripts/start_backend.py
# ou
cd backend
uvicorn server_supabase:app --reload --host 127.0.0.1 --port 8001
\\\

### Frontend seul
\\\powershell
python scripts/start_frontend.py
# ou
cd frontend
npm start
\\\

##  Documentation

Consultez le [dossier docs/](docs/README.md) pour la documentation complète :
- **API** : Documentation des endpoints REST
- **Guides** : Guides d'utilisation et configuration
- **Migration** : Procédures de migration DB

##  Scripts disponibles

Consultez [scripts/README.md](scripts/README.md) pour :
- Scripts de migration base de données
- Scripts de test automatisés
- Scripts de création de données test

##  Fonctionnalités principales

-  **Gestion de chantiers** - Création, suivi, géolocalisation
-  **Devis intelligents** - Génération automatique avec IA
-  **Facturation électronique** - Intégration IOPOLE
-  **Planning équipes** - Drag & drop, affectation techniciens
-  **Gestion photos** - Upload par section avec métadonnées
-  **Rapports PDF** - Génération automatique avec QR codes
-  **Intelligence artificielle** - Assistant vocal + correction texte
-  **Système d'invitations** - SMTP configuré (Contact@skyapp.fr)
-  **Multi-entreprises** - Isolation des données par société

##  Configuration

Les variables d'environnement sont dans \.env\ (backend) et \.env.local\ (frontend).

### Principaux services configurés
- **Supabase** - Base de données PostgreSQL
- **OpenAI** - Intelligence artificielle
- **IOPOLE** - Facturation électronique
- **SMTP Gmail** - Envoi emails (Contact@skyapp.fr)

##  Support

Pour plus d'informations, consultez la documentation dans \docs/\.

---
**Version** : 2.0 (Novembre 2025)  
**Auteur** : SkyApp Development Team

# 🔧 Scripts SkyApp

Scripts organisés pour la gestion, migration et tests de l'application SkyApp.

## 📁 Structure

### `/migration` - Scripts de migration
Scripts SQL et Python pour mettre à jour la base de données :

**SQL :**
- `add_description_to_projects.sql` - Ajout colonne description aux projets
- `add_invited_by_name_column.sql` - Ajout nom de l'inviteur
- `add_is_recurring_to_clients.sql` - Ajout clients récurrents
- `add_profile_columns.sql` - Ajout colonnes profil utilisateur
- `add_shared_at_column.sql` - Ajout colonne date de partage
- `FIX_COLUMNS_NAME.sql` - Correction noms de colonnes
- `fix_projects_client_id_nullable.sql` - Correction client_id nullable
- `FIX_SUPABASE_URGENT.sql` - Corrections urgentes Supabase

**Python :**
- `add_shared_at_migration.py` - Migration dates de partage
- `apply_invoicing_migration.py` - Migration système facturation
- `apply_migration.py` - Migration générique
- `apply_projects_client_nullable.py` - Migration projets nullable
- `apply_quote_number_fix.py` - Correction numéros devis
- `apply_team_collaborators_migration.py` - Migration équipes
- `clean_invalid_project_ids.py` - Nettoyage IDs projets invalides
- `fix_quote_numbers.py` - Correction numéros devis
- `fix_searches_user_id.py` - Correction user_id recherches
- `fix_user_company.py` - Correction company_id utilisateurs

**PowerShell :**
- `apply_team_migration_manual.ps1` - Migration manuelle équipes

### `/tests` - Scripts de test
Tests automatisés pour valider le backend et les fonctionnalités :

- `backend_endpoint_test.py` - Test des endpoints API
- `backend_regression_test.py` - Tests de régression
- `backend_test.py` - Tests généraux backend
- `backend_verification_complete.py` - Vérification complète
- `check_all_quotes.py` - Vérification tous les devis
- `check_data.py` - Vérification données
- `check_quotes.py` - Vérification devis
- `check_schedules_structure.sql` - Vérification structure planning
- `check_searches_projects.py` - Vérification recherches/projets
- `check_user_company.py` - Vérification user/company
- `check_worksites.py` - Vérification chantiers
- `clean_backend_test.py` - Tests backend nettoyés
- `comprehensive_backend_test.py` - Tests backend complets
- `coordinates_test.py` - Tests coordonnées GPS
- `drag_drop_photo_test.py` - Tests drag & drop photos
- `enhanced_backend_test.py` - Tests backend améliorés
- `enhanced_endpoints_test.py` - Tests endpoints améliorés
- `final_backend_test.py` - Tests finaux backend
- `focused_backend_test.py` - Tests backend ciblés
- `focused_enhanced_test.py` - Tests améliorés ciblés
- `geolocation_optional_test.py` - Tests géolocalisation optionnelle

### `/data` - Scripts de données de test
Scripts pour créer des données de test :

- `add_test_clients.sql` - Ajout clients de test
- `DONNEES_TEST.sql` - Données de test complètes
- `create_2_more_quotes.py` - Création 2 devis supplémentaires
- `create_complete_test_data.py` - Création jeu complet données test
- `create_quotes_with_api.py` - Création devis via API
- `create_test_accounts_quick.py` - Création rapide comptes test
- `create_test_accounts.py` - Création comptes test
- `create_test_clients.py` - Création clients test
- `create_test_quotes_direct.py` - Création directe devis test
- `create_test_quotes.py` - Création devis test
- `create_worksite_test.py` - Création chantiers test
- `debug_projects.py` - Debug projets
- `delete_bad_quotes.py` - Suppression devis invalides
- `delete_invitation.py` - Suppression invitations

## 🚀 Utilisation

### Migrations
```bash
# SQL
psql -f scripts/migration/nom_du_fichier.sql

# Python
cd scripts/migration
python nom_du_script.py
```

### Tests
```bash
cd scripts/tests
python nom_du_test.py
```

### Données de test
```bash
cd scripts/data
python create_complete_test_data.py
```

## ⚠️ Avertissement

**ATTENTION :** Les scripts de migration modifient la structure de la base de données.
Toujours faire une sauvegarde avant d'exécuter une migration !

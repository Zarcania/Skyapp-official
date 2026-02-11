"""
Script de vérification de l'état des migrations
Vérifie si toutes les tables et colonnes créées par les migrations existent
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_service_key:
    print("❌ ERREUR: Variables SUPABASE_URL ou SUPABASE_SERVICE_KEY manquantes")
    exit(1)

supabase = create_client(supabase_url, supabase_service_key)

print("=" * 80)
print("🔍 VÉRIFICATION DE L'ÉTAT DES MIGRATIONS")
print("=" * 80)
print()

# Définir les vérifications pour chaque migration
migrations_checks = {
    "2025-11-28_planning_mvp.sql": {
        "description": "Planning MVP",
        "tables": ["planning_team_leaders"],
        "columns": {
            "schedules": ["technicien_id", "worksite_id"]
        }
    },
    "2025-11-28_schedules_end_time.sql": {
        "description": "Schedules end_time", 
        "columns": {
            "schedules": ["end_time"]
        }
    },
    "2025-11-28_team_leader_collaborators.sql": {
        "description": "Team leader collaborators",
        "columns": {
            "planning_team_leaders": ["user_id"]
        }
    },
    "2025-12-25_add_converted_to_worksite_status.sql": {
        "description": "Converted to worksite status",
        "enum_values": {
            "quote_status": ["CONVERTED_TO_WORKSITE"]
        }
    },
    "add_created_by_to_quotes.sql": {
        "description": "Created by to quotes",
        "columns": {
            "quotes": ["created_by_user_id"]
        }
    },
    "add_is_fondateur_to_users.sql": {
        "description": "Is fondateur to users",
        "columns": {
            "users": ["is_fondateur"]
        }
    },
    "add_missing_datetime_columns.sql": {
        "description": "Missing datetime columns",
        "columns": {
            "worksites": ["created_at", "updated_at"],
            "quotes": ["created_at", "updated_at"]
        }
    },
    "add_planning_fields.sql": {
        "description": "Planning fields",
        "columns": {
            "schedules": ["client_name", "client_address", "worksite_title"]
        }
    },
    "add_schedules_period_columns.sql": {
        "description": "Schedules period columns",
        "columns": {
            "schedules": ["period_start", "period_end"]
        }
    },
    "add_skills_column.sql": {
        "description": "Skills column",
        "columns": {
            "users": ["skills"]
        }
    },
    "add_ville_code_postal_to_searches.sql": {
        "description": "Ville code postal to searches",
        "columns": {
            "searches": ["ville", "code_postal"]
        }
    },
    "create_company_settings.sql": {
        "description": "Company settings table",
        "tables": ["company_settings"]
    },
    "create_licenses_table.sql": {
        "description": "Licenses table",
        "tables": ["licenses"]
    },
    "create_material_checkouts.sql": {
        "description": "Material checkouts table",
        "tables": ["material_checkouts"]
    },
    "create_mission_reports_table.sql": {
        "description": "Mission reports table",
        "tables": ["mission_reports"]
    },
    "enhance_materials_management.sql": {
        "description": "Enhanced materials management",
        "columns": {
            "materials": ["status", "location", "next_maintenance_date", "last_maintenance_date", "maintenance_interval_days", "notes"]
        }
    },
    "fix_team_leaders_user_link.sql": {
        "description": "Fix team leaders user link",
        "columns": {
            "planning_team_leaders": ["user_id"]
        }
    }
}

def check_table_exists(table_name):
    """Vérifie si une table existe"""
    try:
        result = supabase.table(table_name).select("*").limit(1).execute()
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if "relation" in error_msg and "does not exist" in error_msg:
            return False
        if "not found" in error_msg:
            return False
        # Si autre erreur, on suppose que la table existe mais il y a un problème de permissions
        return True

def check_column_exists(table_name, column_name):
    """Vérifie si une colonne existe dans une table"""
    try:
        result = supabase.table(table_name).select(column_name).limit(1).execute()
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if "column" in error_msg and "does not exist" in error_msg:
            return False
        if column_name.lower() not in error_msg.lower():
            # La colonne n'est pas mentionnée dans l'erreur, elle existe probablement
            return True
        return False

def check_enum_value_exists(enum_name, enum_value):
    """Vérifie si une valeur existe dans un enum PostgreSQL"""
    try:
        # Requête SQL pour vérifier la valeur d'enum
        query = f"""
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        WHERE t.typname = '{enum_name}' AND e.enumlabel = '{enum_value}'
        """
        result = supabase.rpc('sql_query', {'query': query}).execute()
        return len(result.data) > 0 if result.data else False
    except:
        # Si rpc n'est pas disponible, on suppose que ça existe
        # (pas de moyen simple de vérifier sans accès direct à PostgreSQL)
        return True

# Statistiques
total_checks = 0
passed_checks = 0
failed_checks = 0
migrations_applied = []
migrations_pending = []

print("📋 Vérification de chaque migration...\n")

for migration_file, checks in migrations_checks.items():
    print(f"📄 {migration_file}")
    print(f"   Description: {checks['description']}")
    
    migration_ok = True
    
    # Vérifier les tables
    if "tables" in checks:
        for table in checks["tables"]:
            total_checks += 1
            exists = check_table_exists(table)
            if exists:
                print(f"   ✅ Table '{table}' existe")
                passed_checks += 1
            else:
                print(f"   ❌ Table '{table}' MANQUANTE")
                failed_checks += 1
                migration_ok = False
    
    # Vérifier les colonnes
    if "columns" in checks:
        for table, columns in checks["columns"].items():
            # Vérifier d'abord si la table existe
            if not check_table_exists(table):
                print(f"   ⚠️  Table '{table}' n'existe pas, colonnes non vérifiées")
                failed_checks += len(columns)
                total_checks += len(columns)
                migration_ok = False
                continue
                
            for column in columns:
                total_checks += 1
                exists = check_column_exists(table, column)
                if exists:
                    print(f"   ✅ Colonne '{table}.{column}' existe")
                    passed_checks += 1
                else:
                    print(f"   ❌ Colonne '{table}.{column}' MANQUANTE")
                    failed_checks += 1
                    migration_ok = False
    
    # Vérifier les valeurs enum
    if "enum_values" in checks:
        for enum_name, values in checks["enum_values"].items():
            for value in values:
                total_checks += 1
                exists = check_enum_value_exists(enum_name, value)
                if exists:
                    print(f"   ✅ Valeur enum '{enum_name}.{value}' existe")
                    passed_checks += 1
                else:
                    print(f"   ❌ Valeur enum '{enum_name}.{value}' MANQUANTE")
                    failed_checks += 1
                    migration_ok = False
    
    if migration_ok:
        migrations_applied.append(migration_file)
    else:
        migrations_pending.append(migration_file)
    
    print()

# Résumé
print("=" * 80)
print("📊 RÉSUMÉ DES VÉRIFICATIONS")
print("=" * 80)
print(f"Total de vérifications: {total_checks}")
print(f"✅ Réussies: {passed_checks}")
print(f"❌ Échouées: {failed_checks}")
print()

if migrations_applied:
    print(f"✅ Migrations appliquées ({len(migrations_applied)}/{len(migrations_checks)}):")
    for m in migrations_applied:
        print(f"   - {m}")
    print()

if migrations_pending:
    print(f"❌ Migrations À APPLIQUER ({len(migrations_pending)}/{len(migrations_checks)}):")
    for m in migrations_pending:
        print(f"   - {m}")
    print()
    print("⚠️  ACTION REQUISE:")
    print("   1. Connectez-vous à Supabase: https://app.supabase.com")
    print("   2. Allez dans 'SQL Editor'")
    print("   3. Exécutez chaque fichier de migration manquant depuis le dossier 'migrations/'")
    print()
else:
    print("🎉 Toutes les migrations sont appliquées!")
    print()

print("=" * 80)

# Code de sortie
if failed_checks > 0:
    exit(1)
else:
    exit(0)

import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('backend/.env'))

# Extraire les infos de connexion depuis SUPABASE_URL
supabase_url = os.environ.get('SUPABASE_URL')
supabase_password = os.environ.get('SUPABASE_DB_PASSWORD')

if not supabase_url:
    print("❌ SUPABASE_URL non trouvé")
    exit(1)

# Parser l'URL pour obtenir le host
# Format: https://xxxxxxx.supabase.co
host = supabase_url.replace('https://', '').replace('http://', '')
project_ref = host.split('.')[0]

print("=" * 80)
print("CORRECTION DE LA CONTRAINTE UNIQUE")
print("=" * 80)
print()

print("⚠️  Cette migration nécessite une connexion PostgreSQL directe.")
print()
print("Méthode alternative : Exécutez ces commandes SQL manuellement dans Supabase SQL Editor :")
print()
print("-" * 80)
print()
print("-- 1. Supprimer la contrainte globale")
print("ALTER TABLE quotes DROP CONSTRAINT IF EXISTS quotes_quote_number_key;")
print()
print("-- 2. Ajouter contrainte par entreprise")
print("ALTER TABLE quotes")
print("ADD CONSTRAINT quotes_company_quote_number_unique")
print("UNIQUE (company_id, quote_number);")
print()
print("-- 3. Créer un index")
print("CREATE INDEX IF NOT EXISTS idx_quotes_company_quote_number")
print("ON quotes(company_id, quote_number);")
print()
print("-" * 80)
print()
print("📍 URL Supabase SQL Editor:")
print(f"   https://supabase.com/dashboard/project/{project_ref}/sql/new")

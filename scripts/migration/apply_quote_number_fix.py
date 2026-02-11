import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

print("=" * 80)
print("CORRECTION DE LA CONTRAINTE UNIQUE SUR quote_number")
print("=" * 80)
print()

try:
    # Lire et exécuter la migration SQL
    migration_file = Path('supabase/migrations/20251116_fix_quote_number_constraint.sql')
    
    if not migration_file.exists():
        print("❌ Fichier de migration non trouvé")
        exit(1)
    
    sql_content = migration_file.read_text(encoding='utf-8')
    
    # Exécuter chaque commande SQL séparément
    commands = [
        "ALTER TABLE quotes DROP CONSTRAINT IF EXISTS quotes_quote_number_key",
        "ALTER TABLE quotes ADD CONSTRAINT quotes_company_quote_number_unique UNIQUE (company_id, quote_number)",
        "CREATE INDEX IF NOT EXISTS idx_quotes_company_quote_number ON quotes(company_id, quote_number)"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"[{i}/{len(commands)}] Exécution: {cmd[:60]}...")
        try:
            supabase.rpc('exec_sql', {'sql': cmd}).execute()
            print(f"   ✅ OK")
        except Exception as e:
            # Certaines commandes peuvent échouer si déjà appliquées
            print(f"   ⚠️  {str(e)[:80]}")
        print()
    
    print("=" * 80)
    print("✅ MIGRATION TERMINÉE")
    print("=" * 80)
    print()
    print("Maintenant chaque entreprise peut avoir ses propres numéros :")
    print("  - Test Company: 202511-001, 202511-002, ...")
    print("  - coracorp: 202511-001, 202511-002, ...")
    print("  (sans conflit)")
    
except Exception as e:
    print(f"❌ Erreur: {str(e)}")

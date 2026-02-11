import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

# Voir TOUS les devis
all_quotes = supabase.table('quotes').select('*, companies(name)').execute()

print(f"=== TOUS LES DEVIS ({len(all_quotes.data)}) ===")
print()

for q in all_quotes.data:
    company_name = q['companies']['name'] if q.get('companies') else 'N/A'
    print(f"#{q['quote_number']} - {q['title']}")
    print(f"   Entreprise: {company_name}")
    print(f"   ID: {q['id']}")
    print()

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

# Trouver Test Company
companies = supabase.table('companies').select('*').eq('name', 'Test Company').execute()
company_id = companies.data[0]['id']

print("=" * 80)
print("VÉRIFICATION DES CHANTIERS")
print("=" * 80)
print()

# Vérifier les devis acceptés
quotes = supabase.table('quotes').select('*').eq('company_id', company_id).eq('status', 'ACCEPTED').execute()
print(f"📋 Devis ACCEPTED: {len(quotes.data)}")
for q in quotes.data:
    print(f"   - #{q['quote_number']} - {q['title']}")
print()

# Vérifier les chantiers
worksites = supabase.table('worksites').select('*, quotes(quote_number, title)').eq('company_id', company_id).execute()
print(f"🏗️  Chantiers: {len(worksites.data)}")
for w in worksites.data:
    quote_info = w['quotes'] if w.get('quotes') else None
    quote_text = f"#{quote_info['quote_number']}" if quote_info else "Aucun"
    print(f"   - {w['title']} (Devis: {quote_text})")
print()

print("=" * 80)

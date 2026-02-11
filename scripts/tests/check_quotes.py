import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

companies = supabase.table('companies').select('*').limit(1).execute()
if not companies.data:
    print("Aucune entreprise trouvée")
    exit()

company_id = companies.data[0]['id']
print(f"Entreprise: {companies.data[0].get('name', 'N/A')} ({company_id})")
print()

quotes = supabase.table('quotes').select('*, clients(nom)').eq('company_id', company_id).execute()

print(f"=== {len(quotes.data)} DEVIS TROUVÉS ===")
print()

for q in quotes.data:
    client_name = q['clients']['nom'] if q.get('clients') else 'N/A'
    print(f"#{q['quote_number']} - {q['title']}")
    print(f"   Client: {client_name}")
    print(f"   Montant: {q['amount']}€")
    print(f"   Statut: {q['status']}")
    print(f"   ID: {q['id']}")
    print()

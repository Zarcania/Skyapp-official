import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

# Trouver Test Company et le devis accepté
companies = supabase.table('companies').select('*').eq('name', 'Test Company').execute()
company_id = companies.data[0]['id']

quotes = supabase.table('quotes').select('*').eq('company_id', company_id).eq('status', 'ACCEPTED').execute()
quote = quotes.data[0] if quotes.data else None

if not quote:
    print("❌ Aucun devis accepté trouvé")
    exit()

users = supabase.table('users').select('*').eq('email', 'corradijordan@gmail.com').execute()
user_id = users.data[0]['id'] if users.data else None

print(f"✅ Devis: #{quote['quote_number']} - {quote['title']}")
print(f"✅ Company: {company_id}")
print(f"✅ User: {user_id}")
print()

# Essayer de créer le chantier
worksite_data = {
    "company_id": company_id,
    "created_by": user_id,
    "title": quote['title'],
    "description": quote.get('description', ''),
    "client_id": quote.get('client_id'),
    "status": "PLANNED",
    "progress": 0,
    "budget": float(quote.get('amount', 0)),
    "quote_id": quote['id'],
    "team_size": 1,
    "notes": f"Créé depuis le devis #{quote['quote_number']}"
}

print("Tentative de création du chantier...")
try:
    result = supabase.table('worksites').insert(worksite_data).execute()
    print("✅ Chantier créé avec succès !")
    print(f"   ID: {result.data[0]['id']}")
except Exception as e:
    print(f"❌ Erreur: {str(e)}")

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

# Vérifier l'utilisateur skyapp@gmail.com
users = supabase.table('users').select('*').eq('email', 'skyapp@gmail.com').execute()

if not users.data:
    print("❌ Utilisateur skyapp@gmail.com non trouvé")
    exit()

user = users.data[0]
print("👤 UTILISATEUR")
print(f"   Email: {user['email']}")
print(f"   ID: {user['id']}")
print(f"   Company ID: {user.get('company_id', 'N/A')}")
print()

# Vérifier l'entreprise de l'utilisateur
if user.get('company_id'):
    company = supabase.table('companies').select('*').eq('id', user['company_id']).execute()
    if company.data:
        print("🏢 ENTREPRISE DE L'UTILISATEUR")
        print(f"   Nom: {company.data[0].get('name', 'N/A')}")
        print(f"   ID: {company.data[0]['id']}")
        print()

# Vérifier les devis de cette entreprise
company_id = user.get('company_id')
if company_id:
    quotes = supabase.table('quotes').select('*').eq('company_id', company_id).execute()
    print(f"📋 DEVIS DE CETTE ENTREPRISE: {len(quotes.data)}")
    for q in quotes.data:
        print(f"   - #{q['quote_number']} - {q['title']} ({q['status']})")
    print()
else:
    print("⚠️ L'utilisateur n'a pas de company_id")

# Vérifier TOUS les devis
all_quotes = supabase.table('quotes').select('*, companies(name)').execute()
print(f"📊 TOUS LES DEVIS: {len(all_quotes.data)}")
for q in all_quotes.data:
    company_name = q['companies']['name'] if q.get('companies') else 'N/A'
    print(f"   - #{q['quote_number']} - {q['title']} - Entreprise: {company_name}")

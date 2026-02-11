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
if not companies.data:
    print("❌ Test Company non trouvée")
    exit()

company_id = companies.data[0]['id']
print(f"🏢 Test Company ID: {company_id}")

# Mettre à jour l'utilisateur skyapp@gmail.com
result = supabase.table('users').update({
    'company_id': company_id
}).eq('email', 'skyapp@gmail.com').execute()

if result.data:
    print(f"✅ Utilisateur skyapp@gmail.com associé à Test Company")
else:
    print("❌ Erreur lors de la mise à jour")

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
print()

# Vérifier si l'utilisateur corradijordan@gmail.com existe
user_check = supabase.table('users').select('*').eq('email', 'corradijordan@gmail.com').execute()

if user_check.data:
    # Mettre à jour l'utilisateur existant
    result = supabase.table('users').update({
        'company_id': company_id
    }).eq('email', 'corradijordan@gmail.com').execute()
    print(f"✅ Utilisateur corradijordan@gmail.com associé à Test Company")
else:
    print("❌ Utilisateur corradijordan@gmail.com non trouvé")
    print("Création de l'utilisateur...")
    
    # Créer l'utilisateur (note: il faudra aussi le créer dans Supabase Auth)
    result = supabase.table('users').insert({
        'email': 'corradijordan@gmail.com',
        'company_id': company_id,
        'role': 'admin'
    }).execute()
    
    if result.data:
        print(f"✅ Utilisateur corradijordan@gmail.com créé et associé à Test Company")
    else:
        print("❌ Erreur lors de la création")

# Retirer skyapp@gmail.com de Test Company
supabase.table('users').update({
    'company_id': None
}).eq('email', 'skyapp@gmail.com').execute()
print("✅ skyapp@gmail.com retiré de Test Company")

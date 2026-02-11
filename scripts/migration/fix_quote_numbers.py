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

# Récupérer tous les devis avec numéros simples (#1, #2, #3, #4)
quotes = supabase.table('quotes').select('*').eq('company_id', company_id).execute()

print(f"📋 {len(quotes.data)} devis trouvés")
print()

# Régénérer les numéros pour les devis de Test Company
for i, quote in enumerate(quotes.data, 1):
    old_number = quote['quote_number']
    
    # Appeler la fonction generate_quote_number
    try:
        result = supabase.rpc('generate_quote_number', {'p_company_id': company_id}).execute()
        new_number = result.data
        
        # Mettre à jour le devis
        supabase.table('quotes').update({
            'quote_number': new_number
        }).eq('id', quote['id']).execute()
        
        print(f"✅ Devis {i}: {quote['title']}")
        print(f"   Ancien: #{old_number} → Nouveau: {new_number}")
        print()
    except Exception as e:
        print(f"❌ Erreur pour {quote['title']}: {str(e)}")
        print()

print("=" * 80)
print("✅ Numérotation mise à jour !")
print("=" * 80)

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
print("SUPPRESSION DES DEVIS AVEC MAUVAISE NUMÉROTATION")
print("=" * 80)
print()

# Supprimer les devis avec numéros simples (1, 2, 3, 4)
quotes = supabase.table('quotes').select('*').eq('company_id', company_id).in_('quote_number', ['1', '2', '3', '4']).execute()

print(f"📋 {len(quotes.data)} devis à supprimer")
print()

for quote in quotes.data:
    print(f"🗑️  Suppression: #{quote['quote_number']} - {quote['title']}")
    supabase.table('quotes').delete().eq('id', quote['id']).execute()

print()
print("=" * 80)
print("✅ Devis supprimés !")
print("=" * 80)
print()
print("⚠️  Utilisez maintenant l'application pour créer de nouveaux devis")
print("   avec la numérotation automatique correcte (202511-001, 202511-002, etc.)")

#!/usr/bin/env python3
"""Script pour debugger le devis qui cause l'erreur PDF"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Variables d'environnement manquantes")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

quote_id = "b6a10f61-1332-4022-8c3c-6b8988e69f53"

print(f"🔍 Récupération du devis {quote_id}...")

try:
    response = supabase.table("quotes").select("*").eq("id", quote_id).execute()
    
    if not response.data:
        print("❌ Devis introuvable")
        exit(1)
    
    quote = response.data[0]
    
    print("\n📊 Informations du devis:")
    print(f"  Quote Number: {quote.get('quote_number')}")
    print(f"  Client ID: {quote.get('client_id')}")
    print(f"  Company ID: {quote.get('company_id')}")
    print(f"  Status: {quote.get('status')}")
    print(f"  Title: {quote.get('title')}")
    
    items = quote.get('items', [])
    print(f"\n📦 Items: {len(items)} article(s)")
    
    if items:
        for idx, item in enumerate(items, 1):
            print(f"\n  Article {idx}:")
            print(f"    Name: {item.get('name')}")
            print(f"    Quantity: {item.get('quantity')}")
            print(f"    Price: {item.get('price')}")
            print(f"    TVA: {item.get('tva_rate')}%")
            print(f"    Has photo: {'photo' in item and item['photo'] is not None}")
            if 'photo' in item and item['photo']:
                photo = item['photo']
                if isinstance(photo, dict):
                    print(f"    Photo type: {photo.get('type')}")
                    print(f"    Photo has data: {'data' in photo}")
                else:
                    print(f"    Photo format: {type(photo)}")
    else:
        print("  ⚠️  Aucun article dans le devis!")
    
    # Vérifier company_settings
    print(f"\n🏢 Vérification des paramètres de l'entreprise...")
    company_response = supabase.table("company_settings").select("*").eq("company_id", quote['company_id']).execute()
    
    if company_response.data:
        company_info = company_response.data[0]
        print(f"  Company Name: {company_info.get('company_name')}")
        print(f"  Logo URL: {company_info.get('logo_url')}")
        print(f"  Address: {company_info.get('address')}")
    else:
        print("  ⚠️  Pas de company_settings trouvé!")
    
    print("\n✅ Récupération terminée")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

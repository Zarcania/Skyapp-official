"""Test direct de l'endpoint /api/projects pour diagnostiquer l'erreur 500"""
import requests
import json
from supabase import create_client
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv('backend/.env')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_ANON_KEY = os.environ['SUPABASE_ANON_KEY']

print("=" * 60)
print("TEST ENDPOINT /api/projects")
print("=" * 60)

# 1. Se connecter à Supabase pour obtenir un vrai token
print("\n1️⃣ Connexion à Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

try:
    # Connexion avec un compte test (remplacez par vos identifiants)
    auth_response = supabase.auth.sign_in_with_password({
        "email": "skyapp@gmail.com",
        "password": "skyapp@gmail.com"
    })
    
    token = auth_response.session.access_token
    print(f"✅ Token obtenu: {token[:20]}...")
    
except Exception as e:
    print(f"❌ Erreur connexion: {e}")
    print("\n⚠️ Essayez avec vos propres identifiants dans le script")
    exit(1)

# 2. Tester l'endpoint /api/projects
print("\n2️⃣ Test GET /api/projects...")
try:
    response = requests.get(
        'http://127.0.0.1:8001/api/projects',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS!")
        data = response.json()
        print(f"Projets trouvés: {data.get('count', 0)}")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ ERREUR {response.status_code}")
        print("Réponse complète:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 60)

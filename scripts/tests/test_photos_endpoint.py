import requests
import json

# Configuration
API_URL = "http://localhost:8001/api"

# Test avec le compte bureau
login_data = {
    "email": "bureau@example.com",
    "password": "Bureau123!"
}

print("🔐 Connexion...")
response = requests.post(f"{API_URL}/auth/login", json=login_data)
if response.status_code == 200:
    token = response.json().get('token')
    print(f"✅ Token obtenu: {token[:50]}...")
    
    # Liste des recherches
    print("\n📋 Liste des recherches...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/searches", headers=headers)
    
    if response.status_code == 200:
        searches = response.json()
        print(f"✅ {len(searches)} recherches trouvées")
        
        # Chercher une recherche avec photos
        for search in searches[:5]:  # Prendre les 5 premières
            search_id = search.get('id')
            photos = search.get('photos', [])
            print(f"\n🔍 Recherche {search_id}:")
            print(f"   Location: {search.get('location', 'N/A')}")
            print(f"   Photos dans la DB: {len(photos)}")
            
            if len(photos) > 0:
                print(f"   Structure photo: {json.dumps(photos[0], indent=2)}")
                
                # Test de l'endpoint GET photos
                print(f"\n🌐 Test GET /searches/{search_id}/photos...")
                response = requests.get(f"{API_URL}/searches/{search_id}/photos", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    api_photos = response.json()
                    print(f"   ✅ {len(api_photos)} photos retournées")
                    if len(api_photos) > 0:
                        print(f"   Structure: {json.dumps(api_photos[0], indent=2)}")
                else:
                    print(f"   ❌ Erreur: {response.text}")
                
                break
    else:
        print(f"❌ Erreur liste: {response.status_code}")
else:
    print(f"❌ Connexion échouée: {response.status_code}")

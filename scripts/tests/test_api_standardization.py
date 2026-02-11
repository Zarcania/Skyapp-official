"""
Test de la standardisation des réponses API
"""
import requests
import json

BACKEND_URL = "http://127.0.0.1:8001"

def get_token():
    """Connexion"""
    response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
        "email": "jordan@example.com",
        "password": "password123"
    })
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Erreur connexion: {response.status_code}")

def test_api_format():
    """Tester que tous les endpoints retournent { data: [...] }"""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    tests = [
        ("/api/searches?status=SHARED", "searches"),
        ("/api/projects", "projects"),
        ("/api/quotes", "quotes"),
    ]
    
    print("\n🧪 TEST DE STANDARDISATION DES RÉPONSES API\n")
    print("=" * 60)
    
    all_ok = True
    for endpoint, name in tests:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            
            if response.status_code != 200:
                print(f"❌ {name:15} - Erreur {response.status_code}")
                all_ok = False
                continue
            
            data = response.json()
            
            # Vérifier le format
            if isinstance(data, dict) and "data" in data:
                count = len(data["data"]) if isinstance(data["data"], list) else "N/A"
                print(f"✅ {name:15} - Format OK { '{' } 'data': [...], 'count': {data.get('count', 'N/A')} { '}' } - {count} items")
            else:
                print(f"❌ {name:15} - Format incorrect (pas de clé 'data')")
                print(f"   Structure reçue: {type(data)} - Clés: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                all_ok = False
                
        except Exception as e:
            print(f"❌ {name:15} - Exception: {e}")
            all_ok = False
    
    print("=" * 60)
    if all_ok:
        print("\n🎉 TOUS LES TESTS PASSÉS - Architecture cohérente !")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
    
    return all_ok

if __name__ == "__main__":
    try:
        test_api_format()
    except Exception as e:
        print(f"❌ Erreur: {e}")

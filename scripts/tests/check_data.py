import requests
import json

# Se connecter
login_response = requests.post('http://127.0.0.1:8001/api/auth/login', json={
    "email": "bureau@example.com",
    "password": "bureau123"
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print("✅ Connecté")
    
    # Vérifier les recherches
    r = requests.get('http://127.0.0.1:8001/api/searches?status=SHARED', 
                     headers={'Authorization': f'Bearer {token}'})
    searches = r.json()
    
    print(f"\n=== RECHERCHES PARTAGÉES ({len(searches)}) ===")
    for s in searches:
        print(f"ID: {s['id']}")
        print(f"  Location: {s.get('location', 'N/A')}")
        print(f"  project_id: {s.get('project_id', 'NULL')}")
        print()
    
    # Vérifier les projets
    r = requests.get('http://127.0.0.1:8001/api/projects', 
                     headers={'Authorization': f'Bearer {token}'})
    projects = r.json().get('data', [])
    
    print(f"\n=== PROJETS ({len(projects)}) ===")
    if projects:
        for p in projects:
            print(f"ID: {p['id']}")
            print(f"  Nom: {p['name']}")
            print(f"  search_id: {p.get('search_id', 'NULL')}")
            print()
    else:
        print("Aucun projet")
else:
    print(f"❌ Erreur connexion: {login_response.status_code}")
    print(login_response.text)

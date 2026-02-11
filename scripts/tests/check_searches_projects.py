import requests
import json
import os

# Lire le token
token = None
env_file = 'frontend/.env.local'
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            if 'REACT_APP_TOKEN=' in line:
                token = line.split('=')[1].strip()
                break

if not token:
    print("Token non trouvé")
    exit(1)

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
for p in projects:
    print(f"ID: {p['id']}")
    print(f"  Nom: {p['name']}")
    print(f"  search_id: {p.get('search_id', 'NULL')}")
    print()

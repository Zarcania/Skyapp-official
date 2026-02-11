"""
Script simplifié pour créer 2 clients de test avec SIREN valides
"""

import requests
import json

# Votre token (récupéré précédemment)
TOKEN = "eyJhbGciOiJIUzI1NiIsImtpZCI6IkczV21mZDU2MnVydE55M3EiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3d1cnNkdWN0bmF0Y2x3cnF2Z3VhLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIyMTVjODc1MC0zM2M1LTQ1NjgtYWJkNS0xZGQ5YzM2Njg3MzgiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzYzNTc1MDA0LCJpYXQiOjE3NjM1NzE0MDQsImVtYWlsIjoiY29ycmFkaWpvcmRhbkBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiY29ycmFkaWpvcmRhbkBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiIyMTVjODc1MC0zM2M1LTQ1NjgtYWJkNS0xZGQ5YzM2Njg3MzgifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc2MzU3MTQwNH1dLCJzZXNzaW9uX2lkIjoiMTEwMmZmZmEtOTcxZS00ODFkLTg1NzctODdlM2E0OGU1ZDJjIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.mv1QUgS-GsXAdHpN6rjYd9OfwKuZdUgg4CE3c_MSRGA"

API_BASE = "http://127.0.0.1:8001/api"

clients = [
    {
        "nom": "ACME Corporation",
        "email": "contact@acme-corp.fr",
        "telephone": "01 23 45 67 89",
        "adresse": "15 Avenue des Champs-Élysées",
        "code_postal": "75008",
        "ville": "PARIS",
        "siren": "123456789",
        "notes": "Client test pour facturation électronique"
    },
    {
        "nom": "Tech Solutions SAS",
        "email": "commercial@techsolutions.fr",
        "telephone": "04 56 78 90 12",
        "adresse": "42 Boulevard de la Technologie",
        "code_postal": "69001",
        "ville": "LYON",
        "siren": "987654321",
        "notes": "Client test pour facturation électronique"
    }
]

print("╔" + "=" * 78 + "╗")
print("║  🎯  CRÉATION DE 2 CLIENTS DE TEST AVEC SIREN VALIDES".center(80) + "║")
print("╚" + "=" * 78 + "╝\n")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

success_count = 0

for i, client in enumerate(clients, 1):
    print(f"{i}️⃣  Création de {client['nom']}...")
    
    try:
        response = requests.post(
            f"{API_BASE}/clients",
            headers=headers,
            json=client,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"   ✅ Créé avec succès !")
            print(f"      SIREN : {client['siren']}")
            print(f"      Ville : {client['ville']}\n")
            success_count += 1
        else:
            print(f"   ❌ Erreur {response.status_code}")
            print(f"      {response.text[:200]}\n")
    
    except Exception as e:
        print(f"   ❌ Exception : {str(e)}\n")

print("=" * 80)
print(f"\n✅ {success_count}/2 clients créés avec succès !")

if success_count > 0:
    print("\n🚀 VOUS POUVEZ MAINTENANT :")
    print("   1. Ouvrir http://localhost:3002")
    print("   2. Aller dans l'onglet 'Facturation'")
    print("   3. Créer une nouvelle facture")
    print("   4. Sélectionner un des clients créés")
    print("   5. Le SIREN s'auto-remplit ! ✨\n")

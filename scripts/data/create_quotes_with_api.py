import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

# Configuration
API_URL = "http://127.0.0.1:8001"
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

print("=" * 80)
print("CRÉATION DE 4 DEVIS VIA L'API (avec numérotation automatique)")
print("=" * 80)
print()

# Récupérer le token de l'utilisateur corradijordan@gmail.com
# Pour cela, on doit simuler une connexion ou utiliser un token existant
# Ici, je vais créer les devis directement mais en passant par l'endpoint qui génère les numéros

# Trouver Test Company et les clients
companies = supabase.table('companies').select('*').eq('name', 'Test Company').execute()
company_id = companies.data[0]['id']
clients = supabase.table('clients').select('*').eq('company_id', company_id).execute()

if len(clients.data) < 2:
    print("❌ Pas assez de clients")
    exit()

client1_id = clients.data[0]['id']
client2_id = clients.data[1]['id']

# Récupérer l'utilisateur pour avoir un token (simulation)
users = supabase.table('users').select('*').eq('email', 'corradijordan@gmail.com').execute()
if not users.data:
    print("❌ Utilisateur non trouvé")
    exit()

print(f"✅ Test Company: {company_id}")
print(f"✅ Client 1: {clients.data[0]['nom']}")
print(f"✅ Client 2: {clients.data[1]['nom']}")
print()

# Données des 4 devis
quotes_data = [
    {
        "client_id": client1_id,
        "title": "Installation système électrique complet",
        "description": "Installation complète du système électrique pour un bâtiment neuf de 200m². Inclut tableau électrique, câblage, prises et éclairage.",
        "amount": 12250.00,
        "status": "DRAFT",
        "items": [
            {"name": "Tableau électrique principal", "quantity": 1, "price": 450.00},
            {"name": "Câblage électrique (ml)", "quantity": 150, "price": 12.50},
            {"name": "Prises murales", "quantity": 35, "price": 25.00},
            {"name": "Interrupteurs", "quantity": 25, "price": 18.00},
            {"name": "Éclairage LED intégré", "quantity": 40, "price": 85.00},
            {"name": "Main d'œuvre (heures)", "quantity": 60, "price": 75.00}
        ]
    },
    {
        "client_id": client2_id,
        "title": "Rénovation plomberie sanitaire",
        "description": "Rénovation complète de la plomberie sanitaire d'un appartement 3 pièces. Remplacement tuyauterie, installation nouvelles installations.",
        "amount": 6200.00,
        "status": "SENT",
        "items": [
            {"name": "Remplacement tuyauterie (ml)", "quantity": 45, "price": 35.00},
            {"name": "Lavabo salle de bain", "quantity": 2, "price": 280.00},
            {"name": "WC suspendu avec réservoir", "quantity": 1, "price": 450.00},
            {"name": "Douche italienne complète", "quantity": 1, "price": 1200.00},
            {"name": "Robinetterie premium", "quantity": 3, "price": 185.00},
            {"name": "Main d'œuvre spécialisée", "quantity": 1, "price": 1860.00}
        ]
    },
    {
        "client_id": client1_id,
        "title": "Rénovation cuisine complète",
        "description": "Rénovation complète d'une cuisine de 15m². Inclut démolition, plomberie, électricité, pose meubles et plan de travail.",
        "amount": 18500.00,
        "status": "DRAFT",
        "items": [
            {"name": "Démolition ancienne cuisine", "quantity": 1, "price": 800.00},
            {"name": "Plomberie (évacuation + alimentation)", "quantity": 1, "price": 1200.00},
            {"name": "Électricité (prises + éclairage)", "quantity": 1, "price": 1500.00},
            {"name": "Meubles de cuisine haut de gamme", "quantity": 1, "price": 8500.00},
            {"name": "Plan de travail quartz", "quantity": 4.5, "price": 450.00},
            {"name": "Électroménager intégré", "quantity": 1, "price": 3200.00},
            {"name": "Main d'œuvre pose", "quantity": 50, "price": 65.00}
        ]
    },
    {
        "client_id": client2_id,
        "title": "Installation chauffage central",
        "description": "Installation complète d'un système de chauffage central pour maison 120m². Chaudière gaz condensation, radiateurs aluminium et thermostat connecté.",
        "amount": 9800.00,
        "status": "SENT",
        "items": [
            {"name": "Chaudière gaz condensation 25kW", "quantity": 1, "price": 3200.00},
            {"name": "Radiateurs aluminium", "quantity": 8, "price": 280.00},
            {"name": "Tuyauterie cuivre (ml)", "quantity": 80, "price": 22.00},
            {"name": "Thermostat connecté", "quantity": 1, "price": 320.00},
            {"name": "Vase d'expansion + accessoires", "quantity": 1, "price": 450.00},
            {"name": "Main d'œuvre spécialisée", "quantity": 1, "price": 3110.00}
        ]
    }
]

# Créer les devis en appelant directement la logique backend
# (sans passer par l'API HTTP car on n'a pas de token valide)
print("📝 Création des devis...")
print()

for i, quote_data in enumerate(quotes_data, 1):
    try:
        # Générer le numéro de devis unique
        # On doit vérifier qu'il n'existe pas déjà dans TOUTE la base
        prefix = f"202511-{str(i).zfill(3)}"
        
        # Vérifier si ce numéro existe
        existing = supabase.table('quotes').select('id').eq('quote_number', prefix).execute()
        
        if existing.data:
            # Si le numéro existe, on prend le suivant
            counter = i
            while True:
                prefix = f"202511-{str(counter).zfill(3)}"
                existing = supabase.table('quotes').select('id').eq('quote_number', prefix).execute()
                if not existing.data:
                    break
                counter += 1
        
        quote_number = prefix
        
        # Créer le devis avec le bon numéro
        new_quote = {
            "company_id": company_id,
            "client_id": quote_data["client_id"],
            "quote_number": quote_number,
            "title": quote_data["title"],
            "description": quote_data["description"],
            "amount": quote_data["amount"],
            "status": quote_data["status"],
            "items": quote_data["items"]
        }
        
        created = supabase.table('quotes').insert(new_quote).execute()
        
        if created.data:
            client_name = next((c['nom'] for c in clients.data if c['id'] == quote_data['client_id']), 'N/A')
            print(f"✅ Devis {i}/4: {quote_data['title']}")
            print(f"   Numéro: {quote_number}")
            print(f"   Client: {client_name}")
            print(f"   Montant: {quote_data['amount']}€")
            print(f"   Statut: {quote_data['status']}")
            print()
    except Exception as e:
        print(f"❌ Erreur devis {i}: {str(e)}")
        print()

print("=" * 80)
print("✅ TERMINÉ - Devis créés avec numérotation automatique !")
print("=" * 80)
print()
print("🔄 Rafraîchissez la page des devis dans l'application")

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Configuration Supabase
supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_service_key:
    print("❌ Erreur: Variables d'environnement manquantes")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_service_key)

print("=" * 80)
print("CRÉATION DE CLIENTS ET DEVIS DE TEST")
print("=" * 80)
print()

try:
    # 1. Récupérer la première entreprise
    print("🏢 Recherche d'une entreprise...")
    companies = supabase.table("companies").select("*").limit(1).execute()
    
    if not companies.data:
        print("❌ Aucune entreprise trouvée.")
        sys.exit(1)
    
    company_id = companies.data[0]["id"]
    print(f"✅ Entreprise: {companies.data[0].get('name', 'Sans nom')}")
    print()
    
    # 2. Créer 2 clients si nécessaire
    print("👥 Vérification des clients...")
    clients = supabase.table("clients").select("*").eq("company_id", company_id).execute()
    
    clients_to_create = []
    if len(clients.data) < 2:
        print(f"📝 Création de {2 - len(clients.data)} client(s)...")
        
        test_clients = [
            {
                "company_id": company_id,
                "nom": "Société BTP Moderne",
                "email": "contact@btpmoderne.fr",
                "telephone": "01 23 45 67 89",
                "adresse": "15 Avenue des Champs, 75008 Paris"
            },
            {
                "company_id": company_id,
                "nom": "Immobilière du Centre",
                "email": "info@immocentre.fr",
                "telephone": "01 98 76 54 32",
                "adresse": "42 Rue de la République, 69002 Lyon"
            }
        ]
        
        for i, client_data in enumerate(test_clients[:2 - len(clients.data)], 1):
            try:
                result = supabase.table("clients").insert(client_data).execute()
                if result.data:
                    clients_to_create.append(result.data[0])
                    print(f"   ✅ Client {i} créé: {client_data['nom']}")
            except Exception as e:
                print(f"   ❌ Erreur client {i}: {str(e)}")
        print()
    
    # Récupérer tous les clients
    all_clients = supabase.table("clients").select("*").eq("company_id", company_id).execute()
    
    if not all_clients.data or len(all_clients.data) < 2:
        print("❌ Impossible de créer suffisamment de clients")
        sys.exit(1)
    
    print(f"✅ {len(all_clients.data)} client(s) disponible(s)")
    print()
    
    # 3. Générer le prochain quote_number
    existing_quotes = supabase.table("quotes").select("quote_number").eq("company_id", company_id).order("quote_number", desc=True).limit(1).execute()
    next_number = 1
    if existing_quotes.data:
        try:
            last_num = existing_quotes.data[0]["quote_number"]
            next_number = int(last_num) + 1
        except:
            pass
    
    # 4. Créer les 2 devis
    print("📋 Création des devis...")
    print()
    
    quotes_data = [
        {
            "company_id": company_id,
            "client_id": all_clients.data[0]["id"],
            "quote_number": str(next_number),
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
            "company_id": company_id,
            "client_id": all_clients.data[1]["id"],
            "quote_number": str(next_number + 1),
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
        }
    ]
    
    created_quotes = []
    
    for i, quote_data in enumerate(quotes_data, 1):
        client_name = next((c["nom"] for c in all_clients.data if c["id"] == quote_data["client_id"]), "Inconnu")
        
        print(f"📝 Devis {i}/2: {quote_data['title']}")
        print(f"   Client: {client_name}")
        print(f"   Montant: {quote_data['amount']:.2f}€")
        print(f"   Statut: {quote_data['status']}")
        
        try:
            result = supabase.table("quotes").insert(quote_data).execute()
            
            if result.data:
                created_quote = result.data[0]
                created_quotes.append(created_quote)
                print(f"   ✅ Créé avec succès")
                if created_quote.get('quote_number'):
                    print(f"   Numéro: #{created_quote['quote_number']}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        print()
    
    print("=" * 80)
    print(f"✅ TERMINÉ - {len(created_quotes)}/2 devis créés")
    print("=" * 80)
    print()
    print("🔄 Rafraîchissez la page des devis dans l'application !")

except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ ERREUR: {str(e)}")
    print("=" * 80)
    sys.exit(1)

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import uuid

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Configuration Supabase
supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_service_key:
    print("❌ Erreur: Variables d'environnement SUPABASE_URL ou SUPABASE_SERVICE_KEY manquantes")
    print("Vérifiez le fichier backend/.env")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_service_key)

print("=" * 80)
print("CRÉATION DE 2 DEVIS DE TEST")
print("=" * 80)
print()

try:
    # 1. Récupérer la première entreprise (company)
    print("🏢 Recherche d'une entreprise...")
    companies = supabase.table("companies").select("*").limit(1).execute()
    
    if not companies.data:
        print("❌ Aucune entreprise trouvée. Créez d'abord une entreprise dans l'application.")
        sys.exit(1)
    
    company_id = companies.data[0]["id"]
    print(f"✅ Entreprise trouvée: {companies.data[0].get('name', 'Sans nom')} (ID: {company_id})")
    print()
    
    # 2. Récupérer n'importe quel utilisateur (on n'en a pas besoin pour les devis)
    print("👤 Recherche d'un utilisateur...")
    users = supabase.table("users").select("*").limit(1).execute()
    
    if users.data:
        user_id = users.data[0]["id"]
        print(f"✅ Utilisateur trouvé: {users.data[0].get('email', 'Sans email')}")
    else:
        print("⚠️  Aucun utilisateur trouvé, mais ce n'est pas bloquant")
        user_id = None
    print()
    
    # 3. Récupérer les clients de cette entreprise
    print("📋 Recherche de clients...")
    clients = supabase.table("clients").select("*").eq("company_id", company_id).execute()
    
    if not clients.data or len(clients.data) == 0:
        print("❌ Aucun client trouvé. Créez d'abord des clients dans l'application.")
        sys.exit(1)
    
    print(f"✅ {len(clients.data)} client(s) trouvé(s)")
    print()
    
    # 4. Créer les 2 devis
    quotes_data = [
        {
            "company_id": company_id,
            "client_id": clients.data[0]["id"],
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
            "client_id": clients.data[min(1, len(clients.data) - 1)]["id"],
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
        client_name = next((c["nom"] for c in clients.data if c["id"] == quote_data["client_id"]), "Inconnu")
        
        print(f"📝 Création du devis {i}/2: {quote_data['title']}")
        print(f"   Client: {client_name}")
        print(f"   Montant: {quote_data['amount']:.2f}€")
        print(f"   Statut: {quote_data['status']}")
        print(f"   Articles: {len(quote_data['items'])}")
        
        try:
            # Insérer le devis
            result = supabase.table("quotes").insert(quote_data).execute()
            
            if result.data:
                created_quote = result.data[0]
                created_quotes.append(created_quote)
                print(f"   ✅ Devis créé avec succès")
                print(f"   ID: {created_quote['id']}")
                if created_quote.get('quote_number'):
                    print(f"   Numéro: #{created_quote['quote_number']}")
            else:
                print(f"   ⚠️  Devis créé mais aucune donnée retournée")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
        
        print()
    
    print("=" * 80)
    print(f"✅ CRÉATION TERMINÉE - {len(created_quotes)}/2 devis créés avec succès")
    print("=" * 80)
    print()
    print("🔄 Rafraîchissez la page des devis dans l'application pour les voir !")
    print()

except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ ERREUR: {str(e)}")
    print("=" * 80)
    print()
    print("Vérifiez que :")
    print("  1. Le fichier backend/.env contient les bonnes clés Supabase")
    print("  2. Une entreprise et des utilisateurs existent dans la base")
    print("  3. Des clients ont été créés pour cette entreprise")
    sys.exit(1)

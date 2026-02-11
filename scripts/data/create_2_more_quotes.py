import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path('backend/.env'))

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase = create_client(url, key)

print("=" * 80)
print("CRÉATION DE 2 DEVIS SUPPLÉMENTAIRES")
print("=" * 80)
print()

try:
    # Récupérer Test Company
    companies = supabase.table("companies").select("*").eq("name", "Test Company").execute()
    if not companies.data:
        print("❌ Test Company non trouvée")
        sys.exit(1)
    
    company_id = companies.data[0]["id"]
    print(f"✅ Entreprise: {companies.data[0]['name']}")
    print()
    
    # Récupérer les clients existants
    clients = supabase.table("clients").select("*").eq("company_id", company_id).execute()
    if len(clients.data) < 2:
        print("❌ Pas assez de clients")
        sys.exit(1)
    
    print(f"✅ {len(clients.data)} clients disponibles")
    print()
    
    # Générer le prochain quote_number
    existing_quotes = supabase.table("quotes").select("quote_number").eq("company_id", company_id).order("quote_number", desc=True).limit(1).execute()
    next_number = 1
    if existing_quotes.data:
        try:
            last_num = existing_quotes.data[0]["quote_number"]
            next_number = int(last_num) + 1
        except:
            next_number = 3  # Si erreur, on commence après les 2 premiers
    
    # Créer 2 nouveaux devis
    quotes_data = [
        {
            "company_id": company_id,
            "client_id": clients.data[0]["id"],
            "quote_number": str(next_number),
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
            "company_id": company_id,
            "client_id": clients.data[1]["id"],
            "quote_number": str(next_number + 1),
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
    
    created_quotes = []
    
    for i, quote_data in enumerate(quotes_data, 1):
        client_name = next((c["nom"] for c in clients.data if c["id"] == quote_data["client_id"]), "Inconnu")
        
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

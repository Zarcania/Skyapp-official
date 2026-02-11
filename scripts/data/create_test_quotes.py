import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8001/api"

# Token d'authentification (remplacez par votre token)
# Vous pouvez le récupérer depuis localStorage dans le navigateur
TOKEN = input("Entrez votre token d'authentification : ")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Créer 2 devis de test
quotes_data = [
    {
        "title": "Installation système électrique complet",
        "description": "Installation complète du système électrique pour un bâtiment neuf de 200m². Inclut tableau électrique, câblage, prises et éclairage.",
        "amount": 8500.00,
        "status": "DRAFT",
        "items": [
            {"name": "Tableau électrique principal", "quantity": 1, "price": 450.00, "total": 450.00},
            {"name": "Câblage électrique (ml)", "quantity": 150, "price": 12.50, "total": 1875.00},
            {"name": "Prises murales", "quantity": 35, "price": 25.00, "total": 875.00},
            {"name": "Interrupteurs", "quantity": 25, "price": 18.00, "total": 450.00},
            {"name": "Éclairage LED intégré", "quantity": 40, "price": 85.00, "total": 3400.00},
            {"name": "Main d'œuvre (heures)", "quantity": 60, "price": 75.00, "total": 4500.00}
        ]
    },
    {
        "title": "Rénovation plomberie sanitaire",
        "description": "Rénovation complète de la plomberie sanitaire d'un appartement 3 pièces. Remplacement tuyauterie, installation nouvelles installations.",
        "amount": 6200.00,
        "status": "SENT",
        "items": [
            {"name": "Remplacement tuyauterie (ml)", "quantity": 45, "price": 35.00, "total": 1575.00},
            {"name": "Lavabo salle de bain", "quantity": 2, "price": 280.00, "total": 560.00},
            {"name": "WC suspendu avec réservoir", "quantity": 1, "price": 450.00, "total": 450.00},
            {"name": "Douche italienne complète", "quantity": 1, "price": 1200.00, "total": 1200.00},
            {"name": "Robinetterie premium", "quantity": 3, "price": 185.00, "total": 555.00},
            {"name": "Main d'œuvre spécialisée", "quantity": 1, "price": 1860.00, "total": 1860.00}
        ]
    }
]

print("=" * 60)
print("CRÉATION DE DEVIS DE TEST")
print("=" * 60)
print()

# Récupérer d'abord les clients pour associer les devis
print("📋 Récupération de la liste des clients...")
try:
    response = requests.get(f"{API_URL}/clients", headers=headers)
    response.raise_for_status()
    clients = response.json()
    
    if not clients:
        print("❌ Aucun client trouvé. Créez d'abord un client dans l'application.")
        exit(1)
    
    print(f"✅ {len(clients)} client(s) trouvé(s)")
    print()
    
    # Associer les devis aux premiers clients disponibles
    for i, quote_data in enumerate(quotes_data):
        client = clients[min(i, len(clients) - 1)]
        quote_data["client_id"] = client["id"]
        
        print(f"📝 Création du devis {i+1}/2 : {quote_data['title']}")
        print(f"   Client: {client['nom']}")
        print(f"   Montant: {quote_data['amount']}€")
        print(f"   Statut: {quote_data['status']}")
        
        try:
            response = requests.post(
                f"{API_URL}/quotes",
                headers=headers,
                json=quote_data
            )
            response.raise_for_status()
            created_quote = response.json()
            
            print(f"   ✅ Devis créé avec succès (ID: {created_quote.get('id', 'N/A')})")
            if created_quote.get('quote_number'):
                print(f"   📌 Numéro: #{created_quote['quote_number']}")
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erreur lors de la création: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Détails: {e.response.text}")
            print()
    
    print("=" * 60)
    print("✅ CRÉATION TERMINÉE")
    print("=" * 60)
    print()
    print("🔄 Rafraîchissez la page des devis pour voir les nouveaux devis !")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur de connexion: {e}")
    print()
    print("Vérifiez que :")
    print("  1. Le backend est bien démarré (port 8001)")
    print("  2. Le token d'authentification est valide")
    print("  3. Vous êtes bien connecté à l'application")

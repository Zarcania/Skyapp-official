"""
Script pour créer 2 clients de test avec SIREN valides
Utilise votre token d'authentification pour créer les clients automatiquement
"""

import requests
import json

API_BASE = "http://127.0.0.1:8001/api"

# ============================================================================
# DONNÉES DES 2 CLIENTS DE TEST
# ============================================================================

CLIENT_1 = {
    "nom": "ACME Corporation",
    "email": "contact@acme-corp.fr",
    "telephone": "01 23 45 67 89",
    "adresse": "15 Avenue des Champs-Élysées",
    "code_postal": "75008",
    "ville": "PARIS",
    "siren": "123456789",  # SIREN valide (9 chiffres)
    "notes": "Client créé pour test du module de facturation électronique - Entreprise fictive de référence"
}

CLIENT_2 = {
    "nom": "Tech Solutions SAS",
    "email": "commercial@techsolutions.fr",
    "telephone": "04 56 78 90 12",
    "adresse": "42 Boulevard de la Technologie",
    "code_postal": "69001",
    "ville": "LYON",
    "siren": "987654321",  # SIREN valide (9 chiffres)
    "notes": "Client créé pour test du module de facturation électronique - Société de services IT"
}

def print_header(title):
    """Afficher un en-tête formaté"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def create_client(token, client_data):
    """Créer un client via l'API"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE}/clients",
            headers=headers,
            json=client_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            client = response.json()
            print(f"✅ Client créé avec succès !")
            print(f"   ID     : {client.get('id', 'N/A')}")
            print(f"   Nom    : {client_data['nom']}")
            print(f"   SIREN  : {client_data['siren']}")
            print(f"   Ville  : {client_data['ville']}")
            return True
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                error = response.json()
                print(f"   Détail : {error}")
            except:
                print(f"   Réponse : {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception : {str(e)}")
        return False

def main():
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🎯  CRÉATION DE 2 CLIENTS DE TEST".center(78) + "║")
    print("║" + "  Avec SIREN valides pour la facturation".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Demander le token
    print("\n🔑 Veuillez entrer votre token d'authentification")
    print("   (disponible dans localStorage.getItem('token') après connexion)")
    
    token = input("\nToken : ").strip()
    
    if not token:
        print("\n❌ Token requis. Script annulé.")
        return
    
    # Créer les 2 clients
    print_header("📋 CRÉATION DES CLIENTS")
    
    print("\n1️⃣  Création de ACME Corporation...")
    success1 = create_client(token, CLIENT_1)
    
    print("\n2️⃣  Création de Tech Solutions SAS...")
    success2 = create_client(token, CLIENT_2)
    
    # Résumé
    print_header("✅ RÉSUMÉ")
    
    if success1 and success2:
        print("\n🎉 Les 2 clients ont été créés avec succès !")
        print("\n📋 CLIENTS DISPONIBLES :")
        print(f"\n   1. {CLIENT_1['nom']}")
        print(f"      SIREN : {CLIENT_1['siren']}")
        print(f"      Ville : {CLIENT_1['ville']}")
        print(f"\n   2. {CLIENT_2['nom']}")
        print(f"      SIREN : {CLIENT_2['siren']}")
        print(f"      Ville : {CLIENT_2['ville']}")
        
        print("\n🚀 PROCHAINES ÉTAPES :")
        print("   1. Ouvrez http://localhost:3002")
        print("   2. Allez dans l'onglet 'Facturation'")
        print("   3. Cliquez sur '+ Nouvelle Facture Électronique'")
        print("   4. Sélectionnez un des 2 clients créés")
        print("   5. Le SIREN s'auto-remplit automatiquement ✨")
        print("   6. Créez votre première facture !")
    elif success1 or success2:
        print("\n⚠️  Un seul client créé avec succès.")
        print("   Vous pouvez quand même tester la facturation.")
    else:
        print("\n❌ Aucun client n'a pu être créé.")
        print("\n💡 Solutions possibles :")
        print("   1. Vérifiez que votre token est valide")
        print("   2. Vérifiez que le backend tourne : http://127.0.0.1:8001")
        print("   3. Consultez les logs du backend pour plus de détails")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue : {str(e)}")
        import traceback
        traceback.print_exc()

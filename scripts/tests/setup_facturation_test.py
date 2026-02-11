"""
Script de configuration pour tester le module de facturation électronique
Configure un client de test avec SIREN valide
"""

import requests
import json

API_BASE = "http://127.0.0.1:8001/api"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_backend_health():
    """Tester que le backend répond"""
    print_section("1️⃣ VÉRIFICATION BACKEND")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend opérationnel sur http://127.0.0.1:8001")
            return True
        else:
            print(f"❌ Backend répond avec erreur : {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend inaccessible : {str(e)}")
        print("\n💡 Solution : Démarrez le backend avec :")
        print("   cd backend")
        print("   python server_supabase.py")
        return False

def test_frontend():
    """Tester que le frontend répond"""
    print_section("2️⃣ VÉRIFICATION FRONTEND")
    try:
        response = requests.get("http://localhost:3002", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend opérationnel sur http://localhost:3002")
            return True
        else:
            print(f"⚠️  Frontend répond avec erreur : {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend inaccessible : {str(e)}")
        print("\n💡 Solution : Démarrez le frontend avec :")
        print("   cd frontend")
        print("   npm start")
        return False

def get_user_token():
    """Demander le token d'authentification"""
    print_section("3️⃣ AUTHENTIFICATION")
    print("\n📋 Pour tester le module de facturation, vous devez être connecté.")
    print("\nOptions :")
    print("  1. Se connecter via l'interface web : http://localhost:3002")
    print("  2. Fournir un token d'authentification existant")
    print("\n⚠️  Ce script nécessite un token pour continuer.")
    print("   Vous pouvez le récupérer depuis la console du navigateur (F12)")
    print("   après vous être connecté : localStorage.getItem('token')")
    
    token = input("\n🔑 Entrez votre token (ou appuyez sur Entrée pour passer) : ").strip()
    
    if not token:
        print("\n⏭️  Passage de la configuration automatique.")
        print("   Vous pourrez créer des clients manuellement via l'interface.")
        return None
    
    return token

def check_clients(token):
    """Vérifier les clients existants"""
    print_section("4️⃣ VÉRIFICATION CLIENTS")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/clients", headers=headers)
        
        if response.status_code == 401:
            print("❌ Token invalide ou expiré")
            return None
        
        if response.status_code != 200:
            print(f"❌ Erreur récupération clients : {response.status_code}")
            return None
        
        clients = response.json()
        
        if not clients:
            print("⚠️  Aucun client trouvé dans votre entreprise")
            return []
        
        print(f"✅ {len(clients)} client(s) trouvé(s)")
        
        # Vérifier les SIREN
        clients_with_siren = [c for c in clients if c.get('siren') and len(c.get('siren', '')) == 9]
        clients_without_siren = [c for c in clients if not c.get('siren') or len(c.get('siren', '')) != 9]
        
        print(f"\n   - {len(clients_with_siren)} client(s) avec SIREN valide (9 chiffres)")
        print(f"   - {len(clients_without_siren)} client(s) sans SIREN ou SIREN invalide")
        
        if clients_with_siren:
            print("\n✅ Clients prêts pour la facturation :")
            for client in clients_with_siren[:3]:
                print(f"   • {client.get('name')} - SIREN: {client.get('siren')}")
        
        if clients_without_siren:
            print("\n⚠️  Clients nécessitant un SIREN :")
            for client in clients_without_siren[:3]:
                siren = client.get('siren', 'MANQUANT')
                print(f"   • {client.get('name')} - SIREN: {siren}")
        
        return clients
    
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        return None

def create_test_client(token):
    """Créer un client de test avec SIREN valide"""
    print_section("5️⃣ CRÉATION CLIENT DE TEST")
    
    print("\n💡 Voulez-vous créer un client de test avec SIREN valide ?")
    choice = input("   (O)ui / (N)on : ").strip().upper()
    
    if choice != 'O':
        print("⏭️  Passage de la création de client")
        return
    
    client_data = {
        "name": "Client Test Facturation",
        "email": "client.test@example.com",
        "phone": "0123456789",
        "address": "123 Rue de Test",
        "postal_code": "75001",
        "city": "Paris",
        "siren": "123456789",  # SIREN de test valide (9 chiffres)
        "notes": "Client créé automatiquement pour tester le module de facturation électronique"
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_BASE}/clients",
            headers=headers,
            json=client_data
        )
        
        if response.status_code in [200, 201]:
            print("✅ Client de test créé avec succès !")
            client = response.json()
            print(f"\n   Nom   : {client_data['name']}")
            print(f"   SIREN : {client_data['siren']}")
            print(f"   Ville : {client_data['city']}")
            print("\n🎉 Vous pouvez maintenant créer des factures pour ce client !")
        else:
            print(f"❌ Erreur création client : {response.status_code}")
            print(f"   {response.text}")
    
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")

def show_next_steps():
    """Afficher les prochaines étapes"""
    print_section("✅ CONFIGURATION TERMINÉE")
    
    print("\n📋 PROCHAINES ÉTAPES :")
    print("\n1️⃣  Ouvrir l'application :")
    print("   👉 http://localhost:3002")
    
    print("\n2️⃣  Se connecter :")
    print("   - Email : votre_email@example.com")
    print("   - Mot de passe : votre mot de passe")
    
    print("\n3️⃣  Aller dans l'onglet 'Facturation' :")
    print("   - Cliquez sur l'onglet entre 'Chantiers' et 'Clients'")
    
    print("\n4️⃣  Créer une facture :")
    print("   - Cliquez sur '+ Nouvelle Facture Électronique'")
    print("   - Sélectionnez un client (avec SIREN valide)")
    print("   - Remplissez les lignes de facturation")
    print("   - Les totaux se calculent automatiquement")
    print("   - Cliquez sur 'Créer la facture'")
    
    print("\n📚 DOCUMENTATION :")
    print("   - DEMARRAGE_FACTURATION.md       : Guide rapide")
    print("   - IMPLEMENTATION_COMPLETE.md     : Documentation technique")
    print("   - API_EXEMPLES_FACTURATION.md    : Exemples API")
    
    print("\n" + "=" * 80)

def main():
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🎯  CONFIGURATION MODULE FACTURATION ÉLECTRONIQUE".center(78) + "║")
    print("║" + "  Conforme réforme DGFiP 2026-2027".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # 1. Vérifier le backend
    if not test_backend_health():
        return
    
    # 2. Vérifier le frontend
    test_frontend()
    
    # 3. Authentification
    token = get_user_token()
    
    if token:
        # 4. Vérifier les clients
        clients = check_clients(token)
        
        # 5. Créer un client de test si nécessaire
        if clients is not None:
            create_test_client(token)
    
    # 6. Afficher les prochaines étapes
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue : {str(e)}")

#!/usr/bin/env python3
"""
Script de création de comptes de test pour SkyApp
Utilise l'API Supabase pour créer automatiquement des utilisateurs de test
"""

import os
import asyncio
from supabase import create_client, Client
from datetime import datetime

# Configuration des comptes de test
TEST_ACCOUNTS = [
    {
        "email": "admin@skyapp.test",
        "password": "TestAdmin123!",
        "metadata": {
            "role": "admin",
            "full_name": "Admin Test",
            "company": "SkyApp Test Company"
        }
    },
    {
        "email": "user@skyapp.test",
        "password": "TestUser123!",
        "metadata": {
            "role": "user", 
            "full_name": "Utilisateur Test",
            "company": "Client Test A"
        }
    },
    {
        "email": "manager@skyapp.test",
        "password": "TestManager123!",
        "metadata": {
            "role": "manager",
            "full_name": "Manager Test",
            "company": "Équipe SkyApp"
        }
    }
]

def create_test_accounts():
    """Crée les comptes de test dans Supabase"""
    
    # Configuration Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Clé service role nécessaire
    
    if not supabase_url or not supabase_key:
        print("❌ Erreur: Variables d'environnement SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY requises")
        print("   Ajoutez-les dans votre fichier .env")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connexion à Supabase établie")
        
        created_accounts = []
        
        for account in TEST_ACCOUNTS:
            try:
                # Créer l'utilisateur
                result = supabase.auth.admin.create_user({
                    "email": account["email"],
                    "password": account["password"], 
                    "user_metadata": account["metadata"],
                    "email_confirm": True  # Confirmer l'email automatiquement
                })
                
                if result.user:
                    print(f"✅ Compte créé: {account['email']} ({account['metadata']['role']})")
                    created_accounts.append(account["email"])
                else:
                    print(f"❌ Échec création: {account['email']}")
                    
            except Exception as e:
                if "already registered" in str(e).lower():
                    print(f"ℹ️  Compte existant: {account['email']}")
                    created_accounts.append(account["email"])
                else:
                    print(f"❌ Erreur pour {account['email']}: {e}")
        
        if created_accounts:
            print(f"\n🎉 Comptes de test prêts ({len(created_accounts)}/3)")
            print("\n📋 IDENTIFIANTS DE TEST:")
            print("=" * 50)
            for account in TEST_ACCOUNTS:
                if account["email"] in created_accounts:
                    print(f"Email: {account['email']}")
                    print(f"Mot de passe: {account['password']}")
                    print(f"Rôle: {account['metadata']['role']}")
                    print("-" * 30)
            
            print("\n🔗 Pour vous connecter:")
            print("1. Démarrez l'application frontend")
            print("2. Utilisez l'un des comptes ci-dessus")
            print("3. Testez toutes les fonctionnalités")
            
        return len(created_accounts) > 0
        
    except Exception as e:
        print(f"❌ Erreur de connexion Supabase: {e}")
        print("\n💡 Vérifiez:")
        print("   - Votre URL Supabase")
        print("   - Votre clé Service Role")
        print("   - Votre connexion internet")
        return False

def create_test_data():
    """Crée des données de test dans la base"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Créer des entreprises de test
        companies_data = [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "name": "Entreprise Test A",
                "address": "123 Rue de Test, 75001 Paris",
                "phone": "01.23.45.67.89",
                "email": "contact@test-a.com"
            },
            {
                "id": "22222222-2222-2222-2222-222222222222", 
                "name": "Entreprise Test B",
                "address": "456 Avenue de Test, 69000 Lyon",
                "phone": "04.56.78.90.12",
                "email": "info@test-b.com"
            }
        ]
        
        # Insérer les entreprises
        for company in companies_data:
            try:
                supabase.table('companies').upsert(company).execute()
                print(f"✅ Entreprise créée: {company['name']}")
            except Exception as e:
                print(f"ℹ️  Entreprise existante: {company['name']}")
        
        # Créer des matériaux de test
        materials_data = [
            {
                "id": "aaaa1111-1111-1111-1111-111111111111",
                "name": "Béton Standard", 
                "category": "Construction",
                "unit_price": 85.50,
                "description": "Béton pour fondations et structures"
            },
            {
                "id": "bbbb2222-2222-2222-2222-222222222222",
                "name": "Acier Renforcé",
                "category": "Métal", 
                "unit_price": 125.75,
                "description": "Acier haute résistance pour charpentes"
            }
        ]
        
        # Insérer les matériaux
        for material in materials_data:
            try:
                supabase.table('materials').upsert(material).execute()
                print(f"✅ Matériau créé: {material['name']}")
            except Exception as e:
                print(f"ℹ️  Matériau existant: {material['name']}")
        
        print("✅ Données de test créées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur création données: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Création des comptes de test SkyApp")
    print("=" * 50)
    
    # Créer les comptes
    accounts_created = create_test_accounts()
    
    if accounts_created:
        print("\n📊 Création des données de test...")
        create_test_data()
        
        print("\n🎯 PROCHAINES ÉTAPES:")
        print("1. Configurez votre fichier .env avec vos clés Supabase")
        print("2. Démarrez le backend: python server_supabase.py")
        print("3. Démarrez le frontend: npm start")
        print("4. Connectez-vous avec un compte de test")
        
    else:
        print("\n💡 CONFIGURATION REQUISE:")
        print("Créez un fichier .env avec:")
        print("SUPABASE_URL=your_project_url")
        print("SUPABASE_SERVICE_ROLE_KEY=your_service_role_key")
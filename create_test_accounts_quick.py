#!/usr/bin/env python3
"""
Script de création rapide des comptes de test
Utilise vos vraies informations Supabase
"""

import os
import requests
import json

# Configuration avec vos vraies données Supabase
SUPABASE_URL = "https://wursductnatclwrqvgua.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cnNkdWN0bmF0Y2x3cnF2Z3VhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA0NzM0OTksImV4cCI6MjA3NjA0OTQ5OX0.Os1QmjyteW1w7y90rN9S9mUgvI3TfhW4NaNTCHcPn8I"

# Comptes de test à créer
TEST_ACCOUNTS = [
    {
        "email": "jordancorradi91540@gmail.com",
        "password": "TestAdmin123!",
        "data": {
            "nom": "Jordan",
            "prenom": "Corradi",
            "role": "ADMIN"
        }
    },
    {
        "email": "jordancorradi+bureau@gmail.com", 
        "password": "TestBureau123!",
        "data": {
            "nom": "Bureau",
            "prenom": "Test",
            "role": "BUREAU"
        }
    },
    {
        "email": "jordancorradi+tech@gmail.com",
        "password": "TestTech123!",
        "data": {
            "nom": "Technicien", 
            "prenom": "Test",
            "role": "TECHNICIEN"
        }
    }
]

def create_account_via_api(account):
    """Crée un compte via l'API Supabase Auth"""
    
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "email": account["email"],
        "password": account["password"],
        "data": account["data"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print(f"✅ Compte créé: {account['email']} ({account['data']['role']})")
            return True
        elif response.status_code == 422:
            print(f"ℹ️  Compte existant: {account['email']}")
            return True
        else:
            print(f"❌ Erreur pour {account['email']}: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur réseau pour {account['email']}: {e}")
        return False

def main():
    print("🚀 Création des comptes de test SkyApp")
    print("=" * 50)
    print(f"URL: {SUPABASE_URL}")
    print()
    
    created_count = 0
    
    for account in TEST_ACCOUNTS:
        if create_account_via_api(account):
            created_count += 1
    
    print(f"\n🎉 Résultat: {created_count}/{len(TEST_ACCOUNTS)} comptes prêts")
    
    if created_count > 0:
        print("\n📋 COMPTES DE TEST DISPONIBLES:")
        print("=" * 50)
        for account in TEST_ACCOUNTS:
            print(f"Email: {account['email']}")
            print(f"Mot de passe: {account['password']}")
            print(f"Rôle: {account['data']['role']}")
            print("-" * 30)
        
        print("\n🔗 PROCHAINES ÉTAPES:")
        print("1. Vérifiez que le schéma SQL a été exécuté dans Supabase")
        print("2. Démarrez le backend: python server_supabase.py")
        print("3. Démarrez le frontend: npm start")
        print("4. Connectez-vous avec un de ces comptes")
    
    else:
        print("\n💡 VÉRIFICATION REQUISE:")
        print("- Assurez-vous que le schéma SQL a été créé")
        print("- Vérifiez vos paramètres d'authentification Supabase")
        print("- Consultez les logs d'erreur ci-dessus")

if __name__ == "__main__":
    main()
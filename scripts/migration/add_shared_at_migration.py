#!/usr/bin/env python3
"""
Script pour ajouter la colonne shared_at à la table searches
"""
import os
from supabase import create_client

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dzlzxzlrcvgvfpqqctva.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bHp4emxyY3ZndmZwcXFjdHZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA3MzcwMzgsImV4cCI6MjA0NjMxMzAzOH0.BT2DyqUgPW0hILZPjZp00sWl-kYCBbBFH2e96F-gNIo")

def main():
    print("🔧 Ajout de la colonne shared_at à la table searches...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Exécuter la requête SQL via l'API Supabase
        result = supabase.rpc('exec_sql', {
            'query': 'ALTER TABLE searches ADD COLUMN IF NOT EXISTS shared_at TIMESTAMPTZ;'
        }).execute()
        
        print("✅ Colonne shared_at ajoutée avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("\n⚠️  Veuillez exécuter cette commande SQL manuellement dans Supabase :")
        print("ALTER TABLE searches ADD COLUMN IF NOT EXISTS shared_at TIMESTAMPTZ;")

if __name__ == "__main__":
    main()

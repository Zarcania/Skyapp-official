#!/usr/bin/env python3
"""
Script pour rendre client_id nullable dans la table projects
"""
import os
from supabase import create_client

def apply_migration():
    """Applique la migration pour rendre client_id nullable"""
    
    # Configuration Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Variables d'environnement manquantes")
        print("Assurez-vous que SUPABASE_URL et SUPABASE_KEY sont définies")
        return
    
    print("🔧 Connexion à Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("📝 Application de la migration...")
    
    # Exécuter la migration SQL
    sql = """
    ALTER TABLE projects 
    ALTER COLUMN client_id DROP NOT NULL;
    """
    
    try:
        result = supabase.rpc('exec_sql', {'query': sql}).execute()
        print("✅ Migration appliquée avec succès!")
        
        # Vérifier la modification
        print("\n🔍 Vérification de la modification...")
        verify_sql = """
        SELECT 
            column_name, 
            is_nullable, 
            data_type 
        FROM information_schema.columns 
        WHERE table_name = 'projects' 
        AND column_name = 'client_id';
        """
        
        verify_result = supabase.rpc('exec_sql', {'query': verify_sql}).execute()
        print(f"📊 Résultat: {verify_result.data}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'application de la migration: {e}")
        print("\n💡 Solution alternative:")
        print("Exécutez cette requête manuellement dans le SQL Editor de Supabase:")
        print("\nALTER TABLE projects ALTER COLUMN client_id DROP NOT NULL;")
        print(f"\n🔗 URL: {SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/')}/sql/new")

if __name__ == "__main__":
    apply_migration()

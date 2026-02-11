import os
import sys
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://wursductnatclwrqvgua.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cnNkdWN0bmF0Y2x3cnF2Z3VhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMDg5OTYxMSwiZXhwIjoyMDQ2NDc1NjExfQ.CsXw6AUB_fmLIXWBnKA8lzJ-3MZCl7fNUQNdY3FWZDo')

def apply_migration():
    """Applique la migration team_leader_collaborators"""
    try:
        print("📡 Connexion à Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        migration_file = 'migrations/2025-11-28_team_leader_collaborators.sql'
        
        print(f"📂 Lecture du fichier: {migration_file}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print("🔧 Application de la migration...")
        # Exécuter via RPC ou directement
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        
        print("✅ Migration appliquée avec succès!")
        print(f"✅ Table 'team_leader_collaborators' créée")
        print(f"✅ Vue 'team_leader_stats' créée")
        print(f"✅ Policies RLS activées")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {str(e)}")
        print("\n⚠️  Note: Si la fonction exec_sql n'existe pas, vous devez:")
        print("   1. Ouvrir Supabase SQL Editor")
        print("   2. Copier-coller le contenu de migrations/2025-11-28_team_leader_collaborators.sql")
        print("   3. Exécuter manuellement")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()

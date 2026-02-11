"""
Script pour assigner un user_id aux recherches qui n'en ont pas
"""
import sys
import os
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://izkhlqbhdxyjigdmjqvx.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6a2hscWJoZHh5amlnZG1qcXZ4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMDgwNzQ5OCwiZXhwIjoyMDQ2MzgzNDk4fQ.ixB9gh_cBb-dq5HKpwSAkQfEIbDNNZ6lMmM1PsANS8E")

supabase_service: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def update_searches_with_user():
    try:
        print("🔍 Recherche des searches sans user_id...")
        
        # 1. Trouver toutes les recherches sans user_id
        response = supabase_service.table("searches").select("*").execute()
        all_searches = response.data
        
        searches_without_user = [s for s in all_searches if not s.get("user_id")]
        
        print(f"📊 Total: {len(all_searches)} recherches")
        print(f"🚫 Sans user_id: {len(searches_without_user)}")
        
        if len(searches_without_user) == 0:
            print("✅ Toutes les recherches ont déjà un user_id !")
            return
        
        # 2. Récupérer un utilisateur TECHNICIEN par défaut
        users_response = supabase_service.table("users").select("*").eq("role", "TECHNICIEN").limit(1).execute()
        
        if not users_response.data or len(users_response.data) == 0:
            print("❌ Aucun utilisateur TECHNICIEN trouvé dans la base de données")
            print("💡 Créez d'abord un utilisateur technicien")
            return
        
        default_user = users_response.data[0]
        print(f"\n👤 Utilisateur par défaut trouvé:")
        print(f"   Nom: {default_user.get('first_name')} {default_user.get('last_name')}")
        print(f"   Email: {default_user.get('email')}")
        print(f"   ID: {default_user['id']}")
        
        # 3. Demander confirmation
        print(f"\n⚠️  Cette opération va mettre à jour {len(searches_without_user)} recherche(s)")
        confirm = input("Voulez-vous continuer ? (oui/non): ").strip().lower()
        
        if confirm not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée")
            return
        
        # 4. Mettre à jour les recherches
        print("\n🔄 Mise à jour en cours...")
        updated_count = 0
        
        for search in searches_without_user:
            try:
                supabase_service.table("searches").update({
                    "user_id": default_user["id"]
                }).eq("id", search["id"]).execute()
                
                location = search.get("location", "Sans adresse")[:50]
                print(f"   ✅ {search['id'][:8]}... - {location}")
                updated_count += 1
            except Exception as e:
                print(f"   ❌ Erreur pour {search['id']}: {str(e)}")
        
        print(f"\n✅ Terminé ! {updated_count}/{len(searches_without_user)} recherches mises à jour")
        print(f"👤 Toutes les recherches sont maintenant assignées à: {default_user.get('first_name')} {default_user.get('last_name')}")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_searches_with_user()

import os
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = "https://izkhlqbhdxyjigdmjqvx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6a2hscWJoZHh5amlnZG1qcXZ4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMDgwNzQ5OCwiZXhwIjoyMDQ2MzgzNDk4fQ.ixB9gh_cBb-dq5HKpwSAkQfEIbDNNZ6lMmM1PsANS8E"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Récupérer toutes les recherches sans user_id ou avec user_id null
searches_response = supabase.table("searches").select("*").is_("user_id", "null").execute()
searches_without_user = searches_response.data

print(f"🔍 Trouvé {len(searches_without_user)} recherches sans user_id")

if len(searches_without_user) > 0:
    # 2. Récupérer un utilisateur de type TECHNICIEN pour assigner
    users_response = supabase.table("users").select("*").eq("role", "TECHNICIEN").limit(1).execute()
    
    if users_response.data and len(users_response.data) > 0:
        default_user = users_response.data[0]
        print(f"👤 Utilisateur par défaut: {default_user['first_name']} {default_user['last_name']} (ID: {default_user['id']})")
        
        # 3. Mettre à jour toutes les recherches sans user_id
        for search in searches_without_user:
            supabase.table("searches").update({
                "user_id": default_user["id"]
            }).eq("id", search["id"]).execute()
            print(f"✅ Recherche {search['id']} mise à jour avec user_id {default_user['id']}")
        
        print(f"\n✅ {len(searches_without_user)} recherches mises à jour avec succès!")
    else:
        print("❌ Aucun utilisateur TECHNICIEN trouvé dans la base de données")
else:
    print("✅ Toutes les recherches ont déjà un user_id")

# Vérifier le résultat
all_searches = supabase.table("searches").select("id, user_id, location").execute()
print(f"\n📊 Total de {len(all_searches.data)} recherches dans la base")
without_user = [s for s in all_searches.data if not s.get("user_id")]
print(f"🚫 Recherches sans user_id: {len(without_user)}")

"""
Script pour ajouter les colonnes collaborator_first_name et collaborator_last_name
dans la table schedules, et remplir les noms des schedules existants.
"""
import os, sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

url = os.environ['SUPABASE_URL']
key = os.environ.get('SUPABASE_SERVICE_KEY', os.environ['SUPABASE_ANON_KEY'])
sb = create_client(url, key)

print("=== Migration: Ajout nom/prénom collaborateur dans schedules ===")

# 1. Ajouter les colonnes via RPC SQL (si votre projet a la fonction exec_sql)
#    Sinon, vous devez les créer manuellement dans le SQL Editor de Supabase.
#    Voir: migrations/add_collaborator_name_to_schedules.sql

# 2. Remplir les noms pour les schedules existants
print("\n📋 Récupération des schedules existants...")
schedules = sb.table("schedules").select("id, collaborator_id").execute()

if not schedules.data:
    print("Aucun schedule trouvé.")
    sys.exit(0)

print(f"  {len(schedules.data)} schedules trouvés")

# Récupérer tous les users d'un coup
user_ids = list(set(s["collaborator_id"] for s in schedules.data if s.get("collaborator_id")))
print(f"  {len(user_ids)} collaborateurs uniques")

users_map = {}
for uid in user_ids:
    try:
        res = sb.table("users").select("id, first_name, last_name").eq("id", uid).execute()
        if res.data:
            users_map[uid] = res.data[0]
    except Exception as e:
        print(f"  ⚠️ Erreur pour user {uid}: {e}")

print(f"  {len(users_map)} noms récupérés")

# Mettre à jour chaque schedule
updated = 0
for s in schedules.data:
    cid = s.get("collaborator_id")
    if cid and cid in users_map:
        user = users_map[cid]
        try:
            sb.table("schedules").update({
                "collaborator_first_name": user.get("first_name", ""),
                "collaborator_last_name": user.get("last_name", "")
            }).eq("id", s["id"]).execute()
            updated += 1
        except Exception as e:
            print(f"  ⚠️ Erreur update schedule {s['id']}: {e}")

print(f"\n✅ {updated} schedules mis à jour avec nom/prénom")
print("\nDone!")

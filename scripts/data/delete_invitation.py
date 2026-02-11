"""Script pour supprimer une invitation spécifique"""
from supabase import create_client
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('backend/.env')

# Connexion à Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)

# ID de l'invitation à supprimer
invitation_id = "98e924bd-4472-4747-a291-7b441e58408e"
invitation_email = "squimizgame@gmail.com"

print(f"🔍 Suppression de l'invitation pour {invitation_email}...")
print(f"   ID: {invitation_id}")

try:
    # Vérifier que l'invitation existe
    result = supabase.table('invitations').select('*').eq('id', invitation_id).execute()
    
    if not result.data:
        print("❌ Invitation introuvable")
    else:
        invitation = result.data[0]
        print(f"✅ Invitation trouvée:")
        print(f"   Email: {invitation['email']}")
        print(f"   Statut: {invitation['status']}")
        print(f"   Envoyée le: {invitation['created_at']}")
        
        # Supprimer l'invitation
        supabase.table('invitations').delete().eq('id', invitation_id).execute()
        print(f"\n✅ Invitation supprimée avec succès !")
        
except Exception as e:
    print(f"❌ Erreur: {str(e)}")

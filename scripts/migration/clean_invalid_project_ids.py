"""
Script pour nettoyer les project_id invalides des recherches
Réinitialise à NULL tous les project_id qui pointent vers des projets inexistants
"""
from supabase import create_client, Client
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis backend/.env
backend_dir = Path(__file__).parent / "backend"
env_path = backend_dir / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def get_supabase_client():
    """Créer un client Supabase avec la service key"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise Exception("Variables d'environnement Supabase manquantes dans .env")
    
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def clean_invalid_project_ids():
    """Nettoyer les project_id invalides directement via Supabase"""
    print("\n🔧 Nettoyage des project_id invalides...")
    
    supabase = get_supabase_client()
    
    # 1. Récupérer toutes les recherches avec un project_id
    print("\n📋 Recherche des recherches avec project_id...")
    searches_response = supabase.table("searches")\
        .select("id, location, project_id, company_id")\
        .not_.is_("project_id", "null")\
        .execute()
    
    searches_with_project = searches_response.data
    print(f"✅ {len(searches_with_project)} recherches ont un project_id")
    
    if not searches_with_project:
        print("✅ Aucun nettoyage nécessaire")
        return
    
    # 2. Pour chaque recherche, vérifier si le projet existe et appartient à la même company
    cleaned = 0
    for search in searches_with_project:
        search_id = search["id"]
        project_id = search["project_id"]
        company_id = search["company_id"]
        location = search.get("location", "Sans localisation")[:50]
        
        # Vérifier si le projet existe pour cette company
        project_response = supabase.table("projects")\
            .select("id, name, company_id")\
            .eq("id", project_id)\
            .eq("company_id", company_id)\
            .execute()
        
        if not project_response.data:
            # Le projet n'existe pas ou appartient à une autre company
            print(f"🔧 Nettoyage: {location}")
            print(f"   project_id invalide: {project_id}")
            
            # Réinitialiser le project_id
            supabase.table("searches")\
                .update({"project_id": None})\
                .eq("id", search_id)\
                .execute()
            
            cleaned += 1
    
    print(f"\n✅ Nettoyage terminé: {cleaned} project_id invalides réinitialisés")
    print(f"✅ {len(searches_with_project) - cleaned} project_id valides conservés")
    print("\n💡 Rechargez la page (F5) pour voir les boutons 'Transformer en Projet'")

if __name__ == "__main__":
    try:
        clean_invalid_project_ids()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

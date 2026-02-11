"""
Script pour déboguer pourquoi les projets ne s'affichent pas
"""
from supabase import create_client, Client
import os
from pathlib import Path
from dotenv import load_dotenv
import json

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

def debug_projects():
    """Déboguer l'affichage des projets"""
    print("\n🔍 Débogage des projets...")
    
    supabase = get_supabase_client()
    
    # 1. Récupérer toutes les recherches avec project_id
    print("\n1️⃣ Recherches avec project_id:")
    searches = supabase.table("searches")\
        .select("id, location, project_id, company_id")\
        .not_.is_("project_id", "null")\
        .execute()
    
    for search in searches.data:
        print(f"   📍 {search['location'][:40]}")
        print(f"      project_id: {search['project_id']}")
        print(f"      company_id: {search['company_id']}")
    
    # 2. Récupérer tous les projets
    print("\n2️⃣ Tous les projets en base:")
    all_projects = supabase.table("projects")\
        .select("id, name, company_id, search_id")\
        .execute()
    
    print(f"   Total: {len(all_projects.data)} projets")
    for project in all_projects.data:
        print(f"   📁 {project['name'][:40]}")
        print(f"      id: {project['id']}")
        print(f"      company_id: {project['company_id']}")
        print(f"      search_id: {project.get('search_id', 'None')}")
    
    # 3. Vérifier les company_id
    print("\n3️⃣ Companies en base:")
    companies = supabase.table("companies")\
        .select("id, name")\
        .execute()
    
    for company in companies.data:
        print(f"   🏢 {company['name']}")
        print(f"      id: {company['id']}")
        
        # Compter les recherches et projets
        company_searches = supabase.table("searches")\
            .select("id", count="exact")\
            .eq("company_id", company['id'])\
            .execute()
        
        company_projects = supabase.table("projects")\
            .select("id", count="exact")\
            .eq("company_id", company['id'])\
            .execute()
        
        print(f"      Recherches: {company_searches.count}")
        print(f"      Projets: {company_projects.count}")
    
    # 4. Identifier les incohérences
    print("\n4️⃣ Vérification des incohérences:")
    for search in searches.data:
        project_id = search['project_id']
        search_company = search['company_id']
        
        # Trouver le projet
        project = next((p for p in all_projects.data if p['id'] == project_id), None)
        
        if not project:
            print(f"   ❌ ERREUR: Recherche {search['location'][:30]} pointe vers projet inexistant {project_id}")
        elif project['company_id'] != search_company:
            print(f"   ⚠️  ATTENTION: Recherche et projet ont des company_id différents:")
            print(f"      Recherche: {search['location'][:30]} (company: {search_company})")
            print(f"      Projet: {project['name'][:30]} (company: {project['company_id']})")
        else:
            print(f"   ✅ OK: {search['location'][:30]} → {project['name'][:30]}")

if __name__ == "__main__":
    try:
        debug_projects()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

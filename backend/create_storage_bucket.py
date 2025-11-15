#!/usr/bin/env python3
"""
Script pour créer le bucket Supabase Storage pour les photos
"""

from supabase import create_client
from dotenv import load_dotenv
import os
from pathlib import Path

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

supabase_url = os.environ['SUPABASE_URL']
supabase_service_key = os.environ['SUPABASE_SERVICE_KEY']
bucket_name = os.environ.get('SUPABASE_STORAGE_BUCKET', 'search-photos')

# Client avec service_role pour admin
supabase = create_client(supabase_url, supabase_service_key)

def create_bucket():
    """Créer le bucket Storage pour les photos"""
    try:
        # Vérifier si le bucket existe
        buckets = supabase.storage.list_buckets()
        existing_bucket = next((b for b in buckets if b.name == bucket_name), None)
        
        if existing_bucket:
            print(f"✅ Bucket '{bucket_name}' existe déjà")
        else:
            # Créer le bucket
            supabase.storage.create_bucket(
                bucket_name,
                options={
                    "public": False,  # Privé par défaut
                    "file_size_limit": 5242880,  # 5MB max
                    "allowed_mime_types": ["image/jpeg", "image/png", "image/jpg", "image/webp"]
                }
            )
            print(f"✅ Bucket '{bucket_name}' créé avec succès")
        
        # Configurer les politiques RLS (Row Level Security)
        print(f"\n📋 Configuration du bucket:")
        print(f"   - Nom: {bucket_name}")
        print(f"   - Taille max: 5MB")
        print(f"   - Types: JPEG, PNG, WebP")
        print(f"   - Accès: Privé (authentifié uniquement)")
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de la création du bucket: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configuration du stockage Supabase...\n")
    
    if create_bucket():
        print("\n✅ Configuration terminée avec succès!")
        print(f"\n💡 Pour accéder aux photos:")
        print(f"   URL: {supabase_url}/storage/v1/object/{bucket_name}/{{path}}")
    else:
        print("\n❌ Échec de la configuration")
        exit(1)

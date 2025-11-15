#!/usr/bin/env python3
"""
Script de démarrage du serveur backend SkyApp avec Supabase
"""

import os
import sys
from pathlib import Path

def start_server():
    """Démarre le serveur backend Supabase"""
    
    # Chemin vers le répertoire backend
    backend_dir = Path(__file__).parent / "backend"
    
    # Changer vers le répertoire backend
    os.chdir(backend_dir)
    
    # Ajouter le répertoire backend au path Python
    sys.path.insert(0, str(backend_dir))
    
    try:
        import uvicorn
        print("Démarrage du serveur SkyApp Backend (Supabase)...")
        print(f"Répertoire de travail: {os.getcwd()}")
        print("Serveur disponible sur: http://127.0.0.1:8001")
        print("Documentation API: http://127.0.0.1:8001/docs")
        print("\nAppuyez sur Ctrl+C pour arrêter le serveur")
        
        # Import du server_supabase module (pas server.py qui utilise MongoDB)
        import server_supabase
        
        # Démarrage avec uvicorn
        uvicorn.run(
            server_supabase.app,
            host="127.0.0.1",
            port=8001,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Assurez-vous que toutes les dépendances sont installées avec:")
        print("pip install -r requirements.txt")
        return False
    except KeyboardInterrupt:
        print("\n👋 Serveur arrêté par l'utilisateur")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False

if __name__ == "__main__":
    start_server()
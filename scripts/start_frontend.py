#!/usr/bin/env python3
"""
Script pour démarrer le frontend SkyApp sur un port libre
"""
import subprocess
import sys
import os

def start_frontend():
    """Démarre le serveur frontend React"""
    
    # Aller dans le répertoire frontend
    frontend_dir = r"C:\Users\jorda\Downloads\Skyapp-conflict_141025_2250\Skyapp-conflict_141025_2250\frontend"
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Répertoire frontend non trouvé: {frontend_dir}")
        return False
    
    os.chdir(frontend_dir)
    print(f"📂 Répertoire: {os.getcwd()}")
    
    # Définir le port
    os.environ['PORT'] = '3002'
    
    try:
        print("🚀 Démarrage du frontend React sur http://localhost:3002...")
        print("⚠️  Laissez ce terminal ouvert pour que le serveur fonctionne")
        print("🔄 Pour arrêter: Ctrl+C")
        print("-" * 50)
        
        # Démarrer npm
        process = subprocess.Popen(
            ['npm', 'start'],
            cwd=frontend_dir,
            env=os.environ.copy()
        )
        
        # Attendre que le processus se termine
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur frontend...")
        process.terminate()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎯 SkyApp - Démarrage Frontend")
    print("=" * 40)
    start_frontend()
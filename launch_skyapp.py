#!/usr/bin/env python3
"""
Script de lancement complet SkyApp avec Supabase
Lance le backend et ouvre le frontend
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    print("🚀 LANCEMENT SKYAPP AVEC SUPABASE")
    print("=" * 50)
    
    # Chemins
    base_dir = Path(__file__).parent
    backend_dir = base_dir / "backend"
    frontend_dir = base_dir / "frontend"
    
    print(f"📂 Répertoire base: {base_dir}")
    
    # Vérifier que les dossiers existent
    if not backend_dir.exists():
        print("❌ Répertoire backend non trouvé")
        return False
        
    if not frontend_dir.exists():
        print("❌ Répertoire frontend non trouvé")
        return False
    
    try:
        print("\n🔧 1. Démarrage du backend Supabase...")
        backend_process = subprocess.Popen(
            [sys.executable, "server_supabase.py"],
            cwd=backend_dir
        )
        
        # Attendre un peu que le backend démarre
        print("   Attente du démarrage du backend...")
        time.sleep(3)
        
        print("\n🎨 2. Démarrage du frontend React...")
        frontend_env = os.environ.copy()
        frontend_env['PORT'] = '3001'
        
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            env=frontend_env
        )
        
        print("\n✅ DÉMARRAGE TERMINÉ !")
        print("=" * 50)
        print("🌐 Backend Supabase : http://localhost:8001")
        print("🎯 Frontend React   : http://localhost:3001")
        print("📧 Comptes de test  :")
        print("   - jordancorradi91540@gmail.com / TestAdmin123!")
        print("   - jordancorradi+bureau@gmail.com / TestBureau123!")
        print("   - jordancorradi+tech@gmail.com / TestTech123!")
        print("\n⚠️  Laissez ce terminal ouvert pour que l'application fonctionne")
        print("🛑 Pour arrêter : Ctrl+C")
        
        # Ouvrir le navigateur après quelques secondes
        time.sleep(5)
        print("\n🌐 Ouverture du navigateur...")
        webbrowser.open("http://localhost:3001")
        
        # Attendre que les processus se terminent
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur...")
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait()
            frontend_process.wait()
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("💡 SKYAPP - Lancement automatique avec Supabase")
    main()
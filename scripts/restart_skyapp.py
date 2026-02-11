#!/usr/bin/env python3
"""
Script de redémarrage rapide de Skyapp
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def restart_skyapp():
    """Redémarre Skyapp (stop puis start en arrière-plan)"""
    print("🔄 Redémarrage de Skyapp...")
    
    # Obtenir le répertoire racine
    root_dir = Path(__file__).parent.parent
    
    # 1. Arrêt
    print("\n1️⃣ Arrêt des processus...")
    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], capture_output=True)
    subprocess.run(["taskkill", "/F", "/IM", "node.exe", "/T"], capture_output=True)
    print("✅ Processus arrêtés")
    
    # 2. Attente de 3 secondes pour libérer les ports
    print("\n⏳ Attente de 3 secondes...")
    time.sleep(3)
    
    # 3. Utiliser le script PowerShell pour redémarrer
    print("\n2️⃣ Démarrage de Skyapp...")
    
    if sys.platform == "win32":
        # Utiliser le script PowerShell start_skyapp.ps1
        ps_script = root_dir / "scripts" / "start_skyapp.ps1"
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    
    print("\n✅ Skyapp redémarrée !")
    print("🌐 Backend : http://localhost:8001")
    print("🌐 Frontend : http://localhost:3002")
    print("\n💡 Les serveurs tournent en arrière-plan.")

if __name__ == "__main__":
    restart_skyapp()

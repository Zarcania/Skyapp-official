#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour appliquer la migration SQL des modules réception/e-reporting/archivage
"""

import os
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = "https://wursductnatclwrqvgua.supabase.co"
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

if not SUPABASE_SERVICE_KEY:
    print("❌ SUPABASE_SERVICE_KEY non définie")
    print("Définissez la variable d'environnement ou collez la clé:")
    SUPABASE_SERVICE_KEY = input("Service Key: ").strip()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("📋 Lecture du fichier SQL...")
sql_file = "supabase/migrations/20251119_add_invoicing_reception_reporting_archiving.sql"

with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

print(f"✅ {len(sql_content)} caractères lus")
print("\n🚀 Application de la migration...")

try:
    # Note: Supabase Python client ne supporte pas directement l'exécution SQL brute
    # Il faut utiliser l'API REST ou le CLI
    print("\n⚠️  Ce script nécessite le Supabase CLI")
    print("Exécutez manuellement:")
    print(f"  supabase db execute < {sql_file}")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

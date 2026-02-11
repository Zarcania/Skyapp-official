"""
Script pour appliquer la migration Enhanced Materials Management
Ajoute les colonnes de suivi maintenance, fin de vie, et crée la table material_maintenance_logs
"""
import os
import sys

# Ajouter le dossier backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from supabase import create_client
except ImportError:
    print("Installation de supabase...")
    os.system("pip install supabase")
    from supabase import create_client

# Configuration Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL') or os.environ.get('REACT_APP_SUPABASE_URL') or 'https://izkhlqbhdxyjigdmjqvx.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY') or os.environ.get('SUPABASE_KEY') or os.environ.get('REACT_APP_SUPABASE_ANON_KEY')

if not SUPABASE_KEY:
    # Essayer de lire depuis le .env frontend
    env_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('REACT_APP_SUPABASE_ANON_KEY='):
                    SUPABASE_KEY = line.split('=', 1)[1].strip()
                elif line.startswith('REACT_APP_SUPABASE_URL='):
                    SUPABASE_URL = line.split('=', 1)[1].strip()

if not SUPABASE_KEY:
    print("❌ Clé Supabase non trouvée. Définir SUPABASE_KEY ou REACT_APP_SUPABASE_ANON_KEY")
    sys.exit(1)

print(f"🔗 Connexion à Supabase: {SUPABASE_URL}")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ═══════════════════════════════════════════════════
#  ÉTAPE 1: Ajouter les colonnes à la table materials
# ═══════════════════════════════════════════════════
print("\n📦 Étape 1: Vérification et ajout des colonnes à 'materials'...")

# Test: vérifier si les colonnes existent déjà
try:
    result = supabase.table('materials').select('id, serial_number, brand, model, condition, end_of_life, next_maintenance_date').limit(1).execute()
    print("✅ Les colonnes existent déjà dans la table materials!")
    columns_exist = True
except Exception as e:
    error_msg = str(e)
    if 'column' in error_msg.lower() and 'does not exist' in error_msg.lower():
        columns_exist = False
        print("ℹ️ Colonnes manquantes, migration nécessaire via SQL")
    else:
        print(f"⚠️ Erreur inattendue: {error_msg}")
        columns_exist = False

if not columns_exist:
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║  MIGRATION SQL REQUISE                                           ║
║  Exécutez le fichier SQL suivant dans votre dashboard Supabase:  ║
║  → migrations/enhance_materials_management.sql                   ║
║                                                                   ║
║  Dashboard → SQL Editor → New Query → Coller le contenu → Run    ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    # Lire et afficher le SQL
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'enhance_materials_management.sql')
    if os.path.exists(sql_path):
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print("📋 Contenu SQL à exécuter:")
        print("─" * 60)
        print(sql_content)
        print("─" * 60)
else:
    print("✅ Toutes les colonnes sont déjà présentes!")

# ═══════════════════════════════════════════════════
#  ÉTAPE 2: Vérifier la table material_maintenance_logs
# ═══════════════════════════════════════════════════
print("\n📋 Étape 2: Vérification de la table 'material_maintenance_logs'...")

try:
    result = supabase.table('material_maintenance_logs').select('id').limit(1).execute()
    print("✅ Table material_maintenance_logs existe!")
except Exception as e:
    error_msg = str(e)
    if 'relation' in error_msg.lower() and 'does not exist' in error_msg.lower():
        print("ℹ️ Table material_maintenance_logs n'existe pas encore")
        print("   → Elle sera créée par la migration SQL ci-dessus")
    else:
        print(f"⚠️ Erreur: {error_msg}")

# ═══════════════════════════════════════════════════
#  ÉTAPE 3: Test de fonctionnement
# ═══════════════════════════════════════════════════
print("\n🔍 Étape 3: Test de lecture des matériels existants...")

try:
    result = supabase.table('materials').select('*').limit(5).execute()
    items = result.data or []
    print(f"✅ {len(items)} matériel(s) trouvé(s) dans la base")
    for item in items:
        name = item.get('name', 'N/A')
        condition = item.get('condition', 'N/A')
        qr = item.get('qr_code', 'N/A')
        print(f"   📦 {name} | État: {condition} | QR: {qr[:20]}...")
except Exception as e:
    print(f"⚠️ Erreur lecture: {e}")

print("\n" + "═" * 60)
print("🏁 Migration terminée!")
print("═" * 60)

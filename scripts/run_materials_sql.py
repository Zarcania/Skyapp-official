"""Applique la migration materials via l'API REST Supabase (rpc/sql ou ALTER via postgrest)"""
import os, sys, requests

SUPABASE_URL = "https://wursductnatclwrqvgua.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1cnNkdWN0bmF0Y2x3cnF2Z3VhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDQ3MzQ5OSwiZXhwIjoyMDc2MDQ5NDk5fQ.hWoI3fS9JR11y9tSQrC68QgI7k-jTfOXOoCZ6N4lJy0"

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Lire le fichier SQL
sql_path = os.path.join(os.path.dirname(__file__), '..', 'migrations', 'enhance_materials_management.sql')
with open(sql_path, 'r', encoding='utf-8') as f:
    full_sql = f.read()

# Diviser en statements individuels
statements = []
current = []
for line in full_sql.split('\n'):
    stripped = line.strip()
    if stripped.startswith('--') or not stripped:
        continue
    current.append(line)
    if stripped.endswith(';'):
        stmt = '\n'.join(current).strip()
        if stmt and stmt != ';':
            statements.append(stmt)
        current = []

# Pour les blocks $$ (fonctions), on doit les regrouper
merged = []
i = 0
while i < len(statements):
    s = statements[i]
    if '$$' in s and s.count('$$') % 2 != 0:
        # Besoin de merger avec le suivant
        combined = s
        i += 1
        while i < len(statements):
            combined += '\n' + statements[i]
            if '$$' in statements[i]:
                i += 1
                break
            i += 1
        merged.append(combined)
    else:
        merged.append(s)
        i += 1

print(f"📋 {len(merged)} statements SQL à exécuter\n")

# Essayer via l'endpoint SQL RPC
# Supabase a un endpoint /rest/v1/rpc qui peut exécuter du SQL
# Sinon on utilise /pg pour les migrations

success = 0
errors = 0

for idx, stmt in enumerate(merged, 1):
    short = stmt[:80].replace('\n', ' ')
    print(f"[{idx}/{len(merged)}] {short}...")
    
    # Utiliser l'API Supabase Management (via SQL endpoint)
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"query": stmt}
        )
        if resp.status_code < 300:
            print(f"  ✅ OK")
            success += 1
        else:
            # L'endpoint exec_sql n'existe probablement pas, essayons une autre approche
            print(f"  ⚠️ Status {resp.status_code}: {resp.text[:100]}")
            errors += 1
    except Exception as e:
        print(f"  ❌ {e}")
        errors += 1

print(f"\n{'='*60}")
if errors > 0:
    print(f"⚠️ {success} succès, {errors} erreurs")
    print("""
╔══════════════════════════════════════════════════════════════╗
║  La migration doit être exécutée manuellement:               ║
║                                                              ║
║  1. Allez sur https://supabase.com/dashboard                ║
║  2. Ouvrez votre projet                                      ║
║  3. SQL Editor → New Query                                   ║
║  4. Copiez-collez le contenu du fichier:                     ║
║     migrations/enhance_materials_management.sql              ║
║  5. Cliquez "Run"                                            ║
╚══════════════════════════════════════════════════════════════╝
""")
else:
    print(f"✅ Tous les {success} statements exécutés avec succès!")

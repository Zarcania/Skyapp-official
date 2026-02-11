import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(os.environ['SUPABASE_DB_URL'])
cur = conn.cursor()

# Structure de schedules
print("=" * 80)
print("STRUCTURE DE LA TABLE schedules")
print("=" * 80)
cur.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'schedules'
    ORDER BY ordinal_position
""")
print(f"{'Colonne':<30} {'Type':<25} {'Nullable':<10} {'Défaut'}")
print("-" * 80)
for row in cur.fetchall():
    print(f"{row[0]:<30} {row[1]:<25} {row[2]:<10} {row[3] or ''}")

# Structure de worksites (vérifier colonnes planning)
print("\n" + "=" * 80)
print("COLONNES PERTINENTES DE worksites")
print("=" * 80)
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'worksites'
    AND column_name IN ('id', 'title', 'status', 'client_id', 'start_date', 'end_date', 'progress', 'budget', 'team_size', 'notes')
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"  {row[0]:<20} {row[1]}")

# Structure de planning_team_leaders
print("\n" + "=" * 80)
print("STRUCTURE DE planning_team_leaders")
print("=" * 80)
cur.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'planning_team_leaders'
    ORDER BY ordinal_position
""")
for row in cur.fetchall():
    print(f"  {row[0]:<20} {row[1]}")

cur.close()
conn.close()

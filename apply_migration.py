import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

import psycopg2


def main():
    # Charger les variables d'environnement depuis .env
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Appliquer un fichier SQL sur la base Supabase distante")
    parser.add_argument(
        "--file",
        required=True,
        help="Chemin du fichier SQL à exécuter (relatif au dépôt ou absolu)",
    )
    args = parser.parse_args()

    sql_path = Path(args.file).expanduser().resolve()
    if not sql_path.is_file():
        raise SystemExit(f"Fichier SQL introuvable: {sql_path}")

    with sql_path.open("r", encoding="utf-8") as f:
        sql = f.read()

    database_url = os.environ.get("SUPABASE_DB_URL")
    if not database_url:
        raise SystemExit("❌ SUPABASE_DB_URL non défini dans .env")

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    try:
        cur.execute(sql)
        conn.commit()
        print(f"Migration '{sql_path.name}' appliquée avec succès sur la base distante")
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()

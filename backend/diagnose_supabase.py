#!/usr/bin/env python3
"""Quick diagnostics for Supabase backend startup issues."""
import os, sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

def check_env(keys):
    print("[env] Required variables:")
    ok = True
    for k in keys:
        v = os.environ.get(k)
        print(f"  - {k}: {'OK' if v else 'MISSING'}")
        ok = ok and bool(v)
    return ok

def check_imports(mods):
    print("[imports] Checking Python modules:")
    ok = True
    for m in mods:
        try:
            __import__(m)
            print(f"  - {m}: OK")
        except Exception as e:
            print(f"  - {m}: FAIL -> {e}")
            ok = False
    return ok

if __name__ == "__main__":
    # Load backend/.env if available
    env_path = Path(__file__).parent / ".env"
    if env_path.exists() and load_dotenv is not None:
        load_dotenv(env_path)
        print(f"[env] Loaded .env from {env_path}")
    elif not env_path.exists():
        print(f"[env] WARNING: .env not found at {env_path}")
    else:
        print("[env] WARNING: python-dotenv not installed; skipping .env load")

    env_ok = check_env(["SUPABASE_URL","SUPABASE_ANON_KEY"])  # service key optional
    mods_ok = check_imports(["fastapi","uvicorn","supabase","dotenv"]) 

    # Try creating a Supabase client (optional quick check)
    supa_ok = True
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"):
        try:
            from supabase import create_client
            _client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
            print("[supabase] Client creation: OK")
        except Exception as e:
            print(f"[supabase] Client creation: FAIL -> {e}")
            supa_ok = False

    sys.exit(0 if (env_ok and mods_ok and supa_ok) else 1)

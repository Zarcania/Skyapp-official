-- Migration: add DRAFT status to search_status enum (idempotent)
-- Compatible Postgres (Supabase). Safe to re-run.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    WHERE t.typname = 'search_status' AND e.enumlabel = 'DRAFT'
  ) THEN
    ALTER TYPE search_status ADD VALUE 'DRAFT';
  END IF;
END$$;

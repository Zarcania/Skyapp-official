-- Migration: ajout du statut DRAFT pour les recherches
-- À exécuter dans Supabase (SQL Editor)
-- Vérifie d'abord si la valeur n'existe pas déjà
DO $$
BEGIN
    -- Ajouter la valeur DRAFT à l'ENUM search_status si absente
    IF NOT EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE t.typname = 'search_status' AND e.enumlabel = 'DRAFT'
    ) THEN
        ALTER TYPE search_status ADD VALUE 'DRAFT';
    END IF;
END$$;

-- Mettre à jour éventuellement les recherches existantes sans statut (rare)
UPDATE searches SET status = 'DRAFT' WHERE status IS NULL;

-- Index déjà présent sur status, pas besoin d'ajouter.

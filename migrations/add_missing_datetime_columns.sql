-- Migration: Ajouter les colonnes datetime manquantes
-- Date: 2025-12-21

DO $$
BEGIN
    -- Ajouter start_datetime si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='start_datetime') THEN
        ALTER TABLE schedules ADD COLUMN start_datetime TIMESTAMPTZ;
        COMMENT ON COLUMN schedules.start_datetime IS 'Date et heure de début (legacy)';
    END IF;

    -- Ajouter end_datetime si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='end_datetime') THEN
        ALTER TABLE schedules ADD COLUMN end_datetime TIMESTAMPTZ;
        COMMENT ON COLUMN schedules.end_datetime IS 'Date et heure de fin (legacy)';
    END IF;

    -- Ajouter title si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='title') THEN
        ALTER TABLE schedules ADD COLUMN title TEXT;
        COMMENT ON COLUMN schedules.title IS 'Titre du planning (généré automatiquement)';
    END IF;

END $$;

-- Créer un index sur start_datetime pour les recherches
CREATE INDEX IF NOT EXISTS idx_schedules_start_datetime ON schedules(start_datetime);

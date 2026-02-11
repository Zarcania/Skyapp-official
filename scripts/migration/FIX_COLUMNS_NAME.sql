-- ============================================================================
-- CORRECTION URGENTE - Colonnes name manquantes
-- ============================================================================

-- Ajouter colonne name dans clients
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='clients' AND column_name='name') THEN
        ALTER TABLE clients ADD COLUMN name TEXT;
        -- Remplir avec client_name si elle existe
        UPDATE clients SET name = client_name WHERE name IS NULL AND client_name IS NOT NULL;
    END IF;
END $$;

-- Ajouter colonne name dans worksites  
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='worksites' AND column_name='name') THEN
        ALTER TABLE worksites ADD COLUMN name TEXT;
        -- Remplir avec title si elle existe
        UPDATE worksites SET name = title WHERE name IS NULL AND title IS NOT NULL;
    END IF;
END $$;

SELECT 'Colonnes name ajoutées avec succès!' AS status;

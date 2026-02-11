-- Migration: Lier planning_team_leaders avec users
-- Date: 2025-12-22
-- Description: Ajouter user_id pour synchroniser les noms avec la table users

-- Vérifier si la colonne user_id existe déjà
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'planning_team_leaders' AND column_name = 'user_id'
    ) THEN
        -- Ajouter la colonne user_id
        ALTER TABLE planning_team_leaders 
        ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
        
        -- Index pour performance
        CREATE INDEX idx_planning_team_leaders_user_id ON planning_team_leaders(user_id);
        
        RAISE NOTICE 'Colonne user_id ajoutée à planning_team_leaders';
    ELSE
        RAISE NOTICE 'Colonne user_id existe déjà';
    END IF;
END $$;

-- Si tu veux migrer les données existantes (à adapter selon tes besoins)
-- UPDATE planning_team_leaders SET user_id = id WHERE user_id IS NULL;

COMMENT ON COLUMN planning_team_leaders.user_id IS 'Référence vers users.id pour synchroniser first_name, last_name, email';

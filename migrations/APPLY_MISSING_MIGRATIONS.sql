-- ================================================================================
-- SCRIPT CONSOLIDÉ DES MIGRATIONS MANQUANTES
-- À exécuter dans Supabase SQL Editor
-- Date: 11 février 2026
-- ================================================================================
-- Ce script regroupe toutes les migrations qui n'ont pas encore été appliquées
-- Exécutez-le intégralement dans le SQL Editor de Supabase
-- ================================================================================

-- ============================================================================
-- 1. MIGRATION: 2025-11-28_planning_mvp.sql (Partiel)
--    Ajouter schedules.technicien_id (manquant)
-- ============================================================================
DO $$ 
BEGIN
    -- Ajout colonne technicien_id dans schedules
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='technicien_id') THEN
        ALTER TABLE schedules ADD COLUMN technicien_id UUID REFERENCES users(id) ON DELETE SET NULL;
        COMMENT ON COLUMN schedules.technicien_id IS 'Technicien assigné à cette tâche';
        
        -- Index pour améliorer les performances
        CREATE INDEX IF NOT EXISTS idx_schedules_technicien ON schedules(technicien_id);
    END IF;
END $$;

-- ============================================================================
-- 2. MIGRATION: 2025-12-25_add_converted_to_worksite_status.sql
--    Ajouter le statut CONVERTED_TO_WORKSITE aux devis
-- ============================================================================
-- Ajouter la nouvelle valeur à l'enum quote_status (si elle n'existe pas déjà)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        WHERE t.typname = 'quote_status' AND e.enumlabel = 'CONVERTED_TO_WORKSITE'
    ) THEN
        ALTER TYPE public.quote_status ADD VALUE 'CONVERTED_TO_WORKSITE';
    END IF;
END $$;

-- ============================================================================
-- 3. MIGRATION: add_created_by_to_quotes.sql
--    Ajouter created_by aux devis
-- ============================================================================
DO $$ 
BEGIN
    -- Ajouter la colonne created_by_user_id à la table quotes
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='quotes' AND column_name='created_by_user_id') THEN
        ALTER TABLE quotes ADD COLUMN created_by_user_id UUID REFERENCES users(id);
        
        -- Créer un index pour améliorer les performances
        CREATE INDEX IF NOT EXISTS idx_quotes_created_by_user_id ON quotes(created_by_user_id);
        
        -- Ajouter un commentaire pour documenter la colonne
        COMMENT ON COLUMN quotes.created_by_user_id IS 'ID de l''utilisateur qui a créé le devis';
    END IF;
END $$;

-- ============================================================================
-- 4. MIGRATION: add_planning_fields.sql (Partiel)
--    Ajouter schedules.worksite_title (manquant)
-- ============================================================================
DO $$ 
BEGIN
    -- Ajouter worksite_title si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='worksite_title') THEN
        ALTER TABLE schedules ADD COLUMN worksite_title TEXT;
        COMMENT ON COLUMN schedules.worksite_title IS 'Titre/description du chantier (pour affichage planning)';
    END IF;
END $$;

-- ============================================================================
-- 5. MIGRATION: add_schedules_period_columns.sql
--    Ajouter colonnes period_start et period_end
-- ============================================================================
DO $$ 
BEGIN
    -- Ajouter period_start
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='period_start') THEN
        ALTER TABLE schedules ADD COLUMN period_start DATE;
        COMMENT ON COLUMN schedules.period_start IS 'Date de début de la période (nouveau système)';
    END IF;
    
    -- Ajouter period_end
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='period_end') THEN
        ALTER TABLE schedules ADD COLUMN period_end DATE;
        COMMENT ON COLUMN schedules.period_end IS 'Date de fin de la période (nouveau système)';
    END IF;
    
    -- Index pour les recherches par période
    CREATE INDEX IF NOT EXISTS idx_schedules_period ON schedules(period_start, period_end);
END $$;

-- ============================================================================
-- 6. MIGRATION: add_skills_column.sql
--    Ajouter colonne skills aux users
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='skills') THEN
        ALTER TABLE users ADD COLUMN skills TEXT;
        COMMENT ON COLUMN users.skills IS 'Compétences et spécialités du collaborateur (ex: électricien, plombier, etc.)';
    END IF;
END $$;

-- ============================================================================
-- 7. MIGRATION: enhance_materials_management.sql (Partiel)
--    Ajouter materials.maintenance_date (manquant)
-- ============================================================================
DO $$ 
BEGIN
    -- Ajouter next_maintenance_date
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='materials' AND column_name='next_maintenance_date') THEN
        ALTER TABLE materials ADD COLUMN next_maintenance_date DATE;
        COMMENT ON COLUMN materials.next_maintenance_date IS 'Date de la prochaine maintenance prévue';
        
        -- Index pour faciliter la recherche des maintenances à venir
        CREATE INDEX IF NOT EXISTS idx_materials_next_maintenance ON materials(next_maintenance_date);
    END IF;
    
    -- Ajouter last_maintenance_date si manquant aussi
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='materials' AND column_name='last_maintenance_date') THEN
        ALTER TABLE materials ADD COLUMN last_maintenance_date DATE;
        COMMENT ON COLUMN materials.last_maintenance_date IS 'Date de la dernière maintenance effectuée';
    END IF;
    
    -- Ajouter maintenance_interval_days si manquant
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='materials' AND column_name='maintenance_interval_days') THEN
        ALTER TABLE materials ADD COLUMN maintenance_interval_days INTEGER;
        COMMENT ON COLUMN materials.maintenance_interval_days IS 'Intervalle de maintenance en jours';
    END IF;
END $$;

-- ============================================================================
-- VÉRIFICATION FINALE
-- ============================================================================
-- Afficher un résumé des colonnes ajoutées
SELECT 
    'schedules' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'schedules'
AND column_name IN ('technicien_id', 'worksite_title', 'period_start', 'period_end')
UNION ALL
SELECT 
    'quotes' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'quotes'
AND column_name = 'created_by_user_id'
UNION ALL
SELECT 
    'users' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'skills'
UNION ALL
SELECT 
    'materials' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'materials'
AND column_name IN ('next_maintenance_date', 'last_maintenance_date', 'maintenance_interval_days')
ORDER BY table_name, column_name;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
-- ✅ Si tout s'est bien passé, vous devriez voir une liste de colonnes
-- ✅ Relancez check_migrations_status.py pour vérifier
-- ============================================================================

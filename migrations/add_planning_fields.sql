-- Migration: Ajouter les champs pour le nouveau système de planning
-- Date: 2025-12-21

-- Ajouter les nouvelles colonnes pour le planning flexible (RDV, Chantier, Urgence)
DO $$ 
BEGIN
    -- Ajouter intervention_category si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='intervention_category') THEN
        ALTER TABLE schedules ADD COLUMN intervention_category TEXT DEFAULT 'rdv' CHECK (intervention_category IN ('rdv', 'worksite', 'urgence'));
        COMMENT ON COLUMN schedules.intervention_category IS 'Type d''intervention: rdv, worksite (chantier existant), ou urgence';
    END IF;

    -- Ajouter client_name si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='client_name') THEN
        ALTER TABLE schedules ADD COLUMN client_name TEXT;
        COMMENT ON COLUMN schedules.client_name IS 'Nom du client (pour RDV et urgences)';
    END IF;

    -- Ajouter client_address si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='client_address') THEN
        ALTER TABLE schedules ADD COLUMN client_address TEXT;
        COMMENT ON COLUMN schedules.client_address IS 'Adresse d''intervention (pour RDV et urgences)';
    END IF;

    -- Ajouter client_contact si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='client_contact') THEN
        ALTER TABLE schedules ADD COLUMN client_contact TEXT;
        COMMENT ON COLUMN schedules.client_contact IS 'Coordonnées du client (pour RDV et urgences)';
    END IF;

    -- Ajouter worksite_id si n'existe pas (pour chantiers existants)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='worksite_id') THEN
        ALTER TABLE schedules ADD COLUMN worksite_id UUID REFERENCES worksites(id) ON DELETE SET NULL;
        COMMENT ON COLUMN schedules.worksite_id IS 'ID du chantier (optionnel, pour intervention_category=worksite)';
    END IF;

    -- Ajouter team_leader_id si n'existe pas (optionnel pour RDV)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='team_leader_id') THEN
        ALTER TABLE schedules ADD COLUMN team_leader_id UUID REFERENCES planning_team_leaders(id) ON DELETE SET NULL;
        COMMENT ON COLUMN schedules.team_leader_id IS 'Chef d''équipe assigné (optionnel pour RDV)';
    END IF;

    -- Ajouter date si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='date') THEN
        ALTER TABLE schedules ADD COLUMN date DATE;
        COMMENT ON COLUMN schedules.date IS 'Date de l''intervention';
    END IF;

    -- Ajouter time si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='time') THEN
        ALTER TABLE schedules ADD COLUMN time TIME DEFAULT '08:00:00';
        COMMENT ON COLUMN schedules.time IS 'Heure de début';
    END IF;

    -- Ajouter shift si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='shift') THEN
        ALTER TABLE schedules ADD COLUMN shift TEXT DEFAULT 'day' CHECK (shift IN ('day', 'morning', 'afternoon', 'night'));
        COMMENT ON COLUMN schedules.shift IS 'Type de période: day, morning, afternoon, night';
    END IF;

    -- Ajouter hours si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='hours') THEN
        ALTER TABLE schedules ADD COLUMN hours INTEGER DEFAULT 8;
        COMMENT ON COLUMN schedules.hours IS 'Nombre d''heures de l''intervention';
    END IF;

    -- Ajouter created_by si n'existe pas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='created_by') THEN
        ALTER TABLE schedules ADD COLUMN created_by UUID REFERENCES users(id) ON DELETE SET NULL;
        COMMENT ON COLUMN schedules.created_by IS 'Utilisateur qui a créé le planning';
    END IF;

    -- Modifier collaborator_id pour être optionnel (pour RDV sans équipe) - seulement si la colonne existe
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='schedules' AND column_name='collaborator_id') THEN
        ALTER TABLE schedules ALTER COLUMN collaborator_id DROP NOT NULL;
        COMMENT ON COLUMN schedules.collaborator_id IS 'Collaborateur assigné (optionnel pour RDV)';
    END IF;

    -- Modifier title pour être optionnel (généré automatiquement) - seulement si la colonne existe
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='schedules' AND column_name='title') THEN
        ALTER TABLE schedules ALTER COLUMN title DROP NOT NULL;
    END IF;

    -- Modifier start_datetime et end_datetime pour être optionnels - seulement si les colonnes existent
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='schedules' AND column_name='start_datetime') THEN
        ALTER TABLE schedules ALTER COLUMN start_datetime DROP NOT NULL;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='schedules' AND column_name='end_datetime') THEN
        ALTER TABLE schedules ALTER COLUMN end_datetime DROP NOT NULL;
    END IF;

END $$;

-- Créer un index sur intervention_category pour les recherches
CREATE INDEX IF NOT EXISTS idx_schedules_intervention_category ON schedules(intervention_category);

-- Créer un index sur date pour les recherches
CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(date);

-- Créer un index sur team_leader_id
CREATE INDEX IF NOT EXISTS idx_schedules_team_leader ON schedules(team_leader_id);

-- Créer un index sur worksite_id
CREATE INDEX IF NOT EXISTS idx_schedules_worksite ON schedules(worksite_id);

COMMENT ON TABLE schedules IS 'Plannings et interventions (RDV, Chantiers, Urgences)';

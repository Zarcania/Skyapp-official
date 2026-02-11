-- Migration: Retirer toutes les contraintes NOT NULL pour flexibilité planning
-- Date: 2025-12-22

-- Retirer NOT NULL sur toutes les colonnes qui doivent être optionnelles
ALTER TABLE schedules ALTER COLUMN worksite_id DROP NOT NULL;
ALTER TABLE schedules ALTER COLUMN team_leader_id DROP NOT NULL;
ALTER TABLE schedules ALTER COLUMN collaborator_id DROP NOT NULL;
ALTER TABLE schedules ALTER COLUMN title DROP NOT NULL;
ALTER TABLE schedules ALTER COLUMN start_datetime DROP NOT NULL;
ALTER TABLE schedules ALTER COLUMN end_datetime DROP NOT NULL;
ALTER TABLE schedules ALTER COLUMN description DROP NOT NULL;
ALTER TABLE schedules ALTER COLUMN status DROP NOT NULL;

-- Vérification : afficher les colonnes avec leurs contraintes
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'schedules'
ORDER BY ordinal_position;

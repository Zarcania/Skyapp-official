-- ============================================================
-- SCRIPT DE NETTOYAGE COMPLET - Table schedules
-- À exécuter dans le SQL Editor de Supabase
-- Date: 2026-02-13
-- ============================================================

-- ============================================================
-- 1. AJOUTER LES COLONNES MANQUANTES
-- ============================================================

-- Colonne intervention_category (pour distinguer chantier/rdv/urgence)
ALTER TABLE schedules ADD COLUMN IF NOT EXISTS intervention_category VARCHAR DEFAULT 'worksite';

-- Colonnes nom/prénom du collaborateur (évite de n'avoir que l'UUID)
ALTER TABLE schedules ADD COLUMN IF NOT EXISTS collaborator_first_name VARCHAR DEFAULT NULL;
ALTER TABLE schedules ADD COLUMN IF NOT EXISTS collaborator_last_name VARCHAR DEFAULT NULL;

-- ============================================================
-- 2. CORRIGER LES DONNÉES EXISTANTES
-- ============================================================

-- Les schedules avec un worksite_id doivent être "worksite", pas "rdv"
UPDATE schedules 
SET intervention_category = 'worksite' 
WHERE worksite_id IS NOT NULL 
  AND (intervention_category IS NULL OR intervention_category = 'rdv');

-- Remplir les noms/prénoms pour les schedules existants
UPDATE schedules s
SET 
    collaborator_first_name = u.first_name,
    collaborator_last_name = u.last_name
FROM users u
WHERE s.collaborator_id = u.id
  AND (s.collaborator_first_name IS NULL OR s.collaborator_last_name IS NULL);

-- ============================================================
-- 3. SUPPRIMER LES COLONNES INUTILISÉES (toujours NULL)
-- ============================================================

-- start_datetime / end_datetime → doublons de start_date + time
ALTER TABLE schedules DROP COLUMN IF EXISTS start_datetime;
ALTER TABLE schedules DROP COLUMN IF EXISTS end_datetime;

-- title → redondant avec intervention_category + worksite.title
ALTER TABLE schedules DROP COLUMN IF EXISTS title;

-- technicien_id → doublon de collaborator_id
ALTER TABLE schedules DROP COLUMN IF EXISTS technicien_id;

-- location → pas utilisé dans les schedules (existe dans worksites)
ALTER TABLE schedules DROP COLUMN IF EXISTS location;

-- client_contact → pas utilisé dans le code actif
ALTER TABLE schedules DROP COLUMN IF EXISTS client_contact;

-- ============================================================
-- VÉRIFICATION
-- ============================================================
SELECT 
    id,
    intervention_category,
    collaborator_first_name,
    collaborator_last_name,
    collaborator_id,
    worksite_id,
    start_date,
    end_date,
    time,
    shift,
    hours
FROM schedules
ORDER BY created_at DESC;

-- Migration de la table schedules vers le format période
-- Au lieu d'avoir une ligne par jour, on a une ligne par période avec start_date et end_date

-- Étape 1: Ajouter les colonnes start_date et end_date
ALTER TABLE schedules 
ADD COLUMN IF NOT EXISTS start_date DATE,
ADD COLUMN IF NOT EXISTS end_date DATE;

-- Étape 2: Rendre la colonne 'date' nullable (elle sera supprimée après la migration)
ALTER TABLE schedules 
ALTER COLUMN date DROP NOT NULL;

-- Étape 3: Après migration Python, vous pouvez optionnellement supprimer l'ancienne colonne
-- ALTER TABLE schedules DROP COLUMN date;

-- Étape 4: Rendre les nouvelles colonnes obligatoires (après migration)
-- ALTER TABLE schedules 
-- ALTER COLUMN start_date SET NOT NULL,
-- ALTER COLUMN end_date SET NOT NULL;

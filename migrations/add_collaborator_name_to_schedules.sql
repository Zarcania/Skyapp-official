-- Ajouter les colonnes nom/prénom du collaborateur dans la table schedules
ALTER TABLE schedules ADD COLUMN IF NOT EXISTS collaborator_first_name VARCHAR DEFAULT NULL;
ALTER TABLE schedules ADD COLUMN IF NOT EXISTS collaborator_last_name VARCHAR DEFAULT NULL;

-- Remplir les noms pour les schedules existants à partir de la table users
UPDATE schedules s
SET 
    collaborator_first_name = u.first_name,
    collaborator_last_name = u.last_name
FROM users u
WHERE s.collaborator_id = u.id
AND (s.collaborator_first_name IS NULL OR s.collaborator_last_name IS NULL);

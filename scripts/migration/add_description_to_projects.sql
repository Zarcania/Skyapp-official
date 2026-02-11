-- Ajouter la colonne description à la table projects si elle n'existe pas
ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT;

-- Ajouter un commentaire pour documenter la colonne
COMMENT ON COLUMN projects.description IS 'Description détaillée du projet';

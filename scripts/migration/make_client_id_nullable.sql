-- Rendre la colonne client_id nullable dans la table projects
ALTER TABLE projects ALTER COLUMN client_id DROP NOT NULL;

-- Ajouter un commentaire
COMMENT ON COLUMN projects.client_id IS 'ID du client (optionnel, peut être NULL si pas encore assigné)';

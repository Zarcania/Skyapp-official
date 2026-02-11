-- Ajouter la colonne shared_at à la table searches
ALTER TABLE searches ADD COLUMN IF NOT EXISTS shared_at TIMESTAMPTZ;

-- Ajouter un commentaire pour documenter la colonne
COMMENT ON COLUMN searches.shared_at IS 'Date et heure de partage de la recherche avec le bureau';

-- Ajouter la colonne created_by_user_id à la table quotes
ALTER TABLE quotes ADD COLUMN IF NOT EXISTS created_by_user_id uuid REFERENCES users(id);

-- Créer un index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_quotes_created_by_user_id ON quotes(created_by_user_id);

-- Ajouter un commentaire pour documenter la colonne
COMMENT ON COLUMN quotes.created_by_user_id IS 'ID de l''utilisateur qui a créé le devis';

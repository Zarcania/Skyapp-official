-- Ajouter la colonne is_fondateur à la table users
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_fondateur boolean DEFAULT false;

-- Créer un index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_users_is_fondateur ON users(is_fondateur) WHERE is_fondateur = true;

-- Ajouter un commentaire pour documenter la colonne
COMMENT ON COLUMN users.is_fondateur IS 'Indique si l''utilisateur est un fondateur avec privilèges maximum';

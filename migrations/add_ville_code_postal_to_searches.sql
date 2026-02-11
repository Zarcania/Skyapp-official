-- Ajout des colonnes ville et code_postal à la table searches
ALTER TABLE searches 
ADD COLUMN IF NOT EXISTS ville TEXT,
ADD COLUMN IF NOT EXISTS code_postal TEXT;

-- Index pour améliorer les recherches par ville
CREATE INDEX IF NOT EXISTS idx_searches_ville ON searches(ville);
CREATE INDEX IF NOT EXISTS idx_searches_code_postal ON searches(code_postal);

-- Commentaires
COMMENT ON COLUMN searches.ville IS 'Ville du lieu de recherche';
COMMENT ON COLUMN searches.code_postal IS 'Code postal du lieu de recherche';

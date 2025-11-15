-- Migration: Ajouter nom et prenom à la table searches
-- Date: 2025-11-12
-- Description: Permet de stocker le nom et prénom de la personne recherchée

-- Ajouter les colonnes nom et prenom
ALTER TABLE searches 
ADD COLUMN IF NOT EXISTS nom TEXT,
ADD COLUMN IF NOT EXISTS prenom TEXT;

-- Créer un index pour faciliter les recherches par nom/prenom
CREATE INDEX IF NOT EXISTS idx_searches_nom ON searches(nom);
CREATE INDEX IF NOT EXISTS idx_searches_prenom ON searches(prenom);

-- Commentaires pour documentation
COMMENT ON COLUMN searches.nom IS 'Nom de la personne recherchée';
COMMENT ON COLUMN searches.prenom IS 'Prénom de la personne recherchée';

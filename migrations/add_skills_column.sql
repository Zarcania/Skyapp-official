-- Migration: Ajout de la colonne skills (compétences) à la table users
-- Date: 2025-11-28
-- Description: Permet de stocker les compétences/spécialités de chaque collaborateur

-- Ajouter la colonne skills
ALTER TABLE users ADD COLUMN IF NOT EXISTS skills TEXT;

-- Commentaire pour documentation
COMMENT ON COLUMN users.skills IS 'Compétences et spécialités du collaborateur (ex: électricien, plombier, etc.)';

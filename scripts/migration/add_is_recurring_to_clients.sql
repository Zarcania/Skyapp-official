-- =====================================================
-- MIGRATION: Ajouter colonne is_recurring à clients
-- Date: 2025-11-25
-- Description: Permet de distinguer clients récurrents vs non-récurrents
-- =====================================================

-- Ajouter la colonne is_recurring (par défaut true pour les clients existants)
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT true NOT NULL;

-- Ajouter un index pour optimiser les recherches
CREATE INDEX IF NOT EXISTS idx_clients_is_recurring ON clients(is_recurring);

-- Ajouter prenom si manquant (pour cohérence avec les recherches)
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS prenom TEXT;

-- Vérifier les modifications
SELECT 
    column_name, 
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'clients' 
AND column_name IN ('is_recurring', 'prenom')
ORDER BY column_name;

-- =====================================================
-- MIGRATION: Système de clients non-récurrents
-- Date: 2025-11-25
-- Description: 
-- 1. Ajoute is_recurring aux clients
-- 2. Ajoute prenom aux clients
-- 3. Rend client_id nullable dans projects (pour cas extrêmes)
-- =====================================================

-- 1. Ajouter colonne is_recurring aux clients
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT true NOT NULL;

-- 2. Ajouter colonne prenom aux clients si manquante
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS prenom TEXT;

-- 3. Créer index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_clients_is_recurring ON clients(is_recurring);

-- 4. Rendre client_id nullable dans projects (cas extrêmes sans aucune info)
ALTER TABLE projects 
ALTER COLUMN client_id DROP NOT NULL;

-- Vérification
SELECT 
    table_name,
    column_name, 
    is_nullable, 
    data_type,
    column_default
FROM information_schema.columns 
WHERE (table_name = 'projects' AND column_name = 'client_id')
   OR (table_name = 'clients' AND column_name IN ('is_recurring', 'prenom'))
ORDER BY table_name, column_name;

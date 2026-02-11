-- ============================================================================
-- CORRECTIONS URGENTES SUPABASE - SkyApp
-- Ajouter seulement les colonnes manquantes critiques
-- ============================================================================

-- 1. CLIENTS - Ajouter colonne 'name' manquante
ALTER TABLE clients ADD COLUMN IF NOT EXISTS name TEXT NOT NULL DEFAULT '';

-- 2. WORKSITES - Ajouter colonne 'name' manquante  
ALTER TABLE worksites ADD COLUMN IF NOT EXISTS name TEXT NOT NULL DEFAULT '';

-- 3. Vérification finale
SELECT 'Corrections appliquées avec succès!' AS status;

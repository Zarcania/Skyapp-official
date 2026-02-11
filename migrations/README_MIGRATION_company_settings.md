-- ============================================================================
-- GUIDE D'APPLICATION DE LA MIGRATION company_settings
-- ============================================================================
--
-- Cette migration crée la table company_settings pour stocker les paramètres
-- des sociétés (logo, informations légales, couleurs pour les PDF, etc.)
--
-- ÉTAPES D'APPLICATION :
--
-- 1. Ouvrir Supabase Dashboard: https://app.supabase.com
-- 2. Sélectionner votre projet
-- 3. Aller dans "SQL Editor" (menu de gauche)
-- 4. Cliquer sur "+ New query"
-- 5. Copier-coller le contenu du fichier create_company_settings.sql
-- 6. Cliquer sur "Run" (ou appuyer sur Ctrl+Enter)
-- 7. Vérifier que le message "Success" apparaît
--
-- VÉRIFICATION :
--
-- Pour vérifier que la table a bien été créée, exécuter :
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'company_settings'
ORDER BY ordinal_position;
--
-- Vous devriez voir toutes les colonnes de la table company_settings
--
-- ============================================================================

-- Si vous rencontrez des erreurs, voici les solutions courantes :
--
-- ERREUR: "relation companies does not exist"
-- SOLUTION: Créer d'abord la table companies ou modifier la contrainte FOREIGN KEY
--
-- ERREUR: "function uuid_generate_v4() does not exist"
-- SOLUTION: Activer l'extension uuid-ossp avec :
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
--
-- ============================================================================

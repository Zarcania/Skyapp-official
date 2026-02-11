-- ============================================================================
-- CORRECTIONS COLONNES MANQUANTES - SkyApp
-- Script pour ajouter les colonnes qui manquent dans vos tables existantes
-- ============================================================================

-- ============================================================================
-- 1. TABLE: searches - Ajouter les colonnes pour les photos par section
-- ============================================================================
-- Vérifier si la colonne photos existe déjà
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='searches' AND column_name='photos') THEN
        ALTER TABLE searches ADD COLUMN photos JSONB DEFAULT '[]';
    END IF;
END $$;

-- ============================================================================
-- 2. TABLE: searches - Ajouter les colonnes de géolocalisation
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='searches' AND column_name='latitude') THEN
        ALTER TABLE searches ADD COLUMN latitude DOUBLE PRECISION;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='searches' AND column_name='longitude') THEN
        ALTER TABLE searches ADD COLUMN longitude DOUBLE PRECISION;
    END IF;
END $$;

-- ============================================================================
-- 3. TABLE: invoices_electronic - Ajouter colonnes manquantes
-- ============================================================================
DO $$ 
BEGIN
    -- Colonne status_pdp (statut PDP)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='status_pdp') THEN
        ALTER TABLE invoices_electronic ADD COLUMN status_pdp TEXT DEFAULT 'draft' 
            CHECK (status_pdp IN ('draft', 'sent', 'paid', 'overdue'));
    END IF;
    
    -- Colonne direction (incoming/outgoing)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='direction') THEN
        ALTER TABLE invoices_electronic ADD COLUMN direction TEXT DEFAULT 'outgoing' 
            CHECK (direction IN ('outgoing', 'incoming'));
    END IF;
    
    -- Colonne customer_name
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='customer_name') THEN
        ALTER TABLE invoices_electronic ADD COLUMN customer_name TEXT;
    END IF;
    
    -- Colonne siren_client
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='siren_client') THEN
        ALTER TABLE invoices_electronic ADD COLUMN siren_client TEXT;
    END IF;
    
    -- Colonne address_billing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='address_billing') THEN
        ALTER TABLE invoices_electronic ADD COLUMN address_billing TEXT;
    END IF;
    
    -- Colonne address_delivery
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='address_delivery') THEN
        ALTER TABLE invoices_electronic ADD COLUMN address_delivery TEXT;
    END IF;
    
    -- Colonne payment_terms
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='payment_terms') THEN
        ALTER TABLE invoices_electronic ADD COLUMN payment_terms TEXT;
    END IF;
    
    -- Colonne payment_method
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='payment_method') THEN
        ALTER TABLE invoices_electronic ADD COLUMN payment_method TEXT;
    END IF;
    
    -- Colonne created_by
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invoices_electronic' AND column_name='created_by') THEN
        ALTER TABLE invoices_electronic ADD COLUMN created_by UUID REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================================
-- 4. TABLE: schedules - Vérifier colonnes team_leader
-- ============================================================================
DO $$ 
BEGIN
    -- Renommer collaborator_id en team_leader_id si nécessaire
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='schedules' AND column_name='collaborator_id') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name='schedules' AND column_name='team_leader_id') THEN
        -- Garder collaborator_id mais ajouter alias
        COMMENT ON COLUMN schedules.collaborator_id IS 'Team leader ID (same as team_leader_id)';
    END IF;
    
    -- Ajouter colonne location si manquante
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='schedules' AND column_name='location') THEN
        ALTER TABLE schedules ADD COLUMN location TEXT;
    END IF;
END $$;

-- ============================================================================
-- 5. TABLE: projects - Ajouter colonne search_id si manquante
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='projects' AND column_name='search_id') THEN
        ALTER TABLE projects ADD COLUMN search_id UUID REFERENCES searches(id) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='projects' AND column_name='client_id') THEN
        ALTER TABLE projects ADD COLUMN client_id UUID REFERENCES clients(id) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='projects' AND column_name='budget') THEN
        ALTER TABLE projects ADD COLUMN budget DECIMAL(10, 2);
    END IF;
END $$;

-- ============================================================================
-- 6. TABLE: planning_team_leaders - Ajouter colonne name si manquante
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='planning_team_leaders' AND column_name='name') THEN
        ALTER TABLE planning_team_leaders ADD COLUMN name TEXT;
        -- Remplir avec les noms des users
        UPDATE planning_team_leaders ptl
        SET name = u.email
        FROM users u
        WHERE ptl.user_id = u.id AND ptl.name IS NULL;
    END IF;
END $$;

-- ============================================================================
-- 7. TABLE: worksites - Ajouter colonnes manquantes
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='worksites' AND column_name='quote_id') THEN
        ALTER TABLE worksites ADD COLUMN quote_id UUID REFERENCES quotes(id) ON DELETE SET NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='worksites' AND column_name='end_date') THEN
        ALTER TABLE worksites ADD COLUMN end_date DATE;
    END IF;
END $$;

-- ============================================================================
-- 8. TABLE: quotes - Ajouter colonne items (lignes devis en JSON)
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='quotes' AND column_name='items') THEN
        ALTER TABLE quotes ADD COLUMN items JSONB DEFAULT '[]';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='quotes' AND column_name='valid_until') THEN
        ALTER TABLE quotes ADD COLUMN valid_until DATE;
    END IF;
END $$;

-- ============================================================================
-- 9. TABLE: quote_templates - Ajouter colonne items
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='quote_templates' AND column_name='items') THEN
        ALTER TABLE quote_templates ADD COLUMN items JSONB DEFAULT '[]';
    END IF;
END $$;

-- ============================================================================
-- 10. TABLE: invitations - Ajouter colonne expires_at
-- ============================================================================
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invitations' AND column_name='expires_at') THEN
        ALTER TABLE invitations ADD COLUMN expires_at TIMESTAMPTZ;
        -- Mettre expiration 7 jours après création pour les invitations existantes
        UPDATE invitations 
        SET expires_at = created_at + INTERVAL '7 days' 
        WHERE expires_at IS NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='invitations' AND column_name='invited_by') THEN
        ALTER TABLE invitations ADD COLUMN invited_by UUID REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================================
-- 11. TABLE: company_settings - Créer si manquante
-- ============================================================================
CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE UNIQUE,
    company_name TEXT,
    address TEXT,
    postal_code TEXT,
    city TEXT,
    siret TEXT,
    logo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_company_settings_company ON company_settings(company_id);

-- ============================================================================
-- 12. TABLE: materials - Créer si manquante (pour gestion stock)
-- ============================================================================
CREATE TABLE IF NOT EXISTS materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    category TEXT,
    st_code TEXT,
    location TEXT,
    status TEXT CHECK (status IN ('ACTIVE', 'INACTIVE', 'OUT_OF_STOCK')),
    assigned_to TEXT,
    assigned_date TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_materials_company ON materials(company_id);

-- ============================================================================
-- 13. TABLE: e_reporting - Créer si manquante (rapports électroniques)
-- ============================================================================
CREATE TABLE IF NOT EXISTS e_reporting (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    type_operation TEXT NOT NULL,
    fournisseur TEXT,
    montant DECIMAL(10, 2),
    date_operation DATE NOT NULL,
    resultat TEXT,
    file_attestation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ereporting_company ON e_reporting(company_id);

-- ============================================================================
-- 14. TABLE: reports - Créer si manquante (rapports généraux)
-- ============================================================================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    search_id UUID REFERENCES searches(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT,
    pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_company ON reports(company_id);
CREATE INDEX IF NOT EXISTS idx_reports_search ON reports(search_id);

-- ============================================================================
-- 15. TABLE: invoices_logs - Créer si manquante (historique factures)
-- ============================================================================
CREATE TABLE IF NOT EXISTS invoices_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices_electronic(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    description TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_logs_invoice ON invoices_logs(invoice_id);

-- ============================================================================
-- VÉRIFICATION FINALE
-- ============================================================================
-- Liste toutes les colonnes de la table searches
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'searches'
ORDER BY ordinal_position;

-- Liste toutes les colonnes de la table invoices_electronic
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'invoices_electronic'
ORDER BY ordinal_position;

-- ============================================================================
-- NOTES D'EXÉCUTION
-- ============================================================================
/*
COMMENT UTILISER:
1. Allez sur Supabase SQL Editor
2. Copiez-collez ce script
3. Exécutez (F5)

Ce script utilise DO $$ BEGIN ... END $$ pour éviter les erreurs si les colonnes
existent déjà. Il va seulement ajouter ce qui manque.

APRÈS EXÉCUTION:
- Toutes les colonnes manquantes seront ajoutées
- Aucune donnée existante ne sera perdue
- Les nouvelles colonnes auront des valeurs par défaut appropriées

VÉRIFICATION:
Les 2 dernières requêtes SELECT vous montreront les colonnes après ajout.
*/

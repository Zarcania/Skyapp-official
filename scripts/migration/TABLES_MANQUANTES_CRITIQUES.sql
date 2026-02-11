-- ============================================================================
-- TABLES MANQUANTES CRITIQUES POUR SKYAPP
-- ============================================================================
-- Ces 3 tables sont référencées par le backend mais n'existent pas dans Supabase
-- À exécuter dans l'éditeur SQL de Supabase
-- ============================================================================

-- ============================================================================
-- TABLE: invoices_received (Factures fournisseurs)
-- ============================================================================
-- Utilisée pour gérer les factures reçues des fournisseurs/sous-traitants
-- Référencée 4 fois dans server_supabase.py (ligne 3409 et autres)
-- ============================================================================

CREATE TABLE IF NOT EXISTS invoices_received (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Informations fournisseur
    supplier_name TEXT NOT NULL,
    supplier_siret TEXT,
    supplier_address TEXT,
    
    -- Informations facture
    invoice_number TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    amount_ht DECIMAL(10, 2) NOT NULL,
    amount_tva DECIMAL(10, 2) DEFAULT 0,
    amount_ttc DECIMAL(10, 2) NOT NULL,
    
    -- Statut et traitement
    status TEXT DEFAULT 'received' CHECK (status IN ('received', 'validated', 'paid', 'rejected')),
    payment_date DATE,
    payment_method TEXT,
    
    -- Documents et notes
    pdf_url TEXT,
    notes TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_invoices_received_company ON invoices_received(company_id);
CREATE INDEX IF NOT EXISTS idx_invoices_received_status ON invoices_received(status);
CREATE INDEX IF NOT EXISTS idx_invoices_received_date ON invoices_received(invoice_date);
CREATE INDEX IF NOT EXISTS idx_invoices_received_supplier ON invoices_received(supplier_name);

-- RLS (Row Level Security)
ALTER TABLE invoices_received ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view invoices_received from their company"
    ON invoices_received FOR SELECT
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can insert invoices_received for their company"
    ON invoices_received FOR INSERT
    WITH CHECK (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can update invoices_received from their company"
    ON invoices_received FOR UPDATE
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can delete invoices_received from their company"
    ON invoices_received FOR DELETE
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- ============================================================================
-- TABLE: e_reporting_declarations (Déclarations réglementaires)
-- ============================================================================
-- Utilisée pour gérer les déclarations fiscales et réglementaires
-- Référencée 5 fois dans server_supabase.py (ligne 3569 et autres)
-- ============================================================================

CREATE TABLE IF NOT EXISTS e_reporting_declarations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Type de déclaration
    declaration_type TEXT NOT NULL CHECK (declaration_type IN (
        'TVA',
        'DAS2',
        'URSSAF',
        'DADS',
        'DSN',
        'CFE',
        'CVAE',
        'OTHER'
    )),
    
    -- Période concernée
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    fiscal_year INTEGER,
    
    -- Informations déclaration
    declaration_number TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'accepted', 'rejected', 'corrected')),
    submission_date TIMESTAMPTZ,
    acceptance_date TIMESTAMPTZ,
    
    -- Montants
    declared_amount DECIMAL(12, 2),
    amount_due DECIMAL(12, 2),
    amount_paid DECIMAL(12, 2) DEFAULT 0,
    
    -- Documents
    pdf_url TEXT,
    xml_url TEXT,
    receipt_url TEXT,
    
    -- Détails et notes
    details JSONB DEFAULT '{}',
    notes TEXT,
    
    -- Métadonnées
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_e_reporting_company ON e_reporting_declarations(company_id);
CREATE INDEX IF NOT EXISTS idx_e_reporting_type ON e_reporting_declarations(declaration_type);
CREATE INDEX IF NOT EXISTS idx_e_reporting_status ON e_reporting_declarations(status);
CREATE INDEX IF NOT EXISTS idx_e_reporting_period ON e_reporting_declarations(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_e_reporting_fiscal_year ON e_reporting_declarations(fiscal_year);

-- RLS (Row Level Security)
ALTER TABLE e_reporting_declarations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view declarations from their company"
    ON e_reporting_declarations FOR SELECT
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can insert declarations for their company"
    ON e_reporting_declarations FOR INSERT
    WITH CHECK (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can update declarations from their company"
    ON e_reporting_declarations FOR UPDATE
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can delete declarations from their company"
    ON e_reporting_declarations FOR DELETE
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- ============================================================================
-- TABLE: archives_legal (Archives légales)
-- ============================================================================
-- Utilisée pour stocker les documents légaux et archives obligatoires
-- Référencée 6 fois dans server_supabase.py (ligne 3765 et autres)
-- ============================================================================

CREATE TABLE IF NOT EXISTS archives_legal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Type de document
    document_type TEXT NOT NULL CHECK (document_type IN (
        'INVOICE',
        'QUOTE',
        'CONTRACT',
        'PAYSLIP',
        'TAX_RETURN',
        'ACCOUNTING',
        'LEGAL_NOTICE',
        'STATUTE',
        'MEETING_MINUTES',
        'CERTIFICATE',
        'OTHER'
    )),
    
    -- Informations document
    title TEXT NOT NULL,
    description TEXT,
    reference_number TEXT,
    
    -- Dates importantes
    document_date DATE NOT NULL,
    archiving_date DATE DEFAULT CURRENT_DATE,
    retention_end_date DATE, -- Date de fin de conservation légale
    
    -- Stockage
    file_url TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size_bytes INTEGER,
    file_mime_type TEXT,
    
    -- Hash pour intégrité
    file_hash TEXT, -- SHA-256 du fichier pour vérifier l'intégrité
    
    -- Catégorisation
    category TEXT,
    tags TEXT[],
    
    -- Métadonnées
    metadata JSONB DEFAULT '{}',
    
    -- Accès et confidentialité
    is_confidential BOOLEAN DEFAULT FALSE,
    access_level TEXT DEFAULT 'company' CHECK (access_level IN ('public', 'company', 'restricted', 'confidential')),
    
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    last_accessed_at TIMESTAMPTZ,
    access_count INTEGER DEFAULT 0
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_archives_company ON archives_legal(company_id);
CREATE INDEX IF NOT EXISTS idx_archives_type ON archives_legal(document_type);
CREATE INDEX IF NOT EXISTS idx_archives_date ON archives_legal(document_date);
CREATE INDEX IF NOT EXISTS idx_archives_category ON archives_legal(category);
CREATE INDEX IF NOT EXISTS idx_archives_retention ON archives_legal(retention_end_date);
CREATE INDEX IF NOT EXISTS idx_archives_tags ON archives_legal USING GIN(tags);

-- RLS (Row Level Security)
ALTER TABLE archives_legal ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view archives from their company"
    ON archives_legal FOR SELECT
    USING (
        company_id IN (SELECT company_id FROM users WHERE id = auth.uid())
        AND (
            access_level IN ('public', 'company')
            OR (access_level = 'restricted' AND created_by = auth.uid())
        )
    );

CREATE POLICY "Users can insert archives for their company"
    ON archives_legal FOR INSERT
    WITH CHECK (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can update archives from their company"
    ON archives_legal FOR UPDATE
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can delete archives from their company"
    ON archives_legal FOR DELETE
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- ============================================================================
-- TRIGGERS pour updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour invoices_received
CREATE TRIGGER update_invoices_received_updated_at
    BEFORE UPDATE ON invoices_received
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour e_reporting_declarations
CREATE TRIGGER update_e_reporting_declarations_updated_at
    BEFORE UPDATE ON e_reporting_declarations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour archives_legal
CREATE TRIGGER update_archives_legal_updated_at
    BEFORE UPDATE ON archives_legal
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VÉRIFICATION
-- ============================================================================
-- Commandes pour vérifier que les tables ont bien été créées :
--
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('invoices_received', 'e_reporting_declarations', 'archives_legal');
--
-- ============================================================================

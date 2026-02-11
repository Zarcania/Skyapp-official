-- ============================================================================
-- TABLES SUPABASE MANQUANTES - SkyApp
-- Script SQL complet pour créer toutes les tables nécessaires
-- ============================================================================

-- Note: Certaines tables existent peut-être déjà (users, companies, searches)
-- Ce script crée TOUTES les tables référencées dans server_supabase.py

-- ============================================================================
-- 1. TABLE: companies (Entreprises)
-- ============================================================================
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    siren TEXT UNIQUE,
    address TEXT,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 2. TABLE: users (Utilisateurs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('ADMIN', 'BUREAU', 'TECHNICIEN', 'FOUNDER')),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_company ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================================================
-- 3. TABLE: searches (Recherches terrain)
-- ============================================================================
CREATE TABLE IF NOT EXISTS searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    client_name TEXT,
    address TEXT,
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED')),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    photos JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_searches_company ON searches(company_id);
CREATE INDEX IF NOT EXISTS idx_searches_user ON searches(user_id);
CREATE INDEX IF NOT EXISTS idx_searches_status ON searches(status);

-- ============================================================================
-- 4. TABLE: clients (Clients)
-- ============================================================================
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    siren TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clients_company ON clients(company_id);

-- ============================================================================
-- 5. VIEW: clients_with_company (Vue clients avec entreprise)
-- ============================================================================
CREATE OR REPLACE VIEW clients_with_company AS
SELECT 
    c.*,
    co.name AS company_name
FROM clients c
LEFT JOIN companies co ON c.company_id = co.id;

-- ============================================================================
-- 6. TABLE: worksites (Chantiers)
-- ============================================================================
CREATE TABLE IF NOT EXISTS worksites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    address TEXT,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    status TEXT CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD')),
    start_date DATE,
    end_date DATE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_worksites_company ON worksites(company_id);
CREATE INDEX IF NOT EXISTS idx_worksites_client ON worksites(client_id);

-- ============================================================================
-- 7. TABLE: quotes (Devis)
-- ============================================================================
CREATE TABLE IF NOT EXISTS quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    quote_number TEXT UNIQUE NOT NULL,
    total_ht DECIMAL(10, 2),
    total_tva DECIMAL(10, 2),
    total_ttc DECIMAL(10, 2),
    status TEXT CHECK (status IN ('DRAFT', 'SENT', 'ACCEPTED', 'REJECTED')),
    valid_until DATE,
    items JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quotes_company ON quotes(company_id);
CREATE INDEX IF NOT EXISTS idx_quotes_client ON quotes(client_id);

-- ============================================================================
-- 8. VIEW: quotes_with_client_name (Vue devis avec nom client)
-- ============================================================================
CREATE OR REPLACE VIEW quotes_with_client_name AS
SELECT 
    q.*,
    c.name AS client_name
FROM quotes q
LEFT JOIN clients c ON q.client_id = c.id;

-- ============================================================================
-- 9. TABLE: quote_templates (Modèles de devis)
-- ============================================================================
CREATE TABLE IF NOT EXISTS quote_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    items JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quote_templates_company ON quote_templates(company_id);

-- ============================================================================
-- 10. TABLE: projects (Projets)
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    search_id UUID REFERENCES searches(id) ON DELETE SET NULL,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    status TEXT CHECK (status IN ('PLANNING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10, 2),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_company ON projects(company_id);
CREATE INDEX IF NOT EXISTS idx_projects_search ON projects(search_id);

-- ============================================================================
-- 11. TABLE: project_notes (Notes de projet)
-- ============================================================================
CREATE TABLE IF NOT EXISTS project_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_notes_project ON project_notes(project_id);

-- ============================================================================
-- 12. TABLE: invitations (Invitations collaborateurs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('ADMIN', 'BUREAU', 'TECHNICIEN')),
    token TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'ACCEPTED', 'REJECTED')),
    invited_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_invitations_company ON invitations(company_id);
CREATE INDEX IF NOT EXISTS idx_invitations_email ON invitations(email);
CREATE INDEX IF NOT EXISTS idx_invitations_token ON invitations(token);

-- ============================================================================
-- 13. TABLE: planning_team_leaders (Chefs d'équipe planning)
-- ============================================================================
CREATE TABLE IF NOT EXISTS planning_team_leaders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_planning_team_leaders_company ON planning_team_leaders(company_id);
CREATE INDEX IF NOT EXISTS idx_planning_team_leaders_user ON planning_team_leaders(user_id);

-- ============================================================================
-- 14. TABLE: schedules (Planning / Rendez-vous)
-- ============================================================================
CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    collaborator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ NOT NULL,
    location TEXT,
    status TEXT CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_schedules_company ON schedules(company_id);
CREATE INDEX IF NOT EXISTS idx_schedules_collaborator ON schedules(collaborator_id);
CREATE INDEX IF NOT EXISTS idx_schedules_dates ON schedules(start_datetime, end_datetime);

-- ============================================================================
-- 15. TABLE: invoices_electronic (Factures électroniques)
-- ============================================================================
CREATE TABLE IF NOT EXISTS invoices_electronic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    customer_name TEXT NOT NULL,
    siren_client TEXT,
    address_billing TEXT,
    address_delivery TEXT,
    total_ht DECIMAL(10, 2) NOT NULL,
    total_tva DECIMAL(10, 2) NOT NULL,
    total_ttc DECIMAL(10, 2) NOT NULL,
    format TEXT DEFAULT 'pdf',
    status_pdp TEXT DEFAULT 'draft' CHECK (status_pdp IN ('draft', 'sent', 'paid', 'overdue')),
    direction TEXT DEFAULT 'outgoing' CHECK (direction IN ('outgoing', 'incoming')),
    payment_terms TEXT,
    payment_method TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_company ON invoices_electronic(company_id);
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices_electronic(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices_electronic(invoice_date);

-- ============================================================================
-- 16. TABLE: invoice_lines (Lignes de facture)
-- ============================================================================
CREATE TABLE IF NOT EXISTS invoice_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id UUID NOT NULL REFERENCES invoices_electronic(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    designation TEXT NOT NULL,
    description TEXT,
    quantity DECIMAL(10, 2) NOT NULL,
    unit TEXT,
    unit_price_ht DECIMAL(10, 2) NOT NULL,
    tva_rate DECIMAL(5, 2) NOT NULL,
    tva_amount DECIMAL(10, 2) NOT NULL,
    total_line_ht DECIMAL(10, 2) NOT NULL,
    total_line_ttc DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoice_lines_invoice ON invoice_lines(invoice_id);

-- ============================================================================
-- POLITIQUE RLS (Row Level Security) - IMPORTANT
-- ============================================================================
-- Activer RLS sur toutes les tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE worksites ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quote_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE planning_team_leaders ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices_electronic ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_lines ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- POLITIQUES RLS DE BASE (à adapter selon vos besoins)
-- ============================================================================

-- Politique pour service_role (backend) - accès complet
CREATE POLICY "Service role has full access" ON companies
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON users
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON searches
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON clients
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON worksites
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON quotes
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON quote_templates
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON projects
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON project_notes
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON invitations
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON planning_team_leaders
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON schedules
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON invoices_electronic
    FOR ALL USING (true);

CREATE POLICY "Service role has full access" ON invoice_lines
    FOR ALL USING (true);

-- ============================================================================
-- TRIGGERS UPDATED_AT (mise à jour automatique)
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger sur toutes les tables avec updated_at
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_searches_updated_at BEFORE UPDATE ON searches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_worksites_updated_at BEFORE UPDATE ON worksites
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON quotes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quote_templates_updated_at BEFORE UPDATE ON quote_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_schedules_updated_at BEFORE UPDATE ON schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices_electronic
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VÉRIFICATION DES TABLES CRÉÉES
-- ============================================================================
-- Exécutez cette requête pour vérifier que toutes les tables existent:
/*
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
*/

-- ============================================================================
-- NOTES D'INSTALLATION
-- ============================================================================
/*
COMMENT UTILISER CE SCRIPT:

1. Allez sur votre projet Supabase: https://supabase.com/dashboard
2. Cliquez sur "SQL Editor"
3. Créez une nouvelle requête
4. Copiez-collez TOUT ce script
5. Cliquez sur "Run" (ou F5)

VÉRIFICATION:
- Allez dans "Table Editor" pour voir toutes vos tables
- Vérifiez que les relations (foreign keys) sont bien créées
- Testez avec votre backend

SÉCURITÉ:
- Les politiques RLS sont configurées pour service_role
- Ajustez les politiques selon vos besoins de sécurité
- Pour les utilisateurs authentifiés, ajoutez des politiques spécifiques

PERFORMANCES:
- Tous les index nécessaires sont créés
- Les triggers updated_at automatisent les mises à jour
- Les vues matérialisées peuvent être ajoutées si besoin

DÉPANNAGE:
- Si une table existe déjà: utilisez DROP TABLE IF EXISTS avant CREATE
- Si erreur de permission: vérifiez que vous utilisez le bon rôle
- Si erreur de foreign key: créez les tables dans l'ordre du script
*/

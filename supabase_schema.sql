-- SkyApp Database Schema for Supabase
-- À exécuter dans Supabase SQL Editor

-- ========================================
-- 1. EXTENSIONS ET FONCTIONS UTILITAIRES
-- ========================================

-- Activer l'extension UUID pour générer des IDs uniques
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- 2. ÉNUMÉRATIONS (ENUMS)
-- ========================================

-- Rôles utilisateur
CREATE TYPE user_role AS ENUM ('ADMIN', 'BUREAU', 'TECHNICIEN');

-- Statuts des recherches (inclut DRAFT pour brouillons)
CREATE TYPE search_status AS ENUM ('DRAFT', 'ACTIVE', 'SHARED', 'SHARED_TO_BUREAU', 'PROCESSED', 'ARCHIVED');

-- Statuts des devis
CREATE TYPE quote_status AS ENUM ('DRAFT', 'SENT', 'ACCEPTED', 'REJECTED', 'EXPIRED');

-- Statuts des chantiers  
CREATE TYPE worksite_status AS ENUM ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');

-- Sources des chantiers
CREATE TYPE worksite_source AS ENUM ('QUOTE', 'MANUAL');

-- ========================================
-- 3. TABLES PRINCIPALES
-- ========================================

-- Table des entreprises
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des utilisateurs (liée à l'auth Supabase)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT NOT NULL UNIQUE,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    role user_role NOT NULL,
    company_id UUID REFERENCES companies(id),
    actif BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des clients
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    nom TEXT NOT NULL,
    email TEXT NOT NULL,
    telephone TEXT,
    adresse TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des recherches terrain
CREATE TABLE searches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    observations TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    status search_status DEFAULT 'ACTIVE',
    photos JSONB DEFAULT '[]'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des devis
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    client_id UUID NOT NULL REFERENCES clients(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    status quote_status DEFAULT 'DRAFT',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des chantiers
CREATE TABLE worksites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    client_id UUID REFERENCES clients(id),
    client_name TEXT DEFAULT '',
    quote_id UUID REFERENCES quotes(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    source worksite_source DEFAULT 'MANUAL',
    status worksite_status DEFAULT 'PLANNED',
    description TEXT DEFAULT '',
    address TEXT DEFAULT '',
    amount DECIMAL(10, 2) DEFAULT 0.0,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des rapports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    search_id UUID NOT NULL REFERENCES searches(id),
    user_id UUID NOT NULL REFERENCES users(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    pdf_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table du matériel
CREATE TABLE materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    qr_code TEXT UNIQUE NOT NULL,
    location TEXT,
    status TEXT DEFAULT 'DISPONIBLE',
    assigned_to UUID REFERENCES users(id),
    assigned_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- 4. INDEXES POUR PERFORMANCE
-- ========================================

-- Index sur les colonnes fréquemment utilisées
CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_searches_user_id ON searches(user_id);
CREATE INDEX idx_searches_company_id ON searches(company_id);
CREATE INDEX idx_searches_status ON searches(status);
CREATE INDEX idx_clients_company_id ON clients(company_id);
CREATE INDEX idx_quotes_company_id ON quotes(company_id);
CREATE INDEX idx_quotes_client_id ON quotes(client_id);
CREATE INDEX idx_worksites_company_id ON worksites(company_id);
CREATE INDEX idx_materials_company_id ON materials(company_id);
CREATE INDEX idx_materials_qr_code ON materials(qr_code);

-- ========================================
-- 5. FONCTIONS TRIGGER POUR UPDATED_AT
-- ========================================

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Application des triggers updated_at sur toutes les tables
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_searches_updated_at BEFORE UPDATE ON searches FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON quotes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_worksites_updated_at BEFORE UPDATE ON worksites FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_materials_updated_at BEFORE UPDATE ON materials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 6. ROW LEVEL SECURITY (RLS) POLICIES
-- ========================================

-- Activer RLS sur toutes les tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE searches ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE worksites ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE materials ENABLE ROW LEVEL SECURITY;

-- Politiques pour la table companies
CREATE POLICY "Users can view their own company" ON companies
    FOR SELECT USING (id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Admins can manage their company" ON companies
    FOR ALL USING (id IN (SELECT company_id FROM users WHERE id = auth.uid() AND role = 'ADMIN'));

-- Politiques pour la table users
CREATE POLICY "Users can view users in their company" ON users
    FOR SELECT USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Admins can manage users in their company" ON users
    FOR ALL USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid() AND role = 'ADMIN'));

-- Politiques pour les autres tables (accès basé sur company_id)
CREATE POLICY "Company access" ON clients
    FOR ALL USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Company access" ON searches  
    FOR ALL USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Company access" ON quotes
    FOR ALL USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Company access" ON worksites
    FOR ALL USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Company access" ON reports
    FOR ALL USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Company access" ON materials
    FOR ALL USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- ========================================
-- 7. DONNÉES D'EXEMPLE (OPTIONNEL)
-- ========================================

-- Insertion d'une entreprise de test
INSERT INTO companies (name) VALUES ('Test Company');

-- Note: Les utilisateurs seront créés automatiquement via Supabase Auth
-- Vous devrez ensuite les associer à une entreprise dans la table users

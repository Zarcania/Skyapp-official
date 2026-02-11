-- Création de la table company_settings pour les paramètres des sociétés
-- Date: 2025-12-18

-- Table pour les paramètres des sociétés
CREATE TABLE IF NOT EXISTS company_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL UNIQUE REFERENCES companies(id) ON DELETE CASCADE,
    company_name VARCHAR(255),
    legal_form VARCHAR(100),
    address TEXT,
    postal_code VARCHAR(20),
    city VARCHAR(100),
    siret VARCHAR(14),
    siren VARCHAR(9),
    rcs_rm VARCHAR(100),
    logo_url TEXT,
    primary_color VARCHAR(7) DEFAULT '#6366f1',
    secondary_color VARCHAR(7) DEFAULT '#333333',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_company_settings_company_id ON company_settings(company_id);

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_company_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_company_settings_updated_at
    BEFORE UPDATE ON company_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_company_settings_updated_at();

-- Commentaires
COMMENT ON TABLE company_settings IS 'Paramètres et informations légales des sociétés';
COMMENT ON COLUMN company_settings.company_id IS 'Référence à la société';
COMMENT ON COLUMN company_settings.logo_url IS 'URL du logo de la société pour les PDF';
COMMENT ON COLUMN company_settings.primary_color IS 'Couleur principale pour les documents PDF';

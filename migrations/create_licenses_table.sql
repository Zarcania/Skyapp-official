-- Création de la table licenses pour la gestion des licences
CREATE TABLE IF NOT EXISTS licenses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    license_key text UNIQUE NOT NULL,
    company_id uuid REFERENCES companies(id) ON DELETE CASCADE,
    max_users integer DEFAULT 5,
    expires_at timestamp with time zone,
    is_active boolean DEFAULT true,
    created_by uuid REFERENCES users(id),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_licenses_company_id ON licenses(company_id);
CREATE INDEX IF NOT EXISTS idx_licenses_license_key ON licenses(license_key);
CREATE INDEX IF NOT EXISTS idx_licenses_is_active ON licenses(is_active) WHERE is_active = true;

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_licenses_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_licenses_updated_at
    BEFORE UPDATE ON licenses
    FOR EACH ROW
    EXECUTE FUNCTION update_licenses_updated_at();

-- Commentaires pour documenter la table
COMMENT ON TABLE licenses IS 'Gestion des licences pour les entreprises';
COMMENT ON COLUMN licenses.license_key IS 'Clé unique de la licence';
COMMENT ON COLUMN licenses.max_users IS 'Nombre maximum d''utilisateurs autorisés';
COMMENT ON COLUMN licenses.expires_at IS 'Date d''expiration de la licence';
COMMENT ON COLUMN licenses.is_active IS 'Statut actif/inactif de la licence';

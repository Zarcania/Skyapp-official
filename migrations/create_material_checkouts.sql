-- ==========================================
-- SYSTÈME D'EMPRUNT DE MATÉRIEL
-- ==========================================

-- Table pour suivre les emprunts de matériel
CREATE TABLE IF NOT EXISTS material_checkouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Informations d'emprunt
    checked_out_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expected_return_date TIMESTAMPTZ,
    checked_in_at TIMESTAMPTZ,
    
    -- Statut
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'returned', 'overdue')),
    
    -- Notes
    checkout_notes TEXT,
    checkin_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_material_checkouts_material ON material_checkouts(material_id);
CREATE INDEX IF NOT EXISTS idx_material_checkouts_user ON material_checkouts(user_id);
CREATE INDEX IF NOT EXISTS idx_material_checkouts_company ON material_checkouts(company_id);
CREATE INDEX IF NOT EXISTS idx_material_checkouts_status ON material_checkouts(status);
CREATE INDEX IF NOT EXISTS idx_material_checkouts_active ON material_checkouts(material_id, status) WHERE status = 'active';

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_material_checkouts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_material_checkouts_updated_at ON material_checkouts;
CREATE TRIGGER trigger_update_material_checkouts_updated_at
    BEFORE UPDATE ON material_checkouts
    FOR EACH ROW
    EXECUTE FUNCTION update_material_checkouts_updated_at();

-- Ajouter colonne "disponible" au matériel (true si personne ne l'a emprunté)
ALTER TABLE materials ADD COLUMN IF NOT EXISTS available BOOLEAN DEFAULT true;
ALTER TABLE materials ADD COLUMN IF NOT EXISTS current_holder_id UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE materials ADD COLUMN IF NOT EXISTS current_checkout_id UUID REFERENCES material_checkouts(id) ON DELETE SET NULL;

-- RLS Policies pour material_checkouts
ALTER TABLE material_checkouts ENABLE ROW LEVEL SECURITY;

-- Les utilisateurs peuvent voir les emprunts de leur company
CREATE POLICY "Users can view checkouts in their company"
    ON material_checkouts FOR SELECT
    USING (company_id IN (
        SELECT company_id FROM users WHERE id = auth.uid()
    ));

-- Les utilisateurs peuvent créer des emprunts dans leur company
CREATE POLICY "Users can create checkouts in their company"
    ON material_checkouts FOR INSERT
    WITH CHECK (
        company_id IN (SELECT company_id FROM users WHERE id = auth.uid())
        AND user_id = auth.uid()
    );

-- Retourner : son propre matériel OU si on est ADMIN/BUREAU, n'importe quel matériel de l'entreprise
CREATE POLICY "Users can update their own checkouts or admins can update any"
    ON material_checkouts FOR UPDATE
    USING (
        company_id IN (SELECT company_id FROM users WHERE id = auth.uid())
        AND (
            user_id = auth.uid()
            OR EXISTS (
                SELECT 1 FROM users 
                WHERE id = auth.uid() 
                AND company_id = material_checkouts.company_id
                AND (is_fondateur = true OR role IN ('ADMIN', 'BUREAU'))
            )
        )
    );

-- Fonction pour marquer le matériel en retard automatiquement
CREATE OR REPLACE FUNCTION mark_overdue_checkouts()
RETURNS void AS $$
BEGIN
    UPDATE material_checkouts
    SET status = 'overdue'
    WHERE status = 'active'
    AND expected_return_date IS NOT NULL
    AND expected_return_date < NOW();
END;
$$ LANGUAGE plpgsql;

-- Vue pour obtenir facilement le matériel disponible
CREATE OR REPLACE VIEW available_materials AS
SELECT 
    m.*,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM material_checkouts mc 
            WHERE mc.material_id = m.id 
            AND mc.status = 'active'
        ) THEN false
        ELSE true
    END as is_available,
    u.email as current_holder_email,
    mc.checked_out_at,
    mc.expected_return_date
FROM materials m
LEFT JOIN material_checkouts mc ON m.id = mc.material_id AND mc.status = 'active'
LEFT JOIN users u ON mc.user_id = u.id;

COMMENT ON TABLE material_checkouts IS 'Suivi des emprunts et retours de matériel';
COMMENT ON COLUMN material_checkouts.status IS 'active: emprunté, returned: retourné, overdue: en retard';

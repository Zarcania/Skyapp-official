-- Table pour les comptes-rendus de chantier
CREATE TABLE IF NOT EXISTS mission_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    mission_id UUID NOT NULL REFERENCES schedules(id) ON DELETE CASCADE,
    technician_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    works_performed TEXT NOT NULL,
    materials_used TEXT,
    duration_hours DECIMAL(5, 2),
    observations TEXT,
    issues_encountered TEXT,
    photos_before TEXT[], -- Array de noms de fichiers
    photos_after TEXT[], -- Array de noms de fichiers
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_mission_reports_company ON mission_reports(company_id);
CREATE INDEX IF NOT EXISTS idx_mission_reports_mission ON mission_reports(mission_id);
CREATE INDEX IF NOT EXISTS idx_mission_reports_technician ON mission_reports(technician_id);
CREATE INDEX IF NOT EXISTS idx_mission_reports_created ON mission_reports(created_at DESC);

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_mission_reports_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_mission_reports_updated_at
    BEFORE UPDATE ON mission_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_mission_reports_updated_at();

-- Commentaires
COMMENT ON TABLE mission_reports IS 'Comptes-rendus de chantier créés par les techniciens';
COMMENT ON COLUMN mission_reports.works_performed IS 'Description des travaux effectués';
COMMENT ON COLUMN mission_reports.materials_used IS 'Liste des matériaux utilisés';
COMMENT ON COLUMN mission_reports.duration_hours IS 'Durée de l''intervention en heures';
COMMENT ON COLUMN mission_reports.photos_before IS 'Photos avant les travaux';
COMMENT ON COLUMN mission_reports.photos_after IS 'Photos après les travaux';

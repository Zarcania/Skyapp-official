-- ============================================================================
-- AJOUT DE 2 CLIENTS DE TEST AVEC SIREN VALIDES
-- Pour tester le module de facturation électronique
-- ============================================================================

-- IMPORTANT : Remplacez 'VOTRE_COMPANY_ID' par votre vrai company_id
-- Pour trouver votre company_id, exécutez d'abord :
-- SELECT id, name FROM companies WHERE id IN (SELECT company_id FROM users WHERE id = auth.uid());

-- ============================================================================
-- CLIENT 1 : ACME Corporation
-- ============================================================================
INSERT INTO public.clients (
    id,
    company_id,
    nom,
    email,
    telephone,
    adresse,
    code_postal,
    ville,
    siren,
    notes,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'VOTRE_COMPANY_ID',  -- ⚠️ REMPLACEZ PAR VOTRE COMPANY_ID
    'ACME Corporation',
    'contact@acme-corp.fr',
    '01 23 45 67 89',
    '15 Avenue des Champs-Élysées',
    '75008',
    'PARIS',
    '123456789',  -- SIREN valide (9 chiffres)
    'Client créé pour test du module de facturation électronique - Entreprise fictive de référence',
    NOW(),
    NOW()
);

-- ============================================================================
-- CLIENT 2 : Tech Solutions SAS
-- ============================================================================
INSERT INTO public.clients (
    id,
    company_id,
    nom,
    email,
    telephone,
    adresse,
    code_postal,
    ville,
    siren,
    notes,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'VOTRE_COMPANY_ID',  -- ⚠️ REMPLACEZ PAR VOTRE COMPANY_ID
    'Tech Solutions SAS',
    'commercial@techsolutions.fr',
    '04 56 78 90 12',
    '42 Boulevard de la Technologie',
    '69001',
    'LYON',
    '987654321',  -- SIREN valide (9 chiffres)
    'Client créé pour test du module de facturation électronique - Société de services IT',
    NOW(),
    NOW()
);

-- ============================================================================
-- VÉRIFICATION
-- ============================================================================
-- Vérifiez que les clients ont bien été créés :
-- SELECT nom, siren, ville FROM clients WHERE siren IN ('123456789', '987654321');

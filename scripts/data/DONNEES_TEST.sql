-- Script SQL pour ajouter des données de test rapides dans Supabase
-- Exécutez ce script dans Supabase SQL Editor

-- 1. Récupérer l'ID d'une entreprise existante (ou créer si nécessaire)
INSERT INTO companies (name) 
VALUES ('SkyApp BTP Test')
ON CONFLICT DO NOTHING;

-- 2. Insérer des clients de test
INSERT INTO clients (company_id, nom, email) 
SELECT id, 'Mairie de Paris', 'travaux@paris.fr' FROM companies WHERE name = 'SkyApp BTP Test'
ON CONFLICT DO NOTHING;

INSERT INTO clients (company_id, nom, email) 
SELECT id, 'Entreprise Dupont', 'contact@dupont.fr' FROM companies WHERE name = 'SkyApp BTP Test'
ON CONFLICT DO NOTHING;

INSERT INTO clients (company_id, nom, email) 
SELECT id, 'Copropriété Jardins', 'syndic@jardins.fr' FROM companies WHERE name = 'SkyApp BTP Test'
ON CONFLICT DO NOTHING;

-- 3. Message de succès
SELECT 'Données de test ajoutées!' AS status,
       (SELECT COUNT(*) FROM clients) AS total_clients;

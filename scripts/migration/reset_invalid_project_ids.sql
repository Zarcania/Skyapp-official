-- Script pour réinitialiser les project_id invalides dans les recherches
-- Ce script met à NULL tous les project_id qui pointent vers des projets inexistants ou d'autres companies

-- 1. Trouver les recherches avec project_id invalides (projets inexistants)
SELECT 
    s.id,
    s.address,
    s.project_id,
    'Projet introuvable' as raison
FROM searches s
LEFT JOIN projects p ON s.project_id = p.id
WHERE s.project_id IS NOT NULL
  AND p.id IS NULL;

-- 2. Trouver les recherches avec project_id pointant vers une autre company
SELECT 
    s.id,
    s.address,
    s.project_id,
    s.company_id as search_company,
    p.company_id as project_company,
    'Projet d''une autre company' as raison
FROM searches s
INNER JOIN projects p ON s.project_id = p.id
WHERE s.company_id != p.company_id;

-- 3. Réinitialiser tous les project_id invalides (décommentez pour exécuter)
/*
UPDATE searches
SET project_id = NULL
WHERE id IN (
    -- Projets inexistants
    SELECT s.id
    FROM searches s
    LEFT JOIN projects p ON s.project_id = p.id
    WHERE s.project_id IS NOT NULL
      AND p.id IS NULL
    
    UNION
    
    -- Projets d'une autre company
    SELECT s.id
    FROM searches s
    INNER JOIN projects p ON s.project_id = p.id
    WHERE s.company_id != p.company_id
);
*/

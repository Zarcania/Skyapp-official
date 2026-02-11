-- Ajouter les colonnes first_name, last_name, phone et address à la table users
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone VARCHAR(50);

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS address TEXT;

-- Ajouter la colonne invited_by_name à la table invitations
ALTER TABLE invitations 
ADD COLUMN IF NOT EXISTS invited_by_name VARCHAR(255);

-- Mettre à jour les invitations existantes avec le nom de l'inviteur
UPDATE invitations 
SET invited_by_name = CONCAT(u.first_name, ' ', u.last_name)
FROM users u
WHERE invitations.invited_by = u.id 
  AND u.first_name IS NOT NULL 
  AND u.last_name IS NOT NULL
  AND (invitations.invited_by_name IS NULL OR invitations.invited_by_name = '');

-- Vérifier les résultats
SELECT 
    email,
    role,
    invited_by_name,
    status,
    created_at
FROM invitations
ORDER BY created_at DESC
LIMIT 10;

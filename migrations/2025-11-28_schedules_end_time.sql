-- Migration: Ajouter end_time à schedules pour simplifier la gestion des plages horaires
-- Permet de gérer précisément les intervalles sans recalculer time + hours

alter table if exists schedules
  add column if not exists end_time time without time zone;

-- Index pour détecter les conflits rapidement
create index if not exists idx_schedules_collaborator_date 
  on schedules(collaborator_id, date);

create index if not exists idx_schedules_worksite 
  on schedules(worksite_id);

-- Mettre à jour les lignes existantes si elles ont time et hours
update schedules
set end_time = (time + (hours || ' hours')::interval)::time
where end_time is null and time is not null and hours is not null;

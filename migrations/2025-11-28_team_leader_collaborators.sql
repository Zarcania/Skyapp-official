-- Migration: Gestion des collaborateurs par chef d'équipe
-- Date: 2025-11-28
-- Description: Table de liaison pour assigner 1-10 collaborateurs par chef d'équipe

-- Table de liaison team_leader_collaborators
create table if not exists team_leader_collaborators (
    id uuid default gen_random_uuid() primary key,
    team_leader_id uuid not null references planning_team_leaders(id) on delete cascade,
    collaborator_id uuid not null references users(id) on delete cascade,
    assigned_at timestamp with time zone default now(),
    assigned_by uuid references users(id),
    is_active boolean default true,
    notes text,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now(),
    
    -- Contrainte unicité: un collaborateur ne peut être assigné qu'une fois à un chef
    constraint unique_team_leader_collaborator unique(team_leader_id, collaborator_id)
);

-- Index pour performance
create index idx_team_leader_collaborators_team_leader on team_leader_collaborators(team_leader_id);
create index idx_team_leader_collaborators_collaborator on team_leader_collaborators(collaborator_id);
create index idx_team_leader_collaborators_active on team_leader_collaborators(is_active);

-- RLS Policies
alter table team_leader_collaborators enable row level security;

-- Lecture: Bureau/Admin peuvent voir toutes les assignations, technicien voit son assignation
create policy "team_leader_collaborators_select_policy" on team_leader_collaborators
    for select using (
        auth.jwt() ->> 'role' in ('ADMIN', 'BUREAU')
        or collaborator_id = (auth.jwt() ->> 'sub')::uuid
    );

-- Insertion/Update/Delete: Bureau/Admin seulement
create policy "team_leader_collaborators_insert_policy" on team_leader_collaborators
    for insert with check (auth.jwt() ->> 'role' in ('ADMIN', 'BUREAU'));

create policy "team_leader_collaborators_update_policy" on team_leader_collaborators
    for update using (auth.jwt() ->> 'role' in ('ADMIN', 'BUREAU'));

create policy "team_leader_collaborators_delete_policy" on team_leader_collaborators
    for delete using (auth.jwt() ->> 'role' in ('ADMIN', 'BUREAU'));

-- Vue pour statistiques par chef d'équipe
create or replace view team_leader_stats as
select 
    tl.id as team_leader_id,
    tl.first_name,
    tl.last_name,
    tl.name,
    tl.email,
    count(tlc.id) filter (where tlc.is_active = true) as active_collaborators_count,
    array_agg(
        json_build_object(
            'id', u.id,
            'first_name', u.first_name,
            'last_name', u.last_name,
            'email', u.email,
            'assigned_at', tlc.assigned_at
        )
    ) filter (where tlc.is_active = true) as active_collaborators
from planning_team_leaders tl
left join team_leader_collaborators tlc on tlc.team_leader_id = tl.id and tlc.is_active = true
left join users u on u.id = tlc.collaborator_id
group by tl.id, tl.first_name, tl.last_name, tl.name, tl.email;

comment on table team_leader_collaborators is 'Assignation des collaborateurs aux chefs d''équipe (max 10 par chef)';
comment on view team_leader_stats is 'Vue consolidée: chef d''équipe + nombre et liste de collaborateurs actifs';

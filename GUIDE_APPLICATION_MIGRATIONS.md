# 🔧 Guide d'Application des Migrations Manquantes

## 📊 État actuel

**Migrations appliquées:** 10/17 ✅  
**Migrations manquantes:** 7  
**Éléments à corriger:** 8 colonnes/valeurs

---

## ⚠️ Migrations manquantes détectées

| Table | Colonne/Élément | Migration |
|-------|----------------|-----------|
| `schedules` | `technicien_id` | planning_mvp.sql |
| `quotes` | `converted_to_worksite` (enum) | add_converted_to_worksite_status.sql |
| `quotes` | `created_by_user_id` | add_created_by_to_quotes.sql |
| `schedules` | `worksite_title` | add_planning_fields.sql |
| `schedules` | `period_start` | add_schedules_period_columns.sql |
| `schedules` | `period_end` | add_schedules_period_columns.sql |
| `users` | `skills` | add_skills_column.sql |
| `materials` | `next_maintenance_date` | enhance_materials_management.sql |

---

## 🚀 Procédure d'application (5 minutes)

### Étape 1: Créer un backup (CRITIQUE)

1. Allez sur https://app.supabase.com
2. Sélectionnez votre projet
3. Allez dans **Settings** → **Database** → **Backups**
4. Cliquez sur **"Create backup"** (ou notez la dernière sauvegarde automatique)

⚠️ **Ne passez PAS à l'étape suivante sans backup !**

### Étape 2: Ouvrir SQL Editor

1. Depuis le dashboard Supabase
2. Cliquez sur **SQL Editor** dans le menu de gauche
3. Cliquez sur **"New query"**

### Étape 3: Appliquer le script consolidé

1. Ouvrez le fichier: `APPLY_MISSING_MIGRATIONS.sql`
2. **Copiez TOUT le contenu** du fichier
3. **Collez** dans le SQL Editor de Supabase
4. Cliquez sur **"Run"** (bouton en bas à droite)

### Étape 4: Vérifier les résultats

Le script affichera une table avec toutes les colonnes ajoutées :

```
table_name | column_name            | data_type
-----------|-----------------------|----------
materials  | last_maintenance_date  | date
materials  | maintenance_interval...| integer
materials  | next_maintenance_date  | date
quotes     | created_by_user_id     | uuid
schedules  | period_end             | date
schedules  | period_start           | date
schedules  | technicien_id          | uuid
schedules  | worksite_title         | text
users      | skills                 | text
```

✅ Si vous voyez cette table → Migration réussie !

### Étape 5: Vérifier localement

Dans votre terminal PowerShell :

```powershell
cd backend
python check_migrations_status.py
```

Vous devriez maintenant voir :
```
✅ Migrations appliquées (17/17)
🎉 Toutes les migrations sont appliquées!
```

---

## 🆘 En cas de problème

### Erreur "permission denied"

**Solution:** Utilisez la **clé de service** (service_key) dans vos variables d'environnement, pas la clé anonyme (anon_key).

### Erreur "column already exists"

**Pas de problème !** Le script utilise `IF NOT EXISTS`, donc il ignore les colonnes déjà créées. Continuez.

### Erreur "relation does not exist"

**Problème:** Une table de base n'existe pas.

**Solution:**
1. Vérifiez que vous êtes sur le bon projet Supabase
2. Vérifiez que les tables de base existent : `users`, `schedules`, `quotes`, `materials`

### Restauration du backup

Si quelque chose tourne mal :

1. Supabase → **Settings** → **Database** → **Backups**
2. Sélectionnez le backup d'avant la migration
3. Cliquez sur **"Restore"**

---

## 📝 Que fait le script ?

Le script applique **7 migrations manquantes** de manière sécurisée :

1. ✅ Ajoute `schedules.technicien_id` - Pour assigner des techniciens
2. ✅ Ajoute le statut `CONVERTED_TO_WORKSITE` aux devis
3. ✅ Ajoute `quotes.created_by_user_id` - Pour tracer qui a créé le devis
4. ✅ Ajoute `schedules.worksite_title` - Titre du chantier dans le planning
5. ✅ Ajoute `schedules.period_start/end` - Gestion par périodes
6. ✅ Ajoute `users.skills` - Compétences des collaborateurs
7. ✅ Ajoute `materials.next_maintenance_date` - Maintenance préventive

**Sécurité:**
- Utilise `IF NOT EXISTS` - Aucun risque de doublon
- Pas de suppression de données
- Crée des index pour les performances
- Ajoute des commentaires pour la documentation

---

## ✅ Checklist finale

Après application des migrations :

- [ ] Backup de la base de données créé
- [ ] Script `APPLY_MISSING_MIGRATIONS.sql` exécuté dans Supabase
- [ ] Aucune erreur affichée dans SQL Editor
- [ ] Table de vérification affichée (9 colonnes listées)
- [ ] `check_migrations_status.py` confirme 17/17 migrations
- [ ] Tests de l'application effectués

---

## 🚀 Après les migrations

Une fois les migrations appliquées, vous pouvez :

1. **Tester localement** que tout fonctionne
2. **Passer au déploiement** en suivant [GUIDE_DEPLOIEMENT_RAPIDE.md](GUIDE_DEPLOIEMENT_RAPIDE.md)

---

## 📞 Support

En cas de blocage :
1. Consultez les logs du SQL Editor Supabase
2. Vérifiez que vous utilisez la **service_key** et non l'anon_key
3. Assurez-vous d'être sur le bon projet Supabase

---

**Prêt à appliquer les migrations ?** 

👉 Commencez par l'**Étape 1: Créer un backup** !

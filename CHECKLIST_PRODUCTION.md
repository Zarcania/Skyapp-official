# ✅ Checklist de Mise en Production - Skyapp

**Date de déploiement prévue:** ___________  
**Responsable:** ___________

---

## 🔒 PHASE 1: SÉCURITÉ (CRITIQUE)

### Variables d'environnement
- [ ] Vérifier que `.env` et `.env.local` sont dans `.gitignore`
- [ ] Configurer `ALLOW_DEV_LOGIN=0` sur Render
- [ ] Générer de nouvelles clés Supabase pour la production (différentes du dev)
- [ ] Configurer `SUPABASE_URL` sur Render
- [ ] Configurer `SUPABASE_SERVICE_KEY` sur Render (⚠️ secret)
- [ ] Configurer `SUPABASE_ANON_KEY` sur Render
- [ ] Configurer `FOUNDER_EMAIL` avec l'email du fondateur
- [ ] Configurer `ALLOWED_ORIGINS` avec les domaines exacts (pas de `*`)
  ```
  ALLOWED_ORIGINS=https://votreapp.vercel.app,https://app.votredomaine.com
  ```

### Frontend (Vercel)
- [ ] Configurer `REACT_APP_SUPABASE_URL`
- [ ] Configurer `REACT_APP_SUPABASE_ANON_KEY`
- [ ] Configurer `REACT_APP_BACKEND_URL` (URL Render du backend)
  ```
  REACT_APP_BACKEND_URL=https://skyapp-backend.onrender.com
  ```
- [ ] Vérifier qu'aucune clé secrète n'est exposée côté frontend

### Code
- [ ] Remplacer les `print()` par `logging.info()` ou `logging.error()` dans server_supabase.py
- [ ] Configurer le niveau de logging à `INFO` en production (pas `DEBUG`)
- [ ] Supprimer tous les tokens hardcodés
- [ ] Désactiver les endpoints de dev/debug (si présents)
- [ ] Vérifier que `CORS allow_credentials=True` n'est pas combiné avec `origins=["*"]`

---

## 📊 PHASE 2: BASE DE DONNÉES

### Migrations à appliquer (dans l'ordre)
- [ ] Créer une **copie complète** de la base actuelle
- [ ] Tester toutes les migrations sur la copie
- [ ] Appliquer les migrations sur la base de production:
  - [ ] `2025-11-28_planning_mvp.sql`
  - [ ] `2025-11-28_schedules_end_time.sql`
  - [ ] `2025-11-28_team_leader_collaborators.sql`
  - [ ] `2025-12-25_add_converted_to_worksite_status.sql`
  - [ ] `add_created_by_to_quotes.sql`
  - [ ] `add_is_fondateur_to_users.sql`
  - [ ] `add_missing_datetime_columns.sql`
  - [ ] `add_planning_fields.sql`
  - [ ] `add_schedules_period_columns.sql`
  - [ ] `add_skills_column.sql`
  - [ ] `add_ville_code_postal_to_searches.sql`
  - [ ] `create_company_settings.sql`
  - [ ] `create_licenses_table.sql`
  - [ ] `create_material_checkouts.sql`
  - [ ] `create_mission_reports_table.sql`
  - [ ] `enhance_materials_management.sql`
  - [ ] `fix_team_leaders_user_link.sql`
  - [ ] `remove_all_notnull_constraints.sql`

### Storage Supabase
- [ ] Créer les buckets de storage nécessaires:
  - [ ] `worksite-photos`
  - [ ] `logos`
  - [ ] `documents`
- [ ] Configurer les politiques RLS (Row Level Security)
- [ ] Tester l'upload de fichiers

### Sauvegardes
- [ ] Activer **Point-In-Time Recovery (PITR)** dans Supabase
- [ ] Configurer des sauvegardes automatiques quotidiennes
- [ ] Télécharger un backup manuel avant le déploiement
- [ ] **TESTER** la restauration d'un backup (CRUCIAL)
- [ ] Documenter la procédure de restauration

---

## 🧪 PHASE 3: TESTS

### Tests Backend
- [ ] Exécuter les tests unitaires: `pytest backend/tests/`
- [ ] Tester `/api/health` en local
- [ ] Tester l'authentification (signup/login)
- [ ] Tester la création d'un chantier
- [ ] Tester la génération de devis
- [ ] Tester l'upload de photos
- [ ] Tester la génération de PDF
- [ ] Tester les permissions (ADMIN vs USER vs TECHNICIEN)

### Tests Frontend
- [ ] Tester le build de production: `npm run build`
- [ ] Vérifier qu'il n'y a pas d'erreurs de console
- [ ] Tester sur Chrome, Firefox, Safari
- [ ] Tester sur mobile (responsive)
- [ ] Tester tous les formulaires
- [ ] Tester le drag & drop du planning

### Tests d'intégration
- [ ] Créer un compte fondateur
- [ ] Inviter un utilisateur
- [ ] Créer une entreprise/client
- [ ] Créer un devis complet
- [ ] Convertir le devis en chantier
- [ ] Affecter des techniciens
- [ ] Uploader des photos
- [ ] Générer une facture
- [ ] Tester l'IA (si activée)

---

## 🚀 PHASE 4: DÉPLOIEMENT

### Backend (Render)
- [ ] Créer un nouveau service Web sur Render
- [ ] Connecter le repository GitHub
- [ ] Configurer Root Directory: `backend`
- [ ] Configurer Build Command: `pip install -r requirements.txt`
- [ ] Configurer Start Command: `uvicorn server_supabase:app --host 0.0.0.0 --port $PORT`
- [ ] Sélectionner Python 3.11
- [ ] Ajouter toutes les variables d'environnement (voir Phase 1)
- [ ] Déployer et vérifier les logs
- [ ] Tester `/api/health`: `https://votre-backend.onrender.com/api/health`
- [ ] Noter l'URL publique du backend

### Frontend (Vercel)
- [ ] Importer le repository dans Vercel
- [ ] Configurer Framework: Create React App
- [ ] Configurer Root Directory: `frontend`
- [ ] Configurer Build Command: `npm install && npm run build`
- [ ] Configurer Output Directory: `build`
- [ ] Ajouter les variables d'environnement (voir Phase 1)
- [ ] Déployer
- [ ] Tester l'application
- [ ] Noter l'URL publique

### CORS - Mise à jour finale
- [ ] Mettre à jour `ALLOWED_ORIGINS` sur Render avec l'URL finale Vercel
- [ ] Redéployer le backend
- [ ] Vérifier qu'il n'y a pas d'erreurs CORS dans la console

### Domaines personnalisés (optionnel)
- [ ] Configurer `app.votredomaine.com` vers Vercel (CNAME)
- [ ] Configurer `api.votredomaine.com` vers Render (CNAME)
- [ ] Configurer les certificats SSL (automatique)
- [ ] Mettre à jour `ALLOWED_ORIGINS` si nécessaire

---

## 📈 PHASE 5: MONITORING ET LOGS

### Mise en place du monitoring
- [ ] Créer un compte UptimeRobot ou similaire
- [ ] Configurer un check sur `/api/health` (toutes les 5 min)
- [ ] Configurer des alertes email/SMS en cas de downtime
- [ ] Activer les notifications de build sur Vercel
- [ ] Activer les notifications de déploiement sur Render

### Logs et debugging
- [ ] Vérifier les logs Render (dernier déploiement)
- [ ] Vérifier les logs Vercel
- [ ] Configurer un système de logging centralisé (optionnel: Sentry, LogRocket)
- [ ] Tester l'envoi d'emails (invitations, notifications)

### Performance
- [ ] Activer la compression gzip sur Render
- [ ] Optimiser les images du frontend
- [ ] Configurer le cache des assets statiques
- [ ] Tester la vitesse de chargement (Google PageSpeed)

---

## 📱 PHASE 6: CONFIGURATION DES SERVICES EXTERNES

### OpenAI (Intelligence Artificielle)
- [ ] Créer une clé API OpenAI de production
- [ ] Configurer `OPENAI_API_KEY` sur Render
- [ ] Définir des limites de budget sur OpenAI
- [ ] Tester la génération de descriptions de chantiers

### IOPOLE (Facturation électronique)
- [ ] Vérifier les credentials IOPOLE pour la production
- [ ] Configurer les variables IOPOLE sur Render
- [ ] Tester l'envoi d'une facture test
- [ ] Vérifier la conformité des factures PDF

### Email (SMTP)
- [ ] Configurer le serveur SMTP de production
- [ ] Tester l'envoi d'emails d'invitation
- [ ] Configurer le SPF/DKIM pour éviter les spams
- [ ] Vérifier l'email `Contact@skyapp.fr`

---

## 🔐 PHASE 7: SÉCURITÉ AVANCÉE

### Protection & Limites
- [ ] Implémenter un rate limiting sur les endpoints sensibles
- [ ] Configurer des headers de sécurité (HSTS, CSP, etc.)
- [ ] Vérifier les politiques CORS strictes
- [ ] Activer 2FA pour les comptes administrateurs Render/Vercel/Supabase
- [ ] Configurer des alertes pour les tentatives de connexion suspectes

### Conformité
- [ ] Vérifier la conformité RGPD
- [ ] Ajouter une page Politique de Confidentialité
- [ ] Ajouter une page Conditions Générales d'Utilisation
- [ ] Ajouter un mécanisme de suppression de compte
- [ ] Vérifier la gestion des cookies

---

## 📚 PHASE 8: DOCUMENTATION

### Documentation technique
- [ ] Documenter l'architecture de production
- [ ] Créer un guide de déploiement d'urgence
- [ ] Documenter les procédures de rollback
- [ ] Lister tous les comptes et accès (Render, Vercel, Supabase, etc.)
- [ ] Documenter les procédures de backup/restore

### Documentation utilisateur
- [ ] Créer un guide d'utilisation pour les nouveaux utilisateurs
- [ ] Documenter les rôles et permissions
- [ ] Créer des vidéos tutoriels (optionnel)
- [ ] Préparer une FAQ

---

## 🎯 PHASE 9: LANCEMENT

### Pré-lancement (24h avant)
- [ ] Faire un dernier backup complet
- [ ] Tester tous les parcours utilisateurs critiques
- [ ] Vérifier que tous les services externes fonctionnent
- [ ] Préparer un plan de communication
- [ ] Informer les premiers utilisateurs de la mise en ligne

### Jour J
- [ ] Déployer en production aux heures creuses
- [ ] Monitorer les logs en temps réel pendant 1h
- [ ] Créer le premier compte fondateur en production
- [ ] Tester l'application end-to-end
- [ ] Inviter les premiers beta-testeurs

### Post-lancement (48h)
- [ ] Vérifier les métriques UptimeRobot
- [ ] Analyser les logs d'erreur
- [ ] Collecter les premiers retours utilisateurs
- [ ] Corriger les bugs critiques immédiatement
- [ ] Envoyer un email de suivi aux premiers utilisateurs

---

## 🔄 PHASE 10: MAINTENANCE CONTINUE

### Hebdomadaire
- [ ] Vérifier les logs d'erreur
- [ ] Vérifier les métriques d'uptime
- [ ] Vérifier l'usage des ressources (Render)
- [ ] Vérifier les coûts des services (OpenAI, Supabase, etc.)

### Mensuel
- [ ] Mettre à jour les dépendances (npm audit, pip)
- [ ] Vérifier les backups
- [ ] Analyser les performances
- [ ] Réviser les logs de sécurité

### Procédures d'urgence
- [ ] **Rollback Backend**: Depuis Render, cliquer sur "Rollback" ou redéployer un commit antérieur
- [ ] **Rollback Frontend**: Depuis Vercel, promouvoir une build précédente
- [ ] **Restauration base de données**: Utiliser Point-In-Time Recovery ou restaurer un backup manuel
- [ ] Contact support Supabase: support@supabase.io
- [ ] Contact support Render: support@render.com
- [ ] Contact support Vercel: support@vercel.com

---

## ⚠️ POINTS D'ATTENTION SPÉCIFIQUES SKYAPP

### Identifiés dans le code
1. **Nombreux `print()` dans server_supabase.py** → À remplacer par `logging`
2. **CORS configuré avec `allow_credentials=True` et `allow_origins=["*"]`** → Corriger en production
3. **Mode dev avec `ALLOW_DEV_LOGIN`** → Désactiver absolument en production
4. **Clés Supabase partagées dev/prod** → Créer des instances séparées

### Recommandations supplémentaires
- Utiliser un environnement **staging** identique à la production pour les tests
- Implémenter un système de feature flags pour activer/désactiver des fonctionnalités
- Configurer une page de maintenance pour les déploiements futurs
- Prévoir un plan de scaling si le nombre d'utilisateurs augmente rapidement

---

## 📊 CRITÈRES DE SUCCÈS

Le déploiement est considéré comme réussi si:
- ✅ `/api/health` retourne `{"status": "OK"}`
- ✅ Aucune erreur CORS dans la console browser
- ✅ L'authentification fonctionne (signup/login)
- ✅ Un chantier peut être créé de bout en bout
- ✅ Les photos s'uploadent correctement
- ✅ Les PDF se génèrent sans erreur
- ✅ L'uptime est > 99.5% sur 24h
- ✅ Aucune erreur 500 ou critique dans les logs

---

**Date de déploiement réel:** ___________  
**Notes:** ___________________________________________

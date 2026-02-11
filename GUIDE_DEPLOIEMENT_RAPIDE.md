# 🚀 Guide de Déploiement Production - Skyapp

## TL;DR - Actions Critiques AVANT le Déploiement

### ⚠️ STOP - Ne déployez PAS avant d'avoir fait ceci:

1. **Exécutez le script de vérification:**
   ```powershell
   .\scripts\pre_deploy_check.ps1
   ```

2. **Corrigez ces problèmes critiques dans le code:**
   - ❌ Nombreux `print()` dans [server_supabase.py](backend/server_supabase.py#L13) → Remplacer par `logging`
   - ❌ CORS avec `allow_origins=["*"]` + `allow_credentials=True` → Configurer les domaines exacts
   - ❌ `ALLOW_DEV_LOGIN` → DOIT être `0` en production

3. **Créez de nouvelles clés Supabase pour la production** (différentes du dev)

4. **Testez les migrations sur une copie de la base**

---

## 📋 Procédure de Déploiement (30 min)

### Étape 1: Préparation (5 min)
```powershell
# 1. Vérifier le code
.\scripts\pre_deploy_check.ps1

# 2. Créer un backup manuel de Supabase
# → Aller sur https://app.supabase.com/project/_/settings/storage

# 3. Tester les migrations localement
# (Voir CHECKLIST_PRODUCTION.md Phase 2)
```

### Étape 2: Backend sur Render (10 min)
1. Aller sur https://render.com → New Web Service
2. Connecter votre repository GitHub
3. Configurer:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server_supabase:app --host 0.0.0.0 --port $PORT`
   - **Python Version:** 3.11

4. Ajouter les variables d'environnement:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_KEY=eyJxxx... (⚠️ SECRET)
   SUPABASE_ANON_KEY=eyJxxx...
   FOUNDER_EMAIL=contact@skyapp.fr
   ALLOW_DEV_LOGIN=0
   ALLOWED_ORIGINS=https://votreapp.vercel.app
   ```

5. Déployer → Noter l'URL: `https://skyapp-backend-xxxx.onrender.com`

6. Tester: `https://skyapp-backend-xxxx.onrender.com/api/health`

### Étape 3: Frontend sur Vercel (10 min)
1. Aller sur https://vercel.com → New Project
2. Importer votre repository GitHub
3. Configurer:
   - **Framework:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Output Directory:** `build`

4. Ajouter les variables d'environnement:
   ```
   REACT_APP_SUPABASE_URL=https://xxxxx.supabase.co
   REACT_APP_SUPABASE_ANON_KEY=eyJxxx...
   REACT_APP_BACKEND_URL=https://skyapp-backend-xxxx.onrender.com
   ```

5. Déployer → Noter l'URL: `https://skyapp-xxxx.vercel.app`

### Étape 4: Finalisation CORS (5 min)
1. Retourner sur Render
2. Mettre à jour `ALLOWED_ORIGINS` avec l'URL Vercel finale:
   ```
   ALLOWED_ORIGINS=https://skyapp-xxxx.vercel.app
   ```
3. Redéployer le backend (bouton "Manual Deploy")

4. Tester l'application complète:
   - Ouvrir `https://skyapp-xxxx.vercel.app`
   - Créer un compte
   - Tester la création d'un chantier

---

## 🔧 Corrections de Code Recommandées

### 1. Remplacer les print() par logging

**Fichier:** [backend/server_supabase.py](backend/server_supabase.py#L13)

Remplacer toutes les occurrences de `print()` par:
```python
# Au lieu de:
print(f"🔑 get_user_from_token appelé - credentials présents: {credentials is not None}")

# Utiliser:
logger.info(f"🔑 get_user_from_token appelé - credentials présents: {credentials is not None}")
```

### 2. Sécuriser la configuration CORS

**Fichier:** [backend/server_supabase.py](backend/server_supabase.py#L8115-L8127)

Le code actuel permet `allow_origins=["*"]` avec `allow_credentials=True`, ce qui est dangereux.

**Solution:** S'assurer que `ALLOWED_ORIGINS` est TOUJOURS configuré en production (jamais vide).

### 3. Désactiver le mode dev

**Fichier:** [render.yaml](render.yaml#L15)

```yaml
- key: ALLOW_DEV_LOGIN
  value: "0"  # ✅ DOIT être 0 en production
```

---

## 📊 Monitoring Post-Déploiement

### Jour 1 - Les premières heures
```powershell
# Surveiller les logs Render en temps réel
# Aller sur: https://dashboard.render.com/web/srv-xxx/logs

# Vérifier l'uptime
curl https://skyapp-backend-xxxx.onrender.com/api/health

# Vérifier la console browser (F12) pour les erreurs CORS
```

### Configurer UptimeRobot (gratuit)
1. Créer un compte sur https://uptimerobot.com
2. Ajouter un monitor HTTP(S):
   - URL: `https://skyapp-backend-xxxx.onrender.com/api/health`
   - Interval: 5 minutes
3. Configurer les alertes par email

---

## 🆘 Procédures d'Urgence

### Le backend ne répond plus
1. Vérifier les logs Render: https://dashboard.render.com/web/srv-xxx/logs
2. Vérifier l'état Supabase: https://status.supabase.com
3. **Rollback:** Render Dashboard → "Rollback" vers le déploiement précédent

### Erreurs CORS dans la console
```
Access to fetch at 'https://backend.com/api/...' from origin 'https://frontend.com' 
has been blocked by CORS policy
```

**Solution:**
1. Aller sur Render → Environment → `ALLOWED_ORIGINS`
2. Ajouter l'URL frontend exacte (avec https://)
3. Redéployer

### La base de données est corrompue
1. **Ne pas paniquer** 🧘
2. Aller sur Supabase → Settings → Database → Point in Time Recovery
3. Ou restaurer le backup manuel créé avant le déploiement

### Le frontend affiche une page blanche
1. Ouvrir la console (F12) → Regarder les erreurs
2. Vérifier que `REACT_APP_BACKEND_URL` est correct sur Vercel
3. Vérifier que les variables d'environnement Supabase sont correctes
4. **Rollback:** Vercel Dashboard → Deployments → Cliquer sur un déploiement précédent → "Promote to Production"

---

## 📚 Ressources

- **Checklist complète:** [CHECKLIST_PRODUCTION.md](CHECKLIST_PRODUCTION.md)
- **Guide Render:** https://render.com/docs
- **Guide Vercel:** https://vercel.com/docs
- **Guide Supabase:** https://supabase.com/docs
- **Documentation Skyapp:** [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

---

## ✅ Checklist Rapide (5 min avant de déployer)

- [ ] Script de vérification exécuté sans erreur
- [ ] Backup Supabase créé
- [ ] Nouvelles clés Supabase production créées
- [ ] Variables d'environnement préparées (dans un fichier texte sécurisé)
- [ ] `ALLOW_DEV_LOGIN=0` confirmé
- [ ] `ALLOWED_ORIGINS` avec domaines exacts (pas de `*`)
- [ ] Tests backend passés localement
- [ ] Build frontend réussi localement
- [ ] Équipe avertie du déploiement

---

## 💡 Conseils d'Expert

1. **Déployez pendant les heures creuses** (tôt le matin ou tard le soir)
2. **Testez sur un environnement staging** d'abord si possible
3. **Gardez la console ouverte** pendant les 30 premières minutes
4. **Invitez des beta-testeurs** avant l'ouverture publique
5. **Documentez les problèmes** rencontrés pour la prochaine fois
6. **Ne déployez jamais un vendredi soir** 😅

---

## 🎯 Critères de Succès

Le déploiement est réussi si:
- ✅ `/api/health` retourne 200 OK
- ✅ Vous pouvez créer un compte
- ✅ Vous pouvez créer un chantier
- ✅ Les photos s'uploadent
- ✅ Aucune erreur dans les logs (30 min)
- ✅ Aucune erreur CORS dans la console browser

---

**Prêt à déployer? Courage! 🚀**

*En cas de problème, respirez profondément, consultez les logs, et n'hésitez pas à rollback.*

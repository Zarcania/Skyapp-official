# 🏗️ SkyApp - Plateforme SaaS de Gestion BTP

**SkyApp** est une solution complète de gestion d'équipes pour les entreprises du BTP, artisans et agences. Une plateforme moderne qui centralise la gestion des techniciens, plannings, projets, clients et rapports.

## 🎯 Aperçu de l'Application

![SkyApp Landing](https://smart-inventory-97.preview.emergentagent.com)

### Fonctionnalités Principales

- 🏢 **Multi-entreprise** : Chaque société a son espace isolé
- 👥 **Gestion d'équipe** : Roles Bureau (manager) et Technicien
- 📋 **Planification intelligente** : Assignation de missions aux techniciens
- 📊 **Rapports automatisés** : Suivi des interventions
- 🎨 **Interface moderne** : Design responsive avec dark/light modes
- 🔐 **Sécurité avancée** : JWT, permissions par rôle

## 🚀 Démo Live

**URL**: https://smart-inventory-97.preview.emergentagent.com

### Comptes de Démonstration

**Manager/Bureau:**
- Email: `admin@btp-exemple.fr`
- Mot de passe: `admin123`

**Technicien:**
- Email: `tech@btp-exemple.fr`
- Mot de passe: `tech123`

## 📱 Captures d'Écran

### Landing Page Professionnelle
- Hero section avec call-to-action
- Sections Features, Testimonials, Pricing
- Design responsive mobile/tablet/desktop

### Dashboard Bureau (Manager)
- Vue d'ensemble : Utilisateurs, Clients, Projets, Plannings
- Gestion complète des clients et projets
- Création et assignation de plannings
- Gestion d'équipe (ajout techniciens)

### Dashboard Technicien
- Vue simplifiée : Mes Plannings, Mes Rapports
- Mise à jour du statut des missions
- Création de rapports d'intervention

## 🛠️ Stack Technique

### Backend
- **FastAPI** : API REST moderne et performante
- **MongoDB** : Base de données NoSQL
- **JWT** : Authentification sécurisée
- **Pydantic** : Validation des données

### Frontend
- **React 19** : Interface utilisateur moderne
- **shadcn/ui** : Composants UI professionnels
- **Tailwind CSS** : Design system flexible
- **React Router** : Navigation SPA

### Infrastructure
- **Docker** : Containerisation
- **Kubernetes** : Orchestration
- **Supervisor** : Gestion des processus

## 📁 Structure du Projet

```
/app/
├── backend/                 # API FastAPI
│   ├── server.py           # Application principale
│   ├── requirements.txt    # Dépendances Python
│   └── .env               # Variables d'environnement
├── frontend/               # Application React
│   ├── src/
│   │   ├── App.js         # Composant principal
│   │   ├── App.css        # Styles globaux
│   │   └── components/ui/ # Composants shadcn/ui
│   ├── package.json       # Dépendances Node.js
│   └── .env              # Variables d'environnement
└── README.md             # Cette documentation
```

## 🚀 Installation & Démarrage

### Prérequis
- Node.js 18+
- Python 3.11+
- MongoDB

### Installation
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
yarn install
```

### Démarrage
```bash
# Backend (port 8001)
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Frontend (port 3000)
cd frontend
yarn start
```

### Initialisation des Données
Accédez à la page de connexion et cliquez sur "Initialiser données d'exemple" pour créer les comptes de test.

## 📊 Modèle de Données

### Entités Principales

- **Company** : Entreprise (multi-tenant)
- **User** : Utilisateur (roles: ADMIN, BUREAU, TECHNICIEN)
- **Client** : Client de l'entreprise
- **Project** : Projet lié à un client
- **Planning** : Mission assignée à un technicien
- **Report** : Rapport d'intervention du technicien

### Relations
- Une **Company** a plusieurs **Users**, **Clients**, **Projects**
- Un **Project** appartient à un **Client**
- Un **Planning** relie un **Project**, un **Technicien** et un **Client**
- Un **Report** est créé par un **Technicien**

## 🔐 Système d'Authentification

### Rôles & Permissions

**BUREAU (Manager/Chef de projet):**
- ✅ Gestion complète des clients et projets
- ✅ Création et assignation des plannings
- ✅ Gestion d'équipe (ajout techniciens)
- ✅ Vue sur tous les rapports

**TECHNICIEN:**
- ✅ Vue des plannings assignés
- ✅ Mise à jour du statut des missions
- ✅ Création de rapports d'intervention
- ❌ Pas d'accès aux clients/gestion d'équipe

## 🌟 Parcours Utilisateur

### Workflow Bureau
1. **Inscription** → Création automatique de l'entreprise
2. **Ajout de clients** → Informations complètes
3. **Création de projets** → Liés aux clients
4. **Ajout de techniciens** → Membres d'équipe
5. **Planification** → Assignation de missions
6. **Suivi** → Vue d'ensemble des rapports

### Workflow Technicien
1. **Connexion** → Dashboard simplifié
2. **Mes Plannings** → Missions assignées
3. **Démarrer mission** → Mise à jour du statut
4. **Terminer mission** → Finalisation
5. **Créer rapport** → Documentation détaillée

## 🎨 Design System

### Couleurs Principales
- **Primaire** : Bleu (#2563eb)
- **Secondaire** : Gris (#6b7280)
- **Succès** : Vert (#10b981)
- **Attention** : Orange (#f59e0b)

### Composants UI
- Cards avec hover effects
- Boutons avec micro-animations
- Formulaires avec validation
- Navigation adaptative
- États de chargement

## 📱 Responsive Design

- **Mobile** : < 768px - Menu hamburger, layout adapté
- **Tablet** : 768px - 1024px - Layout optimisé
- **Desktop** : > 1024px - Interface complète

## 🔧 API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/auth/me` - Profil utilisateur

### Gestion des Données
- `GET|POST /api/clients` - Clients
- `GET|POST /api/projects` - Projets
- `GET|POST /api/users` - Équipe
- `GET|POST /api/plannings` - Plannings
- `GET|POST /api/reports` - Rapports

### Statistiques
- `GET /api/dashboard/stats` - Statistiques dashboard

## 🚀 Déploiement

L'application est actuellement déployée sur Kubernetes avec :
- **Frontend** : Serveur de développement React
- **Backend** : Serveur FastAPI avec Uvicorn
- **Base de données** : MongoDB local
- **Load balancer** : Ingress Kubernetes

## 🔮 Fonctionnalités Futures

- 📧 **Notifications email** automatiques
- 📱 **Application mobile** React Native
- 📊 **Analytics avancés** avec graphiques
- 🔗 **Intégrations** (calendriers, ERP)
- 💳 **Paiements Stripe** pour abonnements
- 🤖 **Assistant IA** pour aide à la planification

## 🤝 Contribution

SkyApp est un projet de démonstration. Pour contribuer :

1. Fork le projet
2. Créer une branche feature
3. Commit vos changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou support :
- 📧 Email : support@skyapp.demo
- 🌐 Site web : https://skyapp.demo
- 📱 Téléphone : +33 1 23 45 67 89

---

**SkyApp** - *Gérez vos équipes BTP comme un pro* 🏗️✨

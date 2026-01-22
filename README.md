# Hub Chantier

**Application de gestion de chantiers BTP pour Greg Construction**

> 20 employés | 4,3M€ CA | Solution tout-en-un pour la gestion terrain

## Vue d'ensemble

Hub Chantier est une application web/mobile permettant de :
- Gérer les employés et leurs affectations
- Suivre les pointages (entrées/sorties) sur chantier
- Planifier les équipes et les interventions
- Gérer les documents de chantier
- Remplir des formulaires terrain (rapports, incidents)

## Architecture

Ce projet suit **strictement** les principes de **Clean Architecture** (Uncle Bob).

```
┌─────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE                          │
│  (FastAPI, SQLAlchemy, JWT, External Services)              │
│    ┌─────────────────────────────────────────────────────┐  │
│    │                    ADAPTERS                          │  │
│    │  (Controllers, Presenters, Providers)               │  │
│    │    ┌─────────────────────────────────────────────┐  │  │
│    │    │               APPLICATION                    │  │  │
│    │    │  (Use Cases, DTOs, Ports)                   │  │  │
│    │    │    ┌─────────────────────────────────────┐  │  │  │
│    │    │    │             DOMAIN                   │  │  │  │
│    │    │    │  (Entities, Value Objects,          │  │  │  │
│    │    │    │   Repositories, Events, Services)   │  │  │  │
│    │    │    └─────────────────────────────────────┘  │  │  │
│    │    └─────────────────────────────────────────────┘  │  │
│    └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Règle de dépendance** : Les dépendances pointent TOUJOURS vers l'intérieur.

## Stack technique

### Backend
- **Framework** : FastAPI 0.109+
- **Database** : SQLite (production locale)
- **ORM** : SQLAlchemy 2.0+
- **Auth** : JWT (python-jose)
- **Validation** : Pydantic 2.5+
- **Tests** : pytest + pytest-cov

### Frontend
- **Framework** : React 19
- **Build** : Vite 5
- **Styling** : Tailwind CSS 3
- **Language** : TypeScript 5

## Structure du projet

```
Hub-Chantier/
├── backend/
│   ├── modules/           # Modules métier
│   │   ├── auth/          # Authentification (module référence)
│   │   ├── employes/      # Gestion des employés
│   │   ├── pointages/     # Pointages entrée/sortie
│   │   ├── chantiers/     # Gestion des chantiers
│   │   ├── planning/      # Planning des équipes
│   │   ├── documents/     # Documents de chantier
│   │   └── formulaires/   # Formulaires terrain
│   ├── shared/            # Code partagé
│   │   ├── domain/        # Entités partagées
│   │   ├── infrastructure/# Infra commune (EventBus, etc.)
│   │   └── kernel/        # Utilitaires de base
│   ├── tests/
│   │   ├── unit/          # Tests unitaires
│   │   └── integration/   # Tests d'intégration
│   └── main.py            # Point d'entrée FastAPI
├── frontend/
│   ├── src/
│   │   ├── components/    # Composants React
│   │   ├── pages/         # Pages de l'application
│   │   ├── hooks/         # Hooks personnalisés
│   │   ├── services/      # Services API
│   │   ├── types/         # Types TypeScript
│   │   ├── utils/         # Utilitaires
│   │   └── contexts/      # Contextes React
│   └── public/            # Assets statiques
├── docs/
│   └── architecture/      # Documentation architecture
│       ├── CLEAN_ARCHITECTURE.md
│       └── ADR/           # Architecture Decision Records
├── scripts/               # Scripts utilitaires
├── README.md              # Ce fichier
├── CLAUDE.md              # Etat du projet pour Claude
└── CONTRIBUTING.md        # Guide de contribution
```

## Modules

| Module | Status | Description |
|--------|--------|-------------|
| auth | **Complet** | Authentification JWT, gestion des roles |
| chantiers | Structure | Gestion des chantiers |
| planning | Structure | Planning des equipes |
| planning_charge | Structure | Vision capacitaire |
| feuilles_heures | Structure | Saisie temps de travail |
| formulaires | Structure | Formulaires terrain |
| documents | Structure | Gestion documentaire |
| memos | Structure | Communication urgence |
| logistique | Structure | Reservation materiel |
| interventions | Structure | SAV et maintenance |
| taches | Structure | Gestion des travaux |

> Voir `CLAUDE.md` pour l'etat detaille et les prochaines taches.

## Démarrage rapide

### Prérequis
- Python 3.11+
- Node.js 20+
- npm ou yarn

### Installation

```bash
# Cloner le projet
git clone <repo-url>
cd Hub-Chantier

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Lancement

```bash
# Terminal 1 - Backend
./scripts/start-dev.sh
# ou manuellement:
# cd backend && uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Tests

```bash
# Tests unitaires
pytest backend/tests/unit -v

# Tests d'intégration
pytest backend/tests/integration -v

# Coverage
pytest --cov=backend --cov-report=html
```

## Commandes utiles

```bash
# Vérifier l'architecture (aucune violation)
./scripts/check-architecture.sh

# Générer un nouveau module
./scripts/generate-module.sh nom_module

# Lancer tout l'environnement de dev
./scripts/start-dev.sh
```

## Documentation

| Fichier | Description |
|---------|-------------|
| [CLAUDE.md](./CLAUDE.md) | Etat du projet, prochaines taches |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Guide de contribution, conventions |
| [SPECIFICATIONS.md](./docs/SPECIFICATIONS.md) | Cahier des charges fonctionnel |
| [Clean Architecture](./docs/architecture/CLEAN_ARCHITECTURE.md) | Guide d'architecture |
| [ADRs](./docs/architecture/ADR/) | Decisions d'architecture |

## Licence

Propriétaire - Greg Construction © 2026

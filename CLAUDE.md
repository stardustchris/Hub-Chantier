# Hub Chantier - Contexte pour Claude

> Ce fichier est lu par Claude au debut de chaque session.
> Il permet de reprendre le travail la ou on s'est arrete.

## Projet

- **Client** : Greg Construction (20 employes, 4,3M EUR CA)
- **Type** : Application SaaS de gestion de chantiers BTP
- **Initie le** : 21 janvier 2026

## Documentation

| Fichier | Description |
|---------|-------------|
| `docs/SPECIFICATIONS.md` | Cahier des charges fonctionnel (177 fonctionnalites) |
| `docs/CDC Greg Constructions v2.1.docx` | CDC original client |
| `CONTRIBUTING.md` | Conventions, workflow, checklist |
| `docs/architecture/CLEAN_ARCHITECTURE.md` | Architecture detaillee |
| `docs/architecture/ADR/` | Decisions d'architecture |

## Architecture (resume)

Clean Architecture 4 layers : `Domain → Application → Adapters → Infrastructure`

**Regle d'or** : Les dependances pointent TOUJOURS vers l'interieur.

### Regles critiques

1. **Domain layer = PURE** - Aucune dependance technique (pas de FastAPI, SQLAlchemy, Pydantic)
2. **Use cases dependent d'interfaces** - Jamais d'implementations directes
3. **Communication inter-modules via EventBus** - Pas d'import direct entre modules
4. **Module `auth` = reference** - Toujours s'en inspirer

> Details complets : `CONTRIBUTING.md`

## Etat des modules

| Module | CDC Section | Fonctionnalites | Status |
|--------|-------------|-----------------|--------|
| auth (utilisateurs) | 3 | USR-01 a USR-13 | **COMPLET** |
| dashboard | 2 | FEED-01 a FEED-20 | Structure only |
| chantiers | 4 | CHT-01 a CHT-20 | Structure only |
| planning | 5 | PLN-01 a PLN-28 | Structure only |
| planning_charge | 6 | PDC-01 a PDC-17 | Structure only |
| feuilles_heures | 7 | FDH-01 a FDH-20 | Structure only |
| formulaires | 8 | FOR-01 a FOR-11 | Structure only |
| documents | 9 | GED-01 a GED-15 | Structure only |
| memos | 10 | MEM-01 a MEM-13 | Structure only |
| logistique | 11 | LOG-01 a LOG-18 | Structure only |
| interventions | 12 | INT-01 a INT-17 | Structure only |
| taches | 13 | TAC-01 a TAC-20 | Structure only |

### Detail module auth (USR-01 a USR-13)

Le module auth est maintenant complet selon le CDC Section 3 :

- **4 roles** : Admin, Conducteur, Chef de Chantier, Compagnon
- **2 types** : Employe, Sous-traitant
- **16 couleurs** : Palette complete pour identification visuelle
- **Champs complets** : photo, couleur, telephone, metier, code, contact urgence
- **Use cases** : Login, Register, UpdateUser, DeactivateUser, ActivateUser, ListUsers
- **Tests unitaires** : test_login.py, test_register.py

Note : USR-02 (Invitation SMS) retire du scope.

## Prochaines taches prioritaires

1. [ ] **Module chantiers** (CDC Section 4) - CRUD chantiers avec statuts et GPS
2. [ ] **Module planning** (CDC Section 5) - Affectations utilisateurs aux chantiers
3. [ ] **Module feuilles_heures** (CDC Section 7) - Saisie et validation des heures
4. [ ] **Module taches** (CDC Section 13) - Gestion des travaux par chantier
5. [ ] Connecter le frontend au backend

## Historique des sessions

### Session 2026-01-22 (suite)
- Completion du module auth selon CDC Section 3 (USR-01 a USR-13)
- Retrait USR-02 (Invitation SMS) du scope
- Ajout 4 roles : Admin, Conducteur, Chef de Chantier, Compagnon
- Ajout TypeUtilisateur : Employe, Sous-traitant
- Ajout Couleur (16 couleurs palette CDC)
- Ajout champs User : photo, couleur, telephone, metier, code, contact urgence
- Nouveaux use cases : UpdateUser, DeactivateUser, ActivateUser, ListUsers
- Nouveaux endpoints : /users (CRUD complet)
- Tests unitaires : test_register.py

### Session 2026-01-22
- Import du CDC Greg Constructions v2.1
- Creation de `docs/SPECIFICATIONS.md` (177 fonctionnalites)
- Reorganisation : Tableau de Bord en section 2
- Fusion CONTEXT.md dans CLAUDE.md
- Creation CONTRIBUTING.md

### Session 2026-01-21 (init)
- Initialisation structure Clean Architecture
- Module auth complet (reference)
- Documentation (README, ADRs)
- Configuration backend (FastAPI, SQLAlchemy, pytest)
- Configuration frontend (React 19, Vite, Tailwind)
- Configuration agents (.claude/agents/)

## Commandes utiles

```bash
# Dev
./scripts/start-dev.sh

# Tests
pytest backend/tests/unit -v
pytest --cov=backend --cov-report=html

# Verification architecture
./scripts/check-architecture.sh

# Nouveau module
./scripts/generate-module.sh nom_module
```

## En cas de doute

1. Consulter `modules/auth/` comme module de reference
2. Lire `docs/SPECIFICATIONS.md` pour les specs fonctionnelles
3. Lire `CONTRIBUTING.md` pour les conventions
4. Lancer `./scripts/check-architecture.sh`

## Blocages / Questions en suspens

(Aucun pour l'instant)

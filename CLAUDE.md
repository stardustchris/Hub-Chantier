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
| `.claude/agents.md` | Regles d'utilisation des sous-agents |

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
| dashboard | 2 | FEED-01 a FEED-20 | **COMPLET** |
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

### Detail module dashboard (FEED-01 a FEED-20)

Le module dashboard est maintenant complet selon le CDC Section 2 :

- **Entites** : Post, Comment, Like, PostMedia
- **Value Objects** : PostTargeting (everyone, specific_chantiers, specific_people), PostStatus
- **Use cases** : PublishPost, GetFeed, GetPost, DeletePost, PinPost, AddComment, AddLike, RemoveLike
- **Fonctionnalites implementees** :
  - FEED-01: Publication de messages texte
  - FEED-02: Ajout de photos (max 5 par post)
  - FEED-03: Ciblage des destinataires (Tous, Chantiers, Personnes)
  - FEED-04: Reactions likes
  - FEED-05: Commentaires sur posts
  - FEED-08: Messages urgents epingles (48h max)
  - FEED-09: Filtrage automatique par chantier
  - FEED-16: Moderation (suppression posts)
  - FEED-18: Pagination infinite scroll
  - FEED-20: Archivage apres 7 jours
- **Endpoints** : GET /feed, POST /posts, GET /posts/{id}, DELETE /posts/{id}, POST /posts/{id}/pin, POST /posts/{id}/comments, POST /posts/{id}/like
- **Tests unitaires** : test_publish_post.py, test_get_feed.py, test_add_like.py, test_add_comment.py

Note : FEED-14 (Mentions @) et FEED-15 (Hashtags) marques "future" dans CDC.

## Prochaines taches prioritaires

1. [ ] **Module dashboard** (CDC Section 2) - Tableau de bord avec feed d'activite et widgets
2. [ ] **Module chantiers** (CDC Section 4) - CRUD chantiers avec statuts et GPS
3. [ ] **Module planning** (CDC Section 5) - Affectations utilisateurs aux chantiers
4. [ ] **Module feuilles_heures** (CDC Section 7) - Saisie et validation des heures
5. [ ] **Module taches** (CDC Section 13) - Gestion des travaux par chantier
6. [ ] Connecter le frontend au backend

## Workflow de developpement

**Regles d'utilisation des sous-agents** : `.claude/agents.md`

Quand une fonctionnalite est demandee (ex: "Implemente CHT-03"):
1. Lire `docs/SPECIFICATIONS.md` pour les details
2. `python-pro` implemente selon Clean Architecture
3. `architect-reviewer` verifie la conformite
4. `test-automator` genere les tests pytest
5. `code-reviewer` verifie qualite et securite
6. Mettre a jour SPECIFICATIONS.md:
   - Modifier le contenu si l'implementation differe de la spec initiale
   - Ajouter la feature si nouvelle (hors CDC)
   - Passer le statut a ✅
7. Mettre a jour ce fichier (CLAUDE.md)

> **SPECIFICATIONS.md = source de verite vivante** - elle reflète toujours l'implementation reelle

## Historique des sessions

### Session 2026-01-22 (dashboard)
- Implementation complete du module dashboard selon CDC Section 2 (FEED-01 a FEED-20)
- Couche Domain : entites Post, Comment, Like, PostMedia + value objects PostTargeting, PostStatus
- Couche Application : 8 use cases (PublishPost, GetFeed, GetPost, DeletePost, PinPost, AddComment, AddLike, RemoveLike)
- Couche Infrastructure : models SQLAlchemy, 4 repositories
- Routes FastAPI : /api/dashboard/* (feed, posts, comments, likes)
- Tests unitaires : 4 fichiers de tests
- Integration dans main.py et database.py

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
- Mise a jour .claude/agents.md avec workflow detaille et triggers automatiques
- Liaison SPECIFICATIONS.md, agents.md, CLAUDE.md

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
4. Lire `.claude/agents.md` pour le workflow agents
5. Lancer `./scripts/check-architecture.sh`

## Blocages / Questions en suspens

(Aucun pour l'instant)

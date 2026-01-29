# Changelog - Hub Chantier

Toutes les modifications notables du projet Hub Chantier sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Changed - 2026-01-28

#### Fusion module `planning_charge` dans `planning` - Clean Architecture

**Contexte**: Le module `planning_charge` créait 15+ violations Clean Architecture en important directement depuis `planning`. Pour respecter la règle de dépendance et améliorer la maintenabilité, les deux modules ont été fusionnés.

**Changements**:
- ✅ **Module `planning_charge` fusionné dans `planning`** sous forme de sous-module `planning.charge`
- ✅ **43 fichiers déplacés** de `modules/planning_charge/` vers `modules/planning/`
- ✅ **224+ imports mis à jour** dans tout le codebase
- ✅ **Organisation en sous-répertoires** pour maintenir la clarté
- ✅ **0 violations Clean Architecture** (réduction de 100% depuis 32 violations)

**Détails techniques**:
- Structure réorganisée en sous-dossiers:
  - `planning/domain/entities/besoin_charge.py`
  - `planning/domain/value_objects/charge/` (Semaine, TypeMetier, etc.)
  - `planning/application/use_cases/charge/`
  - `planning/application/dtos/charge/`
  - `planning/adapters/controllers/charge/`
  - `planning/infrastructure/persistence/besoin_charge_model.py`
  - `planning/infrastructure/web/charge_routes.py`
- Router combiné: `planning/infrastructure/web/__init__.py` combine affectations + charge
- Exports mis à jour dans tous les `__init__.py` concernés

**Tests**:
- ✅ **186/186 tests unitaires passent** (100%)
- ✅ **Architect review: 87/100** (objectif 75+ dépassé)
- ✅ **Module import vérifié**: 17 routes API enregistrées

**Corrections liées**:
- Fix imports `EntityInfoServiceImpl` → `SQLAlchemyEntityInfoService` (notifications)
- Fix imports cross-module dans tests d'intégration
- Fix TYPE_CHECKING annotations avec string literals (chantier_routes.py)

**Impact**:
- Meilleure conformité Clean Architecture
- Réduction de la complexité (2 modules → 1)
- Elimination du couplage circulaire planning ↔ planning_charge
- Base plus solide pour évolutions futures

**Commits**:
- `8dd696d` - refactor(p1): merge planning_charge into planning module
- `eaac4d9` - fix(planning): repair imports after planning_charge fusion
- `3947ddf` - fix(infra): repair imports after fusion - EntityInfoServiceImpl

**Documentation**: Cette fusion fait partie de la Phase 2.5 P1 (Clean Architecture refactoring)

---

## Session 2026-01-28 - API Publique v1 Authentication

### Added

#### API Publique v1 avec authentification par clés API

**Fonctionnalités**:
- Génération de clés API sécurisées (format `hbc_xxx`, hash SHA256)
- CRUD complet clés API (/api/auth/api-keys)
- Middleware authentification unifié (JWT OU API Key)
- Rate limiting par clé (configurable)
- Scopes d'autorisation (lecture, écriture)
- Expiration automatique des clés
- Frontend complet gestion clés (page dédiée + modal création)

**Architecture**:
- Migration Alembic: table `api_keys` avec indexes optimisés
- Domain: Entity `ApiKey` pure avec logique métier
- Application: 3 use cases (Create, List, Revoke)
- Infrastructure: Repository SQLAlchemy + routes FastAPI
- Shared: Middleware auth unifié JWT/API Key

**Tests**:
- 38 tests backend (100% pass)
- 6 tests frontend (100% pass)
- Coverage: Domain 100%, Application 95%, Infrastructure 90%

**Sécurité**:
- Hash SHA256 (secret jamais stocké en clair)
- Rate limiting par clé
- Révocation instantanée
- Expiration automatique
- Validation stricte des scopes

**Documentation**:
- Swagger UI mis à jour avec exemples API Key
- Guide d'utilisation dans SPECIFICATIONS.md
- Architecture documentée dans history.md

---

## Session 2026-01-27 - Préparation Production

### Changed

#### Refactoring Frontend TypeScript - 152 → 0 erreurs

- Elimination de 152 erreurs TypeScript (mode strict activé)
- Création de 10 factories réutilisables (`/frontend/src/fixtures/`)
- 40+ fichiers tests corrigés avec fixtures partagées
- Types primitifs, enums, imports corrigés
- Merge main: 29 conflits résolus
- Build: 0 erreurs, compilation 12.76s

#### Tests Fonctionnels Complets - Pre-Pilote Validé

- 5036 tests passés / 5043 total (99.9%)
- 13 modules validés (100%)
- Sécurité: 10/10
- Performance: -30% vs cibles
- Verdict: **Application pré-pilote validée**

#### Audit Backend Complet

- Score global: 8.7/10
- Corrections P1 (Critique): SQL Injection, CSRF renforcé
- Corrections P2 (Important): Audit Trail RGPD, Docstrings, Type hints
- 522/522 tests modules modifiés, 2160/2163 tests unitaires globaux

### Added

#### Infrastructure Déploiement Scaleway

- Stack production: PostgreSQL 16, FastAPI, Nginx SSL (Let's Encrypt)
- Fichiers: docker-compose.prod.yml, nginx.prod.conf, Dockerfile.prod
- Scripts: deploy.sh, init-server.sh
- Documentation: DEPLOYMENT.md complet
- Sécurité: HSTS, CSP strict, firewall UFW
- PWA installable: icônes générées, manifest configuré

#### Module Logistique UX + RGPD

- Planning Logistique: affichage noms complets utilisateurs
- Vue "Toutes les ressources": affichage empilé multi-ressources
- Sélecteur ressources: dropdown avec format [CODE] Nom
- RGPD: endpoints GET/POST /api/auth/consents + bannière fonctionnelle
- Enrichissement DTOs: helpers dto_enrichment.py

### Fixed

- 91 tests frontend corrigés (MemoryRouter, mocks, assertions)
- Icônes PWA générées pour installation mobile
- Pointage clock-in/out persiste côté serveur
- Mock posts supprimés du feed

---

## Session 2026-01-27 - Enrichissement Fonctionnel

### Added

#### Météo Réelle

- API Open-Meteo avec géolocalisation
- Alertes vigilance météo
- Bulletin météo automatique dans feed
- Notifications push alertes météo

#### Dashboard & Planning

- Stats réelles dashboard
- Équipe du jour depuis planning affectations
- Statut réel chantier (ouvert/en_cours/réceptionné/fermé)
- Chantiers spéciaux (Congés, Maladie, Formation, RTT, Absence)
- Resize multi-day affectations avec preview
- Blocs proportionnels selon durée
- Type utilisateur intérimaire
- Auto-geocoding adresses

#### Feuilles d'Heures & Formulaires

- Filtres utilisateurs groupés par rôle
- Heures planifiées vs réalisées (jauge comparaison)
- Navigation cliquable (noms chantier/utilisateurs)
- Seed data formulaires (6 templates + 10 remplis)
- API enrichie (template_nom, chantier_nom, user_nom)
- Types formulaires alignés frontend/backend

---

## Session 2026-01-25 - Infrastructure & Sécurité

### Added

- APScheduler: Jobs planifiés (job scheduler)
- Firebase Cloud Messaging: Notifications push
- DOMPurify: Protection XSS
- Zod: Validation côté client
- Module Interventions COMPLET (INT-01 à INT-17)

### Fixed

- 13 problèmes de sécurité, accessibilité, maintenabilité corrigés
- HttpOnly cookies
- ARIA attributes
- Validation stricte

---

## Légende

- **Added**: Nouvelles fonctionnalités
- **Changed**: Modifications de fonctionnalités existantes
- **Deprecated**: Fonctionnalités obsolètes (à supprimer prochainement)
- **Removed**: Fonctionnalités supprimées
- **Fixed**: Corrections de bugs
- **Security**: Corrections de failles de sécurité

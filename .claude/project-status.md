# Hub Chantier - Etat du projet

> Ce fichier contient l'etat actuel des modules et les prochaines taches.
> Mis a jour a chaque session de developpement.

## Etat des modules

| Module | CDC Section | Fonctionnalites | Done | Infra | Status |
|--------|-------------|-----------------|------|-------|--------|
| auth (utilisateurs) | 3 | USR-01 a USR-13 | 13/13 | 0 | **COMPLET** |
| dashboard (feed) | 2 | FEED-01 a FEED-20 | 17/20 | 1 | **COMPLET** (2 future) |
| dashboard (cards) | 2 | DASH-01 a DASH-15 | 15/15 | 0 | **COMPLET** |
| chantiers | 4 | CHT-01 a CHT-21 | 19/21 | 1 | **COMPLET** (1 future) |
| planning | 5 | PLN-01 a PLN-28 | 26/28 | 2 | **COMPLET** (2 infra) |
| planning_charge | 6 | PDC-01 a PDC-17 | 17/17 | 0 | **COMPLET** |
| feuilles_heures | 7 | FDH-01 a FDH-20 | 16/20 | 4 | **COMPLET** (4 infra) |
| formulaires | 8 | FOR-01 a FOR-11 | 11/11 | 0 | **COMPLET** |
| documents | 9 | GED-01 a GED-17 | 15/17 | 2 | **COMPLET** (2 infra) |
| signalements | 10 | SIG-01 a SIG-20 | 17/20 | 3 | **COMPLET** (3 infra) |
| logistique | 11 | LOG-01 a LOG-18 | 18/18 | 0 | **COMPLET** |
| interventions | 12 | INT-01 a INT-17 | 14/17 | 3 | **COMPLET** (3 infra) |
| taches | 13 | TAC-01 a TAC-20 | 20/20 | 0 | **COMPLET** |

## Statistiques globales

- **Modules complets** : 13/13 (incluant dashboard cards)
- **Fonctionnalites totales** : 237
- **Fonctionnalites done** : 218 (92%)
- **Fonctionnalites infra** : 16 (en attente infrastructure)
- **Fonctionnalites future** : 3 (prevues pour versions futures)

### Code source

- **Backend** : 16 modules, 35+ entites, 50+ value objects, 150+ use cases, 40+ repositories
- **Frontend** : 11 pages, 27 hooks, 23 services, 80+ composants, 3 contextes
- **Architecture** : Clean Architecture 4 layers (Domain > Application > Adapters > Infrastructure)

### Tests

- **Tests backend** : 140+ fichiers (unit + integration)
- **Tests frontend** : 116 fichiers, 2253 tests (2253 pass, 0 fail, 6 skip)
- **Integration tests** : 10 suites API completes

## Features recentes (Sessions 26-27 janvier)

| Feature | Description | Session |
|---------|-------------|---------|
| Formulaires seed data | 6 templates + 10 formulaires remplis demo | 27 jan |
| Formulaires enrichis | API retourne template_nom, chantier_nom, user_nom | 27 jan |
| Types formulaires alignes | Frontend/backend TypeChamp et CategorieFormulaire unifies | 27 jan |
| Feuilles heures filtres | Filtre utilisateurs groupe par role | 27 jan |
| Heures planifiees vs realisees | Jauge comparaison dans feuilles d'heures | 27 jan |
| Navigation cliquable | Noms chantier/utilisateur cliquables dans feuilles | 27 jan |
| Meteo reelle | API Open-Meteo + geolocalisation + alertes vigilance | 27 jan |
| Bulletin meteo feed | Post automatique resume meteo dans actualites | 27 jan |
| Notifications push meteo | Alertes meteo en temps reel via Notification API | 27 jan |
| Statut reel chantier | Affiche ouvert/en_cours/receptionne/ferme | 27 jan |
| Equipe du jour reelle | Collegues charges depuis planning affectations | 27 jan |
| Chantiers speciaux | Conges, Maladie, Formation, RTT, Absence dans planning | 26 jan |
| Resize affectations | Extension et reduction par drag sur bord | 26 jan |
| Blocs proportionnels | Hauteur des blocs proportionnelle a la duree | 26 jan |
| Multi-day affectations | Affectations sur plusieurs jours consecutifs | 26 jan |
| Interimaire type | Nouveau type utilisateur interimaire | 26 jan |
| Auto-geocoding | Geocodage automatique a la modification d'adresse | 26 jan |

## Prochaines taches prioritaires

### Infrastructure (16 features)

| ID | Description |
|----|-------------|
| INT-14/15/16 | Generation rapport PDF interventions |
| SIG-13 | Notifications push signalements |
| SIG-16/17 | Alertes retard + escalade automatique signalements |
| FEED-17 | Notifications push publications |
| PLN-23/24 | Mode Offline PWA |
| FDH-16/17/18/19 | Import ERP, export paie, macros, geolocalisation |
| GED-11/15 | Transfert ERP + synchronisation offline |
| CHT-11 | Integration ERP (Costructor/Graneet) |

### Ameliorations possibles

- Page dediee signalements (actuellement dans chantier detail)
- Page dediee interventions (actuellement backend only pour le frontend)
- Couverture tests frontend > 50% (actuellement ~29%)
- Mode offline complet (PWA)

## Infrastructure disponible

- **APScheduler** : Jobs planifies (job scheduler)
- **Firebase Cloud Messaging** : Notifications push
- **Open-Meteo API** : Donnees meteo en temps reel
- **Nominatim/OpenStreetMap** : Geocodage inverse
- **Alembic** : Migrations base de donnees
- **DOMPurify** : Protection XSS
- **Zod** : Validation cote client

## Tests frontend

**Tous les tests passent : 116 fichiers, 2253 tests, 0 echec, 6 skip.**

Session 27 janvier 2026 : correction des 91 tests en echec sur 12 fichiers.
Causes corrigees : MemoryRouter manquant, mocks de services/hooks obsoletes, assertions sur textes/props modifies.

## Derniere mise a jour

Session 2026-01-27 - Correction des 91 tests en echec (0 remaining)
- 12 fichiers de test corriges : TimesheetGrid (23), TimesheetChantierGrid (19), ChantierDetailPage (14), DashboardPage (10), StatsCard (7), TodayPlanningCard (7), TeamCard (2), FieldRenderer (2), FeuillesHeuresPage (2), WeatherCard (1), FormulairesPage (1), UserDetailPage (1)
- Corrections principales :
  - Ajout MemoryRouter pour composants utilisant useNavigate (49 tests)
  - Mocks de hooks manquants (useTodayPlanning, useWeeklyStats, useTodayTeam, useWeather, useClockCard)
  - Ajout mock planningService pour ChantierDetailPage
  - Alignement assertions sur textes/props actuels (status, boutons, labels)
  - Correction structure alerte meteo (alert via hook, pas via prop)
  - Ajout role aux utilisateurs mock pour filtres par role
  - Retrait test GeolocationConsentModal (supprime du composant)
- Resultat : 116 fichiers, 2253 tests, 0 echec, 6 skip

Session 2026-01-27 - Audit tests frontend
- Audit complet suite tests frontend : 2260 tests, 2163 pass, 91 fail, 6 skip
- Tests auth/securite (AuthContext, LoginPage, api) : tous OK (corrige lors de sessions precedentes)
- 91 echecs dans 12 fichiers — cause : composants enrichis sans mise a jour des tests
- project-status.md mis a jour avec inventaire detaille des echecs

Session 2026-01-27 - Feuilles heures, formulaires, dashboard
- Feuilles heures : filtres par role, heures planifiees vs realisees, navigation cliquable
- Formulaires : seed data (6 templates + 10 formulaires), alignement types frontend/backend, API enrichie (noms)
- Dashboard : stats reelles, equipe du jour, actions rapides
- 43 fichiers modifies (12 backend, 31 frontend)

Session 2026-01-27 - Audit documentation complet (Git + Code scan)
- Scan complet du code source : 16 modules backend, 11 pages frontend, 27 hooks, 23 services
- Ajout statut sur 31 features SIG et INT non marquees dans SPECIFICATIONS.md
- 237 features totales identifiees (218 done, 16 infra, 3 future)
- project-status.md reecrit avec inventaire complet et statistiques a jour

Session 2026-01-27 - Meteo reelle, statut chantier, equipe du jour
- API Open-Meteo avec geolocalisation et alertes vigilance
- Bulletin meteo automatique dans le feed d'actualites
- Statut reel du chantier (ouvert/en_cours/receptionne/ferme)
- Equipe du jour chargee depuis les affectations planning
- Notifications push alertes meteo

Session 2026-01-26 - Planning ameliore et couverture tests
- Chantiers speciaux (Conges, Maladie, Formation, RTT, Absence)
- Resize multi-day affectations avec preview visuel
- Blocs proportionnels selon duree
- Type utilisateur interimaire + auto-geocoding
- Couverture tests firebase 100%

Session 2026-01-25 - Corrections Frontend et Infrastructure
- 13 problemes corriges (securite, accessibilite, maintenabilite)
- DOMPurify, HttpOnly cookies, Zod validation, ARIA
- APScheduler + Firebase Cloud Messaging
- Module Interventions COMPLET (INT-01 a INT-17)

## 7. FEUILLES D'HEURES

### 7.1 Vue d'ensemble

Le module Feuilles d'heures permet la saisie, le suivi et l'export des heures travaillees avec deux vues complementaires (Chantiers et Compagnons) et des variables de paie integrees. Il s'interface avec les ERP pour l'export automatise.

### 7.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| FDH-01 | 2 onglets de vue | [Chantiers] [Compagnons/Sous-traitants] | ✅ |
| FDH-02 | Navigation par semaine | Semaine X avec << < > >> pour naviguer | ✅ |
| FDH-03 | Bouton Exporter | Export des donnees vers fichier ou ERP | ✅ |
| FDH-04 | Filtre utilisateurs | Dropdown de selection multi-criteres | ✅ |
| FDH-05 | Vue tabulaire hebdomadaire | Lundi a Vendredi avec dates completes | ✅ |
| FDH-06 | Multi-chantiers par utilisateur | Plusieurs lignes possibles | ✅ |
| FDH-07 | Badges colores par chantier | Coherence avec le planning | ✅ |
| FDH-08 | Total par ligne | Somme heures par utilisateur + chantier | ✅ |
| FDH-09 | Total groupe | Somme heures utilisateur tous chantiers | ✅ |
| FDH-10 | Creation auto a l'affectation | Lignes pre-remplies depuis le planning | ✅ |
| FDH-11 | Saisie mobile | Selecteur roulette HH:MM intuitif | ⏳ Frontend |
| FDH-12 | Signature electronique | Validation des heures par le compagnon | ✅ |
| FDH-13 | Variables de paie | Panier, transport, conges, primes, absences | ✅ |
| FDH-14 | Jauge d'avancement | Comparaison planifie vs realise | ✅ |
| FDH-15 | Comparaison inter-equipes | Detection automatique des ecarts | ✅ |
| FDH-16 | Import ERP auto | Synchronisation quotidienne/hebdomadaire | ⏳ Infra |
| FDH-17 | Export ERP manuel | Periode selectionnee personnalisable | ✅ |
| FDH-18 | Macros de paie | Calculs automatises parametrables | ⏳ Frontend |
| FDH-19 | Feuilles de route | Generation automatique PDF | ✅ |
| FDH-20 | Mode Offline | Saisie sans connexion, sync auto | ⏳ Frontend |

**Note technique (31/01/2026)** : Phase 1 - Corrections critiques workflow validation feuilles d'heures :
- ✅ **GAP-FDH-001** : Workflow "corriger" implémenté (`CorrectPointageUseCase` + route POST `/{pointage_id}/correct`)
- ✅ **GAP-FDH-002** : Verrouillage mensuel période de paie (`PeriodePaie` value object, clôture vendredi avant dernière semaine)
- ✅ **GAP-FDH-003** : Service de permissions domaine (`PointagePermissionService`, contrôles rôles compagnon/chef/conducteur/admin)
- ✅ **GAP-FDH-005** : Validation 24h par jour (méthode `Pointage.set_heures()` avec vérification total <= 24h)
- ✅ Tous les use cases intègrent la vérification `PeriodePaie.is_locked()` avant modification
- ✅ Tests : +74 tests générés (PeriodePaie, PermissionService, CorrectPointage, validation 24h), 214 tests total (100% pass)
- ✅ Validation agents : architect-reviewer (10/10), test-automator (90%+), code-reviewer (9.5/10), security-auditor (PASS, 0 CRITICAL/HIGH)
- ⏳ **SEC-PTG-001** (MEDIUM) : Regex validation heures à renforcer (accepte formats invalides 99:99)
- ⏳ **SEC-PTG-002** (MEDIUM) : Intégration `PointagePermissionService` dans routes POST/PUT (service créé mais pas encore utilisé)

**Note technique (31/01/2026)** : Phase 2 - Corrections critiques transmission heures_prevues (FDH-10) :
- ✅ **GAP-T5** : Transmission heures_prevues dans événements Planning → Pointages (ajout paramètre `heures_prevues: Optional[float]` dans `AffectationCreatedEvent`)
- ✅ **Type conversion** : Ajout `_convert_heures_to_string()` dans `event_handlers.py` pour convertir float (8.0) → string ("08:00")
- ✅ **Validation NaN/Infinity** : Ajout `field_validator` dans `planning_schemas.py` pour rejeter valeurs invalides (sécurité HIGH)
- ✅ **RGPD logs** : Passage logs sensibles (user_id, chantier_id, heures) de INFO → DEBUG dans `planning_controller.py`
- ✅ **Clean Architecture** : Correction ligne 99 `event_handlers.py` - injection dépendance `chantier_repo` au lieu import direct inter-modules
- ✅ **Security** : Remplacement `print()` par `logger.exception()` dans `planning_routes.py` (finding HIGH résolu)
- ✅ Tests : +43 tests générés (conversion heures, validators Pydantic), 92% couverture (objectif 90% dépassé)
- ✅ Validation agents finale : architect-reviewer (WARN, 0 CRITICAL), test-automator (92%), code-reviewer (APPROVED), security-auditor (PASS, 0 HIGH/CRITICAL)

### 7.3 Variables de paie

| Variable | Type | Description |
|----------|------|-------------|
| Heures normales | Nombre | Heures de travail standard |
| Heures supplementaires | Nombre | Heures au-dela du contrat |
| Panier repas | Montant | Indemnite de repas |
| Indemnite transport | Montant | Frais de deplacement |
| Prime intemperies | Montant | Compensation meteo |
| Conges payes | Jours | Absences conges |
| Maladie | Jours | Absences maladie |
| Absence injustifiee | Jours | Absences non justifiees |

---
# Planning Opérationnel - Analyse des Gaps

**Date** : 30 janvier 2026
**Auteur** : Claude Sonnet 4.5
**Référence** : WORKFLOW_PLANNING_OPERATIONNEL.md

---

## 🎯 Résumé Exécutif

Le module planning est **largement implémenté** (11/11 routes API, 7/7 use cases core) avec une architecture Clean solide. Cependant, il présente **4 gaps critiques** qui bloquent la synchronisation avec les feuilles d'heures (FDH-10) et plusieurs gaps fonctionnels impactant les règles métier.

**Statut global** : ⚠️ **Fonctionnel mais incomplet** (3/5 étoiles)

---

## 🔴 GAPS CRITIQUES (Bloquants)

### 1. ❌ Champ `heures_prevues` MANQUANT

**Impact** : **BLOQUE FDH-10** - Synchronisation Planning → Pointages impossible

**Détail** :
- L'entité `Affectation` n'a pas le champ `heures_prevues`
- DTOs (`CreateAffectationDTO`, `AffectationDTO`) ne le supportent pas
- Schema Pydantic API ne l'expose pas
- `BulkCreateFromPlanningUseCase` essaie d'y accéder (ligne 72) → **CRASH**

**Workflow documenté** (ligne 144-152) :
```python
heures_prevues: Decimal  # Durée planifiée pour la journée (ex: 8.0, 7.5)
# Utilisé pour:
# - Calcul de charge (Planning de Charge)
# - Pré-remplissage feuilles d'heures (FDH-10)
```

**Fichiers à modifier** :
```
backend/modules/planning/domain/entities/affectation.py
backend/modules/planning/application/dtos/create_affectation_dto.py
backend/modules/planning/application/dtos/affectation_dto.py
backend/modules/planning/adapters/controllers/planning_schemas.py
backend/modules/planning/infrastructure/persistence/affectation_model.py (SQLAlchemy)
```

**Code à ajouter** :
```python
# Dans affectation.py (entité)
@dataclass
class Affectation:
    # ... champs existants ...
    heures_prevues: float = 8.0  # Par défaut: journée standard

# Calcul automatique si non fourni
def calculate_heures_prevues(self) -> float:
    if self.heure_debut and self.heure_fin:
        return (self.heure_fin - self.heure_debut).total_seconds() / 3600
    return 8.0
```

**Migration DB** :
```sql
ALTER TABLE affectations ADD COLUMN heures_prevues DECIMAL(4,2) DEFAULT 8.0;
```

---

### 2. ❌ Pas de filtrage chantiers système (CONGES, MALADIE, RTT, FORMATION)

**Impact** : Crée des pointages pour les absences → **Feuilles d'heures corrompues**

**Workflow documenté** (ligne 504-507, 586) :
```
❌ AUCUN pointage n'est créé automatiquement pour chantiers système
Raison : Les absences ne génèrent pas d'heures de travail
```

**État actuel** :
- ✅ Codes chantiers système existent dans module Chantiers
- ❌ Planning ne les traite **PAS différemment**
- ❌ `BulkCreateFromPlanningUseCase` crée pointages pour **TOUS** les chantiers

**Code à ajouter** :
```python
# Dans bulk_create_from_planning.py
CHANTIERS_SYSTEME = ['CONGES', 'MALADIE', 'RTT', 'FORMATION']

# Ligne 60-65 : Filtrer les chantiers système
affectations_filtered = [
    a for a in affectations
    if a.chantier.code not in CHANTIERS_SYSTEME  # ⬅️ AJOUTER
]

for affectation in affectations_filtered:
    # ... créer pointage
```

**Fichiers à modifier** :
```
backend/modules/pointages/application/use_cases/bulk_create_from_planning.py
```

---

### 3. ❌ Règle RG-PLN-004 : Validation chantier actif NON IMPLÉMENTÉE

**Impact** : Permet d'affecter à un chantier fermé/archivé → **Data integrity**

**Workflow documenté** (ligne 523) :
```
RG-PLN-004 : Impossible d'affecter à un chantier `fermé` ou `deleted_at != NULL`
```

**État actuel** :
- ❌ Pas de vérification du statut chantier
- ❌ Pas d'appel au module Chantiers pour validation

**Code à ajouter** :
```python
# Dans create_affectation.py, ligne 120-130
chantier = self.chantier_repository.find_by_id(dto.chantier_id)
if not chantier:
    raise ChantierNotFoundError(f"Chantier {dto.chantier_id} introuvable")

if chantier.deleted_at is not None:
    raise ChantierArchiveError("Impossible d'affecter à un chantier archivé")

if chantier.statut not in [StatutChantier.OUVERT, StatutChantier.EN_COURS]:
    raise ChantierInactifError(
        f"Impossible d'affecter à un chantier {chantier.statut.value}"
    )
```

**Fichiers à modifier** :
```
backend/modules/planning/application/use_cases/create_affectation.py
backend/modules/planning/application/use_cases/update_affectation.py
backend/modules/planning/domain/repositories/chantier_repository.py (à créer)
```

**Dépendances** :
- Ajouter `ChantierRepository` (port) dans Planning
- Implémenter adaptateur vers module Chantiers

---

### 4. ❌ Règle RG-PLN-005 : Validation utilisateur actif NON IMPLÉMENTÉE

**Impact** : Permet d'affecter un utilisateur désactivé → **Data integrity**

**Workflow documenté** (ligne 524) :
```
RG-PLN-005 : Impossible d'affecter un utilisateur désactivé (`is_active = false`)
```

**Code à ajouter** :
```python
# Dans create_affectation.py, ligne 135-140
user = self.user_repository.find_by_id(dto.utilisateur_id)
if not user:
    raise UserNotFoundError(f"Utilisateur {dto.utilisateur_id} introuvable")

if not user.is_active:
    raise UserInactifError(
        "Impossible d'affecter un utilisateur désactivé"
    )
```

**Fichiers à modifier** :
```
backend/modules/planning/application/use_cases/create_affectation.py
backend/modules/planning/application/use_cases/update_affectation.py
backend/modules/planning/domain/repositories/user_repository.py (à créer)
```

**Dépendances** :
- Ajouter `UserRepository` (port) dans Planning
- Implémenter adaptateur vers module Auth

---

## ⚠️ GAPS IMPORTANTS (Réduction fonctionnelle)

### 5. ⚠️ Permissions Chef de Chantier incomplètes

**Impact** : Chef peut créer/modifier affectations sur chantiers où il n'est pas affecté

**État actuel** :
- ✅ GET filtre correctement (chef voit uniquement ses chantiers)
- ❌ **CREATE/UPDATE/DELETE** ne vérifient PAS les droits

**Workflow documenté** (ligne 74-78) :
```
Chef de Chantier :
- Peuvent affecter des compagnons sur **leurs chantiers uniquement**
- Ne voient que les utilisateurs déjà affectés à leurs chantiers
```

**Code à ajouter** :
```python
# Dans planning_routes.py, ligne 85 (POST /affectations)
if role_lower in ("chef_chantier", "chef_equipe"):
    # Vérifier que le chef est affecté au chantier
    user_chantiers = get_user_chantiers(current_user_id)
    if data.chantier_id not in user_chantiers:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez affecter que sur vos chantiers"
        )
```

**Fichiers à modifier** :
```
backend/modules/planning/infrastructure/web/planning_routes.py (lignes 85, 268, 324)
```

---

### 6. ⚠️ Règle RG-PLN-007 : Conflit absences NON IMPLÉMENTÉE

**Impact** : Utilisateur peut être planifié sur chantier réel ET en congés le même jour

**Workflow documenté** (ligne 501-502) :
```
⚠️ BLOQUER si des affectations "réelles" existent déjà sur ces dates
Message : "Impossible d'affecter à CONGES : le compagnon est déjà affecté au chantier X"
```

**Code à ajouter** :
```python
# Dans create_affectation.py, ligne 145-155
if dto.chantier.code in CHANTIERS_SYSTEME:
    # Vérifier absence d'affectations réelles
    existing = self.affectation_repo.find_for_utilisateur_and_date(
        utilisateur_id=dto.utilisateur_id,
        date=dto.date
    )

    if existing and existing.chantier.code not in CHANTIERS_SYSTEME:
        raise AffectationConflictError(
            f"Impossible d'affecter à {dto.chantier.code} : "
            f"le compagnon est déjà affecté au chantier {existing.chantier.nom}"
        )
```

**Fichiers à modifier** :
```
backend/modules/planning/application/use_cases/create_affectation.py
```

---

### 7. ⚠️ Synchronisation FDH-10 pas automatique

**Impact** : Use case `BulkCreateFromPlanningUseCase` existe mais n'est jamais appelé

**État actuel** :
- ✅ Use case implémenté
- ✅ Événement `AffectationCreatedEvent` publié
- ❌ **Pas de subscriber/listener visible**

**Workflow documenté** (ligne 569-608) :
```
Déclencheur : Lorsqu'un compagnon ouvre sa feuille d'heures
GET /api/pointages/feuilles-heures/utilisateur/15/semaine/2026-01-27
→ Appelle BulkCreateFromPlanningUseCase
```

**Code à ajouter** :
```python
# Dans feuilles_heures_routes.py
@router.get("/.../semaine/{date_debut}")
def get_feuille_heures_semaine(...):
    # 1. Récupérer affectations de la semaine
    affectations = get_planning_use_case.execute(...)

    # 2. Créer pointages automatiquement
    bulk_create_use_case.execute(
        utilisateur_id=utilisateur_id,
        date_debut=date_debut,
        date_fin=date_fin
    )

    # 3. Récupérer pointages
    pointages = list_pointages_use_case.execute(...)
    return pointages
```

**Fichiers à modifier** :
```
backend/modules/pointages/infrastructure/web/feuilles_heures_routes.py (à vérifier)
```

---

## 📋 GAPS MINEURS (Qualité)

### 8. 📋 Tests pour chantiers système manquants

**Tests à créer** :
```python
def test_create_affectation_conges_bloque_si_affectation_reelle():
    """RG-PLN-007"""

def test_bulk_create_from_planning_ignore_chantiers_systeme():
    """FDH-10 - Filtrage"""

def test_create_affectation_chantier_ferme_refuse():
    """RG-PLN-004"""
```

---

### 9. 📋 Documentation intégration FDH manquante

**À documenter** :
- Comment activer/désactiver la sync auto
- Que se passe-t-il si affectation supprimée après création pointage
- Gestion des conflits

---

### 10. 📋 Logging/Monitoring basique

**KPIs métier manquants** :
- Taux d'occupation (heures affectées / heures dispo)
- Délai planification (création chantier → première affectation)
- Nombre conflits détectés

---

## 📊 Métriques de Couverture

| Aspect | Couverture | Notes |
|--------|-----------|-------|
| **Routes API** | ✅ 11/11 (100%) | Tous endpoints documentés |
| **Use Cases Core** | ✅ 7/7 (100%) | CRUD + duplication + resize |
| **Règles Métier** | ⚠️ 4/7 (57%) | RG-004, 005, 007 manquantes |
| **Chantiers Spéciaux** | ❌ 0/4 (0%) | Pas de traitement différencié |
| **FDH-10 Sync** | ⚠️ 1/3 (33%) | Use case OK, pas de trigger |
| **Permissions Chef** | ⚠️ 1/4 (25%) | GET OK, CREATE/UPDATE/DELETE KO |
| **Frontend Features** | ✅ 4/4 (100%) | Drag/drop, resize, récurrence, notes |
| **Tests** | ⚠️ ~15 tests | Basique, edge cases manquants |

**Score global** : **55% complet**

---

## 🎯 Plan d'Action Recommandé

### Phase 1 : URGENT (Débloque FDH-10) - 2 jours

**Objectif** : Rendre la synchronisation Planning → Pointages fonctionnelle

1. ✅ **Ajouter champ `heures_prevues`** (4h)
   - Entité + DTOs + Schema + Migration DB
   - Calcul automatique si non fourni

2. ✅ **Filtrer chantiers système dans FDH-10** (2h)
   - Modifier `BulkCreateFromPlanningUseCase`
   - Exclure CONGES, MALADIE, RTT, FORMATION

3. ✅ **Tests validation** (2h)
   - Test `heures_prevues` pré-remplit pointage
   - Test chantiers système ne créent pas pointage

**Livrables** :
- FDH-10 fonctionnel
- Tests passent (2 nouveaux)
- Documentation mise à jour

---

### Phase 2 : Important (Data Integrity) - 2 jours

**Objectif** : Garantir qualité des données

4. ✅ **Implémenter RG-PLN-004** (3h)
   - Validation chantier actif
   - Repository port + adaptateur

5. ✅ **Implémenter RG-PLN-005** (2h)
   - Validation utilisateur actif
   - Repository port + adaptateur

6. ✅ **Implémenter RG-PLN-007** (3h)
   - Validation conflit absences
   - Messages erreur clairs

**Livrables** :
- 3 règles métier validées
- Tests (3 nouveaux)
- Messages erreur user-friendly

---

### Phase 3 : Permissions (Sécurité) - 1 jour

**Objectif** : Isolation chef de chantier correcte

7. ✅ **Corriger permissions Chef** (4h)
   - CREATE : vérifier chantier dans liste chef
   - UPDATE : vérifier chantier dans liste chef
   - DELETE : vérifier chantier dans liste chef

8. ✅ **Tests permissions** (2h)
   - Test chef ne peut pas affecter sur chantier autre
   - Test chef peut affecter sur son chantier

**Livrables** :
- Permissions Chef strictes
- Tests sécurité (2 nouveaux)

---

### Phase 4 : Qualité (Optionnel) - 1 jour

9. ✅ **Tests edge cases** (3h)
10. ✅ **Documentation technique** (2h)
11. ✅ **Monitoring/KPIs** (1h)

---

## 📁 Fichiers à Créer/Modifier

### Backend - Modifications

| Fichier | Action | Phase |
|---------|--------|-------|
| `domain/entities/affectation.py` | AJOUTER `heures_prevues: float` | 1 |
| `application/dtos/create_affectation_dto.py` | AJOUTER `heures_prevues: float` | 1 |
| `application/dtos/affectation_dto.py` | AJOUTER `heures_prevues: float` | 1 |
| `adapters/controllers/planning_schemas.py` | AJOUTER `heures_prevues: float` | 1 |
| `infrastructure/persistence/affectation_model.py` | AJOUTER colonne SQL | 1 |
| `../pointages/.../bulk_create_from_planning.py` | FILTRER chantiers système | 1 |
| `application/use_cases/create_affectation.py` | AJOUTER RG-004, 005, 007 | 2 |
| `domain/repositories/chantier_repository.py` | CRÉER port | 2 |
| `domain/repositories/user_repository.py` | CRÉER port | 2 |
| `infrastructure/web/planning_routes.py` | MODIFIER CREATE/UPDATE/DELETE | 3 |

### Backend - Nouveaux fichiers

| Fichier | Action | Phase |
|---------|--------|-------|
| `application/exceptions.py` | AJOUTER ChantierInactifError, UserInactifError | 2 |
| `adapters/chantier_adapter.py` | IMPLÉMENTER ChantierRepository | 2 |
| `adapters/user_adapter.py` | IMPLÉMENTER UserRepository | 2 |

### Frontend - OK

✅ Aucune modification frontend requise

---

## 🔗 Références

- **Workflow complet** : `docs/workflows/WORKFLOW_PLANNING_OPERATIONNEL.md`
- **Spécifications** : `docs/SPECIFICATIONS.md` (Section 5 - PLN-01 à PLN-28)
- **Module Pointages** : `backend/modules/pointages/`
- **Agent Explore** : `abd1d31` (pour reprendre l'analyse)

---

**Rapport généré** : 30 janvier 2026
**Auteur** : Claude Sonnet 4.5
**Statut** : ⚠️ Incomplet - 4 gaps critiques identifiés

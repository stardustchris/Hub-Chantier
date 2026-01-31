# Rapport Test Automator - Analyse champ `heures_prevues`

**Agent** : test-automator
**Date** : 2026-01-31
**Modifications analysées** : Ajout champ `heures_prevues` dans `AffectationCreatedEvent`
**Objectif** : >= 90% couverture

---

## 1. RÉSUMÉ EXÉCUTIF

### Statut Global : ⚠️ COUVERTURE PARTIELLE

| Métrique | État | Objectif |
|----------|------|----------|
| **Couverture actuelle** | ~70% | >= 90% |
| **Tests manquants** | 6 | 0 |
| **Tests à modifier** | 1 | - |
| **Risque** | MOYEN | - |

### Actions requises
- ✅ **1 test existant** à vérifier/modifier (event handler pointages)
- 🆕 **6 nouveaux tests** à créer (domaine + use case)

---

## 2. ANALYSE DU CHAMP `heures_prevues`

### 2.1 Implémentation actuelle

**Entité Affectation** (`backend/modules/planning/domain/entities/affectation.py:54`)
```python
heures_prevues: float = 8.0  # Nombre d'heures prevues (defaut: journee standard)
```

**Event AffectationCreatedEvent** (`backend/modules/planning/domain/events/affectation_events.py:42`)
```python
heures_prevues: Optional[float] = None
```

**Publication dans Use Case** (`backend/modules/planning/application/use_cases/create_affectation.py:209`)
```python
event = AffectationCreatedEvent(
    affectation_id=affectations[0].id,
    utilisateur_id=affectations[0].utilisateur_id,
    chantier_id=affectations[0].chantier_id,
    date=affectations[0].date,
    created_by=created_by,
    heures_prevues=affectations[0].heures_prevues,  # ✅ Transmission du champ
)
```

### 2.2 Flux de données

```
Affectation.heures_prevues (float, défaut: 8.0)
    ↓
AffectationCreatedEvent.heures_prevues (Optional[float])
    ↓
Event Handler Pointages (conversion en str "08:00")
    ↓
BulkCreateFromPlanningUseCase.execute_from_event()
```

---

## 3. ANALYSE DES TESTS EXISTANTS

### 3.1 ✅ Tests du Use Case (`test_create_affectation_use_case.py`)

**Tests exécutés** : 20 tests, tous PASSED

**Couverture actuelle** :
- ✅ Création d'affectation unique (lignes 84-108)
- ✅ Création avec horaires (lignes 109-134)
- ✅ Création avec note (lignes 135-156)
- ✅ Publication de l'event `AffectationCreatedEvent` (lignes 259-285)
- ✅ Création récurrente + event bulk (lignes 335-431)

**❌ GAP IDENTIFIÉ - Test event avec `heures_prevues`** :
Le test `test_should_publish_created_event` (lignes 259-285) vérifie la publication de l'event mais **NE VÉRIFIE PAS** le champ `heures_prevues`.

```python
# Ligne 279-284 (ACTUEL)
assert isinstance(event, AffectationCreatedEvent)
assert event.affectation_id == 1
assert event.utilisateur_id == 1
assert event.chantier_id == 2
assert event.created_by == 3
# ❌ MANQUE : assert event.heures_prevues == 8.0
```

### 3.2 ✅ Tests des Event Handlers (`test_event_handlers.py`)

**Tests exécutés** : 10 tests pour `handle_affectation_created`

**Couverture actuelle** :
- ✅ Ligne 40-58 : Test création pointage avec `heures_prevues="08:00"` (mock)
- ✅ Ligne 64-85 : Test valeur par défaut "08:00" si `heures_prevues=None`
- ✅ Ligne 91-110 : Test gestion absence attribut `heures_prevues`

**✅ COUVERTURE CORRECTE** : Les tests couvrent déjà la transmission de `heures_prevues` via l'event, avec gestion des cas :
- Event avec `heures_prevues` fourni
- Event avec `heures_prevues=None`
- Event sans attribut `heures_prevues`

**⚠️ ATTENTION** : Les tests utilisent des **mocks** (ligne 22-29), ils vérifient donc la **logique** mais pas la **structure réelle** de l'event.

### 3.3 ❌ Tests du Domaine (MANQUANTS)

**Fichier** : `backend/tests/unit/planning/domain/test_affectation_events.py`
**Statut** : ❌ **N'EXISTE PAS**

Ce fichier devrait tester :
- Structure des events
- Méthode `to_dict()`
- Sérialisation du champ `heures_prevues`

---

## 4. TESTS À AJOUTER/MODIFIER

### 4.1 ✏️ Test à MODIFIER

**Fichier** : `backend/tests/unit/planning/test_create_affectation_use_case.py`

#### Test 1 : `test_should_publish_created_event` (ligne 259-285)

**Action** : AJOUTER assertion pour `heures_prevues`

**Modification** :
```python
def test_should_publish_created_event(
    self, use_case, mock_affectation_repository, mock_event_bus
):
    """Test: publication de l'event apres creation."""
    # Arrange
    mock_affectation_repository.save.side_effect = lambda a: (
        setattr(a, "id", 1) or a
    )

    dto = CreateAffectationDTO(
        utilisateur_id=1,
        chantier_id=2,
        date=date(2026, 1, 22),
    )

    # Act
    use_case.execute(dto, created_by=3)

    # Assert
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, AffectationCreatedEvent)
    assert event.affectation_id == 1
    assert event.utilisateur_id == 1
    assert event.chantier_id == 2
    assert event.created_by == 3
    # 🆕 AJOUT : Vérification heures_prevues
    assert event.heures_prevues == 8.0  # Valeur par défaut
```

**Impact** : +1 assertion, couvre le flux use case → event

---

### 4.2 🆕 Tests à CRÉER

#### Fichier : `backend/tests/unit/planning/domain/test_affectation_events.py` (NOUVEAU)

**Tests requis** : 6 tests

---

##### Test 1 : Création event avec `heures_prevues` fourni

```python
def test_affectation_created_event_with_heures_prevues():
    """Test: AffectationCreatedEvent avec heures_prevues fourni."""
    # Arrange & Act
    event = AffectationCreatedEvent(
        affectation_id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
        heures_prevues=7.5
    )

    # Assert
    assert event.heures_prevues == 7.5
```

**Raison** : Valide que le champ est stocké correctement dans l'event.

---

##### Test 2 : Création event sans `heures_prevues` (défaut None)

```python
def test_affectation_created_event_without_heures_prevues():
    """Test: AffectationCreatedEvent sans heures_prevues (defaut None)."""
    # Arrange & Act
    event = AffectationCreatedEvent(
        affectation_id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
        # heures_prevues non fourni
    )

    # Assert
    assert event.heures_prevues is None
```

**Raison** : Valide le comportement par défaut (optionnel).

---

##### Test 3 : Sérialisation `to_dict()` avec `heures_prevues`

```python
def test_affectation_created_event_to_dict_with_heures_prevues():
    """Test: Serialisation to_dict() avec heures_prevues."""
    # Arrange
    event = AffectationCreatedEvent(
        affectation_id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
        heures_prevues=8.0
    )

    # Act
    result = event.to_dict()

    # Assert
    assert result["heures_prevues"] == 8.0
    assert "heures_prevues" in result
```

**Raison** : Vérifie que `to_dict()` inclut bien le champ `heures_prevues`.

---

##### Test 4 : Sérialisation `to_dict()` avec `heures_prevues=None`

```python
def test_affectation_created_event_to_dict_with_none_heures_prevues():
    """Test: Serialisation to_dict() avec heures_prevues=None."""
    # Arrange
    event = AffectationCreatedEvent(
        affectation_id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
        heures_prevues=None
    )

    # Act
    result = event.to_dict()

    # Assert
    assert result["heures_prevues"] is None
    assert "heures_prevues" in result
```

**Raison** : Vérifie que `to_dict()` gère correctement la valeur `None`.

---

##### Test 5 : Immutabilité de l'event (frozen=True)

```python
def test_affectation_created_event_is_frozen():
    """Test: AffectationCreatedEvent est immutable (frozen=True)."""
    # Arrange
    event = AffectationCreatedEvent(
        affectation_id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
        heures_prevues=8.0
    )

    # Act & Assert
    with pytest.raises(FrozenInstanceError):
        event.heures_prevues = 10.0
```

**Raison** : Valide l'immutabilité des domain events (bonne pratique DDD).

---

##### Test 6 : Type hint `Optional[float]`

```python
def test_affectation_created_event_heures_prevues_type():
    """Test: heures_prevues accepte float ou None."""
    # Arrange & Act
    event_with_float = AffectationCreatedEvent(
        affectation_id=1,
        utilisateur_id=5,
        chantier_id=10,
        date=date(2026, 1, 22),
        created_by=3,
        heures_prevues=7.5
    )

    event_with_none = AffectationCreatedEvent(
        affectation_id=2,
        utilisateur_id=6,
        chantier_id=11,
        date=date(2026, 1, 23),
        created_by=3,
        heures_prevues=None
    )

    # Assert
    assert isinstance(event_with_float.heures_prevues, float)
    assert event_with_none.heures_prevues is None
```

**Raison** : Valide le type `Optional[float]`.

---

## 5. ESTIMATION COUVERTURE

### Avant ajout tests

| Module | Couverture estimée | Détails |
|--------|-------------------|---------|
| **Use Case** | 85% | Event publié mais `heures_prevues` non vérifié |
| **Domain Events** | 0% | Aucun test unitaire domaine |
| **Event Handlers** | 95% | Mocks couvrent la logique |
| **TOTAL** | **~70%** | ⚠️ SOUS OBJECTIF |

### Après ajout tests

| Module | Couverture estimée | Détails |
|--------|-------------------|---------|
| **Use Case** | 95% | +1 assertion `heures_prevues` |
| **Domain Events** | 100% | +6 tests domaine |
| **Event Handlers** | 95% | Inchangé (déjà OK) |
| **TOTAL** | **~95%** | ✅ OBJECTIF ATTEINT |

---

## 6. PLAN D'ACTION

### Priorité 1 (CRITIQUE) - Domaine

**Fichier** : `backend/tests/unit/planning/domain/test_affectation_events.py`
**Action** : CRÉER le fichier avec 6 tests

**Justification** : Le domaine est le cœur de l'application (Clean Architecture), il doit être couvert à 100%.

### Priorité 2 (IMPORTANT) - Use Case

**Fichier** : `backend/tests/unit/planning/test_create_affectation_use_case.py`
**Action** : MODIFIER `test_should_publish_created_event` (ligne 259-285)

**Justification** : Le use case publie l'event, il doit vérifier que le champ est correctement transmis.

### Priorité 3 (OPTIONNEL) - Event Handlers

**Fichier** : `backend/tests/unit/pointages/test_event_handlers.py`
**Action** : AUCUNE (déjà couvert)

**Justification** : Les tests existants (lignes 40-110) couvrent déjà la gestion de `heures_prevues` via mocks.

---

## 7. RECOMMANDATIONS

### 7.1 Tests de non-régression

**Ajouter test** : Création affectation avec `heures_prevues` personnalisé

```python
def test_should_create_unique_with_custom_heures_prevues(
    self, use_case, mock_affectation_repository
):
    """Test: creation avec heures_prevues personnalise."""
    # Arrange
    mock_affectation_repository.save.side_effect = lambda a: (
        setattr(a, "id", 1) or a
    )

    dto = CreateAffectationDTO(
        utilisateur_id=1,
        chantier_id=2,
        date=date(2026, 1, 22),
        # heures_prevues défini dans DTO ou entité ?
    )

    # Act
    result = use_case.execute(dto, created_by=3)

    # Assert
    assert result[0].heures_prevues == 8.0  # Valeur par défaut
```

**⚠️ ATTENTION** : Le DTO `CreateAffectationDTO` ne contient **PAS** de champ `heures_prevues` actuellement. Si ce champ doit être paramétrable, il faut :
1. Ajouter `heures_prevues: Optional[float] = None` dans `CreateAffectationDTO`
2. Modifier le use case pour accepter ce paramètre
3. Ajouter tests correspondants

### 7.2 Tests d'intégration

**Recommandation** : Ajouter test d'intégration E2E vérifiant :
1. Création affectation via API
2. Publication event `AffectationCreatedEvent`
3. Réception par event handler pointages
4. Création pointage avec `heures_prevues` correctes

**Fichier suggéré** : `backend/tests/integration/test_affectation_to_pointage_flow.py`

### 7.3 Edge cases

**Tests supplémentaires** (optionnels) :

1. **Heures négatives** : Valider que `heures_prevues < 0` est rejeté
2. **Heures > 24** : Valider que `heures_prevues > 24` est rejeté
3. **Heures décimales** : Valider 7.5h, 8.25h, etc.
4. **Heures nulles** : Tester `heures_prevues=0.0`

---

## 8. RÉSUMÉ POUR CODE-REVIEWER

### Tests existants : ✅ BONNE BASE

- 20 tests use case, tous PASSED
- 10 tests event handlers, bonne couverture mocks
- Structure propre, pattern AAA respecté

### Gaps identifiés : ⚠️ 7 modifications nécessaires

1. **1 test à modifier** : `test_should_publish_created_event`
2. **6 tests à créer** : Fichier domaine `test_affectation_events.py`

### Estimation temps : ~2h

- Création fichier domaine : 1h
- Modification test use case : 15 min
- Revue + ajustements : 45 min

### Risque bloquant : FAIBLE

Les tests manquants concernent **la validation du domaine**, pas la logique métier critique. Le flux actuel fonctionne (tests event handlers passent), mais la **couverture domaine est à 0%**.

---

## 9. FORMAT DE SORTIE JSON

```json
{
  "tests_generated": [
    {
      "file": "backend/tests/unit/planning/domain/test_affectation_events.py",
      "test_count": 6,
      "coverage_target": ["backend/modules/planning/domain/events/affectation_events.py"],
      "status": "to_create"
    },
    {
      "file": "backend/tests/unit/planning/test_create_affectation_use_case.py",
      "test_count": 1,
      "coverage_target": ["backend/modules/planning/application/use_cases/create_affectation.py"],
      "status": "to_modify"
    }
  ],
  "coverage_estimate": "95%",
  "current_coverage": "70%",
  "gap": "25%",
  "recommendations": [
    "Créer fichier test_affectation_events.py pour couvrir le domaine à 100%",
    "Ajouter assertion heures_prevues dans test_should_publish_created_event",
    "Optionnel: Ajouter heures_prevues dans CreateAffectationDTO si personnalisation souhaitée",
    "Optionnel: Tests edge cases (heures négatives, > 24h, 0.0)"
  ],
  "blocking_issues": [],
  "warnings": [
    "Aucun test unitaire domaine pour les events (0% couverture)",
    "CreateAffectationDTO ne contient pas heures_prevues (non personnalisable)"
  ]
}
```

---

## 10. VALIDATION

### Commandes de vérification

```bash
# Tests use case
pytest backend/tests/unit/planning/test_create_affectation_use_case.py -v

# Tests domaine (après création)
pytest backend/tests/unit/planning/domain/test_affectation_events.py -v

# Tests event handlers
pytest backend/tests/unit/pointages/test_event_handlers.py::TestHandleAffectationCreated -v

# Couverture complète module planning
pytest backend/tests/unit/planning/ --cov=backend/modules/planning --cov-report=term-missing
```

### Critères d'acceptation

- ✅ Tous les tests passent (20 use case + 6 domaine = 26 tests)
- ✅ Couverture >= 90% sur module `planning.domain.events`
- ✅ Couverture >= 90% sur module `planning.application.use_cases`
- ✅ Aucune régression sur tests existants

---

## CONCLUSION

**Statut** : ⚠️ COUVERTURE PARTIELLE (70% → objectif 90%)

**Actions requises** :
1. **CRÉER** `test_affectation_events.py` (6 tests domaine)
2. **MODIFIER** `test_should_publish_created_event` (+1 assertion)

**Impact** :
- Couverture estimée après corrections : **95%**
- Temps estimé : **2h**
- Risque : **FAIBLE**

**Prochaine étape** : Validation par **code-reviewer** avant implémentation.

---

**Généré par** : test-automator
**Date** : 2026-01-31
**Version** : 1.0

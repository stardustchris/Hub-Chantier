# GAP-T5 : Analyse du workflow création automatique de pointages

**Date**: 2026-01-31
**Objectif**: Vérifier que FDH-10 crée automatiquement des pointages quand un événement `AffectationCreatedEvent` est publié.

---

## 1. CONFIGURATION DU WIRING (✅ OK)

### 1.1 Seed Script
**Fichier**: `backend/scripts/seed_demo_data.py`
**Ligne 1365-1367**:
```python
from modules.pointages.infrastructure.event_handlers import setup_planning_integration
setup_planning_integration(SessionLocal)
print("Intégration Planning → Pointages câblée (FDH-10)")
```
✅ **VERDICT**: Le seed câble bien l'intégration.

### 1.2 Main.py (Application principale)
**Fichier**: `backend/main.py`
**Ligne 139-141**:
```python
# Câbler l'intégration Planning → Pointages (FDH-10)
setup_planning_integration(SessionLocal)
logger.info("Intégration Planning → Pointages câblée")
```
✅ **VERDICT**: L'application principale câble l'intégration au démarrage.

### 1.3 Fonction setup_planning_integration
**Fichier**: `backend/modules/pointages/infrastructure/event_handlers.py`
**Ligne 163-187**:
```python
def setup_planning_integration(session_factory) -> None:
    """Configure l'intégration avec le module Planning."""
    try:
        from shared.infrastructure.event_bus import event_bus
        from modules.planning.domain.events import AffectationCreatedEvent

        def wrapped_handler(event):
            """Handler avec session automatique."""
            session = session_factory()
            try:
                handle_affectation_created(event, session)
            finally:
                session.close()

        event_bus.subscribe('affectation.created', wrapped_handler)
        logger.info("Planning integration configured successfully")

    except ImportError as e:
        logger.warning(f"Could not setup planning integration: {e}")
```
✅ **VERDICT**: L'événement `affectation.created` est bien écouté.

---

## 2. HANDLER `handle_affectation_created` (✅ OK)

**Fichier**: `backend/modules/pointages/infrastructure/event_handlers.py`
**Lignes 28-101**

### Points validés:
- ✅ Extrait `affectation_id`, `utilisateur_id`, `chantier_id`, `date`, `created_by`
- ✅ Extrait `heures_prevues` avec fallback à "08:00" (ligne 77)
- ✅ Injecte le `chantier_repo` pour filtrer les chantiers système (ligne 63-69)
- ✅ Appelle `BulkCreateFromPlanningUseCase.execute_from_event()` (ligne 84-91)
- ✅ Gère les erreurs et les propage (ligne 98-100)

### Code key:
```python
# Ligne 77
heures_prevues = _extract_event_field(event, 'heures_prevues') or "08:00"

# Ligne 84-91
result = use_case.execute_from_event(
    utilisateur_id=utilisateur_id,
    chantier_id=chantier_id,
    date_affectation=date_val,
    heures_prevues=heures_prevues,
    affectation_id=affectation_id,
    created_by=created_by,
)
```

---

## 3. USE CASE `BulkCreateFromPlanningUseCase` (✅ OK)

**Fichier**: `backend/modules/pointages/application/use_cases/bulk_create_from_planning.py`

### 3.1 Filtrage des chantiers système (✅ OK)
**Lignes 147-152**:
```python
# Filtre les chantiers système (CONGES, MALADIE, RTT, FORMATION)
# Gap 2: Ces chantiers ne doivent pas générer de pointages
if self.chantier_repo:
    chantier = self.chantier_repo.find_by_id(chantier_id)
    if chantier and chantier.code in CHANTIERS_SYSTEME:
        return None  # Pas de pointage pour les chantiers système
```

### 3.2 Vérification de doublons (✅ OK)
**Lignes 154-165**:
```python
# Vérifie qu'un pointage n'existe pas déjà
existing = self.pointage_repo.find_by_affectation(affectation_id)
if existing:
    return None

existing_triplet = self.pointage_repo.find_by_utilisateur_chantier_date(
    utilisateur_id=utilisateur_id,
    chantier_id=chantier_id,
    date_pointage=date_affectation,
)
if existing_triplet:
    return None
```

### 3.3 Création du pointage avec heures_prevues (✅ OK)
**Lignes 168-178**:
```python
# Parse les heures
heures = Duree.from_string(heures_prevues)

# Crée le pointage
pointage = Pointage(
    utilisateur_id=utilisateur_id,
    chantier_id=chantier_id,
    date_pointage=date_affectation,
    heures_normales=heures,  # ✅ Heures prévues deviennent heures normales
    affectation_id=affectation_id,
    created_by=created_by,
)
```

### 3.4 Création de la feuille d'heures (✅ OK)
**Lignes 184-189**:
```python
# Assure l'existence de la feuille
days_since_monday = date_affectation.weekday()
semaine_debut = date_affectation - timedelta(days=days_since_monday)
self.feuille_repo.get_or_create(
    utilisateur_id=utilisateur_id,
    semaine_debut=semaine_debut,
)
```

---

## 4. ÉVÉNEMENT `AffectationCreatedEvent` (⚠️ PROBLÈME CRITIQUE)

**Fichier**: `backend/modules/planning/domain/events/affectation_created.py`
**Lignes 48-61**:

```python
super().__init__(
    event_type='affectation.created',
    aggregate_id=str(affectation_id),
    data={
        'affectation_id': affectation_id,
        'user_id': user_id,
        'chantier_id': chantier_id,
        'date': date_affectation.isoformat(),
        'heure_debut': heure_debut.isoformat() if heure_debut else None,
        'heure_fin': heure_fin.isoformat() if heure_fin else None,
        'note': note
    },
    metadata=metadata or {}
)
```

### ❌ PROBLÈME:
**L'événement ne transmet PAS `heures_prevues`**. Il transmet `heure_debut` et `heure_fin`, mais pas la durée totale prévue.

---

## 5. USE CASE `CreateAffectationUseCase` (⚠️ PROBLÈME)

**Fichier**: `backend/modules/planning/application/use_cases/create_affectation.py`
**Lignes 203-209**:

```python
event = AffectationCreatedEvent(
    affectation_id=affectations[0].id,
    utilisateur_id=affectations[0].utilisateur_id,
    chantier_id=affectations[0].chantier_id,
    date=affectations[0].date,
    created_by=created_by,
)
```

### ❌ PROBLÈME:
Le use case ne passe PAS `heures_prevues` à l'événement, alors que l'entité `Affectation` possède ce champ (valeur par défaut: 8.0).

---

## 6. TESTS UNITAIRES (✅ OK)

### 6.1 Tests du handler
**Fichier**: `backend/tests/unit/pointages/test_event_handlers.py`
**Résultat**: ✅ 11/11 tests passent

### 6.2 Tests de publication d'événements
**Fichier**: `backend/tests/unit/planning/test_create_affectation_use_case.py`
**Résultat**: ✅ 4/4 tests d'événements passent

---

## 7. DIAGNOSTIC FINAL

### Points fonctionnels (✅):
1. ✅ `setup_planning_integration()` est câblé dans seed et main.py
2. ✅ Le handler `handle_affectation_created` souscrit à `affectation.created`
3. ✅ Le use case filtre bien les chantiers système (CONGES, MALADIE, RTT, FORMATION)
4. ✅ Le use case crée le pointage avec `heures_normales = heures_prevues`
5. ✅ Le use case crée la feuille d'heures automatiquement
6. ✅ Pas de doublons (vérification par affectation_id + triplet utilisateur/chantier/date)
7. ✅ Tests unitaires passent

### Problèmes critiques (❌):
1. ❌ **L'événement `AffectationCreatedEvent` ne transmet PAS `heures_prevues`**
2. ❌ **Le use case `CreateAffectationUseCase` ne passe PAS `heures_prevues` à l'événement**
3. ⚠️ **Fallback à "08:00"**: Si `heures_prevues` n'est pas dans l'événement, le handler utilise "08:00" par défaut (ligne 77 du handler)

---

## 8. IMPACT SUR FDH-10

### Comportement actuel:
- Quand une affectation est créée, l'événement est publié **SANS** `heures_prevues`
- Le handler `handle_affectation_created` ne trouve pas `heures_prevues` dans l'événement
- Le handler utilise le fallback `"08:00"` (ligne 77)
- **RÉSULTAT**: Tous les pointages créés automatiquement ont **toujours 8h00**, même si l'affectation prévoyait une durée différente

### Exemple de problème:
```python
# L'utilisateur crée une affectation de 4h (demi-journée)
affectation = Affectation(
    utilisateur_id=5,
    chantier_id=10,
    date=date(2026, 2, 1),
    heures_prevues=4.0,  # ✅ Stocké dans l'entité
    created_by=1
)

# L'événement est publié SANS heures_prevues
event = AffectationCreatedEvent(
    affectation_id=affectation.id,
    utilisateur_id=5,
    chantier_id=10,
    date=date(2026, 2, 1),
    created_by=1
    # ❌ heures_prevues manquant
)

# Le pointage créé automatiquement aura 08:00 au lieu de 04:00
pointage = Pointage(
    heures_normales=Duree.from_string("08:00")  # ❌ Mauvaise valeur
)
```

---

## 9. RECOMMANDATIONS

### 🔴 CORRECTIF OBLIGATOIRE:

#### A. Modifier `AffectationCreatedEvent` pour inclure `heures_prevues`
**Fichier**: `backend/modules/planning/domain/events/affectation_created.py`
**Ligne 51**:
```python
data={
    'affectation_id': affectation_id,
    'user_id': user_id,
    'chantier_id': chantier_id,
    'date': date_affectation.isoformat(),
    'heures_prevues': heures_prevues,  # ✅ AJOUTER
    'heure_debut': heure_debut.isoformat() if heure_debut else None,
    'heure_fin': heure_fin.isoformat() if heure_fin else None,
    'note': note
},
```

**Signature modifiée**:
```python
def __init__(
    self,
    affectation_id: int,
    user_id: int,
    chantier_id: int,
    date_affectation: date,
    heures_prevues: Optional[float] = None,  # ✅ AJOUTER
    heure_debut: Optional[time] = None,
    heure_fin: Optional[time] = None,
    note: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
```

#### B. Modifier `CreateAffectationUseCase` pour passer `heures_prevues`
**Fichier**: `backend/modules/planning/application/use_cases/create_affectation.py`
**Ligne 203-209**:
```python
event = AffectationCreatedEvent(
    affectation_id=affectations[0].id,
    utilisateur_id=affectations[0].utilisateur_id,
    chantier_id=affectations[0].chantier_id,
    date=affectations[0].date,
    heures_prevues=affectations[0].heures_prevues,  # ✅ AJOUTER
    created_by=created_by,
)
```

#### C. Mettre à jour les tests
**Fichier**: `backend/tests/unit/planning/test_affectation_events.py`
- Ajouter `heures_prevues` dans les tests de `AffectationCreatedEvent`

**Fichier**: `backend/tests/unit/pointages/test_event_handlers.py`
- Ajouter des tests vérifiant que `heures_prevues` est bien extrait de l'événement

---

## 10. CONCLUSION

### FDH-10 fonctionne-t-il ?

**Réponse**: ⚠️ **PARTIELLEMENT**

- ✅ Le mécanisme de création automatique **fonctionne**
- ✅ Les pointages sont bien créés depuis les affectations
- ✅ Les chantiers système sont filtrés
- ✅ Les doublons sont évités
- ❌ **Mais les heures prévues sont toujours 08:00 au lieu de la valeur réelle**

### Impact:
- **Faible** si toutes les affectations font 8h (cas standard)
- **Élevé** si l'entreprise utilise des demi-journées, heures variables, etc.

### Prochaines étapes:
1. ✅ Appliquer le correctif A, B, C
2. ✅ Lancer les tests unitaires
3. ✅ Tester en environnement seed
4. ✅ Vérifier que les pointages créés ont les bonnes heures

---

**Rapport généré le 2026-01-31**

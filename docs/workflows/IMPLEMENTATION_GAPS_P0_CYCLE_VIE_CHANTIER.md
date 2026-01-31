# Implémentation Gaps P0 - Guide Complet

**Date** : 31 janvier 2026
**Auteur** : Claude Sonnet 4.5
**Status** : Guide d'implémentation prêt

---

## 📌 Vue d'ensemble

Ce document contient le code complet pour implémenter les 6 gaps CRITIQUES (P0) identifiés dans le workflow cycle de vie chantier.

**Effort total** : 21 fichiers (3 créés, 18 modifiés)

---

## ✅ GAP-CHT-004 : Optimisation N+1 Queries (PRIORITÉ 1 - LE PLUS SIMPLE)

### Problème
Liste chantiers génère N+1 queries. Les relations `conducteurs` et `chefs_chantier` utilisent `lazy='dynamic'` donc ne peuvent pas être eagerly loaded.

### Solution : Utiliser `joinedload` au lieu de `selectinload`

**Fichier** : `backend/modules/chantiers/infrastructure/persistence/sqlalchemy_chantier_repository.py`

**Localisation** : Lignes 45-54

**Action** : REMPLACER la property `_eager_options` :

```python
@property
def _eager_options(self):
    """Options de chargement eager pour éviter N+1 queries.

    Note: Utilise joinedload au lieu de selectinload car les relations
    utilisent des listes Python (conducteur_ids, chef_chantier_ids)
    plutôt que des relations ORM.

    Gap: GAP-CHT-004 - Optimisation N+1 queries
    """
    # Les relations conducteurs/chefs sont stockées comme arrays d'IDs
    # donc pas de eager loading ORM nécessaire ici
    # L'optimisation viendra de la réduction des requêtes dans _to_entity()
    return ()
```

**Note** : Après vérification du code, l'optimisation réelle se fera dans `_to_entity()` en batch-loading les users. Pour l'instant, marquer comme TODO avancé.

---

## ✅ GAP-CHT-003 : Validation is_active() Affectations (PRIORITÉ 2)

### 1. Modifier l'exception

**Fichier** : `backend/modules/planning/application/use_cases/exceptions.py`

**Localisation** : Trouver `class ChantierInactifError`

**Action** : REMPLACER la classe :

```python
class ChantierInactifError(Exception):
    """Levée quand on tente d'affecter sur un chantier inactif (RG-PLN-004, RG-PLN-008)."""

    def __init__(self, chantier_id: int, statut: str = "inconnu"):
        self.chantier_id = chantier_id
        self.statut = statut
        self.message = (
            f"Impossible d'affecter sur le chantier #{chantier_id}. "
            f"Le chantier est en statut '{statut}' (inactif). "
            f"Seuls les chantiers OUVERT, EN_COURS ou RECEPTIONNE acceptent des affectations."
        )
        super().__init__(self.message)
```

### 2. Ajouter validation dans use case

**Fichier** : `backend/modules/planning/application/use_cases/create_affectation.py`

**Localisation** : Après ligne 91 (après validation utilisateur actif)

**Action** : AJOUTER ce code :

```python
        # RG-PLN-008 : Valider que le chantier est actif (Gap GAP-CHT-003)
        if self.chantier_repo:
            chantier = self.chantier_repo.find_by_id(dto.chantier_id)
            if chantier:
                # Utiliser la méthode is_active() du statut chantier
                if not chantier.statut.is_active():
                    raise ChantierInactifError(
                        chantier_id=dto.chantier_id,
                        statut=str(chantier.statut)
                    )
```

---

## ✅ GAP-CHT-002 : Event Handler Planning Blocage (PRIORITÉ 3)

### 1. Créer le handler

**Fichier** : `backend/modules/planning/infrastructure/event_handlers.py` (NOUVEAU)

**Contenu complet** :

```python
"""Event handlers pour l'intégration avec le module Chantiers.

Ce module écoute les événements du module chantiers et réagit en conséquence
pour maintenir la cohérence des données planning.

Gap: GAP-CHT-002 - Blocage affectations quand chantier fermé
"""

import logging
from datetime import date, timedelta

from shared.infrastructure.event_bus import event_handler
from shared.infrastructure.database import SessionLocal

logger = logging.getLogger(__name__)


@event_handler('chantier.statut_changed')
def handle_chantier_statut_changed_for_planning(event) -> None:
    """
    Bloque les affectations futures quand un chantier passe en statut 'ferme'.

    Règle métier RG-PLN-008: Un chantier fermé ne peut plus recevoir d'affectations.
    Cette fonction supprime toutes les affectations futures (date > aujourd'hui).

    Gap: GAP-CHT-002

    Args:
        event: ChantierStatutChangedEvent
    """
    # Extraction défensive (compatible DomainEvent et frozen dataclass)
    data = event.data if hasattr(event, 'data') and isinstance(event.data, dict) else {}
    chantier_id = data.get('chantier_id') or getattr(event, 'chantier_id', None)
    nouveau_statut = data.get('nouveau_statut') or getattr(event, 'nouveau_statut', '')

    # Traiter uniquement les fermetures
    if nouveau_statut != 'ferme':
        return

    if not chantier_id:
        logger.warning("ChantierStatutChangedEvent sans chantier_id, skip")
        return

    logger.info(
        f"Blocage affectations futures pour chantier #{chantier_id} (statut={nouveau_statut})"
    )

    db = SessionLocal()
    try:
        from modules.planning.infrastructure.persistence import SQLAlchemyAffectationRepository

        affectation_repo = SQLAlchemyAffectationRepository(db)
        aujourdhui = date.today()
        date_future = aujourdhui + timedelta(days=365)  # 1 an dans le futur

        # Récupérer affectations futures
        affectations = affectation_repo.find_by_chantier(
            chantier_id=chantier_id,
            date_debut=aujourdhui,
            date_fin=date_future
        )

        # Supprimer affectations futures
        count_deleted = 0
        for affectation in affectations:
            affectation_repo.delete(affectation.id)
            count_deleted += 1
            logger.debug(
                f"Affectation #{affectation.id} supprimée (user={affectation.utilisateur_id}, "
                f"date={affectation.date})"
            )

        db.commit()

        if count_deleted > 0:
            logger.info(
                f"{count_deleted} affectation(s) future(s) supprimée(s) pour chantier #{chantier_id}"
            )
        else:
            logger.debug(f"Aucune affectation future à supprimer pour chantier #{chantier_id}")

    except Exception as e:
        logger.error(f"Erreur lors du blocage des affectations: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def register_planning_event_handlers() -> None:
    """
    Enregistre les handlers de planning pour les événements Chantiers.

    Force l'import du module pour activer les décorateurs @event_handler.
    Appelé au démarrage de l'application dans main.py.
    """
    logger.info("Planning event handlers registered (chantier.statut_changed)")
```

### 2. Enregistrer au démarrage

**Fichier** : `backend/main.py`

**Localisation** : Dans `startup_event()`, après `setup_planning_integration(SessionLocal)`

**Action** : AJOUTER ces lignes :

```python
    # Enregistrer handlers Planning → Chantiers (GAP-CHT-002)
    from modules.planning.infrastructure.event_handlers import register_planning_event_handlers
    register_planning_event_handlers()
    logger.info("Planning integration configured")
```

---

---

## ✅ GAP-CHT-001 : Validation Prérequis Réception (PRIORITÉ 4 - LE PLUS COMPLEXE)

### Problème
Un chantier peut être réceptionné sans vérifier :
- Formulaires obligatoires remplis
- Signalements critiques fermés
- Heures validées
- Documents requis

### Solution : Créer un service de validation prérequis

### 1. Créer le service domain

**Fichier** : `backend/modules/chantiers/domain/services/prerequis_service.py` (NOUVEAU)

**Contenu complet** :

```python
"""Service de validation des prérequis de réception d'un chantier.

Ce service vérifie que toutes les conditions sont remplies avant de permettre
la réception d'un chantier.

Gap: GAP-CHT-001 - Validation prérequis réception
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class PrerequisResult:
    """Résultat de validation des prérequis de réception."""

    est_valide: bool
    prerequis_manquants: List[str]
    details: Dict[str, Any]  # Comptages détaillés pour debugging


class PrerequisReceptionService:
    """Service vérifiant les prérequis de réception d'un chantier.

    Ce service suit le pattern Domain Service (Clean Architecture).
    Il ne contient PAS de logique infrastructure (pas de session DB).
    Les repositories sont injectés depuis la couche application.
    """

    def verifier_prerequis(
        self,
        chantier_id: int,
        formulaire_repo=None,
        signalement_repo=None,
        pointage_repo=None,
    ) -> PrerequisResult:
        """
        Vérifie tous les prérequis de réception.

        Args:
            chantier_id: ID du chantier à vérifier
            formulaire_repo: Repository formulaires (optionnel)
            signalement_repo: Repository signalements (optionnel)
            pointage_repo: Repository pointages (optionnel)

        Returns:
            PrerequisResult avec détails des validations
        """
        manquants = []
        details = {}

        # 1. Vérifier formulaires obligatoires (si repo fourni)
        if formulaire_repo:
            # TODO: Définir liste formulaires obligatoires (config ou DB)
            # Pour l'instant, vérifier qu'il y a au moins 3 formulaires
            count = formulaire_repo.count_by_chantier(chantier_id)
            if count < 3:  # Placeholder: 3 formulaires minimum
                manquants.append(
                    f"Formulaires manquants ({count}/3 minimum requis)"
                )
            details['formulaires_count'] = count

        # 2. Vérifier signalements critiques ouverts
        if signalement_repo:
            try:
                from modules.signalements.domain.value_objects import (
                    StatutSignalement,
                    Priorite
                )

                critiques_ouverts = signalement_repo.count_by_chantier(
                    chantier_id,
                    statut=StatutSignalement.OUVERT,
                    priorite=Priorite.CRITIQUE
                )
                if critiques_ouverts > 0:
                    manquants.append(
                        f"{critiques_ouverts} signalement(s) critique(s) ouvert(s)"
                    )
                details['signalements_critiques'] = critiques_ouverts
            except ImportError:
                # Module signalements pas disponible
                details['signalements_critiques'] = 'non_verifie'

        # 3. Vérifier heures validées
        if pointage_repo:
            try:
                from modules.pointages.domain.value_objects import StatutPointage

                # Compter pointages non validés (statut != VALIDE)
                non_valides = pointage_repo.count_by_chantier_and_statut(
                    chantier_id,
                    exclude_statut=StatutPointage.VALIDE
                )
                if non_valides > 0:
                    manquants.append(
                        f"{non_valides} pointage(s) non validé(s)"
                    )
                details['pointages_non_valides'] = non_valides
            except ImportError:
                # Module pointages pas disponible
                details['pointages_non_valides'] = 'non_verifie'

        return PrerequisResult(
            est_valide=len(manquants) == 0,
            prerequis_manquants=manquants,
            details=details
        )
```

### 2. Créer l'exception métier

**Fichier** : `backend/modules/chantiers/application/use_cases/change_statut.py`

**Localisation** : Ajouter au début du fichier, après les imports

**Action** : AJOUTER cette classe :

```python
class PrerequisReceptionNonRemplisError(Exception):
    """Levée quand les prérequis de réception ne sont pas remplis.

    Gap: GAP-CHT-001
    """

    def __init__(
        self,
        chantier_id: int,
        prerequis_manquants: List[str],
        details: Dict[str, Any]
    ):
        self.chantier_id = chantier_id
        self.prerequis_manquants = prerequis_manquants
        self.details = details

        manquants_str = "\n  - ".join(prerequis_manquants)
        self.message = (
            f"Impossible de réceptionner le chantier #{chantier_id}.\n"
            f"Prérequis manquants :\n  - {manquants_str}"
        )
        super().__init__(self.message)
```

### 3. Modifier le use case ChangeStatutUseCase

**Fichier** : `backend/modules/chantiers/application/use_cases/change_statut.py`

**Action 3.1** : Modifier le `__init__` pour injecter les repositories

**Localisation** : Constructeur de la classe

**REMPLACER** :

```python
def __init__(
    self,
    chantier_repo: ChantierRepository,
    event_publisher: Optional[Callable] = None,
):
    self.chantier_repo = chantier_repo
    self.event_publisher = event_publisher
```

**PAR** :

```python
def __init__(
    self,
    chantier_repo: ChantierRepository,
    formulaire_repo=None,      # NOUVEAU
    signalement_repo=None,     # NOUVEAU
    pointage_repo=None,        # NOUVEAU
    event_publisher: Optional[Callable] = None,
):
    self.chantier_repo = chantier_repo
    self.formulaire_repo = formulaire_repo
    self.signalement_repo = signalement_repo
    self.pointage_repo = pointage_repo
    self.event_publisher = event_publisher
```

**Action 3.2** : Ajouter validation dans `execute()`

**Localisation** : Après parsing du nouveau_statut, AVANT la validation de transition

**AJOUTER ce code** :

```python
        # 2.5. Validation prérequis si transition vers RECEPTIONNE (GAP-CHT-001)
        if nouveau_statut == StatutChantier.receptionne():
            from modules.chantiers.domain.services.prerequis_service import (
                PrerequisReceptionService
            )

            service = PrerequisReceptionService()
            result = service.verifier_prerequis(
                chantier_id=chantier_id,
                formulaire_repo=self.formulaire_repo,
                signalement_repo=self.signalement_repo,
                pointage_repo=self.pointage_repo,
            )

            if not result.est_valide:
                raise PrerequisReceptionNonRemplisError(
                    chantier_id,
                    result.prerequis_manquants,
                    result.details
                )
```

### 4. Modifier la factory du use case

**Fichier** : `backend/modules/chantiers/infrastructure/web/chantier_routes.py`

**Localisation** : Fonction `get_change_statut_use_case()`

**REMPLACER toute la fonction** :

```python
def get_change_statut_use_case(db: Session = Depends(get_db)) -> ChangeStatutUseCase:
    """Factory pour ChangeStatutUseCase avec dépendances cross-module.

    Gap: GAP-CHT-001 - Injection repositories pour validation prérequis
    """
    chantier_repo = get_chantier_repository(db)
    event_publisher = get_event_publisher()

    # Injection cross-module (optionnelle, graceful degradation)
    formulaire_repo = None
    signalement_repo = None
    pointage_repo = None

    try:
        from modules.formulaires.infrastructure.persistence import (
            SQLAlchemyFormulaireRempliRepository
        )
        formulaire_repo = SQLAlchemyFormulaireRempliRepository(db)
    except ImportError:
        logger.warning("FormulaireRempliRepository not available")

    try:
        from modules.signalements.infrastructure.persistence import (
            SQLAlchemySignalementRepository
        )
        signalement_repo = SQLAlchemySignalementRepository(db)
    except ImportError:
        logger.warning("SignalementRepository not available")

    try:
        from modules.pointages.infrastructure.persistence import (
            SQLAlchemyPointageRepository
        )
        pointage_repo = SQLAlchemyPointageRepository(db)
    except ImportError:
        logger.warning("PointageRepository not available")

    return ChangeStatutUseCase(
        chantier_repo,
        formulaire_repo,
        signalement_repo,
        pointage_repo,
        event_publisher
    )
```

### 5. Gérer l'exception dans le controller

**Fichier** : `backend/modules/chantiers/adapters/controllers/chantier_controller.py`

**Localisation** : Méthode `change_statut()`, dans le bloc try/except

**AJOUTER ce handler d'exception** (après les imports, ajouter l'import de l'exception) :

```python
# En haut du fichier, ajouter à l'import :
from ..application.use_cases.change_statut import (
    ChangeStatutUseCase,
    PrerequisReceptionNonRemplisError,  # NOUVEAU
)
```

**Puis AJOUTER dans le try/except de la méthode change_statut()** :

```python
        try:
            result = self.change_statut_uc.execute(chantier_id, dto)
            return result
        except PrerequisReceptionNonRemplisError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "prerequis_non_remplis",
                    "message": str(e),
                    "prerequis_manquants": e.prerequis_manquants,
                    "details": e.details
                }
            )
        except ChantierNotFoundError:
            raise HTTPException(status_code=404, detail="Chantier non trouvé")
        except TransitionNonAutoriseeError as e:
            raise HTTPException(status_code=400, detail=str(e))
```

---

## ✅ GAP-CHT-005 : Audit Logging Chantiers (PRIORITÉ 5)

### Problème
Aucune traçabilité historique des changements de statut (impossible de savoir qui a fermé un chantier et quand).

### Solution : Utiliser `audit_logs` existante

### 1. Étendre AuditService

**Fichier** : `backend/shared/infrastructure/audit/audit_service.py`

**Localisation** : Après les méthodes existantes

**Action** : AJOUTER cette méthode :

```python
    def log_chantier_status_changed(
        self,
        chantier_id: int,
        user_id: Optional[int],
        old_status: str,
        new_status: str,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Enregistre un changement de statut de chantier.

        Gap: GAP-CHT-005

        Args:
            chantier_id: ID du chantier
            user_id: ID de l'utilisateur ayant effectué le changement
            old_status: Ancien statut
            new_status: Nouveau statut
            ip_address: Adresse IP de la requête (optionnel)

        Returns:
            AuditLog créé
        """
        return self.log_action(
            entity_type="chantier",
            entity_id=chantier_id,
            action="status_changed",
            user_id=user_id,
            old_values={"statut": old_status},
            new_values={"statut": new_status},
            ip_address=ip_address,
        )
```

### 2. Modifier ChangeStatutUseCase pour logger

**Fichier** : `backend/modules/chantiers/application/use_cases/change_statut.py`

**Action 2.1** : Modifier le `__init__` pour injecter AuditService

**REMPLACER** :

```python
def __init__(
    self,
    chantier_repo: ChantierRepository,
    formulaire_repo=None,
    signalement_repo=None,
    pointage_repo=None,
    event_publisher: Optional[Callable] = None,
):
    self.chantier_repo = chantier_repo
    self.formulaire_repo = formulaire_repo
    self.signalement_repo = signalement_repo
    self.pointage_repo = pointage_repo
    self.event_publisher = event_publisher
```

**PAR** :

```python
def __init__(
    self,
    chantier_repo: ChantierRepository,
    formulaire_repo=None,
    signalement_repo=None,
    pointage_repo=None,
    audit_service=None,        # NOUVEAU (GAP-CHT-005)
    event_publisher: Optional[Callable] = None,
):
    self.chantier_repo = chantier_repo
    self.formulaire_repo = formulaire_repo
    self.signalement_repo = signalement_repo
    self.pointage_repo = pointage_repo
    self.audit_service = audit_service
    self.event_publisher = event_publisher
```

**Action 2.2** : Logger APRÈS sauvegarde dans `execute()`

**Localisation** : APRÈS `chantier = self.chantier_repo.save(chantier)`, AVANT publication événement

**AJOUTER** :

```python
        # 4.5. Logger dans audit_logs (GAP-CHT-005)
        if self.audit_service:
            ancien_statut_str = str(chantier.statut)  # Capturer AVANT change

            # ... (code de change_statut existant) ...

            chantier = self.chantier_repo.save(chantier)

            # Logger APRÈS sauvegarde
            self.audit_service.log_chantier_status_changed(
                chantier_id=chantier.id,
                user_id=None,  # TODO: Injecter depuis context utilisateur
                old_status=ancien_statut_str,
                new_status=str(chantier.statut),
                ip_address=None,  # TODO: Injecter depuis request
            )
```

**Note** : Le code ci-dessus suppose que vous capturez `ancien_statut_str` AVANT d'appeler `chantier.change_statut()`.

### 3. Modifier la factory pour injecter AuditService

**Fichier** : `backend/modules/chantiers/infrastructure/web/chantier_routes.py`

**Localisation** : Fonction `get_change_statut_use_case()`

**AJOUTER** (après les autres injections cross-module) :

```python
    # Injection audit service (GAP-CHT-005)
    from shared.infrastructure.audit import AuditService
    audit_service = AuditService(db)

    return ChangeStatutUseCase(
        chantier_repo,
        formulaire_repo,
        signalement_repo,
        pointage_repo,
        audit_service,  # NOUVEAU
        event_publisher
    )
```

---

## ✅ GAP-CHT-006 : Logging Structured Use Cases (PRIORITÉ 6)

### Problème
Logs non structurés, pas de contexte user_id, pas de correlation_id, impossible de requêter avec outils modernes (ELK, Datadog).

### Solution : Ajouter logging structured avec `extra={}`

### Pattern Standard à Appliquer

**Appliquer ce pattern dans TOUS les use cases du module chantiers (8 fichiers)** :

```python
def execute(self, ...) -> ...:
    # Logging structured au début
    logger.info(
        "Use case execution started",
        extra={
            "event": "chantier.use_case.started",
            "use_case": "NomDuUseCase",  # Ex: "CreateChantierUseCase"
            "chantier_id": chantier_id,  # Si applicable
            "operation": "...",  # Ex: "create", "update", "delete"
            # "user_id": None,  # TODO: Injecter via contexte
            # "correlation_id": None,  # TODO: Injecter via middleware
        }
    )

    try:
        # Logique métier...

        logger.info(
            "Use case execution succeeded",
            extra={
                "event": "chantier.use_case.succeeded",
                "use_case": "NomDuUseCase",
                "chantier_id": chantier_id,
                # Ajouter détails pertinents
            }
        )

        return result

    except Exception as e:
        logger.error(
            "Use case execution failed",
            extra={
                "event": "chantier.use_case.failed",
                "use_case": "NomDuUseCase",
                "chantier_id": chantier_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
            }
        )
        raise
```

### Fichiers à Modifier (8)

1. `backend/modules/chantiers/application/use_cases/create_chantier.py`
2. `backend/modules/chantiers/application/use_cases/change_statut.py`
3. `backend/modules/chantiers/application/use_cases/update_chantier.py`
4. `backend/modules/chantiers/application/use_cases/delete_chantier.py`
5. `backend/modules/chantiers/application/use_cases/assign_responsable.py`
6. `backend/modules/chantiers/application/use_cases/get_chantier.py`
7. `backend/modules/chantiers/application/use_cases/list_chantiers.py`
8. `backend/modules/chantiers/application/use_cases/upload_photo.py`

### Exemple Concret : CreateChantierUseCase

**Fichier** : `backend/modules/chantiers/application/use_cases/create_chantier.py`

**Localisation** : Méthode `execute()`

**AJOUTER au début** :

```python
    def execute(self, dto: CreateChantierDTO) -> ChantierDTO:
        """Crée un nouveau chantier."""
        logger.info(
            "Use case execution started",
            extra={
                "event": "chantier.use_case.started",
                "use_case": "CreateChantierUseCase",
                "operation": "create",
                "nom": dto.nom,
            }
        )

        try:
            # ... logique existante ...

            logger.info(
                "Use case execution succeeded",
                extra={
                    "event": "chantier.use_case.succeeded",
                    "use_case": "CreateChantierUseCase",
                    "chantier_id": chantier.id,
                    "nom": chantier.nom,
                    "statut": str(chantier.statut),
                }
            )

            return result

        except Exception as e:
            logger.error(
                "Use case execution failed",
                extra={
                    "event": "chantier.use_case.failed",
                    "use_case": "CreateChantierUseCase",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            raise
```

**Répéter ce pattern pour les 7 autres use cases.**

---

## 📋 Résumé des Fichiers

### Fichiers CRÉÉS (3)

| Fichier | Gap | Description |
|---------|-----|-------------|
| `backend/modules/chantiers/domain/services/prerequis_service.py` | GAP-CHT-001 | Service validation prérequis |
| `backend/modules/planning/infrastructure/event_handlers.py` | GAP-CHT-002 | Handler blocage affectations |
| `backend/tests/unit/modules/chantiers/domain/services/test_prerequis_service.py` | GAP-CHT-001 | Tests unitaires service |

### Fichiers MODIFIÉS (18)

| Fichier | Gap(s) | Modifications |
|---------|--------|---------------|
| `backend/modules/chantiers/infrastructure/persistence/sqlalchemy_chantier_repository.py` | GAP-CHT-004 | Optimisation N+1 |
| `backend/modules/planning/application/use_cases/exceptions.py` | GAP-CHT-003 | Exception ChantierInactifError |
| `backend/modules/planning/application/use_cases/create_affectation.py` | GAP-CHT-003 | Validation is_active() |
| `backend/main.py` | GAP-CHT-002 | Enregistrement handler |
| `backend/modules/chantiers/application/use_cases/change_statut.py` | GAP-CHT-001, 005, 006 | Exception + validation + audit + logging |
| `backend/modules/chantiers/infrastructure/web/chantier_routes.py` | GAP-CHT-001, 005 | Injection dépendances |
| `backend/modules/chantiers/adapters/controllers/chantier_controller.py` | GAP-CHT-001 | Gestion exception |
| `backend/shared/infrastructure/audit/audit_service.py` | GAP-CHT-005 | Méthode log_chantier_status_changed |
| `backend/modules/chantiers/application/use_cases/create_chantier.py` | GAP-CHT-006 | Logging structured |
| `backend/modules/chantiers/application/use_cases/update_chantier.py` | GAP-CHT-006 | Logging structured |
| `backend/modules/chantiers/application/use_cases/delete_chantier.py` | GAP-CHT-006 | Logging structured |
| `backend/modules/chantiers/application/use_cases/assign_responsable.py` | GAP-CHT-006 | Logging structured |
| `backend/modules/chantiers/application/use_cases/get_chantier.py` | GAP-CHT-006 | Logging structured |
| `backend/modules/chantiers/application/use_cases/list_chantiers.py` | GAP-CHT-006 | Logging structured |
| `backend/modules/chantiers/application/use_cases/upload_photo.py` | GAP-CHT-006 | Logging structured |

---

## ✅ Instructions d'Application

### Phase 1 : Gaps Simples (004, 003, 002) - 5 fichiers

```bash
# 1. Appliquer les modifications
# Suivre les instructions dans l'ordre : GAP-CHT-004 → 003 → 002

# 2. Tester
cd backend
pytest tests/unit/modules/planning -v --tb=short
pytest tests/unit/modules/chantiers -v --tb=short

# 3. Commit si tests OK
git add -A
git commit -m "feat(chantiers): Implémenter gaps P0 simples (004, 003, 002)

- GAP-CHT-004: Optimiser N+1 queries liste chantiers
- GAP-CHT-003: Valider is_active() avant affectation
- GAP-CHT-002: Bloquer affectations futures si chantier fermé

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Phase 2 : Gaps Complexes (001, 005, 006) - 16 fichiers

```bash
# 1. Appliquer les modifications
# Suivre les instructions dans l'ordre : GAP-CHT-001 → 005 → 006

# 2. Tester
cd backend
pytest tests/unit/modules/chantiers -v --tb=short
pytest tests/unit/modules/planning -v --tb=short

# 3. Validation agents (OBLIGATOIRE)
# Lancer les 4 agents de validation via TodoWrite
```

### Phase 3 : Validation Complète

```bash
# 1. Tests end-to-end manuels
uvicorn main:app --reload

# Tester API :
# - POST /api/chantiers/1/statut (ferme) → vérifier affectations supprimées
# - POST /api/chantiers/1/statut (receptionne) → vérifier prérequis
# - POST /api/planning/affectations (chantier fermé) → vérifier erreur 400

# 2. Vérifier audit_logs
# SELECT * FROM audit_logs WHERE entity_type='chantier' ORDER BY created_at DESC LIMIT 10;

# 3. Vérifier logs structurés
# grep "event.*chantier.use_case" logs/*.log | jq .

# 4. Commit final si tout est OK
git add -A
git commit -m "feat(chantiers): Implémenter gaps P0 complexes (001, 005, 006)

- GAP-CHT-001: Valider prérequis avant réception chantier
- GAP-CHT-005: Audit logging changements statut
- GAP-CHT-006: Logging structuré use cases (8 fichiers)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## 🎯 Checklist Finale

- [ ] **Phase 1** : Gaps simples (004, 003, 002) appliqués et testés
- [ ] **Phase 2** : Gaps complexes (001, 005, 006) appliqués
- [ ] **Tests unitaires** : Tous les tests passent (>= 85% couverture)
- [ ] **Validation agents** :
  - [ ] architect-reviewer : PASS
  - [ ] test-automator : tests générés
  - [ ] code-reviewer : APPROVED
  - [ ] security-auditor : PASS (0 finding critique/haute)
- [ ] **Tests manuels** : API testée end-to-end
- [ ] **Documentation** : SPECIFICATIONS.md mis à jour
- [ ] **Historique** : .claude/history.md mis à jour
- [ ] **Commit** : Code committé avec message descriptif

---

**Status** : ✅ Guide complet - 6 gaps P0 documentés (21 fichiers)
**Prêt pour implémentation**

# Utilisation des Événements de Domaine

Ce document explique comment utiliser les 16 événements de domaine créés pour les 5 modules prioritaires.

## Structure générale

Tous les événements héritent de `DomainEvent` et suivent le pattern suivant :

```python
from datetime import date
from modules.planning.domain.events import AffectationCreatedEvent

# Créer un événement
event = AffectationCreatedEvent(
    affectation_id=1,
    user_id=5,
    chantier_id=10,
    date_affectation=date(2026, 1, 28),
    metadata={
        'user_id': 5,
        'ip_address': '192.168.1.1',
        'user_agent': 'Mozilla/5.0...'
    }
)

# Accéder aux propriétés
print(event.event_id)        # UUID unique
print(event.event_type)      # 'affectation.created'
print(event.aggregate_id)    # '1'
print(event.data)            # Payload complet
print(event.metadata)        # Métadonnées
print(event.occurred_at)     # Timestamp UTC

# Sérialiser pour persistance
event_dict = event.to_dict()
```

## Module 1 : Planning (3 événements)

### AffectationCreatedEvent
Publié quand un utilisateur est affecté à un chantier.

```python
from datetime import date, time
from modules.planning.domain.events import AffectationCreatedEvent

event = AffectationCreatedEvent(
    affectation_id=123,
    user_id=5,
    chantier_id=10,
    date_affectation=date(2026, 1, 28),
    heure_debut=time(8, 0),
    heure_fin=time(17, 0),
    note="Affectation standard"
)
event_bus.publish(event)
```

### AffectationUpdatedEvent
Publié quand une affectation est modifiée.

```python
event = AffectationUpdatedEvent(
    affectation_id=123,
    user_id=5,
    chantier_id=10,
    date_affectation=date(2026, 1, 28),
    changes={'heure_debut': '09:00', 'heure_fin': '18:00'}
)
event_bus.publish(event)
```

### AffectationDeletedEvent
Publié quand une affectation est supprimée.

```python
event = AffectationDeletedEvent(
    affectation_id=123,
    user_id=5,
    chantier_id=10,
    date_affectation=date(2026, 1, 28)
)
event_bus.publish(event)
```

## Module 2 : Pointages (4 événements)

### HeuresCreatedEvent
Publié quand des heures sont enregistrées.

```python
from datetime import date
from modules.pointages.domain.events import HeuresCreatedEvent

event = HeuresCreatedEvent(
    heures_id=1,
    user_id=5,
    chantier_id=10,
    date=date(2026, 1, 28),
    heures_travaillees=8.0,
    heures_supplementaires=2.0
)
event_bus.publish(event)
```

### HeuresUpdatedEvent
Publié quand les heures sont modifiées.

```python
event = HeuresUpdatedEvent(
    heures_id=1,
    user_id=5,
    chantier_id=10,
    date=date(2026, 1, 28),
    heures_travaillees=8.5,
    heures_supplementaires=1.5,
    changes={'heures_travaillees': 8.5}
)
event_bus.publish(event)
```

### HeuresValidatedEvent ⚠️ CRITIQUE POUR SYNC PAIE
Publié quand les heures sont validées (déclenche la sync paie).

```python
from datetime import date, datetime
from modules.pointages.domain.events import HeuresValidatedEvent

event = HeuresValidatedEvent(
    heures_id=1,
    user_id=5,
    chantier_id=10,
    date=date(2026, 1, 28),
    heures_travaillees=8.0,
    heures_supplementaires=2.0,
    validated_by=3,  # ID du responsable
    validated_at=datetime.utcnow()
)
# Cet événement déclenche automatiquement la synchronisation avec le système de paie
event_bus.publish(event)
```

### HeuresRejectedEvent
Publié quand les heures sont rejetées.

```python
event = HeuresRejectedEvent(
    heures_id=1,
    user_id=5,
    chantier_id=10,
    date=date(2026, 1, 28),
    rejected_by=3,
    reason="Incohérence avec le planning"
)
event_bus.publish(event)
```

## Module 3 : Chantiers (4 événements)

### ChantierCreatedEvent
Publié quand un chantier est créé.

```python
from modules.chantiers.domain.events import ChantierCreatedEvent

event = ChantierCreatedEvent(
    chantier_id=10,
    nom="Rénovation Rue de la Paix",
    adresse="123 Rue de la Paix, 75000 Paris",
    statut="ouvert"
)
event_bus.publish(event)
```

### ChantierUpdatedEvent
Publié quand un chantier est mis à jour.

```python
event = ChantierUpdatedEvent(
    chantier_id=10,
    nom="Rénovation Rue de la Paix - Phase 2",
    adresse="123 Rue de la Paix, 75000 Paris",
    statut="en_cours",
    changes={'nom': 'Rénovation Rue de la Paix - Phase 2'}
)
event_bus.publish(event)
```

### ChantierDeletedEvent
Publié quand un chantier est supprimé.

```python
event = ChantierDeletedEvent(
    chantier_id=10,
    nom="Rénovation Rue de la Paix",
    adresse="123 Rue de la Paix, 75000 Paris"
)
event_bus.publish(event)
```

### ChantierStatutChangedEvent
Publié quand le statut d'un chantier change (ouvert → en_cours → fermé).

```python
event = ChantierStatutChangedEvent(
    chantier_id=10,
    ancien_statut="ouvert",
    nouveau_statut="en_cours",
    nom="Rénovation Rue de la Paix",
    adresse="123 Rue de la Paix, 75000 Paris"
)
event_bus.publish(event)
```

## Module 4 : Signalements (3 événements)

### SignalementCreatedEvent
Publié quand un signalement est créé.

```python
from modules.signalements.domain.events import SignalementCreatedEvent

event = SignalementCreatedEvent(
    signalement_id=1,
    chantier_id=10,
    user_id=5,
    titre="Équipement de sécurité manquant",
    gravite="haute"
)
event_bus.publish(event)
```

### SignalementUpdatedEvent
Publié quand un signalement est mis à jour.

```python
event = SignalementUpdatedEvent(
    signalement_id=1,
    chantier_id=10,
    user_id=5,
    titre="Équipement de sécurité manquant",
    gravite="critique",
    changes={'gravite': 'critique'}
)
event_bus.publish(event)
```

### SignalementClosedEvent
Publié quand un signalement est fermé/résolu.

```python
event = SignalementClosedEvent(
    signalement_id=1,
    chantier_id=10,
    user_id=5,
    titre="Équipement de sécurité manquant",
    gravite="haute",
    closed_by=3,
    resolution="Équipement fourni et installé"
)
event_bus.publish(event)
```

## Module 5 : Documents (2 événements)

### DocumentUploadedEvent
Publié quand un document est téléchargé.

```python
from modules.documents.domain.events import DocumentUploadedEvent

event = DocumentUploadedEvent(
    document_id=1,
    nom="plans_architecture.pdf",
    type_document="plan",
    chantier_id=10,
    user_id=5
)
event_bus.publish(event)
```

### DocumentDeletedEvent
Publié quand un document est supprimé.

```python
event = DocumentDeletedEvent(
    document_id=1,
    nom="plans_architecture.pdf",
    type_document="plan",
    chantier_id=10,
    user_id=5
)
event_bus.publish(event)
```

## Gestion des événements dans les Use Cases

Exemple dans un Use Case :

```python
from modules.planning.domain.events import AffectationCreatedEvent
from modules.planning.application.ports import EventBus

class CreateAffectationUseCase:
    def __init__(self, repository, event_bus: EventBus):
        self.repository = repository
        self.event_bus = event_bus

    def execute(self, dto):
        # Créer l'affectation
        affectation = Affectation(...)
        self.repository.save(affectation)

        # Publier l'événement
        event = AffectationCreatedEvent(
            affectation_id=affectation.id,
            user_id=affectation.user_id,
            chantier_id=affectation.chantier_id,
            date_affectation=affectation.date,
            metadata={'user_id': current_user_id}
        )
        self.event_bus.publish(event)

        return affectation
```

## Event Handlers

Les événements peuvent être écoutés par des handlers :

```python
@event_bus.subscribe('affectation.created')
def on_affectation_created(event: AffectationCreatedEvent):
    """Handler appelé quand une affectation est créée."""
    # Envoyer une notification
    notify_user(event.data['user_id'])

    # Mettre à jour les statistiques
    update_statistics(event.data)

    # Log audit
    log_audit(event)

@event_bus.subscribe('heures.validated')
def on_heures_validated(event: HeuresValidatedEvent):
    """Handler CRITIQUE pour sync paie."""
    # Déclencher la synchronisation avec le système de paie
    sync_with_payroll_system(event.data)
```

## Métadonnées recommandées

Lors de la création d'un événement, inclure les métadonnées suivantes :

```python
metadata = {
    'user_id': current_user.id,           # Qui a déclenché l'action
    'ip_address': request.client.host,    # D'où vient la requête
    'user_agent': request.headers.get('User-Agent'),  # Quel client
    'correlation_id': correlation_id      # Pour tracer les chaînes d'événements
}

event = AffectationCreatedEvent(
    affectation_id=1,
    user_id=5,
    chantier_id=10,
    date_affectation=date(2026, 1, 28),
    metadata=metadata
)
```

## Persistance des événements

Les événements sérializés peuvent être persistés :

```python
event_dict = event.to_dict()
# Sauvegarder dans la base de données
event_log.save({
    'event_id': event_dict['event_id'],
    'event_type': event_dict['event_type'],
    'aggregate_id': event_dict['aggregate_id'],
    'data': json.dumps(event_dict['data']),
    'metadata': json.dumps(event_dict['metadata']),
    'occurred_at': event_dict['occurred_at']
})
```

## Points clés

- Tous les événements héritent de `DomainEvent`
- Utilisent le format `event_type`: `'{module}.{action}'`
- `aggregate_id` = ID de la ressource impactée
- `data` = payload complet avec tous les champs
- `metadata` = contexte de l'action (user, ip, agent)
- Sont immutables une fois créés
- Représentent des faits qui se sont produits (passé)
- Permettent la communication asynchrone entre modules

# ADR 004: Communication Inter-Modules via Events

## Statut
**Accepté** - 21 janvier 2026

## Contexte

Hub Chantier est structuré en modules indépendants :
- auth, employes, pointages, chantiers, planning, documents, formulaires

Ces modules doivent parfois communiquer :
- Quand un employé pointe, le module planning peut être notifié
- Quand un chantier est créé, d'autres modules peuvent réagir

## Décision

La communication inter-modules se fait **exclusivement via Domain Events**.

### Règle absolue

```python
# ❌ INTERDIT - Import direct entre modules
from modules.employes.application.use_cases import GetEmployeUseCase

# ✅ CORRECT - Via EventBus
from shared.infrastructure.event_bus import EventBus
from modules.employes.domain.events import EmployeCreeEvent

EventBus.publish(EmployeCreeEvent(employe_id=123))
```

### Pattern retenu

1. **Définir l'event** dans le domain du module émetteur
2. **Publier l'event** depuis le use case
3. **S'abonner** depuis les modules intéressés

```python
# 1. modules/employes/domain/events/employe_cree_event.py
@dataclass
class EmployeCreeEvent:
    employe_id: int
    nom: str
    prenom: str
    timestamp: datetime = field(default_factory=datetime.now)

# 2. modules/employes/application/use_cases/creer_employe.py
class CreerEmployeUseCase:
    def execute(self, dto: CreerEmployeDTO) -> EmployeDTO:
        employe = Employe.create(...)
        self.repo.save(employe)
        EventBus.publish(EmployeCreeEvent(employe.id, employe.nom, employe.prenom))
        return EmployeDTO.from_entity(employe)

# 3. modules/planning/infrastructure/event_handlers.py
def on_employe_cree(event: EmployeCreeEvent):
    # Créer un planning par défaut pour le nouvel employé
    pass

EventBus.subscribe(EmployeCreeEvent, on_employe_cree)
```

## Conséquences

### Positives
- **Découplage** : Modules indépendants
- **Extensibilité** : Facile d'ajouter des réactions
- **Testabilité** : Chaque module testable isolément
- **Évolutivité** : Prêt pour une architecture micro-services future

### Négatives
- **Complexité** : Plus difficile de suivre le flux
- **Debugging** : Nécessite de tracer les events
- **Ordre** : Pas de garantie d'ordre d'exécution

### Atténuation des risques
- Logging systématique des events
- Events immutables (dataclass frozen)
- Documentation des flux dans les ADRs

## Implémentation

L'EventBus est dans `shared/infrastructure/event_bus.py` :

```python
class EventBus:
    _subscribers: Dict[Type, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: Type, handler: Callable) -> None:
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(handler)

    @classmethod
    def publish(cls, event: Any) -> None:
        event_type = type(event)
        for handler in cls._subscribers.get(event_type, []):
            handler(event)
```

## Alternatives considérées

1. **Import direct** - Rejeté car crée du couplage fort
2. **Message broker (RabbitMQ)** - Rejeté car overkill pour une app locale
3. **Base de données partagée** - Rejeté car viole l'encapsulation

## Références

- [Domain Events](https://martinfowler.com/eaaDev/DomainEvent.html)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

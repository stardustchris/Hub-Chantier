# ADR 001: Adoption de Clean Architecture

## Statut
**Accepté** - 21 janvier 2026

## Contexte

Greg Construction a besoin d'une application de gestion de chantiers qui :
- Sera maintenue sur plusieurs années
- Évoluera avec les besoins métier
- Doit être fiable (gestion des pointages = paie)
- Sera potentiellement étendue (mobile, intégrations)

## Décision

Nous adoptons **Clean Architecture** (Uncle Bob) comme architecture logicielle.

### Structure retenue

```
modules/{module}/
├── domain/           # Layer 1 - Règles métier pures
├── application/      # Layer 2 - Cas d'utilisation
├── adapters/         # Layer 3 - Adaptateurs
└── infrastructure/   # Layer 4 - Frameworks et drivers
```

### Règle de dépendance

Les dépendances pointent **toujours** vers l'intérieur :
- Infrastructure → Adapters → Application → Domain
- Le Domain ne dépend de rien d'externe

## Conséquences

### Positives
- **Testabilité** : Domain et Application testables sans infrastructure
- **Évolutivité** : Facile d'ajouter de nouveaux modules
- **Maintenabilité** : Changements isolés par layer
- **Flexibilité** : Possibilité de changer de framework/DB

### Négatives
- **Complexité initiale** : Plus de fichiers et de structure
- **Courbe d'apprentissage** : L'équipe doit comprendre les concepts
- **Verbosité** : Plus de code boilerplate (interfaces, DTOs)

### Risques atténués
- La structure modulaire permet de travailler en parallèle
- Les conventions strictes réduisent les erreurs d'architecture
- Le script `check-architecture.sh` valide automatiquement

## Alternatives considérées

1. **Architecture en couches classique** (MVC) - Rejetée car couplage trop fort
2. **Microservices** - Rejetée car trop complexe pour 20 utilisateurs
3. **Monolithe simple** - Rejetée car difficile à maintenir à long terme

## Références

- Robert C. Martin, "Clean Architecture" (2017)
- [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

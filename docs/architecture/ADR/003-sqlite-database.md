# ADR 003: SQLite pour la Base de Données

## Statut
**Accepté** - 21 janvier 2026

## Contexte

Greg Construction (20 employés, 4,3M€ CA) a besoin d'une base de données :
- Simple à déployer et maintenir
- Fiable pour les données critiques (pointages)
- Sans coût de licence
- Accessible depuis une application locale

## Décision

Nous utilisons **SQLite** comme base de données de production.

### Justification
- **20 employés** = faible volume de données
- **Application locale** = pas besoin de serveur DB centralisé
- **Backup simple** = copie de fichier
- **Zéro configuration** = pas d'administration DB

### Configuration
- Fichier : `backend/data/hub_chantier.db`
- WAL mode activé pour la concurrence
- Backups automatiques quotidiens

## Conséquences

### Positives
- **Simplicité** : Pas de serveur à gérer
- **Portabilité** : Un seul fichier
- **Performance** : Excellente pour les petits volumes
- **Fiabilité** : ACID compliant
- **Coût** : Gratuit

### Négatives
- **Scalabilité** : Limité à ~100 utilisateurs concurrents
- **Réseau** : Pas de connexions distantes natives
- **Fonctionnalités** : Moins riche que PostgreSQL

### Migration future

Si l'entreprise grandit significativement :
1. Grâce à SQLAlchemy, migration vers PostgreSQL possible
2. Le Domain reste inchangé (abstraction via Repository)
3. Seule l'infrastructure change

## Alternatives considérées

1. **PostgreSQL** - Rejeté car overkill pour 20 utilisateurs
2. **MySQL** - Rejeté car complexité inutile
3. **MongoDB** - Rejeté car données relationnelles

## Références

- [SQLite When To Use](https://www.sqlite.org/whentouse.html)
- [SQLAlchemy SQLite](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)

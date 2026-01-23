# Hub Chantier - Etat du projet

> Ce fichier contient l'etat actuel des modules et les prochaines taches.
> Mis a jour a chaque session de developpement.

## Etat des modules

| Module | CDC Section | Fonctionnalites | Status |
|--------|-------------|-----------------|--------|
| auth (utilisateurs) | 3 | USR-01 a USR-13 | **COMPLET** |
| dashboard | 2 | FEED-01 a FEED-20 | **COMPLET** |
| chantiers | 4 | CHT-01 a CHT-20 | **COMPLET** |
| planning | 5 | PLN-01 a PLN-28 | **COMPLET** |
| planning_charge | 6 | PDC-01 a PDC-17 | Structure only |
| feuilles_heures | 7 | FDH-01 a FDH-20 | **COMPLET** |
| formulaires | 8 | FOR-01 a FOR-11 | **COMPLET** |
| documents | 9 | GED-01 a GED-17 | **COMPLET** (15/17, 2 infra) |
| signalements | 10 | SIG-01 a SIG-20 | Structure only |
| logistique | 11 | LOG-01 a LOG-18 | Structure only |
| interventions | 12 | INT-01 a INT-17 | Structure only |
| taches | 13 | TAC-01 a TAC-20 | **COMPLET** |

## Statistiques

- **Modules complets** : 8/12
- **Fonctionnalites totales** : 186 (incluant GED-16, GED-17, SIG-14 a SIG-20)
- **Tests unitaires** : 827+ (658 + 169 documents)
- **Tests integration** : 17+ (formulaires)

## Prochaine tache prioritaire

**Module Signalements (SIG)** (CDC Section 10)
- Fonctionnalites de base (SIG-01 a SIG-13)
- Systeme de priorite 4 niveaux (SIG-14)
- Date resolution souhaitee (SIG-15)
- Alertes retard et escalade (SIG-16, SIG-17)
- Tableau de bord alertes + filtres avances (SIG-18 a SIG-20)

## Modules en attente

| Module | Priorite | Dependances |
|--------|----------|-------------|
| signalements | Moyenne | Aucune |
| logistique | Moyenne | chantiers (OK) |
| interventions | Basse | planning (OK), taches (OK) |
| planning_charge | Basse | planning (OK) |

## Fonctionnalites en attente infrastructure

- GED-11 : Transfert auto depuis ERP (Costructor/Graneet)
- GED-15 : Synchronisation Offline
- PLN-23/24 : Notifications push / Mode Offline
- FDH-16 : Import ERP auto
- FEED-17 : Notifications push
- SIG-13 : Notifications push signalements
- SIG-16/17 : Alertes retard et escalade automatique

## Derniere mise a jour

Session 2026-01-23 - Module Documents (GED) COMPLET (GED-01 a GED-17, 15/17 done, 2 infra)

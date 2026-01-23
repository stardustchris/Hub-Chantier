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
| memos | 10 | MEM-01 a MEM-13 | Structure only |
| logistique | 11 | LOG-01 a LOG-18 | Structure only |
| interventions | 12 | INT-01 a INT-17 | Structure only |
| taches | 13 | TAC-01 a TAC-20 | **COMPLET** |

## Statistiques

- **Modules complets** : 8/12
- **Fonctionnalites totales** : 179 (incluant GED-16, GED-17)
- **Tests unitaires** : 827+ (658 + 169 documents)
- **Tests integration** : 17+ (formulaires)

## Prochaine tache prioritaire

**Module Memos (MEM)** (CDC Section 10)
- Rattachement chantier obligatoire (MEM-01)
- Liste chronologique avec indicateur statut (MEM-02, MEM-03)
- Fil de conversation type chat (MEM-06)
- Ajout photo/video dans reponses (MEM-08)
- Signature dans reponses (MEM-09)
- Notifications push (MEM-13)

## Modules en attente

| Module | Priorite | Dependances |
|--------|----------|-------------|
| memos | Moyenne | Aucune |
| logistique | Moyenne | chantiers (OK) |
| interventions | Basse | planning (OK), taches (OK) |
| planning_charge | Basse | planning (OK) |

## Fonctionnalites en attente infrastructure

- GED-11 : Transfert auto depuis ERP (Costructor/Graneet)
- GED-15 : Synchronisation Offline
- PLN-23/24 : Notifications push / Mode Offline
- FDH-16 : Import ERP auto
- FEED-17 : Notifications push

## Derniere mise a jour

Session 2026-01-23 - Module Documents (GED) COMPLET (GED-01 a GED-17, 15/17 done, 2 infra)

# Etat du projet Hub Chantier

> Ce fichier est lu par Claude au debut de chaque session.
> Il permet de reprendre le travail la ou on s'est arrete.

## Derniere mise a jour
- **Date** : 2026-01-22
- **Session** : Import du CDC et creation SPECIFICATIONS.md

## Specifications fonctionnelles

**Document de reference** : `docs/SPECIFICATIONS.md`
**CDC Original** : `docs/CDC Greg Constructions v2.1.docx`

## Etat des modules

| Module | CDC Ref | Fonctionnalites | Status | Derniere action |
|--------|---------|-----------------|--------|-----------------|
| auth (utilisateurs) | Section 2 | USR-01 à USR-14 | **COMPLET** | Module de reference cree |
| chantiers | Section 3 | CHT-01 à CHT-20 | Structure only | A implementer |
| planning | Section 4 | PLN-01 à PLN-28 | Structure only | A implementer |
| planning_charge | Section 5 | PDC-01 à PDC-17 | Structure only | A implementer |
| feuilles_heures | Section 6 | FDH-01 à FDH-20 | Structure only | A implementer |
| formulaires | Section 7 | FOR-01 à FOR-11 | Structure only | A implementer |
| documents | Section 8 | GED-01 à GED-15 | Structure only | A implementer |
| memos | Section 9 | MEM-01 à MEM-13 | Structure only | A implementer |
| logistique | Section 10 | LOG-01 à LOG-18 | Structure only | A implementer |
| interventions | Section 11 | INT-01 à INT-17 | Structure only | A implementer |
| taches | Section 12 | TAC-01 à TAC-20 | Structure only | A implementer |

## Prochaines taches prioritaires

1. [ ] **Module chantiers** (Section 3) - CRUD chantiers avec statuts et coordonnees GPS
2. [ ] **Module planning** (Section 4) - Affectations utilisateurs aux chantiers
3. [ ] **Module feuilles_heures** (Section 6) - Saisie et validation des heures
4. [ ] **Module taches** (Section 12) - Gestion des travaux par chantier
5. [ ] Connecter le frontend au backend

## Roles utilisateurs (Section 2.3)

| Role | Web | Mobile | Perimetre |
|------|-----|--------|-----------|
| Administrateur | ✅ | ✅ | Global |
| Conducteur | ✅ | ✅ | Ses chantiers |
| Chef de Chantier | ❌ | ✅ | Ses chantiers assignes |
| Compagnon | ❌ | ✅ | Planning perso |

## Corps de metier (Section 4.3)

- Employe (polyvalent)
- Macon
- Coffreur
- Ferrailleur
- Grutier
- Charpentier
- Couvreur
- Electricien
- Sous-traitant

## Ce qui a ete fait

### Session 2026-01-22
- Import du CDC Greg Constructions v2.1
- Creation de docs/SPECIFICATIONS.md (178 fonctionnalites documentees)
- Mise a jour CLAUDE.md avec details CDC

### Session 2026-01-21 (init)
- Initialisation structure Clean Architecture
- Module auth complet (reference)
- Documentation (README, CONTEXT, ADRs)
- Configuration backend (FastAPI, SQLAlchemy, pytest)
- Configuration frontend (React 19, Vite, Tailwind)
- Configuration agents (.claude/agents/)

## Notes importantes

- **CDC** : Toujours se referer a `docs/SPECIFICATIONS.md` pour les details fonctionnels
- **Architecture** : Le module `auth` sert de reference Clean Architecture
- **Workflow** : Domain → Application → Adapters → Infrastructure
- **Agents** : Configures dans `.claude/agents/`
- **Intégrations** : Costructor et Graneet (Section 13)

## Blocages / Questions en suspens

(Aucun pour l'instant)

# Workflow : Validation des Feuilles d'Heures

**Complexité** : ⭐⭐⭐⭐⭐ (Très élevée)
**Module** : `backend/modules/pointages`
**Date** : 30 janvier 2026
**Statut** : ✅ Documenté

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Acteurs et permissions](#2-acteurs-et-permissions)
3. [Entités métier](#3-entités-métier)
4. [Machine à états](#4-machine-à-états)
5. [Workflows détaillés](#5-workflows-détaillés)
6. [Calculs et agrégations](#6-calculs-et-agrégations)
7. [Synchronisation Planning (FDH-10)](#7-synchronisation-planning-fdh-10)
8. [Export paie](#8-export-paie)
9. [Interactions avec autres modules](#9-interactions-avec-autres-modules)
10. [Architecture technique](#10-architecture-technique)
11. [Scénarios de test](#11-scénarios-de-test)
12. [Points d'attention](#12-points-dattention)

---

## 1. Vue d'ensemble

### 1.1 Définition

Le **Workflow de Validation des Feuilles d'Heures** couvre l'ensemble du cycle de vie d'un pointage, depuis la saisie initiale par le compagnon jusqu'à l'export vers le logiciel de paie. C'est le workflow le plus critique de Hub Chantier car il conditionne directement la rémunération des salariés.

Le workflow se décompose en 3 niveaux imbriqués :

```
┌─────────────────────────────────────────────────────────────┐
│  FEUILLE D'HEURES (FeuilleHeures)                           │
│  = Agrégat hebdomadaire par compagnon                       │
│  Ex: "Semaine 5 - 2026 de Sébastien ACHKAR"                │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  POINTAGE (Pointage)                                    │ │
│  │  = Entrée unitaire : 1 jour + 1 chantier + 1 compagnon │ │
│  │  Ex: "Lundi 27/01 - Villa Duplex - 8h normales"        │ │
│  │                                                          │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │  VARIABLE DE PAIE (VariablePaie)                    ││ │
│  │  │  = Complément lié au pointage                       ││ │
│  │  │  Ex: "Panier repas 10.50€", "Prime salissure"      ││ │
│  │  └─────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Vocabulaire clé** :

| Terme | Définition | Analogie papier |
|-------|-----------|-----------------|
| **Pointage** | 1 ligne = 1 jour + 1 chantier + heures travaillées | 1 case dans la feuille |
| **Feuille d'heures** | Regroupement de tous les pointages d'un compagnon sur 1 semaine | La feuille papier hebdo |
| **Variable de paie** | Prime, indemnité ou absence rattachée à un pointage | Note manuscrite en marge |
| **Signature** | Signature manuscrite tactile du compagnon (tablette/mobile) | Signature en bas de la feuille |

### 1.2 Objectifs métier

| Objectif | Description |
|----------|-------------|
| **Exactitude paie** | Garantir que chaque compagnon est payé correctement (heures normales, supplémentaires, primes) |
| **Traçabilité** | Savoir qui a saisi, signé, soumis, validé ou rejeté chaque pointage |
| **Conformité BTP** | Respecter les obligations légales (heures max, repos, primes conventionnelles) |
| **Fluidité terrain** | Permettre la saisie rapide sur tablette/mobile, même en conditions de chantier |
| **Verrouillage paie** | Empêcher toute modification après la date de clôture mensuelle |

### 1.3 Périmètre fonctionnel

**Inclus** :
- Saisie des heures (normales + supplémentaires) par jour et par chantier
- Signature manuscrite tactile (tablette/mobile)
- Workflow de validation multi-niveaux (soumission → validation/rejet)
- Cycle de correction après rejet
- Calculs automatiques (totaux jour/semaine/chantier)
- Variables de paie (primes, indemnités, absences)
- Export vers logiciel de paie (CSV/XLSX/PDF/ERP)
- Verrouillage après clôture mensuelle

**Exclus** :
- Création des affectations → module `planning`
- Gestion des chantiers → module `chantiers`
- Gestion des utilisateurs → module `auth`
- Calcul bulletin de paie → logiciel externe (ERP)

### 1.4 Références CDC

| CDC ID | Fonctionnalité | Description |
|--------|----------------|-------------|
| FDH-01 | Vue Compagnons | Liste des compagnons avec affectations actives |
| FDH-02 | Vue hebdomadaire | Affichage par semaine (lundi → dimanche) |
| FDH-05 | Grille tabulaire | Tableau jours × chantiers |
| FDH-06 | Multi-chantiers | Un compagnon peut pointer sur plusieurs chantiers/jour |
| FDH-08 | Totaux par jour | Somme heures normales + sup par jour |
| FDH-09 | Totaux par chantier | Somme heures normales + sup par chantier |
| FDH-10 | Création auto | Pointages pré-remplis depuis le planning |
| FDH-11 | Format HH:MM | Heures saisies au format heures:minutes |
| FDH-12 | Workflow validation | BROUILLON → SOUMIS → VALIDÉ / REJETÉ |
| FDH-13 | Variables de paie | Primes, indemnités, absences |
| FDH-20 | Export paie | Formats CSV, XLSX, PDF, ERP |

---

## 2. Acteurs et permissions

### 2.1 Rôles dans le workflow

| Rôle | Actions autorisées | Périmètre |
|------|-------------------|-----------|
| **Compagnon** | Saisir ses heures, signer, soumettre, corriger après rejet | Ses propres pointages uniquement |
| **Chef de chantier** | Tout ce que fait le compagnon + **valider/rejeter** les pointages | Pointages des compagnons de **ses chantiers** |
| **Conducteur de travaux** | Tout ce que fait le chef + **valider/rejeter** tous les pointages | Pointages des compagnons de **ses chantiers** |
| **Admin** | Toutes les actions sans restriction | **Tous** les pointages |

### 2.2 Qui valide quoi ?

```
┌────────────────────────────────────────────────────────────────────┐
│                     CHAÎNE DE VALIDATION                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Compagnon                                                         │
│  (Sébastien ACHKAR)                                                │
│       │                                                            │
│       │  Saisit ses heures                                         │
│       │  Signe sur tablette                                        │
│       │  Soumet la feuille                                         │
│       ▼                                                            │
│  Chef de chantier  ──OU──  Conducteur de travaux  ──OU──  Admin   │
│  (Nicolas DELSALLE)        (Robert BIANCHINI)       (Super ADMIN)  │
│       │                         │                        │         │
│       ├─── VALIDER ────────────>├──── VALIDER ──────────>│         │
│       │                         │                        │         │
│       └─── REJETER ────────────>└──── REJETER ──────────>│         │
│            (motif obligatoire)       (motif obligatoire)           │
│                                                                    │
│  N'importe lequel des 3 rôles peut valider ou rejeter.            │
│  Le premier qui agit verrouille le pointage.                       │
└────────────────────────────────────────────────────────────────────┘
```

**Règles clés** :
- Le chef de chantier ne voit que les pointages des compagnons affectés à **ses** chantiers
- Le conducteur de travaux ne voit que les pointages des chantiers **dont il est responsable**
- L'admin voit et peut agir sur **tous** les pointages
- Un seul validateur suffit (pas de double validation)

### 2.3 Matrice de permissions

| Action | Compagnon | Chef chantier | Conducteur | Admin |
|--------|:---------:|:-------------:|:----------:|:-----:|
| Créer pointage (ses heures) | ✅ | ✅ | ✅ | ✅ |
| Créer pointage (autre compagnon) | ❌ | ✅ | ✅ | ✅ |
| Modifier pointage BROUILLON | ✅ (sien) | ✅ | ✅ | ✅ |
| Modifier pointage REJETÉ | ✅ (sien) | ✅ | ✅ | ✅ |
| Signer | ✅ (sien) | ❌ | ❌ | ❌ |
| Soumettre | ✅ (sien) | ✅ | ✅ | ✅ |
| Valider | ❌ | ✅ | ✅ | ✅ |
| Rejeter | ❌ | ✅ | ✅ | ✅ |
| Supprimer pointage BROUILLON | ✅ (sien) | ✅ | ✅ | ✅ |
| Voir feuilles d'heures | ✅ (siennes) | ✅ (ses chantiers) | ✅ (ses chantiers) | ✅ (tout) |
| Export paie | ❌ | ❌ | ✅ | ✅ |

---

## 3. Entités métier

### 3.1 Pointage (entrée unitaire)

**Fichier** : `backend/modules/pointages/domain/entities/pointage.py`

Un pointage représente **les heures travaillées par un compagnon, sur un chantier, pour un jour donné**.

```
┌──────────────────────────────────────────────────────────┐
│ POINTAGE                                                  │
├──────────────────────────────────────────────────────────┤
│ utilisateur_id : int          → Qui a travaillé           │
│ chantier_id    : int          → Où                        │
│ date_pointage  : date         → Quand                     │
│ heures_normales: Duree        → Combien (ex: 7h30)       │
│ heures_supplementaires: Duree → Heures sup (ex: 1h30)    │
│ statut         : StatutPointage → État du workflow        │
│ signature_utilisateur: str    → Signature manuscrite b64  │
│ signature_date : datetime     → Horodatage signature      │
│ validateur_id  : int          → Qui a validé/rejeté       │
│ validation_date: datetime     → Quand validé/rejeté       │
│ motif_rejet    : str          → Raison du rejet           │
│ commentaire    : str          → Note libre                │
│ affectation_id : int          → Lien planning (FDH-10)    │
│ created_by     : int          → Qui a créé l'entrée       │
└──────────────────────────────────────────────────────────┘
```

**Contrainte d'unicité** : `(utilisateur_id, chantier_id, date_pointage)` — Un compagnon ne peut avoir qu'un seul pointage par jour et par chantier.

**Méthodes métier clés** :

| Méthode | Description | Précondition |
|---------|-------------|-------------|
| `set_heures(normales, sup)` | Modifier les heures | Statut BROUILLON ou REJETÉ |
| `signer(signature)` | Apposer la signature manuscrite | Statut BROUILLON uniquement |
| `soumettre()` | Passer BROUILLON → SOUMIS | Statut BROUILLON |
| `valider(validateur_id)` | Passer SOUMIS → VALIDÉ | Statut SOUMIS |
| `rejeter(validateur_id, motif)` | Passer SOUMIS → REJETÉ | Statut SOUMIS, motif obligatoire |
| `corriger()` | Passer REJETÉ → BROUILLON | Statut REJETÉ |
| `total_heures` | Normales + supplémentaires | — |
| `is_editable` | Modifiable ? | True si BROUILLON ou REJETÉ |
| `is_validated` | Validé ? | True si VALIDÉ |
| `is_signed` | Signé ? | True si signature présente |

### 3.2 Feuille d'heures (agrégat hebdomadaire)

**Fichier** : `backend/modules/pointages/domain/entities/feuille_heures.py`

La feuille d'heures regroupe **tous les pointages d'un compagnon sur une semaine** (lundi → dimanche).

```
┌──────────────────────────────────────────────────────────────────────┐
│ FEUILLE D'HEURES (Semaine 5 - 2026 - Sébastien ACHKAR)             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  semaine_debut : date (toujours un lundi)                            │
│  annee         : int (2026)                                          │
│  numero_semaine: int (5, norme ISO)                                  │
│  statut_global : StatutPointage (calculé automatiquement)            │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐│
│  │ POINTAGES (liste)                                                ││
│  │                                                                   ││
│  │  Lun 27/01 │ Villa Duplex    │ 7h30 norm + 0h00 sup = 7h30     ││
│  │  Lun 27/01 │ Résidence Alpes │ 0h00 norm + 1h30 sup = 1h30     ││
│  │  Mar 28/01 │ Villa Duplex    │ 8h00 norm + 0h00 sup = 8h00     ││
│  │  Mer 29/01 │ Villa Duplex    │ 7h00 norm + 1h00 sup = 8h00     ││
│  │  Jeu 30/01 │ Villa Duplex    │ 8h00 norm + 0h00 sup = 8h00     ││
│  │  Ven 31/01 │ Villa Duplex    │ 7h30 norm + 0h30 sup = 8h00     ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐│
│  │ VARIABLES DE PAIE (liste)                                        ││
│  │                                                                   ││
│  │  Panier repas  │ 10.50€ × 5 jours                               ││
│  │  Indemnité transport │ 8.20€ × 5 jours                          ││
│  │  Prime salissure │ 3.00€ × 5 jours                              ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  TOTAUX :                                                            │
│  - Heures normales   : 38h00                                        │
│  - Heures sup        :  3h00                                        │
│  - Total             : 41h00                                        │
│  - Variables paie    : 108.50€                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Méthodes de calcul** :

| Méthode | Retour | Usage |
|---------|--------|-------|
| `total_heures_normales` | Duree | Somme heures normales de tous les pointages |
| `total_heures_supplementaires` | Duree | Somme heures sup |
| `total_heures` | Duree | Normales + sup |
| `total_heures_decimal` | float | Pour la paie (ex: 41.0 au lieu de 41h00) |
| `total_heures_par_jour()` | Dict[date, Duree] | Ventilation par jour |
| `total_heures_par_chantier()` | Dict[int, Duree] | Ventilation par chantier (FDH-08, FDH-09) |
| `is_complete` | bool | Tous les jours ouvrés ont au moins 1 pointage |
| `is_all_validated` | bool | Tous les pointages sont VALIDÉ |
| `has_pending_validation` | bool | Au moins 1 pointage SOUMIS |
| `has_rejected` | bool | Au moins 1 pointage REJETÉ |
| `calculer_statut_global()` | StatutPointage | Statut agrégé de la feuille |

**Règle de calcul du statut global** :

```
Si au moins 1 pointage REJETÉ     → statut_global = REJETÉ
Si au moins 1 pointage BROUILLON  → statut_global = BROUILLON
Si au moins 1 pointage SOUMIS     → statut_global = SOUMIS
Si tous les pointages sont VALIDÉ  → statut_global = VALIDÉ
```

### 3.3 Variable de paie

**Fichier** : `backend/modules/pointages/domain/entities/variable_paie.py`

Les variables de paie sont les **compléments de rémunération** rattachés à un pointage.

**Types disponibles** (enum `TypeVariablePaie`) :

| Catégorie | Types | Unité |
|-----------|-------|-------|
| **Heures** | HEURES_NORMALES, HEURES_SUPPLEMENTAIRES, HEURES_NUIT, HEURES_DIMANCHE, HEURES_FERIE | Heures |
| **Indemnités** | PANIER_REPAS, INDEMNITE_TRANSPORT | Euros |
| **Primes** | PRIME_INTEMPERIES, PRIME_SALISSURE, PRIME_OUTILLAGE | Euros |
| **Absences** | CONGES_PAYES, RTT, MALADIE, ACCIDENT_TRAVAIL, ABSENCE_INJUSTIFIEE, ABSENCE_JUSTIFIEE | Heures |
| **Divers** | FORMATION, DEPLACEMENT | Heures/Euros |

**Propriétés utiles** :

| Propriété | Rôle |
|-----------|------|
| `is_hours` | True si le type est compté en heures |
| `is_amount` | True si le type est compté en euros |
| `is_absence` | True si le type est une absence (impact planning) |
| `libelle` | Libellé français pour affichage/export |

### 3.4 Value Object : Duree (HH:MM)

**Fichier** : `backend/modules/pointages/domain/value_objects/duree.py`

La durée est le format natif des heures dans Hub Chantier. Toutes les saisies et tous les calculs utilisent ce format.

```
┌───────────────────────────────────────────────────────────┐
│ DUREE                                                      │
├───────────────────────────────────────────────────────────┤
│ heures  : int (0-999)                                      │
│ minutes : int (0-59)                                       │
├───────────────────────────────────────────────────────────┤
│ Stockage interne : en MINUTES (pour précision)             │
│ Affichage        : HH:MM (ex: "7:30")                     │
│ Export paie      : décimal (ex: 7.5)                       │
├───────────────────────────────────────────────────────────┤
│ Exemples :                                                 │
│   7h30  → Duree(7, 30)  → 450 min → 7.5 décimal          │
│   8h00  → Duree(8, 0)   → 480 min → 8.0 décimal          │
│   1h45  → Duree(1, 45)  → 105 min → 1.75 décimal         │
│   0h15  → Duree(0, 15)  →  15 min → 0.25 décimal         │
└───────────────────────────────────────────────────────────┘
```

**Opérations supportées** : addition (`+`), soustraction (`-`), comparaison (`<`, `<=`, `>`, `>=`).

---

## 4. Machine à états

### 4.1 Diagramme de la machine à états

**Fichier** : `backend/modules/pointages/domain/value_objects/statut_pointage.py`

```
                        ┌────────────────────────────────────────────────┐
                        │         WORKFLOW DE VALIDATION (FDH-12)        │
                        └────────────────────────────────────────────────┘

                                    ┌─────────────┐
                              ┌────>│  BROUILLON  │<────────────────────────┐
                              │     └──────┬──────┘                         │
                              │            │                                │
                              │            │ signer(signature)              │
                              │            │ Compagnon appose sa            │
                              │            │ signature manuscrite            │
                              │            │ sur tablette                    │
                              │            │                                │
                              │            ▼                                │
                              │     ┌──────────────┐                       │
                              │     │  BROUILLON   │                       │
                              │     │  (signé)     │                       │
                              │     └──────┬───────┘                       │
                              │            │                                │
                              │            │ soumettre()                    │
                              │            │ Compagnon envoie               │
                              │            │ pour validation                │
                              │            │                                │
                              │            ▼                                │
                              │     ┌─────────────┐                        │
     corriger()               │     │   SOUMIS    │                        │
     Compagnon reprend        │     └──────┬──────┘                        │
     son pointage pour        │            │                                │
     correction               │            ├───────────────┐               │
                              │            │               │               │
                              │            ▼               ▼               │
                              │     ┌─────────────┐ ┌───────────┐         │
                              │     │   VALIDÉ    │ │  REJETÉ   │─────────┘
                              │     │   (final)   │ │           │  corriger()
                              │     └─────────────┘ └───────────┘
                              │                           │
                              └───────────────────────────┘

    Légende :
    ─────────
    BROUILLON : Pointage en cours de saisie (modifiable)
    SOUMIS    : Envoyé au chef/conducteur pour validation
    VALIDÉ    : Approuvé (verrouillé sauf admin avant clôture)
    REJETÉ    : Refusé avec motif (retour en saisie)
```

### 4.2 Transitions autorisées

| Depuis | Vers | Méthode | Qui | Condition |
|--------|------|---------|-----|-----------|
| BROUILLON | SOUMIS | `soumettre()` | Compagnon | — |
| SOUMIS | VALIDÉ | `valider(validateur_id)` | Chef / Conducteur / Admin | — |
| SOUMIS | REJETÉ | `rejeter(validateur_id, motif)` | Chef / Conducteur / Admin | Motif obligatoire |
| REJETÉ | BROUILLON | `corriger()` | Compagnon | — |

### 4.3 Transitions interdites

| Depuis | Vers | Raison |
|--------|------|--------|
| BROUILLON | VALIDÉ | On ne peut pas valider sans soumettre d'abord |
| BROUILLON | REJETÉ | Idem |
| SOUMIS | BROUILLON | Le compagnon ne peut pas retirer sa soumission |
| VALIDÉ | * | Aucune transition depuis VALIDÉ (voir verrouillage §4.4) |
| REJETÉ | SOUMIS | Il faut d'abord repasser en BROUILLON |
| REJETÉ | VALIDÉ | Idem |

### 4.4 Règle de verrouillage mensuel

**Règle métier critique** : Un pointage — quel que soit son statut — reste modifiable **jusqu'au vendredi précédant la dernière semaine du mois en cours**.

```
Exemple pour janvier 2026 :
─────────────────────────────────────────────────
  Lun 26   Mar 27   Mer 28   Jeu 29   Ven 30   Sam 31
  │         │         │         │       │
  │         │         │         │       └── Dernière semaine commence le Lun 26
  │         │         │         │
  │         │         │         └── Dernier vendredi avant = Ven 23/01
  │         │         │
─────────────────────────────────────────────────
  → Tous les pointages de janvier sont VERROUILLÉS à partir du samedi 24 janvier.
  → Après cette date : aucune modification possible (même par un admin).

Exemple pour février 2026 :
─────────────────────────────────────────────────
  Dernière semaine du mois : Lun 23/02 → Dim 01/03
  Vendredi précédant        : Ven 20/02
  → Verrouillage le samedi 21 février.
─────────────────────────────────────────────────
```

**Conséquences du verrouillage** :

| Action | Avant verrouillage | Après verrouillage |
|--------|-------------------|-------------------|
| Modifier heures | ✅ (si BROUILLON ou REJETÉ) | ❌ Interdit |
| Signer | ✅ | ❌ Interdit |
| Soumettre | ✅ | ❌ Interdit |
| Valider | ✅ | ❌ Interdit |
| Rejeter | ✅ | ❌ Interdit |
| Consulter | ✅ | ✅ Toujours possible |
| Exporter | ✅ | ✅ Toujours possible |

**Cas particulier** : Si un pointage est encore en BROUILLON au moment du verrouillage, il reste BROUILLON mais ne peut plus être modifié ni soumis. Le conducteur ou l'admin doit traiter ces cas manuellement (saisie d'office, régularisation sur le mois suivant).

### 4.5 Implémentation de la validation de statut

**Fichier** : `backend/modules/pointages/domain/value_objects/statut_pointage.py`

```python
TRANSITIONS = {
    "brouillon": ["soumis"],
    "soumis": ["valide", "rejete"],
    "valide": [],       # État final
    "rejete": ["brouillon"],
}

def can_transition_to(self, target: "StatutPointage") -> bool:
    return target.value in TRANSITIONS.get(self.value, [])

def is_editable(self) -> bool:
    return self.value in ("brouillon", "rejete")

def is_final(self) -> bool:
    return self.value == "valide"
```

---

## 5. Workflows détaillés

### 5.1 Workflow A : Saisie des heures

**Acteur** : Compagnon (ou chef/conducteur pour le compte d'un compagnon)
**Prérequis** : Affectation active sur au moins un chantier

#### 5.1.1 Flux nominal

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌─────────┐
│ Compagnon    │────►│ Frontend         │────►│ POST /pointages  │────►│ Database│
│ (tablette)   │     │ Grille FDH       │     │                  │     │         │
└──────────────┘     └──────────────────┘     └──────────────────┘     └─────────┘
      │                      │                         │
      │  1. Ouvre feuille    │                         │
      │     de la semaine    │                         │
      │                      │  2. Affiche grille      │
      │                      │     jours × chantiers   │
      │                      │                         │
      │  3. Clique sur       │                         │
      │     cellule          │                         │
      │     "Lundi - Villa"  │                         │
      │                      │                         │
      │  4. Saisit 7h30     │                         │
      │     normales         │                         │
      │                      │  5. Envoie requête     │
      │                      │────────────────────────►│
      │                      │                         │  6. Sauvegarde
      │                      │                         │     BROUILLON
      │                      │  7. Confirmation       │
      │                      │◄────────────────────────│
      │                      │                         │
      │  8. Cellule mise     │                         │
      │     à jour           │                         │
```

#### 5.1.2 Requête de création

```http
POST /api/pointages
Content-Type: application/json
Authorization: Bearer <token_compagnon>

{
  "utilisateur_id": 7,
  "chantier_id": 1,
  "date_pointage": "2026-01-27",
  "heures_normales": "7:30",
  "heures_supplementaires": "0:00",
  "commentaire": "Coulage dalle RDC",
  "affectation_id": 42
}
```

**Réponse** :

```json
{
  "id": 156,
  "utilisateur_id": 7,
  "chantier_id": 1,
  "date_pointage": "2026-01-27",
  "heures_normales": "7:30",
  "heures_supplementaires": "0:00",
  "total_heures": "7:30",
  "statut": "brouillon",
  "signature_utilisateur": null,
  "commentaire": "Coulage dalle RDC",
  "affectation_id": 42,
  "created_at": "2026-01-27T17:30:00Z"
}
```

#### 5.1.3 Modification d'un pointage existant

```http
PUT /api/pointages/156
Content-Type: application/json
Authorization: Bearer <token_compagnon>

{
  "heures_normales": "7:30",
  "heures_supplementaires": "1:30",
  "commentaire": "Coulage dalle RDC + finitions"
}
```

**Précondition** : Statut BROUILLON ou REJETÉ. Sinon → `400 Bad Request`.

#### 5.1.4 Cas d'erreur

| Erreur | Code HTTP | Message | Cause |
|--------|-----------|---------|-------|
| Doublon | 409 Conflict | `Un pointage existe déjà pour cet utilisateur, ce chantier et cette date` | Contrainte d'unicité |
| Chantier inactif | 400 Bad Request | `Impossible de pointer sur un chantier fermé` | Chantier au statut FERMÉ |
| Période verrouillée | 403 Forbidden | `La période de paie est verrouillée` | Après date de clôture |
| Heures invalides | 400 Bad Request | `Le format d'heures est invalide` | Format != HH:MM |
| Non autorisé | 403 Forbidden | `Vous ne pouvez modifier que vos propres pointages` | Compagnon essaie de modifier les heures d'un autre |

---

### 5.2 Workflow B : Signature manuscrite

**Acteur** : Compagnon uniquement
**Prérequis** : Pointage au statut BROUILLON

#### 5.2.1 Principe

La signature est une **signature manuscrite réalisée sur tablette ou mobile**. Le compagnon dessine sa signature à l'écran avec le doigt ou un stylet. Le frontend capture l'image et l'encode en base64.

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   ┌──────────────────────────────────────────┐                       │
│   │                                          │                       │
│   │    ╱╲                                    │                       │
│   │   ╱  ╲   ╱╲      ╱╲                     │  ← Zone de signature │
│   │  ╱    ╲ ╱  ╲    ╱  ╲╱╲                  │    tactile            │
│   │ ╱      ╲    ╲  ╱      ╲                 │                       │
│   │╱             ╲╱                          │                       │
│   │                                          │                       │
│   └──────────────────────────────────────────┘                       │
│                                                                      │
│   [ Effacer ]                    [ Valider la signature ]            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

#### 5.2.2 Flux

```
1. Compagnon ouvre sa feuille d'heures
2. Vérifie que toutes les heures sont correctes
3. Appuie sur "Signer"
4. Zone de dessin s'affiche
5. Compagnon trace sa signature au doigt/stylet
6. Appuie sur "Valider la signature"
7. Frontend encode l'image en base64
8. Requête API envoyée
9. Backend horodate la signature
```

#### 5.2.3 Requête de signature

```http
POST /api/pointages/156/signer
Content-Type: application/json
Authorization: Bearer <token_compagnon>

{
  "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
}
```

**Réponse** :

```json
{
  "id": 156,
  "statut": "brouillon",
  "signature_utilisateur": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "signature_date": "2026-01-27T17:45:00Z",
  "is_signed": true
}
```

**Règles** :
- Seul le compagnon propriétaire du pointage peut signer
- La signature n'est possible que si le statut est BROUILLON
- La signature est stockée en base64 (image PNG)
- L'horodatage est ajouté automatiquement côté serveur
- La signature est conservée même après soumission/validation (preuve légale)

---

### 5.3 Workflow C : Soumission pour validation

**Acteur** : Compagnon
**Prérequis** : Pointage au statut BROUILLON

#### 5.3.1 Flux nominal

```
┌─────────────┐                    ┌───────────────────┐
│ Compagnon   │                    │ Chef de chantier  │
│             │                    │ ou Conducteur     │
│             │                    │ ou Admin          │
│             │                    │                   │
│  1. Revoit  │                    │                   │
│     ses     │                    │                   │
│     heures  │                    │                   │
│             │                    │                   │
│  2. Signe   │                    │                   │
│     (optionnel mais recommandé)  │                   │
│             │                    │                   │
│  3. Clique  │                    │                   │
│     "Soumettre"                  │                   │
│             │    ──────────►     │                   │
│             │    BROUILLON       │  4. Notification  │
│             │    → SOUMIS        │     reçue         │
│             │                    │                   │
│             │                    │  5. Apparaît dans │
│             │                    │     "À valider"   │
└─────────────┘                    └───────────────────┘
```

#### 5.3.2 Requête de soumission

```http
POST /api/pointages/156/soumettre
Authorization: Bearer <token_compagnon>
```

**Réponse** :

```json
{
  "id": 156,
  "statut": "soumis",
  "updated_at": "2026-01-27T18:00:00Z"
}
```

**Event publié** : `PointageSubmittedEvent`

```python
PointageSubmittedEvent(
    pointage_id=156,
    utilisateur_id=7,
    chantier_id=1,
    date_pointage=date(2026, 1, 27),
    heures_normales="7:30",
    heures_supplementaires="1:30",
)
```

#### 5.3.3 Cas d'erreur

| Erreur | Code HTTP | Message |
|--------|-----------|---------|
| Statut incompatible | 400 Bad Request | `Impossible de soumettre : le pointage n'est pas en brouillon` |
| Période verrouillée | 403 Forbidden | `La période de paie est verrouillée` |

---

### 5.4 Workflow D : Validation

**Acteur** : Chef de chantier, Conducteur de travaux ou Admin
**Prérequis** : Pointage au statut SOUMIS

#### 5.4.1 Flux nominal

```
┌───────────────────┐                    ┌─────────────┐
│ Chef / Conducteur │                    │ Compagnon   │
│ ou Admin          │                    │             │
│                   │                    │             │
│  1. Ouvre liste   │                    │             │
│     "À valider"   │                    │             │
│                   │                    │             │
│  2. Examine les   │                    │             │
│     heures        │                    │             │
│     - Cohérence   │                    │             │
│       planning    │                    │             │
│     - Signature   │                    │             │
│       présente ?  │                    │             │
│     - Commentaire │                    │             │
│                   │                    │             │
│  3. Clique        │                    │             │
│     "Valider"     │                    │             │
│             │    ──────────►          │             │
│             │    SOUMIS               │  4. Notif.  │
│             │    → VALIDÉ             │     reçue   │
│             │                         │  "Validé ✅" │
└─────────────┘                         └─────────────┘
```

#### 5.4.2 Requête de validation

```http
POST /api/pointages/156/valider
Content-Type: application/json
Authorization: Bearer <token_chef>

{
  "validateur_id": 4
}
```

**Réponse** :

```json
{
  "id": 156,
  "statut": "valide",
  "validateur_id": 4,
  "validation_date": "2026-01-28T09:15:00Z",
  "updated_at": "2026-01-28T09:15:00Z"
}
```

**Event publié** : `PointageValidatedEvent`

#### 5.4.3 Points de vérification pour le validateur

Le validateur devrait vérifier avant d'approuver :

| Vérification | Description |
|-------------|-------------|
| **Heures cohérentes** | Les heures déclarées correspondent au planning prévu |
| **Signature présente** | Le compagnon a signé (recommandé, pas bloquant) |
| **Pas de doublon** | Le compagnon n'a pas pointé le même jour sur un autre chantier avec un total > 10h |
| **Commentaire** | Si heures inhabituelles, un commentaire explique pourquoi |
| **Heures supplémentaires** | Les heures sup sont justifiées (demande préalable) |

---

### 5.5 Workflow E : Rejet et correction

**Acteur rejet** : Chef de chantier, Conducteur ou Admin
**Acteur correction** : Compagnon

#### 5.5.1 Flux complet (aller-retour)

```
┌───────────────────┐                    ┌─────────────┐
│ Chef / Conducteur │                    │ Compagnon   │
│                   │                    │             │
│  1. Examine les   │                    │             │
│     heures        │                    │             │
│                   │                    │             │
│  2. Constate une  │                    │             │
│     anomalie      │                    │             │
│     (ex: 12h sup  │                    │             │
│      non justifiées)                   │             │
│                   │                    │             │
│  3. Clique        │                    │             │
│     "Rejeter"     │                    │             │
│     + saisit motif│                    │             │
│                   │   ──────────►      │             │
│                   │   SOUMIS → REJETÉ  │  4. Notif   │
│                   │                    │  "Rejeté ❌" │
│                   │                    │  + motif    │
│                   │                    │             │
│                   │                    │  5. Ouvre   │
│                   │                    │     pointage│
│                   │                    │             │
│                   │                    │  6. Corrige │
│                   │                    │     heures  │
│                   │                    │  REJETÉ     │
│                   │                    │  → BROUILLON│
│                   │                    │             │
│                   │                    │  7. Re-signe│
│                   │                    │             │
│                   │                    │  8. Re-     │
│                   │   ◄──────────      │  soumet     │
│                   │   BROUILLON        │             │
│                   │   → SOUMIS         │             │
│                   │                    │             │
│  9. Re-examine    │                    │             │
│                   │                    │             │
│  10. Valide ✅    │                    │             │
│                   │   ──────────►      │  11. Notif  │
│                   │   SOUMIS → VALIDÉ  │  "Validé ✅" │
└───────────────────┘                    └─────────────┘
```

#### 5.5.2 Requête de rejet

```http
POST /api/pointages/156/rejeter
Content-Type: application/json
Authorization: Bearer <token_chef>

{
  "validateur_id": 4,
  "motif": "12h supplémentaires non justifiées. Merci de corriger ou d'ajouter un commentaire explicatif."
}
```

**Réponse** :

```json
{
  "id": 156,
  "statut": "rejete",
  "validateur_id": 4,
  "validation_date": "2026-01-28T09:20:00Z",
  "motif_rejet": "12h supplémentaires non justifiées. Merci de corriger ou d'ajouter un commentaire explicatif.",
  "updated_at": "2026-01-28T09:20:00Z"
}
```

**Event publié** : `PointageRejectedEvent`

**Règle** : Le motif de rejet est **obligatoire**. Un rejet sans motif est refusé (400 Bad Request).

#### 5.5.3 Requête de correction (reprise par le compagnon)

Après un rejet, le compagnon peut :

1. **Reprendre en brouillon** :

```http
POST /api/pointages/156/corriger
Authorization: Bearer <token_compagnon>
```

→ Statut passe de REJETÉ à BROUILLON.

2. **Modifier les heures** (maintenant possible car BROUILLON) :

```http
PUT /api/pointages/156
Content-Type: application/json

{
  "heures_supplementaires": "1:30",
  "commentaire": "1h30 sup validées oralement par chef - finition urgente dalle"
}
```

3. **Re-signer et re-soumettre** (retour au workflow C)

---

## 6. Calculs et agrégations

### 6.1 Totaux par jour (FDH-08)

Pour un compagnon donné sur une semaine :

```
          Lundi    Mardi    Mercredi  Jeudi    Vendredi  TOTAL
          27/01    28/01    29/01     30/01    31/01
─────────────────────────────────────────────────────────────────
Villa     7h30     8h00     7h00      8h00     7h30      38h00
Duplex    norm     norm     norm      norm     norm

Villa     0h00     0h00     1h00      0h00     0h30       1h30
Duplex    sup      sup      sup       sup      sup

Résid.    1h30     0h00     0h00      0h00     0h00       1h30
Alpes     sup      sup      sup       sup      sup
─────────────────────────────────────────────────────────────────
TOTAL     9h00     8h00     8h00      8h00     8h00      41h00
JOUR
```

### 6.2 Totaux par chantier (FDH-09)

```
                    Normales    Sup     Total
──────────────────────────────────────────────
Villa Duplex        38h00      1h30    39h30
Résidence Alpes      0h00      1h30     1h30
──────────────────────────────────────────────
TOTAL SEMAINE       38h00      3h00    41h00
```

### 6.3 Conversion décimale (pour paie)

| HH:MM | Décimal | Calcul |
|-------|---------|--------|
| 7:00 | 7.0 | 7 + 0/60 |
| 7:15 | 7.25 | 7 + 15/60 |
| 7:30 | 7.5 | 7 + 30/60 |
| 7:45 | 7.75 | 7 + 45/60 |
| 8:00 | 8.0 | 8 + 0/60 |

**Formule** : `decimal = heures + (minutes / 60)`

### 6.4 Récapitulatif mensuel

Le récapitulatif mensuel agrège toutes les feuilles d'heures d'un compagnon sur le mois :

```
┌──────────────────────────────────────────────────────────┐
│ RÉCAPITULATIF JANVIER 2026 - Sébastien ACHKAR            │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Semaine 1 (05-11/01) :  39h00 norm + 2h00 sup = 41h00  │
│  Semaine 2 (12-18/01) :  38h30 norm + 1h30 sup = 40h00  │
│  Semaine 3 (19-25/01) :  35h00 norm + 0h00 sup = 35h00  │
│  Semaine 4 (26-31/01) :  38h00 norm + 3h00 sup = 41h00  │
│  ─────────────────────────────────────────────────────── │
│  TOTAL MOIS :            150h30 norm + 6h30 sup = 157h00 │
│                                                           │
│  Variables de paie :                                      │
│  - Paniers repas    : 20 × 10.50€ = 210.00€             │
│  - Indemnité trajet : 20 ×  8.20€ = 164.00€             │
│  - Prime salissure  : 20 ×  3.00€ =  60.00€             │
│  ─────────────────────────────────────────────────────── │
│  TOTAL VARIABLES :                     434.00€            │
│                                                           │
│  Absences :                                               │
│  - Aucune                                                 │
│                                                           │
│  Statut : ✅ Tous validés                                 │
└──────────────────────────────────────────────────────────┘
```

---

## 7. Synchronisation Planning (FDH-10)

### 7.1 Principe

Quand un compagnon est **affecté à un chantier via le planning**, le système peut automatiquement **pré-créer les pointages** pour la semaine correspondante. Cela évite au compagnon de saisir manuellement chaque jour.

```
┌──────────────────────┐         ┌──────────────────────┐
│ MODULE PLANNING      │         │ MODULE POINTAGES     │
│                      │         │                      │
│ Affectation :        │  FDH-10 │ Pointages générés :  │
│ Sébastien ACHKAR     │ ──────► │                      │
│ Villa Duplex         │ (bulk)  │ Lun 27/01 - 7h00    │
│ 27/01 → 31/01       │         │ Mar 28/01 - 7h00    │
│ 07:00 → 16:00       │         │ Mer 29/01 - 7h00    │
│                      │         │ Jeu 30/01 - 7h00    │
│                      │         │ Ven 31/01 - 7h00    │
│                      │         │                      │
│                      │         │ Statut : BROUILLON   │
│                      │         │ (modifiable)         │
└──────────────────────┘         └──────────────────────┘
```

### 7.2 Requête de création bulk

```http
POST /api/pointages/bulk
Content-Type: application/json
Authorization: Bearer <token>

{
  "utilisateur_id": 7,
  "semaine_debut": "2026-01-27",
  "affectations": [
    {
      "affectation_id": 42,
      "chantier_id": 1,
      "dates": ["2026-01-27", "2026-01-28", "2026-01-29", "2026-01-30", "2026-01-31"],
      "heures_normales": "7:00",
      "heures_supplementaires": "0:00"
    }
  ]
}
```

**Réponse** : Liste des pointages créés (tous en statut BROUILLON).

### 7.3 Comportement

| Situation | Comportement |
|-----------|-------------|
| Aucun pointage existant | Création de tous les pointages |
| Pointage déjà existant pour un jour/chantier | Le pointage existant est **conservé** (pas d'écrasement) |
| Affectation sans horaires | Pointage créé avec heures à 0:00 (à remplir par le compagnon) |
| Affectation récurrente | Un pointage par jour de récurrence |

**Règle clé** : Les pointages générés sont toujours en BROUILLON. Le compagnon doit les vérifier, ajuster si besoin, signer et soumettre.

---

## 8. Export paie

### 8.1 Formats disponibles

| Format | Usage | Contenu |
|--------|-------|---------|
| **CSV** | Import logiciel paie | Colonnes structurées, séparateur `;` |
| **XLSX** | Consultation bureau | Feuille Excel avec mise en forme |
| **PDF** | Archive légale / impression | Mise en page formelle avec signatures |
| **ERP** | Intégration directe | Format spécifique au logiciel de paie du client |

### 8.2 Requête d'export

```http
POST /api/pointages/export
Content-Type: application/json
Authorization: Bearer <token_conducteur>

{
  "format": "xlsx",
  "date_debut": "2026-01-01",
  "date_fin": "2026-01-31",
  "utilisateur_ids": [7, 8, 9, 10],
  "inclure_variables_paie": true,
  "inclure_signatures": true,
  "grouper_par": "utilisateur"
}
```

### 8.3 Contenu de l'export

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `matricule` | ID utilisateur | 7 |
| `nom` | Nom complet | ACHKAR Sébastien |
| `date` | Date du pointage | 27/01/2026 |
| `code_chantier` | Code du chantier | A001 |
| `nom_chantier` | Nom du chantier | Villa Duplex |
| `heures_normales` | Heures normales (décimal) | 7.50 |
| `heures_sup` | Heures supplémentaires (décimal) | 1.50 |
| `total_heures` | Total (décimal) | 9.00 |
| `statut` | Statut du pointage | VALIDÉ |
| `panier_repas` | Montant panier | 10.50 |
| `indemnite_transport` | Montant trajet | 8.20 |
| `prime_salissure` | Montant prime | 3.00 |
| `signature` | Signé ? | OUI |
| `validateur` | Qui a validé | Nicolas DELSALLE |
| `date_validation` | Quand | 28/01/2026 |

### 8.4 Règles d'export

| Règle | Description |
|-------|-------------|
| Seuls les pointages VALIDÉ sont exportables pour la paie | Evite de payer sur des pointages non vérifiés |
| Les pointages BROUILLON/SOUMIS apparaissent avec un avertissement | Pour repérer les retards de validation |
| Les pointages REJETÉ sont exclus par défaut | Optionnellement inclus pour audit |
| L'export inclut les variables de paie rattachées | Primes, indemnités et absences |

---

## 9. Interactions avec autres modules

### 9.1 Schéma d'interactions

```
┌──────────────┐     FDH-10 (bulk)     ┌──────────────────┐
│   PLANNING   │ ──────────────────────►│   POINTAGES      │
│              │                        │                  │
│ Affectations │     Lien FK            │ Pointages        │
│ (PLN-*)      │ ◄─────────────────────│ (affectation_id) │
└──────┬───────┘                        └────────┬─────────┘
       │                                         │
       │ chantier_id                              │ utilisateur_id
       │                                         │ chantier_id
       ▼                                         │
┌──────────────┐                                 │
│  CHANTIERS   │◄────────────────────────────────┘
│              │     chantier_id (FK)
│ Statut actif │
│ requis       │
└──────────────┘
       │
       │ Events
       ▼
┌──────────────┐     PointageValidatedEvent     ┌──────────────┐
│   AUTH       │                                │  DASHBOARD   │
│              │                                │              │
│ utilisateur  │                                │ KPIs heures  │
│ validateur   │                                │ travaillées  │
└──────────────┘                                └──────────────┘
                                                        │
                                                        ▼
                                                ┌──────────────┐
                                                │  EXPORT PAIE │
                                                │  (ERP)       │
                                                └──────────────┘
```

### 9.2 Détail des interactions

| Source | Cible | Type | Description |
|--------|-------|------|-------------|
| Planning → Pointages | FDH-10 | Création bulk | Les affectations pré-remplissent les pointages |
| Pointages → Planning | FK | Référence | `affectation_id` trace l'origine |
| Chantiers → Pointages | Validation | Contrôle | Chantier doit être actif pour pointer |
| Pointages → Auth | FK | Référence | `utilisateur_id`, `validateur_id`, `created_by` |
| Pointages → Dashboard | Event | Agrégation | Heures travaillées par chantier/équipe |
| Pointages → Export | Endpoint | Lecture | Génération fichiers paie |

### 9.3 Events publiés

| Event | Déclencheur | Contenu | Consommateurs |
|-------|-------------|---------|--------------|
| `PointageSubmittedEvent` | Compagnon soumet | pointage_id, utilisateur_id, chantier_id, date, heures | Notifications (alerte chef) |
| `PointageValidatedEvent` | Chef/Conducteur/Admin valide | pointage_id, validateur_id, date_validation | Dashboard, Export paie, **Notifications** (`heures.validated` → notifie le compagnon) |
| `PointageRejectedEvent` | Chef/Conducteur/Admin rejette | pointage_id, validateur_id, motif_rejet | Notifications (alerte compagnon) |

---

## 10. Architecture technique

### 10.1 Structure des fichiers

```
backend/modules/pointages/
│
├── domain/                              # Couche Domain
│   ├── entities/
│   │   ├── pointage.py                 # Entity Pointage (workflow + règles)
│   │   ├── feuille_heures.py           # Entity FeuilleHeures (agrégat semaine)
│   │   └── variable_paie.py            # Entity VariablePaie (primes/absences)
│   ├── value_objects/
│   │   ├── statut_pointage.py          # VO StatutPointage (machine à états)
│   │   ├── duree.py                    # VO Duree (HH:MM)
│   │   └── type_variable_paie.py       # VO TypeVariablePaie (enum)
│   ├── repositories.py                  # Interface Repository
│   └── events/
│       ├── pointage_submitted.py
│       ├── pointage_validated.py
│       └── pointage_rejected.py
│
├── application/                         # Couche Application
│   ├── use_cases/
│   │   ├── create_pointage.py          # UC Création
│   │   ├── update_pointage.py          # UC Modification
│   │   ├── sign_pointage.py            # UC Signature
│   │   ├── submit_pointage.py          # UC Soumission
│   │   ├── validate_pointage.py        # UC Validation
│   │   ├── reject_pointage.py          # UC Rejet
│   │   ├── correct_pointage.py         # UC Correction
│   │   ├── bulk_create_pointage.py     # UC Création bulk (FDH-10)
│   │   ├── get_feuille_heures.py       # UC Lecture feuille
│   │   ├── list_pointages.py           # UC Lecture liste
│   │   ├── export_pointages.py         # UC Export paie
│   │   └── create_variable_paie.py     # UC Variable paie
│   └── dtos/
│       ├── create_pointage_dto.py
│       ├── update_pointage_dto.py
│       ├── sign_pointage_dto.py
│       ├── validate_pointage_dto.py
│       ├── reject_pointage_dto.py
│       ├── export_pointage_dto.py
│       ├── pointage_dto.py             # DTO sortie
│       └── feuille_heures_dto.py       # DTO sortie agrégé
│
├── adapters/                            # Couche Adapters
│   └── controllers/
│       └── pointage_controller.py      # Controller FastAPI
│
└── infrastructure/                      # Couche Infrastructure
    ├── persistence/
    │   ├── models.py                   # SQLAlchemy Models
    │   └── sqlalchemy_pointage_repository.py
    └── web/
        └── pointage_routes.py          # Routes FastAPI
```

### 10.2 Clean Architecture - Flux d'une validation

```
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│  HTTP Request                                                         │
│  POST /api/pointages/156/valider                                      │
│       │                                                               │
│       ▼                                                               │
│  ┌─────────────────────────────────┐                                 │
│  │ Infrastructure / Web            │  pointage_routes.py             │
│  │ Route FastAPI                   │  Parse JSON, auth middleware     │
│  └──────────────┬──────────────────┘                                 │
│                 │                                                      │
│                 ▼                                                      │
│  ┌─────────────────────────────────┐                                 │
│  │ Adapters / Controllers          │  pointage_controller.py         │
│  │ PointageController.valider()    │  Convertit Request → DTO        │
│  └──────────────┬──────────────────┘                                 │
│                 │                                                      │
│                 ▼                                                      │
│  ┌─────────────────────────────────┐                                 │
│  │ Application / Use Cases         │  validate_pointage.py           │
│  │ ValidatePointageUseCase         │                                 │
│  │                                 │  1. Récupère pointage (repo)    │
│  │                                 │  2. Vérifie statut = SOUMIS     │
│  │                                 │  3. Vérifie verrouillage mois   │
│  │                                 │  4. Appelle pointage.valider()  │
│  │                                 │  5. Sauvegarde (repo)           │
│  │                                 │  6. Publie event                │
│  └──────────────┬──────────────────┘                                 │
│                 │                                                      │
│                 ▼                                                      │
│  ┌─────────────────────────────────┐                                 │
│  │ Domain / Entities               │  pointage.py                    │
│  │ Pointage.valider()              │                                 │
│  │                                 │  Vérifie can_transition_to()    │
│  │                                 │  Met à jour statut → VALIDÉ     │
│  │                                 │  Met à jour validateur_id       │
│  │                                 │  Met à jour validation_date     │
│  └─────────────────────────────────┘                                 │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### 10.3 Modèle de données (SQLAlchemy)

**Table `pointages`** :

| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| `id` | SERIAL | PK | Identifiant auto-incrémenté |
| `utilisateur_id` | INT | NOT NULL, INDEX | Référence utilisateur |
| `chantier_id` | INT | NOT NULL, INDEX | Référence chantier |
| `date_pointage` | DATE | NOT NULL | Date du travail |
| `heures_normales_minutes` | INT | DEFAULT 0 | Stockage interne en minutes |
| `heures_supplementaires_minutes` | INT | DEFAULT 0 | Stockage interne en minutes |
| `statut` | VARCHAR(20) | DEFAULT 'brouillon' | État du workflow |
| `signature_utilisateur` | TEXT | NULLABLE | Base64 de la signature manuscrite |
| `signature_date` | TIMESTAMPTZ | NULLABLE | Horodatage signature |
| `validateur_id` | INT | NULLABLE | Qui a validé/rejeté |
| `validation_date` | TIMESTAMPTZ | NULLABLE | Quand validé/rejeté |
| `motif_rejet` | TEXT | NULLABLE | Raison du rejet |
| `commentaire` | TEXT | NULLABLE | Note libre |
| `affectation_id` | INT | NULLABLE | Lien planning |
| `created_by` | INT | NULLABLE | Créateur |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Création |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Modification |

**Contrainte d'unicité** : `UNIQUE(utilisateur_id, chantier_id, date_pointage)`

**Index** :
- `ix_pointage_semaine` : `(utilisateur_id, date_pointage)`
- `ix_pointage_chantier_semaine` : `(chantier_id, date_pointage)`

**Table `feuilles_heures`** :

| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| `id` | SERIAL | PK | Identifiant |
| `utilisateur_id` | INT | NOT NULL | Référence utilisateur |
| `semaine_debut` | DATE | NOT NULL | Lundi de la semaine |
| `annee` | INT | NOT NULL | Année ISO |
| `numero_semaine` | INT | NOT NULL | Numéro semaine ISO |
| `statut_global` | VARCHAR(20) | NULLABLE | Statut agrégé |
| `commentaire_global` | TEXT | NULLABLE | Note globale |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Création |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Modification |

**Contrainte d'unicité** : `UNIQUE(utilisateur_id, semaine_debut)`

**Table `variables_paie`** :

| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| `id` | SERIAL | PK | Identifiant |
| `pointage_id` | INT | FK CASCADE | Lien vers pointage |
| `type_variable` | VARCHAR(50) | NOT NULL | Type de variable |
| `valeur` | NUMERIC(10,2) | NOT NULL | Montant ou heures |
| `date_application` | DATE | NOT NULL | Date d'application |
| `commentaire` | TEXT | NULLABLE | Note |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Création |

---

## 11. Scénarios de test

### 11.1 Happy path : Cycle complet de validation

```python
def test_workflow_complet_validation(client, db_session):
    """
    Test cycle complet :
    1. Création pointage (BROUILLON)
    2. Signature manuscrite
    3. Soumission (SOUMIS)
    4. Validation par chef (VALIDÉ)
    """
    # 1. Création
    response = client.post("/api/pointages", json={
        "utilisateur_id": 7,
        "chantier_id": 1,
        "date_pointage": "2026-01-27",
        "heures_normales": "7:30",
        "heures_supplementaires": "1:30",
    })
    assert response.status_code == 201
    pointage_id = response.json()["id"]
    assert response.json()["statut"] == "brouillon"

    # 2. Signature
    response = client.post(f"/api/pointages/{pointage_id}/signer", json={
        "signature": "data:image/png;base64,iVBORw0KGgo...",
    })
    assert response.status_code == 200
    assert response.json()["is_signed"] is True

    # 3. Soumission
    response = client.post(f"/api/pointages/{pointage_id}/soumettre")
    assert response.status_code == 200
    assert response.json()["statut"] == "soumis"

    # 4. Validation
    response = client.post(f"/api/pointages/{pointage_id}/valider", json={
        "validateur_id": 4,
    })
    assert response.status_code == 200
    assert response.json()["statut"] == "valide"
    assert response.json()["validateur_id"] == 4
    assert response.json()["validation_date"] is not None
```

### 11.2 Cycle de rejet et correction

```python
def test_workflow_rejet_correction(client, db_session):
    """
    Test cycle rejet :
    1. Création + soumission
    2. Rejet par chef (avec motif)
    3. Correction par compagnon
    4. Re-soumission
    5. Validation finale
    """
    # 1. Création + soumission
    pointage_id = create_and_submit_pointage(client)

    # 2. Rejet
    response = client.post(f"/api/pointages/{pointage_id}/rejeter", json={
        "validateur_id": 4,
        "motif": "Heures sup non justifiées",
    })
    assert response.status_code == 200
    assert response.json()["statut"] == "rejete"
    assert response.json()["motif_rejet"] == "Heures sup non justifiées"

    # 3. Correction (reprise en brouillon)
    response = client.post(f"/api/pointages/{pointage_id}/corriger")
    assert response.status_code == 200
    assert response.json()["statut"] == "brouillon"

    # 4. Modification des heures
    response = client.put(f"/api/pointages/{pointage_id}", json={
        "heures_supplementaires": "0:30",
        "commentaire": "Corrigé : 30min sup seulement",
    })
    assert response.status_code == 200

    # 5. Re-soumission
    response = client.post(f"/api/pointages/{pointage_id}/soumettre")
    assert response.status_code == 200
    assert response.json()["statut"] == "soumis"

    # 6. Validation finale
    response = client.post(f"/api/pointages/{pointage_id}/valider", json={
        "validateur_id": 4,
    })
    assert response.status_code == 200
    assert response.json()["statut"] == "valide"
```

### 11.3 Transitions interdites

```python
def test_transitions_interdites(client, db_session):
    """Test que les transitions illégales sont refusées."""

    # BROUILLON → VALIDÉ (interdit : doit passer par SOUMIS)
    pointage_id = create_pointage(client, statut="brouillon")
    response = client.post(f"/api/pointages/{pointage_id}/valider", json={
        "validateur_id": 4,
    })
    assert response.status_code == 400

    # VALIDÉ → BROUILLON (interdit : état final)
    pointage_id = create_validated_pointage(client)
    response = client.post(f"/api/pointages/{pointage_id}/corriger")
    assert response.status_code == 400

    # SOUMIS → BROUILLON (interdit : le compagnon ne retire pas)
    pointage_id = create_submitted_pointage(client)
    response = client.put(f"/api/pointages/{pointage_id}", json={
        "heures_normales": "5:00",
    })
    assert response.status_code == 400
```

### 11.4 Rejet sans motif (interdit)

```python
def test_rejet_sans_motif_interdit(client, db_session):
    """Le motif est obligatoire lors d'un rejet."""
    pointage_id = create_submitted_pointage(client)

    response = client.post(f"/api/pointages/{pointage_id}/rejeter", json={
        "validateur_id": 4,
        # pas de "motif"
    })
    assert response.status_code == 400
```

### 11.5 Verrouillage mensuel

```python
def test_verrouillage_mensuel(client, db_session):
    """
    Après le vendredi précédant la dernière semaine du mois,
    aucune modification n'est possible.
    """
    # Créer un pointage pour le 5 janvier 2026
    pointage_id = create_pointage(client, date="2026-01-05")

    # Simuler qu'on est le 25 janvier (après verrouillage)
    with freeze_time("2026-01-25"):
        # Modifier → interdit
        response = client.put(f"/api/pointages/{pointage_id}", json={
            "heures_normales": "8:00",
        })
        assert response.status_code == 403

        # Soumettre → interdit
        response = client.post(f"/api/pointages/{pointage_id}/soumettre")
        assert response.status_code == 403

        # Consulter → toujours OK
        response = client.get(f"/api/pointages/{pointage_id}")
        assert response.status_code == 200
```

### 11.6 Contrainte d'unicité

```python
def test_doublon_pointage_interdit(client, db_session):
    """Un seul pointage par (utilisateur, chantier, date)."""
    # Premier pointage → OK
    response = client.post("/api/pointages", json={
        "utilisateur_id": 7,
        "chantier_id": 1,
        "date_pointage": "2026-01-27",
        "heures_normales": "7:30",
    })
    assert response.status_code == 201

    # Même combinaison → 409 Conflict
    response = client.post("/api/pointages", json={
        "utilisateur_id": 7,
        "chantier_id": 1,
        "date_pointage": "2026-01-27",
        "heures_normales": "8:00",
    })
    assert response.status_code == 409
```

### 11.7 Multi-chantiers par jour

```python
def test_multi_chantiers_par_jour(client, db_session):
    """Un compagnon peut pointer sur plusieurs chantiers le même jour."""
    # Chantier 1 → OK
    response = client.post("/api/pointages", json={
        "utilisateur_id": 7,
        "chantier_id": 1,
        "date_pointage": "2026-01-27",
        "heures_normales": "4:00",
    })
    assert response.status_code == 201

    # Chantier 2, même jour → OK (chantier_id différent)
    response = client.post("/api/pointages", json={
        "utilisateur_id": 7,
        "chantier_id": 2,
        "date_pointage": "2026-01-27",
        "heures_normales": "4:00",
    })
    assert response.status_code == 201
```

### 11.8 Couverture de tests attendue

| Module | Couverture cible |
|--------|-----------------|
| `domain/entities/pointage.py` | >= 95% |
| `domain/entities/feuille_heures.py` | >= 90% |
| `domain/entities/variable_paie.py` | >= 85% |
| `domain/value_objects/statut_pointage.py` | 100% |
| `domain/value_objects/duree.py` | 100% |
| `application/use_cases/validate_pointage.py` | >= 95% |
| `application/use_cases/reject_pointage.py` | >= 95% |
| `application/use_cases/submit_pointage.py` | >= 90% |
| `application/use_cases/bulk_create_pointage.py` | >= 85% |

**Commande** :

```bash
cd backend
pytest tests/unit/modules/pointages -v --cov=modules/pointages --cov-report=html
```

---

## 12. Points d'attention

### 12.1 Sécurité

| Point | Risque | Mitigation |
|-------|--------|------------|
| **Signature falsifiée** | Quelqu'un signe à la place d'un compagnon | Seul le propriétaire peut signer (vérif token JWT) |
| **Validation non autorisée** | Un compagnon valide ses propres heures | Contrôle de rôle côté backend (chef/conducteur/admin) |
| **Modification après validation** | Heures modifiées après approbation | Machine à états bloque toute modification sur VALIDÉ |
| **Période verrouillée** | Modification rétroactive de pointages | Vérification date de verrouillage à chaque action |
| **Injection motif rejet** | XSS dans le motif de rejet | Sanitisation des champs texte |

### 12.2 Performance

| Point | Impact | Optimisation |
|-------|--------|--------------|
| **Chargement feuille hebdo** | N+1 queries (pointages + variables) | JOIN eagerly les variables de paie |
| **Export mensuel** | Volume important (N compagnons × 20 jours) | Pagination + streaming |
| **Calcul totaux** | Recalcul à chaque affichage | Cache en mémoire ou recalcul paresseux |
| **Stockage signatures** | Base64 = ~50Ko par signature | Envisager stockage S3 avec URL |

### 12.3 Cohérence données

| Point | Problème | Solution |
|-------|----------|----------|
| **Heures > 24h/jour** | Saisie absurde | Validation : total heures par jour <= 24h |
| **Heures sup sans normales** | Incohérence | Avertissement (non bloquant) |
| **Pointage sans chantier actif** | Chantier fermé entre-temps | Vérification statut chantier à la soumission |
| **Utilisateur désactivé** | Compagnon parti pendant le mois | Permettre validation des pointages existants |
| **Feuille incomplète** | Jours manquants | Avertissement visuel, pas de blocage |

### 12.4 RGPD

| Point | Obligation | Implémentation |
|-------|-----------|----------------|
| **Données personnelles** | Heures travaillées = donnée personnelle | Accès restreint par rôle |
| **Signature manuscrite** | Donnée biométrique sensible | Stockage chiffré, accès audit |
| **Conservation** | 5 ans (droit du travail) | Archivage automatique après 5 ans |
| **Droit d'accès** | Le salarié peut demander ses données | Export personnel disponible |
| **Droit de rectification** | Le salarié peut demander correction | Processus via admin uniquement |

### 12.5 UX terrain (mobile/tablette)

| Point | Contrainte | Solution |
|-------|-----------|----------|
| **Gros doigts** | Cellules trop petites sur mobile | Cellules tactiles >= 48px |
| **Soleil** | Écran illisible en extérieur | Contraste élevé, mode "chantier" |
| **Gants** | Saisie difficile avec gants | Zone de signature large, boutons XL |
| **Réseau** | Pas de 4G sur certains chantiers | Mode offline (saisie locale + sync) |
| **Vitesse** | Le compagnon a 2 minutes en fin de journée | Pré-remplissage depuis planning (FDH-10) |

### 12.6 Évolutions futures

| Amélioration | Priorité | Description |
|-------------|----------|-------------|
| Validation par lot | Haute | Valider tous les pointages d'une feuille en un clic |
| Notification push | Haute | Alerter le chef quand un compagnon soumet |
| Mode offline | Haute | Saisie sans réseau, synchronisation différée |
| Double validation | Moyenne | Chef valide puis conducteur contre-valide |
| Alerte heures anormales | Moyenne | Notification si > 10h/jour ou > 48h/semaine |
| Historique modifications | Basse | Log de toutes les modifications d'un pointage |
| Géolocalisation pointage | Basse | Vérifier que le compagnon est bien sur le chantier |

---

## 13. Résumé

### 13.1 Vue synthétique du workflow

```
    COMPAGNON                     CHEF / CONDUCTEUR / ADMIN
    ─────────                     ─────────────────────────

    ┌─────────────┐
    │ 1. Saisir   │
    │    heures   │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │ 2. Signer   │
    │  (tablette) │
    └──────┬──────┘
           │
    ┌──────▼──────┐               ┌──────────────┐
    │ 3. Soumettre│──────────────►│ 4. Examiner  │
    └─────────────┘               └──────┬───────┘
                                         │
                                    ┌────┴────┐
                                    │         │
                              ┌─────▼───┐ ┌───▼─────┐
                              │ VALIDER │ │ REJETER │
                              │   ✅    │ │   ❌    │
                              └─────────┘ └────┬────┘
                                               │
    ┌─────────────┐                            │
    │ 5. Corriger │◄───────────────────────────┘
    └──────┬──────┘
           │
           └──── Retour à l'étape 2 (re-signer + re-soumettre)


    VERROUILLAGE : Vendredi avant la dernière semaine du mois
    → Plus aucune action possible après cette date.
```

### 13.2 Forces

- **Machine à états rigoureuse** : Transitions contrôlées, pas de raccourcis possibles
- **Traçabilité complète** : Qui a saisi, signé, soumis, validé/rejeté, quand, avec quel motif
- **Signature manuscrite** : Preuve légale sur tablette (conformité BTP)
- **Multi-validateurs** : Chef, conducteur ou admin — le premier qui agit tranche
- **Verrouillage mensuel** : Sécurité paie, impossible de modifier rétroactivement
- **Sync planning** : Pré-remplissage automatique (gain de temps terrain)

### 13.3 Prochaines étapes

1. ✅ **Documentation complète** (ce fichier)
2. Implémenter la vérification de verrouillage mensuel dans les use cases
3. Ajouter la validation par lot (tous les pointages d'une feuille)
4. ~~Implémenter les notifications lors des validations~~ ✅ Done (`heures.validated` handler dans notifications)
5. Tests d'intégration du cycle complet (>= 85% couverture)

---

**Auteur** : Claude Opus 4.5
**Date dernière mise à jour** : 31 janvier 2026
**Version** : 1.1 (audit executabilite : handler heures.validated cable dans notifications)
**Statut** : ✅ Complet + Audite

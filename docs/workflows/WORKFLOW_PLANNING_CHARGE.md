# Workflow Planning de Charge - Hub Chantier

> Document cree le 30 janvier 2026
> Analyse complete du workflow de planning de charge et taux d'occupation

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entites et objets metier](#2-entites-et-objets-metier)
3. [Taux d'occupation et seuils](#3-taux-doccupation-et-seuils)
4. [Types de metiers](#4-types-de-metiers)
5. [Flux de planification des besoins](#5-flux-de-planification-des-besoins)
6. [Vue tabulaire du planning](#6-vue-tabulaire-du-planning)
7. [Footer d'occupation](#7-footer-doccupation)
8. [Details d'occupation par semaine](#8-details-doccupation-par-semaine)
9. [Calculs et formules](#9-calculs-et-formules)
10. [Permissions et roles](#10-permissions-et-roles)
11. [Evenements domaine](#11-evenements-domaine)
12. [API REST - Endpoints](#12-api-rest---endpoints)
13. [Architecture technique](#13-architecture-technique)
14. [Scenarios de test](#14-scenarios-de-test)
15. [Evolutions futures](#15-evolutions-futures)
16. [References CDC](#16-references-cdc)

---

## 1. VUE D'ENSEMBLE

### Objectif du module

Le module Planning de Charge permet aux conducteurs de travaux et administrateurs de visualiser la charge de travail de l'entreprise sur plusieurs semaines. Il compare les **besoins** (heures necessaires par chantier) a la **capacite** (heures disponibles des compagnons) pour detecter les surcharges ou sous-charges.

### Concepts cles

```
CAPACITE = Nombre de compagnons actifs x 35h/semaine
PLANIFIE = Heures reellement affectees (module planning operationnel)
BESOIN   = Heures estimees necessaires (saisie manuelle par le conducteur)

Taux d'occupation = (PLANIFIE / CAPACITE) x 100%

A recruter = ceil(max(BESOIN - CAPACITE, 0) / 35)
A placer   = Nombre de compagnons non planifies cette semaine
```

### Flux global simplifie

```
1. CAPACITE (automatique)
   Les compagnons et chefs de chantier actifs sont comptes
   Capacite = nombre x 35h/semaine
       |
       v
2. PLANIFIE (automatique - module Planning Operationnel)
   Les affectations actives sont converties en heures
   7h/jour x nombre de jours dans la semaine
       |
       v
3. BESOINS (saisie manuelle)
   Le conducteur estime les besoins par chantier/semaine/metier
       |
       v
4. VISUALISATION
   Tableau croise : chantiers (lignes) x semaines (colonnes)
   Footer : taux d'occupation, alertes, a recruter, a placer
```

### Fonctionnalites couvertes (CDC Section 6)

| ID | Fonctionnalite | Description |
|----|----------------|-------------|
| PDC-01 | Vue tabulaire | Chantiers en lignes, semaines en colonnes |
| PDC-02 | Compteur chantiers | Nombre total de chantiers affiches |
| PDC-03 | Barre de recherche | Filtrer par nom/code chantier |
| PDC-04 | Toggle mode avance | Affichage detaille (besoin + planifie) |
| PDC-05 | Toggle Hrs / J/H | Basculer entre heures et jours/homme |
| PDC-06 | Navigation temporelle | Defilement semaine par semaine |
| PDC-07 | Colonnes semaines | Format SXX-YYYY (ISO 8601) |
| PDC-08 | Colonne Charge | Budget total heures par chantier |
| PDC-09 | Double colonne | Planifie (bleu) + Besoin (violet) par semaine |
| PDC-10 | Cellules besoin | Fond violet pour les cellules avec besoin |
| PDC-11 | Footer repliable | Ligne de synthese avec taux d'occupation |
| PDC-12 | Taux occupation + couleur | Code couleur selon seuils |
| PDC-13 | Alerte surcharge | Icone si >= 100% |
| PDC-14 | A recruter | Nombre de personnes a recruter |
| PDC-15 | A placer | Nombre de personnes non planifiees |
| PDC-16 | Modal besoins | Formulaire de saisie des besoins |
| PDC-17 | Modal details | Details d'occupation par type de metier |

### Perimetre de la capacite

La capacite est calculee sur les **profils terrain** uniquement :
- Compagnons
- Chefs de chantier

Les conducteurs de travaux et administrateurs ne sont **pas** comptes dans la capacite terrain. Le filtrage par metier est possible pour affiner l'analyse.

---

## 2. ENTITES ET OBJETS METIER

### 2.1 Entite BesoinCharge

**Fichier** : `backend/modules/planning/domain/entities/besoin_charge.py`

Un BesoinCharge represente le nombre d'heures estimees necessaires pour un chantier donne, une semaine donnee, et un type de metier donne.

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `chantier_id` | int | Oui | FK vers chantier |
| `semaine` | Semaine | Oui | Semaine concernee (annee + numero) |
| `type_metier` | TypeMetier | Oui | Type de metier concerne |
| `besoin_heures` | float | Oui | Nombre d'heures estimees (>= 0) |
| `note` | str | Non | Note explicative |
| `created_by` | int | Non | Utilisateur createur |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |

**Proprietes calculees** :

| Propriete | Type | Calcul |
|-----------|------|--------|
| `besoin_jours_homme` | float | `besoin_heures / 7.0` |
| `has_note` | bool | `note is not None and note != ""` |
| `code_unique` | str | `"{chantier_id}-{semaine.code}-{type_metier}"` |

**Methodes** :
- `modifier_besoin(nouvelles_heures, note?)` : Met a jour les heures et/ou la note
- `ajouter_note(note)` / `supprimer_note()` : Gestion de la note
- `changer_type_metier(nouveau_type)` : Change le type de metier
- `est_pour_semaine(semaine)` : Verifie si le besoin concerne la semaine
- `est_pour_chantier(chantier_id)` : Verifie si le besoin concerne le chantier

**Contrainte d'unicite** : Un seul besoin par combinaison `(chantier_id, semaine, type_metier)`.

### 2.2 Value Objects

#### Semaine

**Fichier** : `backend/modules/planning/domain/value_objects/charge/semaine.py`

| Propriete | Type | Description |
|-----------|------|-------------|
| `annee` | int | Annee (2020-2100) |
| `numero` | int | Numero de semaine ISO 8601 (1-53) |
| `code` | str | Format "SXX-YYYY" (ex: "S05-2026") |
| `lundi` | date | Premier jour de la semaine |
| `dimanche` | date | Dernier jour de la semaine |

**Methodes** :
- `from_date(date)` : Cree depuis une date
- `from_code("S05-2026")` : Parse depuis le code
- `current()` : Semaine courante
- `date_range(debut, fin)` : Genere les semaines entre debut et fin
- `next()` / `previous()` : Semaine suivante/precedente
- Supports comparaison : `<`, `<=`, `>`, `>=`

#### TypeMetier

**Fichier** : `backend/modules/planning/domain/value_objects/charge/type_metier.py`

| Valeur | Label | Couleur |
|--------|-------|---------|
| `EMPLOYE` | "Employe" | #2C3E50 (bleu fonce) |
| `SOUS_TRAITANT` | "Sous-traitant" | #E74C3C (rouge/corail) |
| `CHARPENTIER` | "Charpentier" | #27AE60 (vert) |
| `COUVREUR` | "Couvreur" | #E67E22 (orange) |
| `ELECTRICIEN` | "Electricien" | #EC407A (magenta/rose) |
| `MACON` | "Macon" | #795548 (marron) |
| `COFFREUR` | "Coffreur" | #F1C40F (jaune) |
| `FERRAILLEUR` | "Ferrailleur" | #607D8B (gris fonce) |
| `GRUTIER` | "Grutier" | #1ABC9C (cyan) |

#### TauxOccupation

**Fichier** : `backend/modules/planning/domain/value_objects/charge/taux_occupation.py`

Voir section 3 pour les details.

#### UniteCharge

**Fichier** : `backend/modules/planning/domain/value_objects/charge/unite_charge.py`

| Valeur | Label court | Conversion |
|--------|-------------|------------|
| `HEURES` | "Hrs" | Valeur brute |
| `JOURS_HOMME` | "J/H" | `heures / 7.0` |

Methodes : `convertir(heures, unite)`, `formater(valeur, unite)`

---

## 3. TAUX D'OCCUPATION ET SEUILS

### 3.1 Niveaux d'occupation

**Enum** : `NiveauOccupation`

| Niveau | Seuil | Couleur | Label | Alerte |
|--------|-------|---------|-------|--------|
| `SOUS_CHARGE` | < 70% | #27AE60 (vert) | "Sous-charge" | Non |
| `NORMAL` | 70% - 90% | #3498DB (bleu clair) | "Normal" | Non |
| `HAUTE` | 90% - 100% | #F39C12 (jaune/orange) | "Haute" | Non |
| `SURCHARGE` | = 100% | #E74C3C (rouge) | "Surcharge" | **Oui** |
| `CRITIQUE` | > 100% | #C0392B (rouge fonce) | "Critique" | **Oui** |

### 3.2 Representation visuelle

```
0%        70%       90%      100%        150%        200%
|---------|---------|--------|-----------|-----------|
 SOUS-     NORMAL    HAUTE    SURCHARGE   CRITIQUE
 CHARGE
 (vert)   (bleu)    (orange)  (rouge)    (rouge fonce)
```

### 3.3 Constantes de seuils

```python
class TauxOccupation:
    SEUIL_NORMAL = 70.0
    SEUIL_HAUTE = 90.0
    SEUIL_SURCHARGE = 100.0

    @classmethod
    def calculer(cls, planifie: float, capacite: float) -> 'TauxOccupation':
        if capacite <= 0:
            return cls(valeur=0.0)
        return cls(valeur=(planifie / capacite) * 100)
```

### 3.4 Signification metier

| Situation | Interpretation | Action recommandee |
|-----------|---------------|-------------------|
| **Sous-charge** (< 70%) | Equipes sous-utilisees | Chercher de nouveaux chantiers ou redeploy |
| **Normal** (70-90%) | Fonctionnement optimal | Maintenir |
| **Haute** (90-100%) | Charge elevee mais tenable | Surveiller, anticiper |
| **Surcharge** (100%) | Plus de capacite disponible | Recruter ou sous-traiter |
| **Critique** (> 100%) | Depassement de capacite | Action urgente : recrutement/report |

---

## 4. TYPES DE METIERS

### 4.1 Utilisation dans le planning de charge

Les types de metiers permettent de ventiler les besoins et la capacite par specialite. Cela aide a identifier les metiers en tension.

### 4.2 Mapping utilisateur --> type metier

Le `SQLAlchemyUtilisateurProvider` mappe le champ `metier` de l'utilisateur vers l'enum `TypeMetier` :

```python
def _map_metier_to_type(self, metier: str) -> TypeMetier:
    """Mappe la profession de l'utilisateur vers le type de metier."""
    # Mapping direct si le metier correspond a un TypeMetier
    # Sinon fallback vers EMPLOYE
```

### 4.3 Capacite par metier

La capacite par metier est calculee automatiquement :

```
Capacite(MACON) = Nombre de macons actifs x 35h/semaine
Capacite(COFFREUR) = Nombre de coffreurs actifs x 35h/semaine
...
```

Cela permet de savoir, par exemple, qu'il manque 2 macons la semaine S06 parce que les besoins en maconnerie depassent la capacite disponible.

---

## 5. FLUX DE PLANIFICATION DES BESOINS

### 5.1 Saisie manuelle des besoins (PDC-16)

Le conducteur de travaux estime les besoins futurs par chantier, semaine et type de metier.

```
Conducteur ouvre le Planning de Charge
    |
    v
Clique sur une cellule "Besoin" d'un chantier/semaine
    |
    v
Modal de saisie :
    - Chantier : Villa Duplex (pre-rempli)
    - Semaine : S06-2026 (pre-rempli)
    - Type metier : [MACON]
    - Besoin heures : [70] h
    - Note : "Coulage fondations + murs RDC"
    |
    v
POST /api/planning-charge/besoins
    |
    v
Besoin cree --> Tableau mis a jour
```

### 5.2 Donnees du formulaire

```python
class CreateBesoinRequest:
    chantier_id: int       # Chantier concerne
    semaine_code: str      # Format "SXX-YYYY"
    type_metier: str       # Valeur de TypeMetier
    besoin_heures: float   # Heures estimees (>= 0)
    note: Optional[str]    # Note explicative
```

### 5.3 Diagramme de sequence

```
Conducteur         Frontend            Backend             BDD
    |                   |                  |                 |
    | Clique cellule    |                  |                 |
    |------------------>|                  |                 |
    |                   | Modal saisie     |                 |
    |                   |                  |                 |
    | Saisit besoin     |                  |                 |
    |------------------>|                  |                 |
    |                   | POST /besoins    |                 |
    |                   |----------------->|                 |
    |                   |                  | Verifie unicite |
    |                   |                  | (chantier +     |
    |                   |                  |  semaine +      |
    |                   |                  |  type_metier)   |
    |                   |                  |                 |
    |                   |                  | Si existe :     |
    |                   |                  | 409 Conflict    |
    |                   |                  |                 |
    |                   |                  | Sinon :         |
    |                   |                  |---------------->|
    |                   |                  | INSERT          |
    |                   |                  |<----------------|
    |                   |                  |                 |
    |                   |                  | Publie event    |
    |                   |                  | BesoinCreated   |
    |                   |                  |                 |
    |                   |                  | Invalide cache  |
    |                   |<-----------------|                 |
    |<------------------|                  |                 |
    | Tableau mis a jour|                  |                 |
```

### 5.4 Modification et suppression

- **Modification** : `PUT /api/planning-charge/besoins/{id}` (conducteur/admin)
- **Suppression** : `DELETE /api/planning-charge/besoins/{id}` (soft delete, conducteur/admin)
- Chaque operation invalide le cache du planning et publie un evenement domaine
- Un **audit trail** est enregistre (utilisateur + action)

---

## 6. VUE TABULAIRE DU PLANNING

### 6.1 Structure du tableau (PDC-01, PDC-07, PDC-09)

```
+------------------+--------+------------------+------------------+------------------+
| Chantier         | Charge | S05-2026         | S06-2026         | S07-2026         |
|                  | (h)    | Planif. | Besoin | Planif. | Besoin | Planif. | Besoin |
+------------------+--------+---------+--------+---------+--------+---------+--------+
| Villa Duplex     |   420  |   105   |   70   |   140   |  140   |   105   |   70   |
| Residence Pins   |   280  |    70   |   35   |   105   |  105   |    70   |   35   |
| Immeuble Centre  |   560  |   210   |  175   |   175   |  175   |   140   |  105   |
+------------------+--------+---------+--------+---------+--------+---------+--------+
| FOOTER           |        |  385/   | 280    |  420/   | 420    |  315/   | 210    |
| Taux occupation  |        |   490   |        |  490    |        |  490    |        |
| (capacite)       |        |  78.6%  |        |  85.7%  |        |  64.3%  |        |
|                  |        | NORMAL  |        | NORMAL  |        | SOUS-CH |        |
| A recruter       |        |    0    |        |    0    |        |    0    |        |
| A placer         |        |    3    |        |    2    |        |    5    |        |
+------------------+--------+---------+--------+---------+--------+---------+--------+
```

### 6.2 Elements du tableau

| Element | Description | Feature |
|---------|-------------|---------|
| **Ligne chantier** | Un chantier actif par ligne | PDC-01 |
| **Colonne Charge** | Budget total heures du chantier | PDC-08 |
| **Colonne Planifie** (bleu) | Heures reellement affectees (auto) | PDC-09 |
| **Colonne Besoin** (violet) | Heures estimees necessaires (manuel) | PDC-09, PDC-10 |
| **Compteur chantiers** | "3 chantiers" en haut | PDC-02 |
| **Barre recherche** | Filtre par nom/code | PDC-03 |

### 6.3 Mode avance (PDC-04)

Le toggle "Mode avance" affiche des informations supplementaires :
- Heures non couvertes par chantier
- Pourcentage de couverture
- Details par type de metier

### 6.4 Toggle unite (PDC-05)

| Unite | Affichage | Conversion |
|-------|-----------|------------|
| **Heures** (Hrs) | 105h, 70h | Valeur brute |
| **Jours/Homme** (J/H) | 15 J/H, 10 J/H | heures / 7 |

### 6.5 Navigation temporelle (PDC-06)

```
[< Semaine prec.] [S05-2026 ... S07-2026] [Semaine suiv. >]
```

Les parametres `semaine_debut` et `semaine_fin` controlent la plage affichee.

---

## 7. FOOTER D'OCCUPATION

### 7.1 Structure (PDC-11)

Le footer est une ligne repliable en bas du tableau qui synthetise la charge par semaine.

```typescript
interface FooterChargeDTO {
  semaine_code: string       // "S05-2026"
  taux_occupation: float     // 78.6
  taux_couleur: string       // "#3498DB" (bleu = normal)
  taux_label: string         // "Normal"
  alerte_surcharge: boolean  // false
  a_recruter: number         // 0
  a_placer: number           // 3
}
```

### 7.2 Donnees affichees par semaine

| Donnee | Calcul | Exemple |
|--------|--------|---------|
| **Taux d'occupation** | `(planifie / capacite) * 100` | "78.6%" |
| **Code couleur** | Selon seuils (vert/bleu/orange/rouge) | Bleu = normal |
| **Alerte** (PDC-13) | Si taux >= 100% | Icone avertissement |
| **A recruter** (PDC-14) | `ceil(max(besoin - capacite, 0) / 35)` | "0 pers." |
| **A placer** (PDC-15) | Compagnons non planifies cette semaine | "3 pers." |

---

## 8. DETAILS D'OCCUPATION PAR SEMAINE

### 8.1 Modal details (PDC-17)

Un clic sur une cellule du footer ouvre un modal detaillant l'occupation par type de metier pour la semaine selectionnee.

```
GET /api/planning-charge/occupation/S05-2026
```

### 8.2 Donnees retournees

```typescript
interface OccupationDetailsDTO {
  semaine_code: string          // "S05-2026"
  semaine_label: string         // "Semaine 5 - 2026"
  taux_global: float            // 78.6
  taux_global_couleur: string   // "#3498DB"
  alerte_globale: boolean       // false
  types: TypeOccupationDTO[]    // Detail par metier
  planifie_total: float         // 385
  besoin_total: float           // 280
  capacite_totale: float        // 490
  a_recruter: number            // 0
  a_placer: number              // 3
}

interface TypeOccupationDTO {
  type_metier: string           // "macon"
  type_metier_label: string     // "Macon"
  type_metier_couleur: string   // "#795548"
  planifie_heures: float        // 140
  besoin_heures: float          // 105
  capacite_heures: float        // 175
  taux_occupation: float        // 80.0
  taux_couleur: string          // "#3498DB"
  alerte: boolean               // false
}
```

### 8.3 Exemple d'affichage

```
Modal : Details occupation S05-2026
-----------------------------------
Taux global : 78.6% (NORMAL)
Planifie : 385h | Besoin : 280h | Capacite : 490h

Par metier :
+------------------+---------+--------+----------+--------+-------+
| Metier           | Planif. | Besoin | Capacite | Taux   | Alerte|
+------------------+---------+--------+----------+--------+-------+
| Macon            |   140h  |  105h  |   175h   | 80.0%  |       |
| Coffreur         |   105h  |   70h  |   105h   | 100.0% |  !!   |
| Ferrailleur      |    70h  |   35h  |    70h   | 100.0% |  !!   |
| Charpentier      |    35h  |   35h  |    70h   | 50.0%  |       |
| Electricien      |    35h  |   35h  |    70h   | 50.0%  |       |
+------------------+---------+--------+----------+--------+-------+
A recruter : 0 | A placer : 3
```

---

## 9. CALCULS ET FORMULES

### 9.1 Constantes

| Constante | Valeur | Source |
|-----------|--------|--------|
| `HEURES_PAR_SEMAINE` | 35.0 | Duree legale francaise |
| `HEURES_PAR_JOUR` | 7.0 | 35h / 5 jours |

### 9.2 Capacite

```
capacite_semaine = nombre_utilisateurs_actifs_terrain x HEURES_PAR_SEMAINE

# Par metier :
capacite_macon = nombre_macons_actifs x HEURES_PAR_SEMAINE
```

**Population comptee** : Uniquement les profils terrain (compagnons + chefs de chantier). Les conducteurs et admins ne sont pas inclus.

### 9.3 Planifie

```
planifie_chantier_semaine = Somme(affectations actives du chantier cette semaine)
                          = nombre_jours_affectes x HEURES_PAR_JOUR

# Exemple : 3 compagnons affectes 5 jours = 3 x 5 x 7 = 105h
```

Le planifie est **automatique** : il provient des affectations du module Planning Operationnel.

### 9.4 Besoin

```
besoin_chantier_semaine = Somme(besoins saisis pour ce chantier cette semaine)
                        = besoin_macon + besoin_coffreur + besoin_electricien + ...
```

Le besoin est **manuel** : saisi par le conducteur de travaux.

### 9.5 Taux d'occupation

```
taux_occupation = (planifie / capacite) x 100

# Si capacite = 0 : taux = 0%
```

### 9.6 A recruter (PDC-14)

```
deficit = max(besoin - capacite, 0)
a_recruter = ceil(deficit / HEURES_PAR_SEMAINE)

# Exemple : besoin = 560h, capacite = 490h
# deficit = 70h
# a_recruter = ceil(70 / 35) = 2 personnes
```

### 9.7 A placer (PDC-15)

```
a_placer = nombre_utilisateurs_actifs - nombre_utilisateurs_planifies_semaine

# Exemple : 14 actifs, 11 planifies = 3 a placer
```

### 9.8 Conversion Heures <-> Jours/Homme

```
jours_homme = heures / HEURES_PAR_JOUR

# 105h = 15 J/H
# 35h = 5 J/H
```

---

## 10. PERMISSIONS ET ROLES

### 10.1 Matrice de permissions

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|-----------|---------------|-----------|
| Voir planning charge | Oui | Oui | Oui | Non |
| Voir details occupation | Oui | Oui | Oui | Non |
| Creer besoin | Oui | Oui | Non | Non |
| Modifier besoin | Oui | Oui | Non | Non |
| Supprimer besoin | Oui | Oui | Non | Non |

### 10.2 Justification

- **Compagnons exclus** : Le planning de charge est un outil de pilotage strategique, pas un outil terrain
- **Chefs en lecture** : Ils voient la charge globale mais ne saisissent pas les besoins
- **Conducteurs** : Ils estiment les besoins de leurs chantiers
- **Admins** : Acces complet pour pilotage global

---

## 11. EVENEMENTS DOMAINE

### 11.1 Liste des evenements

**Fichier** : `backend/modules/planning/domain/events/charge/besoin_events.py`

| Evenement | Donnees | Declencheur |
|-----------|---------|-------------|
| `BesoinChargeCreated` | besoin_id, chantier_id, semaine_code, type_metier, besoin_heures, created_by | Creation besoin |
| `BesoinChargeUpdated` | besoin_id, chantier_id, semaine_code, type_metier, ancien_besoin_heures, nouveau_besoin_heures, updated_by | Modification besoin |
| `BesoinChargeDeleted` | besoin_id, chantier_id, semaine_code, type_metier, besoin_heures, deleted_by | Suppression besoin |

**Propriete calculee** sur `BesoinChargeUpdated` :
- `difference_heures` : `nouveau_besoin_heures - ancien_besoin_heures`

### 11.2 Invalidation du cache

Chaque operation d'ecriture (POST/PUT/DELETE) invalide le cache du planning de charge. Le prefixe de cache est `planning_charge`.

---

## 12. API REST - ENDPOINTS

### 12.1 Routes

**Router** : `/api/planning-charge`

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| GET | `/` | Chef+ | Planning de charge complet | PDC-01 |
| GET | `/occupation/{semaine_code}` | Chef+ | Details occupation par metier | PDC-17 |
| GET | `/chantiers/{id}/besoins` | Chef+ | Liste besoins par chantier | - |
| POST | `/besoins` | Conducteur+ | Creer un besoin | PDC-16 |
| PUT | `/besoins/{id}` | Conducteur+ | Modifier un besoin | - |
| DELETE | `/besoins/{id}` | Conducteur+ | Supprimer un besoin (soft) | - |

### 12.2 Parametres du GET principal

```
GET /api/planning-charge?semaine_debut=S05-2026&semaine_fin=S07-2026&recherche=villa&mode_avance=true&unite=heures
```

| Parametre | Type | Description |
|-----------|------|-------------|
| `semaine_debut` | str | Code semaine debut (SXX-YYYY) |
| `semaine_fin` | str | Code semaine fin (SXX-YYYY) |
| `recherche` | str | Recherche par nom/code chantier (PDC-03) |
| `mode_avance` | bool | Affichage avance (PDC-04) |
| `unite` | str | "heures" ou "jours_homme" (PDC-05) |

### 12.3 Reponse du GET principal

```typescript
interface PlanningChargeResponse {
  total_chantiers: number           // PDC-02
  semaine_debut: string             // "S05-2026"
  semaine_fin: string               // "S07-2026"
  unite: string                     // "heures" ou "jours_homme"
  semaines: SemaineChargeResponse[] // Liste des semaines
  chantiers: ChantierChargeResponse[] // Lignes du tableau
  footer: FooterChargeResponse[]    // Footer par semaine
  capacite_totale: number           // Capacite globale
  planifie_total: number            // Planifie global
  besoin_total: number              // Besoin global
}
```

### 12.4 Schemas de creation/modification

**CreateBesoinRequest** :
```python
{
    "chantier_id": int,
    "semaine_code": str,     # Pattern SXX-YYYY
    "type_metier": str,      # Valeur TypeMetier
    "besoin_heures": float,  # >= 0
    "note": Optional[str]
}
```

**UpdateBesoinRequest** :
```python
{
    "besoin_heures": Optional[float],  # >= 0
    "note": Optional[str],
    "type_metier": Optional[str]
}
```

### 12.5 Pagination des besoins

```
GET /api/planning-charge/chantiers/{id}/besoins?semaine_debut=S05-2026&semaine_fin=S10-2026&page=1&page_size=50
```

```typescript
interface ListeBesoinResponse {
  items: BesoinChargeResponse[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
```

---

## 13. ARCHITECTURE TECHNIQUE

### 13.1 Structure des fichiers

```
backend/modules/planning/
|
+-- domain/
|   +-- entities/
|   |   +-- besoin_charge.py          # Entite besoin
|   +-- value_objects/
|   |   +-- charge/
|   |       +-- semaine.py            # Semaine ISO 8601
|   |       +-- type_metier.py        # 9 types de metiers
|   |       +-- taux_occupation.py    # Seuils + calcul
|   |       +-- unite_charge.py       # Heures / J-H
|   +-- repositories/
|   |   +-- besoin_charge_repository.py  # Interface abstraite
|   +-- events/
|       +-- charge/
|           +-- besoin_events.py      # 3 evenements domaine
|
+-- application/
|   +-- use_cases/
|   |   +-- charge/
|   |       +-- create_besoin.py      # Creation besoin
|   |       +-- update_besoin.py      # Modification besoin
|   |       +-- delete_besoin.py      # Suppression besoin (soft)
|   |       +-- get_planning_charge.py # Vue tabulaire complete
|   |       +-- get_occupation_details.py # Details par metier
|   |       +-- get_besoins_by_chantier.py # Liste besoins
|   |       +-- exceptions.py         # Exceptions metier
|   +-- dtos/
|       +-- charge/
|           +-- planning_charge_dto.py # DTOs vue tabulaire
|           +-- besoin_charge_dto.py   # DTOs besoins
|           +-- occupation_dto.py      # DTOs occupation
|
+-- adapters/
|   +-- controllers/
|       +-- charge/
|           +-- planning_charge_controller.py  # Orchestrateur
|           +-- planning_charge_schemas.py      # Pydantic schemas
|
+-- infrastructure/
    +-- persistence/
    |   +-- besoin_charge_model.py     # SQLAlchemy model
    |   +-- sqlalchemy_besoin_charge_repository.py
    +-- providers/
    |   +-- chantier_provider.py       # Cross-module : chantiers
    |   +-- affectation_provider.py    # Cross-module : affectations
    |   +-- utilisateur_provider.py    # Cross-module : utilisateurs
    +-- web/
        +-- charge_routes.py           # FastAPI router
```

### 13.2 Cross-module providers

Le Planning de Charge consomme des donnees de 3 modules externes via des **providers** (interfaces) :

| Provider | Source module | Donnees fournies |
|----------|-------------|-----------------|
| `ChantierProvider` | Chantiers | Chantiers actifs, recherche par nom/code |
| `AffectationProvider` | Planning Operationnel | Heures planifiees par chantier/semaine, capacite, non planifies |
| `UtilisateurProvider` | Users | Capacite par metier, nombre par metier |

Ces providers respectent le principe de Clean Architecture : le module Planning de Charge ne depend pas directement des modules externes, mais de leurs interfaces.

### 13.3 Table base de donnees

**Table `besoins_charge`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| chantier_id | INTEGER | FK chantiers, CASCADE |
| semaine_annee | INTEGER | NOT NULL |
| semaine_numero | INTEGER | NOT NULL |
| type_metier | VARCHAR(50) | NOT NULL |
| besoin_heures | FLOAT | default 0.0 |
| note | TEXT | nullable |
| created_by | INTEGER | FK users, SET NULL |
| is_deleted | BOOLEAN | default false |
| deleted_at | DATETIME | nullable |
| deleted_by | INTEGER | FK users, SET NULL |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes :
- `(chantier_id, semaine_annee, semaine_numero)` -- Recherche par chantier/semaine
- `(semaine_annee, semaine_numero)` -- Recherche par semaine
- `UNIQUE (chantier_id, semaine_annee, semaine_numero, type_metier)` -- Unicite
- `(is_deleted)` -- Filtrage soft delete

### 13.4 Frontend

> **Note** : Le frontend du Planning de Charge n'est **pas encore implemente**. Le backend expose les APIs necessaires, mais les composants React ne sont pas encore crees. Le module Planning Operationnel (page PlanningPage.tsx) existe mais concerne les affectations, pas la charge.

---

## 14. SCENARIOS DE TEST

### Scenario 1 : Saisie de besoin

```
GIVEN le conducteur "Nicolas DELSALLE" connecte
AND le chantier "Villa Duplex" (id=1) actif
WHEN il cree un besoin :
    chantier_id = 1
    semaine_code = "S06-2026"
    type_metier = "macon"
    besoin_heures = 70
    note = "Coulage fondations"
THEN le besoin est cree avec id auto
AND un BesoinChargeCreated event est publie
AND le cache planning_charge est invalide
```

### Scenario 2 : Unicite des besoins

```
GIVEN un besoin existant (chantier=1, semaine=S06-2026, type=macon)
WHEN on tente de creer un autre besoin avec les memes cles
THEN HTTP 409 Conflict (BesoinAlreadyExistsError)
```

### Scenario 3 : Calcul du taux d'occupation

```
GIVEN 14 compagnons actifs (capacite = 14 x 35 = 490h)
AND 385h planifiees pour la semaine S05-2026
WHEN on consulte le planning de charge
THEN taux_occupation = (385 / 490) x 100 = 78.57%
AND niveau = NORMAL
AND couleur = #3498DB (bleu)
AND alerte = false
```

### Scenario 4 : Surcharge detectee

```
GIVEN 14 compagnons actifs (capacite = 490h)
AND 525h planifiees pour la semaine S06-2026
WHEN on consulte le planning de charge
THEN taux_occupation = (525 / 490) x 100 = 107.14%
AND niveau = CRITIQUE
AND couleur = #C0392B (rouge fonce)
AND alerte = true
```

### Scenario 5 : Calcul "a recruter"

```
GIVEN capacite = 490h (14 personnes)
AND besoin total = 560h pour la semaine S06-2026
WHEN on calcule "a recruter"
THEN deficit = 560 - 490 = 70h
AND a_recruter = ceil(70 / 35) = 2 personnes
```

### Scenario 6 : Calcul "a placer"

```
GIVEN 14 compagnons actifs
AND 11 planifies pour la semaine S05-2026
WHEN on calcule "a placer"
THEN a_placer = 14 - 11 = 3 personnes
```

### Scenario 7 : Details par metier

```
GIVEN la semaine S05-2026 avec :
    - 5 macons actifs (capacite 175h), 140h planifiees
    - 3 coffreurs actifs (capacite 105h), 105h planifiees
    - 2 ferrailleurs actifs (capacite 70h), 70h planifiees
WHEN on consulte GET /occupation/S05-2026
THEN on obtient :
    macon : taux = 80.0% (NORMAL)
    coffreur : taux = 100.0% (SURCHARGE, alerte)
    ferrailleur : taux = 100.0% (SURCHARGE, alerte)
```

### Scenario 8 : Conversion Heures <-> J/H

```
GIVEN une valeur de 105 heures
WHEN on demande la conversion en J/H
THEN resultat = 105 / 7 = 15.0 J/H
```

### Scenario 9 : Soft delete d'un besoin

```
GIVEN un besoin existant (id=42)
WHEN le conducteur supprime le besoin
THEN is_deleted = true
AND deleted_at = now
AND deleted_by = conducteur_id
AND le besoin n'apparait plus dans les listes
AND un BesoinChargeDeleted event est publie
```

---

## 15. EVOLUTIONS FUTURES

| Evolution | Description | Impact |
|-----------|-------------|--------|
| **Frontend Planning Charge** | Composants React pour la vue tabulaire | Page dediee + composants |
| **Previsionnel automatique** | Estimation des besoins basee sur l'historique | IA / ML |
| **Export Excel** | Export du tableau en XLSX | Integration librairie export |
| **Alertes email** | Notification en cas de surcharge detectee | Integration SMTP |
| **Objectifs de charge** | Seuils personnalisables par entreprise | Configuration admin |
| **Vue par metier** | Tableau croise metiers x semaines | Nouveau endpoint |
| **Scenario planning** | Simuler des ajouts/retraits de personnel | Mode simulation |
| **Integration RH** | Import automatique des embauches/departs | Cross-module |
| **Budget heures chantier** | Suivi budget vs consomme | Nouveau champ sur chantier |

---

## 16. REFERENCES CDC

| Section CDC | Description | Fonctionnalites |
|-------------|-------------|-----------------|
| Section 6 | Planning de Charge | PDC-01 a PDC-17 |
| Section 5 | Planning Operationnel | Source des affectations |
| Section 3 | Gestion utilisateurs | Source de la capacite |
| Section 4 | Gestion chantiers | Source des chantiers |

### Fichiers sources principaux

| Fichier | Role |
|---------|------|
| `backend/modules/planning/domain/entities/besoin_charge.py` | Entite besoin |
| `backend/modules/planning/domain/value_objects/charge/semaine.py` | Semaine ISO |
| `backend/modules/planning/domain/value_objects/charge/type_metier.py` | 9 types metiers |
| `backend/modules/planning/domain/value_objects/charge/taux_occupation.py` | Seuils occupation |
| `backend/modules/planning/domain/value_objects/charge/unite_charge.py` | Conversion unites |
| `backend/modules/planning/application/use_cases/charge/get_planning_charge.py` | Vue tabulaire |
| `backend/modules/planning/application/use_cases/charge/get_occupation_details.py` | Details metier |
| `backend/modules/planning/infrastructure/web/charge_routes.py` | 6 endpoints |
| `backend/modules/planning/infrastructure/providers/` | 3 cross-module providers |
| `backend/modules/planning/infrastructure/persistence/besoin_charge_model.py` | Table SQL |

### Tests

| Fichier | Description |
|---------|-------------|
| `backend/tests/unit/planning/charge/test_besoin_charge.py` | Tests entite |
| `backend/tests/unit/planning/charge/test_semaine.py` | Tests semaine |
| `backend/tests/unit/planning/charge/test_taux_occupation.py` | Tests seuils |
| `backend/tests/unit/planning/charge/test_type_metier.py` | Tests metiers |
| `backend/tests/unit/planning/charge/test_unite_charge.py` | Tests conversion |
| `backend/tests/unit/planning/charge/test_create_besoin.py` | Tests creation |
| `backend/tests/unit/planning/charge/test_update_besoin.py` | Tests modification |
| `backend/tests/unit/planning/charge/test_delete_besoin.py` | Tests suppression |
| `backend/tests/unit/planning/charge/test_get_planning_charge.py` | Tests vue |
| `backend/tests/unit/planning/charge/test_get_occupation_details.py` | Tests details |
| `backend/tests/integration/test_planning_charge_api.py` | Tests API |

### Migration

| Fichier | Description |
|---------|-------------|
| `backend/migrations/versions/20260124_0002_create_besoins_charge.py` | Creation table + indexes |

---

**Document genere automatiquement par analyse du code source.**
**Dernier audit : 30 janvier 2026**

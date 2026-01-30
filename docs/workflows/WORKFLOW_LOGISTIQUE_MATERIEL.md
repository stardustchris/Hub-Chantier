# Workflow Logistique Materiel - Hub Chantier

> Document cree le 30 janvier 2026
> Analyse complete du workflow de gestion logistique et reservation de materiel

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entites et objets metier](#2-entites-et-objets-metier)
3. [Machine a etats - Reservations](#3-machine-a-etats---reservations)
4. [Catalogue de ressources](#4-catalogue-de-ressources)
5. [Flux de reservation](#5-flux-de-reservation)
6. [Validation N+1](#6-validation-n1)
7. [Detection de conflits](#7-detection-de-conflits)
8. [Planning et calendrier](#8-planning-et-calendrier)
9. [Notifications et rappels](#9-notifications-et-rappels)
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

Le module Logistique permet de gerer le parc de ressources materielles (engins, vehicules, equipements) et leur reservation par les equipes terrain. Chaque reservation passe par un workflow de validation configurable par categorie de ressource.

### Flux global simplifie

```
Admin cree les ressources dans le catalogue
    |
    v
Chef/Compagnon demande une reservation
    |
    v
[EN_ATTENTE] --> Detection automatique de conflits
    |
    +-- Si validation_requise = false --> [VALIDEE] automatiquement
    |
    +-- Si validation_requise = true --> Conducteur/Admin valide
    |       |
    |       +-- [VALIDEE] (acceptee)
    |       +-- [REFUSEE] (avec motif optionnel)
    |
    +-- Le demandeur peut annuler --> [ANNULEE]
```

### Deux entites principales

| Entite | Role | Gestion |
|--------|------|---------|
| **Ressource** | Fiche identite du materiel (grue, camion, etc.) | Admin uniquement |
| **Reservation** | Demande d'utilisation d'une ressource sur un creneau | Tous les roles |

### Fonctionnalites couvertes (CDC Section 9)

| ID | Fonctionnalite | Description |
|----|----------------|-------------|
| LOG-01 | Catalogue ressources | CRUD des ressources avec categories |
| LOG-02 | Categories | 5 categories avec validation par defaut |
| LOG-03 | Planning par ressource | Vue calendrier 7 jours |
| LOG-04 | Navigation semaine | Semaine precedente / suivante / aujourd'hui |
| LOG-05 | Plage horaire | Axe vertical 08:00 - 18:00 |
| LOG-06 | Creation par clic | Clic sur creneau = creation reservation |
| LOG-07 | Demande reservation | Formulaire de reservation |
| LOG-08 | Selection chantier | Chantier obligatoire pour la reservation |
| LOG-09 | Selection creneau | Date + heure debut + heure fin |
| LOG-10 | Config validation | Activation/desactivation N+1 par ressource |
| LOG-11 | File de validation | Liste des reservations en attente |
| LOG-13 | Notif demande | Notification a la creation |
| LOG-14 | Notif decision | Notification a la validation/refus |
| LOG-15 | Rappel J-1 | Rappel la veille de la reservation |
| LOG-16 | Motif refus | Explication en cas de refus |
| LOG-17 | Detection conflits | Chevauchement de creneaux |
| LOG-18 | Historique | Historique complet par ressource |

---

## 2. ENTITES ET OBJETS METIER

### 2.1 Entite Ressource

**Fichier** : `backend/modules/logistique/domain/entities/ressource.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `nom` | str | Oui | Nom de la ressource |
| `code` | str | Oui | Code unique (max 20 chars, pattern `^[A-Z0-9\-]+$`) |
| `categorie` | CategorieRessource | Oui | Categorie (enum) |
| `photo_url` | str | Non | Photo de la ressource |
| `couleur` | str | Non | Couleur hex (defaut "#3B82F6") |
| `plage_horaire_defaut` | PlageHoraire | Auto | Horaires par defaut (08:00-18:00) |
| `validation_requise` | bool | Non | N+1 requis (defaut: true) |
| `actif` | bool | Auto | Ressource active (defaut: true) |
| `description` | str | Non | Description libre (max 2000 chars) |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |
| `created_by` | int | Non | Utilisateur createur |
| `deleted_at` | datetime | Auto | Soft delete (nullable) |
| `deleted_by` | int | Auto | Utilisateur ayant supprime |

**Methodes cles** :
- `activer()` / `desactiver()` : Active ou desactive la ressource
- `activer_validation()` / `desactiver_validation()` : Toggle N+1 (LOG-10)
- `peut_etre_reservee()` : Verifie si active et non supprimee
- `supprimer(deleted_by)` : Soft delete
- `label_complet` : Retourne "[CODE] Nom"

### 2.2 Entite Reservation

**Fichier** : `backend/modules/logistique/domain/entities/reservation.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `ressource_id` | int | Oui | FK vers ressource |
| `chantier_id` | int | Oui | FK vers chantier (LOG-08) |
| `demandeur_id` | int | Oui | FK vers utilisateur |
| `date_reservation` | date | Oui | Date de reservation (LOG-09) |
| `heure_debut` | time | Oui | Heure debut (LOG-09) |
| `heure_fin` | time | Oui | Heure fin (LOG-09, > heure_debut) |
| `statut` | StatutReservation | Auto | Statut (defaut: EN_ATTENTE) |
| `motif_refus` | str | Conditionnel | Motif de refus (LOG-16) |
| `commentaire` | str | Non | Commentaire du demandeur |
| `valideur_id` | int | Auto | ID du valideur |
| `validated_at` | datetime | Auto | Date de validation |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |
| `deleted_at` | datetime | Auto | Soft delete |
| `deleted_by` | int | Auto | Utilisateur ayant supprime |

**Proprietes calculees** :

| Propriete | Type | Description |
|-----------|------|-------------|
| `plage_horaire` | PlageHoraire | Objet PlageHoraire construit |
| `est_en_attente` | bool | statut == EN_ATTENTE |
| `est_validee` | bool | statut == VALIDEE |
| `est_active` | bool | EN_ATTENTE ou VALIDEE, non supprimee |
| `est_passee` | bool | date_reservation < aujourd'hui |
| `est_demain` | bool | date_reservation == demain (LOG-15) |

**Methodes cles** :
- `valider(valideur_id)` : EN_ATTENTE --> VALIDEE (LOG-11)
- `refuser(valideur_id, motif?)` : EN_ATTENTE --> REFUSEE (LOG-16)
- `annuler()` : EN_ATTENTE ou VALIDEE --> ANNULEE
- `chevauche(autre)` : Detection de chevauchement horaire (LOG-17)

**Exceptions specifiques** :
- `ReservationConflitError` : Chevauchement de creneaux detecte
- `TransitionStatutInvalideError` : Transition de statut interdite

### 2.3 Value Objects

#### StatutReservation

**Fichier** : `backend/modules/logistique/domain/value_objects/statut_reservation.py`

| Valeur | Label | Emoji | Couleur | Actif | Final |
|--------|-------|-------|---------|-------|-------|
| `EN_ATTENTE` | "En attente" | -- | #FFC107 (jaune) | Oui | Non |
| `VALIDEE` | "Validee" | -- | #4CAF50 (vert) | Oui | Non |
| `REFUSEE` | "Refusee" | -- | #F44336 (rouge) | Non | Oui |
| `ANNULEE` | "Annulee" | -- | #9E9E9E (gris) | Non | Oui |

#### CategorieRessource

**Fichier** : `backend/modules/logistique/domain/value_objects/categorie_ressource.py`

| Valeur | Label | Exemples | Validation N+1 par defaut |
|--------|-------|----------|--------------------------|
| `ENGIN_LEVAGE` | Engin de levage | Grue mobile, Manitou, Nacelle | **Oui** |
| `ENGIN_TERRASSEMENT` | Engin terrassement | Mini-pelle, Pelleteuse, Dumper | **Oui** |
| `VEHICULE` | Vehicule | Camion benne, Fourgon, Utilitaire | **Non** |
| `GROS_OUTILLAGE` | Gros outillage | Betonniere, Vibrateur, Pompe a beton | **Non** |
| `EQUIPEMENT` | Equipement | Echafaudage, Etais, Banches | **Oui** |

> **Regle metier** : La validation N+1 est configurable individuellement par ressource (LOG-10).
> Le parametre `validation_requise` de la categorie sert uniquement de **valeur par defaut** lors de la creation d'une ressource.
> Un admin peut ensuite activer ou desactiver la validation pour chaque ressource independamment.

#### PlageHoraire

**Fichier** : `backend/modules/logistique/domain/value_objects/plage_horaire.py`

| Propriete | Type | Description |
|-----------|------|-------------|
| `heure_debut` | time | Debut (defaut 08:00) |
| `heure_fin` | time | Fin (defaut 18:00, doit etre > debut) |
| `duree_minutes` | int | Duree en minutes |
| `duree_heures` | float | Duree en heures |

Methodes : `chevauche(autre)`, `contient(heure)`, `from_strings("08:00", "18:00")`

---

## 3. MACHINE A ETATS - RESERVATIONS

### 3.1 Diagramme de transitions

```
                    +-------------+
                    |             |
                    | EN_ATTENTE  |
                    |   (jaune)   |
                    +------+------+
                           |
              +------------+------------+
              |            |            |
         valider()    refuser()    annuler()
              |            |            |
              v            v            v
        +-----------+ +-----------+ +-----------+
        |           | |           | |           |
        |  VALIDEE  | |  REFUSEE  | |  ANNULEE  |
        |  (vert)   | |  (rouge)  | |  (gris)   |
        +-----------+ +-----------+ +-----------+
              |            (final)      (final)
              |
         annuler()
              |
              v
        +-----------+
        |           |
        |  ANNULEE  |
        |  (gris)   |
        +-----------+
```

### 3.2 Regles de transition

| Depuis | Vers | Action | Qui |
|--------|------|--------|-----|
| EN_ATTENTE | VALIDEE | `valider(valideur_id)` | Conducteur / Admin |
| EN_ATTENTE | REFUSEE | `refuser(valideur_id, motif?)` | Conducteur / Admin |
| EN_ATTENTE | ANNULEE | `annuler()` | Demandeur / Admin |
| VALIDEE | ANNULEE | `annuler()` | Demandeur / Admin |
| REFUSEE | - | Etat final, pas de transition | - |
| ANNULEE | - | Etat final, pas de transition | - |

### 3.3 Auto-validation

```python
# Dans CreateReservationUseCase :
if not ressource.validation_requise:
    reservation.valider(demandeur_id)  # Auto-validation immediate
    # Pas besoin de passage par la file de validation
```

**Explication** : Si la ressource n'exige pas de validation N+1 (ex: vehicules, gros outillage), la reservation est automatiquement validee a la creation. Le demandeur est a la fois le demandeur et le valideur.

---

## 4. CATALOGUE DE RESSOURCES

### 4.1 Gestion du catalogue (LOG-01, LOG-02)

Le catalogue est gere exclusivement par les administrateurs. Chaque ressource a :

- Un **code unique** alphanumerique (ex: "GRU-001", "CAM-003") utilise comme identifiant metier
- Une **categorie** qui determine la validation par defaut
- Une **couleur** affichee dans le calendrier pour differencier visuellement les reservations
- Une **plage horaire par defaut** (08:00-18:00 configurable)

### 4.2 Soft delete

La suppression d'une ressource est **logique** (soft delete). Le champ `deleted_at` est renseigne, et la ressource n'apparait plus dans les listes. Les reservations existantes sont conservees (FK RESTRICT sur reservations).

### 4.3 Exemples de ressources par categorie

```
ENGIN_LEVAGE        : [GRU-001] Grue mobile 40T    (validation: OUI)
ENGIN_TERRASSEMENT  : [PEL-001] Mini-pelle 3T      (validation: OUI)
VEHICULE            : [CAM-001] Camion benne 19T    (validation: NON)
GROS_OUTILLAGE      : [BET-001] Betonniere 350L     (validation: NON)
EQUIPEMENT          : [ECH-001] Echafaudage 20m     (validation: OUI)
```

---

## 5. FLUX DE RESERVATION

### 5.1 Diagramme de sequence

```
Demandeur          Frontend           Backend              BDD
    |                   |                  |                  |
    |  Ouvre planning   |                  |                  |
    |  ressource        |                  |                  |
    |------------------>|                  |                  |
    |                   | GET /ressources/ |                  |
    |                   | {id}/planning    |                  |
    |                   |----------------->|                  |
    |                   |<-----------------|                  |
    |                   | Calendrier 7j    |                  |
    |                   |                  |                  |
    |  Clique creneau   |                  |                  |
    |  libre (LOG-06)   |                  |                  |
    |------------------>|                  |                  |
    |                   | Modal creation   |                  |
    |                   |                  |                  |
    |  Remplit :        |                  |                  |
    |  - Chantier       |                  |                  |
    |  - Date           |                  |                  |
    |  - Heure debut    |                  |                  |
    |  - Heure fin      |                  |                  |
    |  - Commentaire    |                  |                  |
    |------------------>|                  |                  |
    |                   | POST /reservations                  |
    |                   |----------------->|                  |
    |                   |                  | Verifications :  |
    |                   |                  | 1. Ressource     |
    |                   |                  |    existe+active |
    |                   |                  | 2. Detection     |
    |                   |                  |    conflits      |
    |                   |                  | 3. heure_fin >   |
    |                   |                  |    heure_debut   |
    |                   |                  |                  |
    |                   |                  | Si validation    |
    |                   |                  | non requise :    |
    |                   |                  | auto-valider     |
    |                   |                  |                  |
    |                   |                  |----------------->|
    |                   |                  |  INSERT          |
    |                   |                  |<-----------------|
    |                   |                  |                  |
    |                   |                  | Publish event :  |
    |                   |                  | ReservationCreated|
    |                   |                  | + ConflitEvent   |
    |                   |                  | (si conflit)     |
    |                   |<-----------------|                  |
    |<------------------|                  |                  |
    |  Confirmation     |                  |                  |
```

### 5.2 Donnees du formulaire

```typescript
interface ReservationCreate {
  ressource_id: number     // ID de la ressource
  chantier_id: number      // Chantier pour lequel on reserve (LOG-08)
  date_reservation: string // Date ISO YYYY-MM-DD (LOG-09)
  heure_debut: string      // "HH:MM" (LOG-09)
  heure_fin: string        // "HH:MM" > heure_debut (LOG-09)
  commentaire?: string     // Optionnel (max 1000 chars)
}
```

### 5.3 Verifications a la creation

| Verification | Erreur HTTP | Message |
|--------------|-------------|---------|
| Ressource introuvable | 404 | "Ressource non trouvee" |
| Ressource inactive | 400 | "Ressource inactive" |
| heure_fin <= heure_debut | 400 | CHECK constraint |
| Conflit de creneau | 409 Conflict | "Conflit avec reservation existante" |

---

## 6. VALIDATION N+1

### 6.1 Principe

La validation N+1 signifie qu'un superieur hierarchique doit approuver la demande de reservation. Ce mecanisme est **configurable par ressource** (LOG-10).

```
                     Validation requise ?
                            |
                +-----------+-----------+
                |                       |
               OUI                     NON
                |                       |
     Reservation EN_ATTENTE     Reservation VALIDEE
                |                 (auto-validation)
     Conducteur/Admin decide
                |
        +-------+-------+
        |               |
    VALIDEE          REFUSEE
                   (motif optionnel)
```

### 6.2 Valeurs par defaut par categorie

| Categorie | Validation N+1 | Raison |
|-----------|---------------|--------|
| Engins de levage | **Oui** | Securite, CACES requis, cout eleve |
| Engins terrassement | **Oui** | Securite, CACES requis |
| Vehicules | **Non** | Usage courant, faible risque |
| Gros outillage | **Non** | Usage courant |
| Equipements | **Oui** | Montage/demontage, securite |

### 6.3 File de validation (LOG-11)

Les conducteurs et administrateurs accedent a une file des reservations en attente :

```
GET /api/logistique/reservations/en-attente?limit=100&offset=0
```

Cette file affiche toutes les reservations en statut `EN_ATTENTE` avec :
- Ressource demandee (nom, code, couleur)
- Demandeur (nom)
- Chantier
- Date et creneau horaire
- Commentaire
- Boutons : Valider / Refuser

### 6.4 Refus avec motif (LOG-16)

Le valideur peut refuser une reservation avec un motif optionnel :

```python
POST /reservations/{id}/refuser
Body: { "motif": "Grue deja reservee pour une operation critique" }
```

Le motif est stocke dans `motif_refus` et visible par le demandeur.

---

## 7. DETECTION DE CONFLITS

### 7.1 Principe (LOG-17)

Avant de creer une reservation, le systeme detecte les chevauchements de creneaux horaires sur la meme ressource et la meme date.

### 7.2 Algorithme de detection

```python
def chevauche(self, autre: Reservation) -> bool:
    """Deux reservations se chevauchent si :
    - Meme ressource
    - Meme date
    - Les plages horaires se superposent
    """
    if self.ressource_id != autre.ressource_id:
        return False
    if self.date_reservation != autre.date_reservation:
        return False
    # Chevauchement de plages horaires
    return self.heure_debut < autre.heure_fin and autre.heure_debut < self.heure_fin
```

### 7.3 Comportement en cas de conflit

| Situation | Comportement |
|-----------|-------------|
| Conflit avec reservation VALIDEE | **Erreur 409** - Reservation refusee |
| Conflit avec reservation EN_ATTENTE | **Evenement** `ReservationConflitEvent` publie |
| Conflit avec REFUSEE/ANNULEE | Ignore (statuts finaux) |

### 7.4 Index de performance

La table `reservations` dispose d'un index composite optimise pour la detection de conflits :

```sql
INDEX ix_reservations_conflit (ressource_id, statut, date_reservation)
-- + Partial unique index WHERE statut IN ('en_attente', 'validee')
```

### 7.5 Verification frontend

Le frontend dispose aussi d'une fonction utilitaire pour verifier les chevauchements cote client :

```typescript
function plagesHorairesSeChevauchent(
  debut1: string, fin1: string,
  debut2: string, fin2: string
): boolean
```

---

## 8. PLANNING ET CALENDRIER

### 8.1 Vue calendrier (LOG-03, LOG-04, LOG-05)

Le planning est une vue calendrier hebdomadaire par ressource :

```
        Lundi 26    Mardi 27    Mercredi 28  Jeudi 29   Vendredi 30
08:00   |           |           |            |           |
        | [CAM-001] |           |            |           |
09:00   | Chantier  |           | [CAM-001]  |           |
        | Villa     |           | Chantier   |           |
10:00   | Duplex    |           | Residence  |           |
        |           |           | LES PINS   |           |
11:00   |           |           |            |           |
        |           |           |            |           |
12:00   |           |           |            |           |
        |           |           |            |           |
...
18:00   |           |           |            |           |
```

### 8.2 Interactions

| Action | Resultat |
|--------|---------|
| Clic sur creneau **libre** | Ouvre le modal de creation pre-rempli (LOG-06) |
| Clic sur reservation **existante** | Ouvre le modal de detail/validation |
| Bouton "< Semaine precedente" | Navigation (LOG-04) |
| Bouton "Semaine suivante >" | Navigation (LOG-04) |
| Bouton "Aujourd'hui" | Retour a la semaine courante |

### 8.3 Endpoint planning

```
GET /api/logistique/ressources/{id}/planning?date_debut=2026-01-26&date_fin=2026-02-01
```

**Reponse** :

```typescript
interface PlanningRessource {
  ressource_id: number
  ressource_nom: string
  ressource_code: string
  ressource_couleur: string
  date_debut: string
  date_fin: string
  reservations: Reservation[]  // Uniquement EN_ATTENTE et VALIDEE
  jours: string[]              // Liste des 7 jours
}
```

### 8.4 Constantes d'affichage

| Constante | Valeur | Description |
|-----------|--------|-------------|
| Jours affiches | Lundi a Dimanche | 7 jours |
| Plage horaire | 08:00 a 18:00 | 10 heures |
| Navigation | Semaine par semaine | +/- 7 jours |

### 8.5 Historique (LOG-18)

L'historique complet d'une ressource (toutes les reservations, tous statuts) :

```
GET /api/logistique/ressources/{id}/historique?limit=100&offset=0
```

---

## 9. NOTIFICATIONS ET RAPPELS

### 9.1 Evenements de notification

| Evenement | Destinataire | Moment | Feature |
|-----------|-------------|---------|---------|
| `ReservationCreatedEvent` | Conducteur/Admin | A la creation | LOG-13 |
| `ReservationValideeEvent` | Demandeur | A la validation | LOG-14 |
| `ReservationRefuseeEvent` | Demandeur | Au refus | LOG-14 |
| `ReservationRappelEvent` | Demandeur | Veille J-1 | LOG-15 |
| `ReservationConflitEvent` | Conducteur/Admin | Conflit detecte | LOG-17 |

### 9.2 Rappel J-1 (LOG-15)

Le systeme identifie les reservations prevues pour le lendemain :

```python
def find_a_rappeler_demain() -> List[Reservation]:
    """Retourne les reservations actives (EN_ATTENTE ou VALIDEE)
    dont date_reservation == demain"""
```

La propriete `est_demain` sur l'entite permet aussi de verifier cote code metier.

### 9.3 Implementation actuelle

Les evenements sont publies via le bus d'evenements interne. Les handlers de notification (push, email) ne sont pas encore implementes. Les evenements servent actuellement de base pour les futurs systemes de notification.

---

## 10. PERMISSIONS ET ROLES

### 10.1 Matrice de permissions - Ressources

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|-----------|---------------|-----------|
| Creer ressource | Oui | Non | Non | Non |
| Modifier ressource | Oui | Non | Non | Non |
| Supprimer ressource | Oui | Non | Non | Non |
| Voir catalogue | Oui | Oui | Oui | Oui |
| Voir planning | Oui | Oui | Oui | Oui |
| Voir historique | Oui | Oui | Oui | Oui |

### 10.2 Matrice de permissions - Reservations

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|-----------|---------------|-----------|
| Creer reservation | Oui | Oui | Oui | Oui |
| Voir sa reservation | Oui | Oui | Oui | Oui |
| Voir toute reservation | Oui | Oui | Oui | Non |
| Modifier reservation | Oui | Oui | Non (sauf sienne) | Non (sauf sienne) |
| Valider reservation | Oui | Oui | Non | Non |
| Refuser reservation | Oui | Oui | Non | Non |
| Annuler reservation | Oui | Oui | Non (sauf sienne) | Non (sauf sienne) |
| Voir file validation | Oui | Oui | Non | Non |

### 10.3 Securite

| Code | Regle | Endpoint |
|------|-------|----------|
| SEC-001 | GET reservation : proprietaire ou role privilegie | `GET /reservations/{id}` |
| SEC-002 | PUT reservation : proprietaire uniquement | `PUT /reservations/{id}` |
| SEC-003 | Annulation : proprietaire ou role privilegie | `POST /reservations/{id}/annuler` |

---

## 11. EVENEMENTS DOMAINE

### 11.1 Liste des evenements

**Fichier** : `backend/modules/logistique/domain/events/logistique_events.py`

| Evenement | Donnees | Declencheur |
|-----------|---------|-------------|
| `RessourceCreatedEvent` | ressource_id, nom, code, categorie, created_by | Creation ressource |
| `RessourceUpdatedEvent` | ressource_id, nom, code, updated_by | Modification ressource |
| `RessourceDeletedEvent` | ressource_id, deleted_by | Suppression ressource |
| `ReservationCreatedEvent` | reservation_id, ressource_id, ressource_nom, chantier_id, demandeur_id, date_reservation, heure_debut, heure_fin, validation_requise | Creation reservation |
| `ReservationValideeEvent` | reservation_id, ressource_id, ressource_nom, demandeur_id, valideur_id, date_reservation | Validation |
| `ReservationRefuseeEvent` | reservation_id, ressource_id, ressource_nom, demandeur_id, valideur_id, date_reservation, motif | Refus |
| `ReservationAnnuleeEvent` | reservation_id, ressource_id, demandeur_id, date_reservation | Annulation |
| `ReservationRappelEvent` | reservation_id, ressource_id, ressource_nom, demandeur_id, chantier_id, date_reservation, heure_debut, heure_fin | Rappel J-1 |
| `ReservationConflitEvent` | ressource_id, date_reservation, reservations_en_conflit, nouvelle_reservation_id | Conflit detecte |

---

## 12. API REST - ENDPOINTS

### 12.1 Ressources

**Router** : `/api/logistique`

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| POST | `/ressources` | Admin | Creer ressource | LOG-01 |
| GET | `/ressources` | Authentifie | Liste avec filtres | LOG-01 |
| GET | `/ressources/{id}` | Authentifie | Detail ressource | LOG-01 |
| PUT | `/ressources/{id}` | Admin | Modifier ressource | LOG-01 |
| DELETE | `/ressources/{id}` | Admin | Supprimer (soft) | LOG-01 |
| GET | `/ressources/{id}/planning` | Authentifie | Planning 7 jours | LOG-03/04 |
| GET | `/ressources/{id}/historique` | Authentifie | Historique complet | LOG-18 |

### 12.2 Reservations

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| POST | `/reservations` | Authentifie | Creer reservation | LOG-07/08/09 |
| GET | `/reservations/en-attente` | Conducteur/Admin | File validation | LOG-11 |
| GET | `/reservations/{id}` | Proprietaire/Privilegie | Detail reservation | - |
| PUT | `/reservations/{id}` | Proprietaire | Modifier (EN_ATTENTE) | - |
| POST | `/reservations/{id}/valider` | Conducteur/Admin | Valider | LOG-11/14 |
| POST | `/reservations/{id}/refuser` | Conducteur/Admin | Refuser (+ motif) | LOG-14/16 |
| POST | `/reservations/{id}/annuler` | Proprietaire/Privilegie | Annuler | - |

### 12.3 Schemas de validation (Pydantic)

**RessourceCreateRequest** :
```python
{
    "nom": str,                       # 1-200 chars
    "code": str,                      # 1-20 chars, pattern ^[A-Z0-9\-]+$
    "categorie": CategorieRessource,  # enum
    "photo_url": Optional[str],
    "couleur": Optional[str],         # pattern hex
    "heure_debut_defaut": Optional[time],  # default 08:00
    "heure_fin_defaut": Optional[time],    # default 18:00
    "validation_requise": Optional[bool],
    "description": Optional[str]      # max 2000
}
```

**ReservationCreateRequest** :
```python
{
    "ressource_id": int,   # > 0
    "chantier_id": int,    # > 0
    "date_reservation": date,
    "heure_debut": time,
    "heure_fin": time,     # CHECK > heure_debut
    "commentaire": Optional[str]  # max 1000
}
```

**RefuserReservationRequest** :
```python
{
    "motif": Optional[str]  # max 1000
}
```

---

## 13. ARCHITECTURE TECHNIQUE

### 13.1 Structure des fichiers

```
backend/modules/logistique/
|
+-- domain/
|   +-- entities/
|   |   +-- ressource.py          # Entite ressource
|   |   +-- reservation.py        # Entite reservation
|   +-- value_objects/
|   |   +-- statut_reservation.py # Machine a etats
|   |   +-- categorie_ressource.py # 5 categories
|   |   +-- plage_horaire.py      # Creneau horaire
|   +-- repositories/
|   |   +-- ressource_repository.py   # Interface abstraite
|   |   +-- reservation_repository.py # Interface abstraite
|   +-- events/
|       +-- logistique_events.py   # 9 evenements domaine
|
+-- application/
|   +-- use_cases/
|   |   +-- ressource_use_cases.py   # 5 use cases (CRUD + list)
|   |   +-- reservation_use_cases.py # 9 use cases
|   +-- dtos/
|   |   +-- ressource_dtos.py  # 4 DTOs
|   |   +-- reservation_dtos.py # 6 DTOs
|   +-- helpers/
|       +-- dto_enrichment.py  # Enrichissement DTOs (cache N+1)
|
+-- infrastructure/
    +-- persistence/
    |   +-- models.py              # 2 tables SQLAlchemy
    |   +-- sqlalchemy_ressource_repository.py
    |   +-- sqlalchemy_reservation_repository.py
    +-- web/
        +-- logistique_routes.py   # 14 endpoints FastAPI
        +-- dependencies.py        # Injection de dependances
        +-- mappers.py             # Request -> DTO mappers
```

### 13.2 Tables base de donnees

**Table `ressources`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| nom | VARCHAR(200) | NOT NULL |
| code | VARCHAR(20) | NOT NULL, UNIQUE, INDEX |
| categorie | ENUM | NOT NULL, INDEX |
| photo_url | VARCHAR(500) | nullable |
| couleur | VARCHAR(7) | default "#3B82F6" |
| heure_debut_defaut | TIME | default 08:00 |
| heure_fin_defaut | TIME | default 18:00 |
| validation_requise | BOOLEAN | default true |
| actif | BOOLEAN | default true, INDEX |
| description | TEXT | nullable |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |
| created_by | INTEGER | FK users, SET NULL |
| deleted_at | DATETIME | nullable (soft delete) |
| deleted_by | INTEGER | FK users, SET NULL |

Index composite : `(categorie, actif)`
CHECK : `heure_fin_defaut > heure_debut_defaut`

**Table `reservations`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| ressource_id | INTEGER | FK ressources, RESTRICT, INDEX |
| chantier_id | INTEGER | FK chantiers, RESTRICT, INDEX |
| demandeur_id | INTEGER | FK users, RESTRICT, INDEX |
| date_reservation | DATE | INDEX |
| heure_debut | TIME | |
| heure_fin | TIME | |
| statut | ENUM | default "en_attente", INDEX |
| motif_refus | TEXT | nullable |
| commentaire | TEXT | nullable |
| valideur_id | INTEGER | FK users, SET NULL |
| validated_at | DATETIME | nullable |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |
| deleted_at | DATETIME | nullable (soft delete) |
| deleted_by | INTEGER | FK users, SET NULL |

Indexes composites :
- `(ressource_id, date_reservation)` -- Planning (LOG-03)
- `(statut, date_reservation)` -- File validation (LOG-11)
- `(chantier_id, date_reservation)`
- `(demandeur_id, statut)`
- `(ressource_id, statut, date_reservation)` -- Conflits (LOG-17)
- Partial unique : `(ressource_id, date_reservation, heure_debut, heure_fin) WHERE statut IN ('en_attente', 'validee')`

CHECK : `heure_fin > heure_debut`

### 13.3 Frontend - Composants

| Composant | Fichier | Responsabilite |
|-----------|---------|---------------|
| `RessourceList` | RessourceList.tsx | Catalogue avec recherche et filtres |
| `RessourceCard` | RessourceCard.tsx | Carte ressource (code, nom, categorie, couleur) |
| `RessourceModal` | RessourceModal.tsx | Creation / edition ressource |
| `ReservationCalendar` | ReservationCalendar.tsx | Calendrier 7 jours (LOG-03/04/05) |
| `ReservationModal` | ReservationModal.tsx | Creation / detail / actions |
| `ReservationFormFields` | ReservationFormFields.tsx | Champs du formulaire |
| `ReservationActions` | ReservationActions.tsx | Boutons d'action (valider, refuser, annuler) |

**Hook principal** : `useLogistique.ts`
- Gere les onglets (ressources / planning / en-attente)
- Synchro URL query params
- Permissions (isAdmin, canValidate)
- Selection ressource/reservation
- Modal state + initial data

**Hook modal** : `useReservationModal.ts`
- Gere le formulaire de reservation
- Operations API (create, valider, refuser, annuler)
- Etats loading / error

---

## 14. SCENARIOS DE TEST

### Scenario 1 : Reservation avec validation N+1

```
GIVEN une ressource [GRU-001] "Grue mobile 40T" avec validation_requise = true
AND un chef de chantier "Sebastien ACHKAR"
AND le chantier "Villa Duplex"

WHEN Sebastien cree une reservation pour le 30 janvier 08:00-12:00
THEN la reservation est creee en statut EN_ATTENTE
AND un ReservationCreatedEvent est publie avec validation_requise = true

WHEN le conducteur valide la reservation
THEN le statut passe a VALIDEE
AND valideur_id et validated_at sont renseignes
AND un ReservationValideeEvent est publie
```

### Scenario 2 : Auto-validation

```
GIVEN une ressource [CAM-001] "Camion benne" avec validation_requise = false
WHEN un compagnon cree une reservation pour le 31 janvier 07:00-17:00
THEN la reservation est creee directement en statut VALIDEE
AND le demandeur_id = valideur_id (auto-validation)
```

### Scenario 3 : Conflit de creneaux

```
GIVEN [GRU-001] reservee le 30 janvier 08:00-12:00 (VALIDEE)
WHEN un autre utilisateur tente de reserver le 30 janvier 10:00-14:00
THEN HTTP 409 Conflict
AND la reservation n'est PAS creee
AND un ReservationConflitEvent est publie
```

### Scenario 4 : Refus avec motif

```
GIVEN une reservation EN_ATTENTE pour [ECH-001] le 30 janvier
WHEN le conducteur refuse avec motif "Echafaudage en maintenance"
THEN le statut passe a REFUSEE
AND motif_refus = "Echafaudage en maintenance"
AND un ReservationRefuseeEvent est publie
AND la reservation est en etat FINAL (pas de retour possible)
```

### Scenario 5 : Annulation par le demandeur

```
GIVEN une reservation VALIDEE pour [PEL-001] le 1er fevrier
WHEN le demandeur annule sa reservation
THEN le statut passe a ANNULEE
AND un ReservationAnnuleeEvent est publie
AND la reservation est en etat FINAL
```

### Scenario 6 : Ressource inactive

```
GIVEN une ressource [BET-001] desactivee (actif = false)
WHEN un utilisateur tente de la reserver
THEN HTTP 400 "Ressource inactive"
AND la reservation n'est PAS creee
```

### Scenario 7 : Permissions

```
GIVEN une reservation creee par le compagnon Carlos
WHEN un autre compagnon tente GET /reservations/{id}
THEN HTTP 403 Forbidden (SEC-001)

WHEN un conducteur tente GET /reservations/{id}
THEN HTTP 200 (role privilegie)
```

---

## 15. EVOLUTIONS FUTURES

| Evolution | Description | Impact |
|-----------|-------------|--------|
| **Notifications push** | Push a la creation/validation/refus/rappel | Integration FCM/OneSignal |
| **Reservations recurrentes** | Reserver chaque lundi 08:00-12:00 | Nouveau champ recurrence |
| **Vue multi-ressources** | Calendrier avec plusieurs ressources | Composant Gantt |
| **Suivi GPS** | Localisation temps reel des engins | Integration GPS/IoT |
| **Maintenance planifiee** | Periodes d'indisponibilite programmees | Nouvelle entite Maintenance |
| **Cout / facturation** | Prix par heure/jour par ressource | Champs cout + factures |
| **Documents associes** | Certificats CACES, assurances | Lien avec module GED |
| **QR Code** | Scan QR pour identifier la ressource | Generation + scan mobile |
| **Reporting** | Taux d'utilisation par ressource/chantier | Dashboard analytique |

---

## 16. REFERENCES CDC

| Section CDC | Description | Fonctionnalites |
|-------------|-------------|-----------------|
| Section 9 | Logistique Materiel | LOG-01 a LOG-18 |
| Section 3 | Gestion utilisateurs | Roles et permissions |
| Section 4 | Gestion chantiers | `chantier_id` FK |

### Fichiers sources principaux

| Fichier | Role |
|---------|------|
| `backend/modules/logistique/domain/entities/ressource.py` | Entite ressource |
| `backend/modules/logistique/domain/entities/reservation.py` | Entite reservation + conflits |
| `backend/modules/logistique/domain/value_objects/statut_reservation.py` | Machine a etats |
| `backend/modules/logistique/domain/value_objects/categorie_ressource.py` | Categories + N+1 defaut |
| `backend/modules/logistique/domain/value_objects/plage_horaire.py` | Creneaux horaires |
| `backend/modules/logistique/application/use_cases/reservation_use_cases.py` | 9 use cases |
| `backend/modules/logistique/infrastructure/web/logistique_routes.py` | 14 endpoints |
| `backend/modules/logistique/infrastructure/persistence/models.py` | Tables SQL |
| `frontend/src/types/logistique.ts` | Types TypeScript |
| `frontend/src/api/logistique.ts` | Client API |
| `frontend/src/components/logistique/` | 7 composants |
| `frontend/src/hooks/useLogistique.ts` | Hook principal |
| `frontend/src/hooks/useReservationModal.ts` | Hook modal |

### Migration

| Fichier | Description |
|---------|-------------|
| `backend/migrations/versions/20260124_0003_logistique_schema.py` | Creation tables + indexes |

---

**Document genere automatiquement par analyse du code source.**
**Dernier audit : 30 janvier 2026**

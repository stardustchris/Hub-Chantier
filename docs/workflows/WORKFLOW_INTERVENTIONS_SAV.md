# Workflow Interventions / SAV - Hub Chantier

> Document cree le 30 janvier 2026
> Analyse complete du workflow de gestion des interventions et SAV

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entites et objets metier](#2-entites-et-objets-metier)
3. [Machine a etats - Statuts](#3-machine-a-etats---statuts)
4. [Types et priorites](#4-types-et-priorites)
5. [Flux de creation](#5-flux-de-creation)
6. [Flux de planification et execution](#6-flux-de-planification-et-execution)
7. [Affectation des techniciens](#7-affectation-des-techniciens)
8. [Fil d'activite et messagerie](#8-fil-dactivite-et-messagerie)
9. [Signature client et technicien](#9-signature-client-et-technicien)
10. [Rapport PDF - PV Client](#10-rapport-pdf---pv-client)
11. [Permissions et roles](#11-permissions-et-roles)
12. [Evenements domaine](#12-evenements-domaine)
13. [API REST - Endpoints](#13-api-rest---endpoints)
14. [Architecture technique](#14-architecture-technique)
15. [Etat du frontend](#15-etat-du-frontend)
16. [Scenarios de test](#16-scenarios-de-test)
17. [Evolutions futures](#17-evolutions-futures)
18. [References CDC](#18-references-cdc)

---

## 1. VUE D'ENSEMBLE

### Objectif du module

Le module Interventions gere les interventions courte duree (SAV, maintenance, depannage, levee de reserves) distinctes des chantiers long terme. Chaque intervention suit un cycle de vie complet : creation, planification, execution terrain avec signature client, et generation d'un rapport PDF faisant office de PV client.

### Flux global simplifie

```
Conducteur cree une intervention (client, adresse, type)
    |
    v
[A_PLANIFIER] Code INT-YYYY-NNNN genere automatiquement
    |
    v
[PLANIFIER] Date + horaires + techniciens affectes
    |
    v
[PLANIFIEE] Techniciens notifies
    |
    v
[DEMARRER] Heure debut reelle enregistree
    |
    v
[EN_COURS] Messages, photos, actions dans le fil d'activite
    |
    +---> Signature technicien (geoloc + IP + horodatage)
    +---> Signature client (geoloc + IP + horodatage)
    |
    v
[TERMINER] Travaux realises + anomalies
    |
    v
[TERMINEE] --> Generation rapport PDF (PV client)
```

### Chantier d'origine optionnel

Le champ `chantier_origine_id` est **optionnel** (nullable, FK ON DELETE SET NULL). Cela permet de gerer les interventions post-livraison qui ne sont plus rattachees a un chantier actif. C'est typique des interventions SAV et levees de reserves.

### Fonctionnalites couvertes (CDC Section Interventions)

| ID | Fonctionnalite | Description |
|----|----------------|-------------|
| INT-01 | Onglet dedie Planning | Structure module interventions |
| INT-02 | Liste interventions | Vue tableau avec filtres et pagination |
| INT-03 | Creation intervention | Formulaire complet (client, type, priorite) |
| INT-04 | Fiche intervention | Detail complet avec mise a jour |
| INT-05 | Gestion statuts | Machine a etats 5 statuts |
| INT-06 | Planning hebdomadaire | Liste par technicien et plage de dates |
| INT-07 | Blocs horaires colores | Couleurs par type et priorite |
| INT-08 | Interventions multiples/jour | Pas de limite (1-2 = guideline design) |
| INT-10 | Affectation techniciens | Entite dediee avec technicien principal |
| INT-11 | Fil d'activite | Messages type ACTION, PHOTO, COMMENTAIRE |
| INT-12 | Chat / messagerie | Messages type COMMENTAIRE |
| INT-13 | Signature client mobile | Base64 + geolocalisation + IP |
| INT-14 | Generation rapport PDF | PV client avec signatures |
| INT-15 | Selection messages rapport | Toggle inclure/exclure par message |
| INT-17 | Affectation sous-traitant | Via AffectationIntervention (pas de distinction role) |

---

## 2. ENTITES ET OBJETS METIER

### 2.1 Intervention (entite principale)

**Fichier** : `backend/modules/interventions/domain/entities/intervention.py`

| Champ | Type | Defaut | Requis | Notes |
|-------|------|--------|--------|-------|
| id | Optional[int] | None | Non | Cle primaire auto-increment |
| code | Optional[str] | None | Non | Format INT-YYYY-NNNN (ex: INT-2026-0001) |
| type_intervention | TypeIntervention | - | Oui | SAV, MAINTENANCE, DEPANNAGE, LEVEE_RESERVES, AUTRE |
| statut | StatutIntervention | A_PLANIFIER | Non | Machine a etats 5 statuts |
| priorite | PrioriteIntervention | NORMALE | Non | BASSE, NORMALE, HAUTE, URGENTE |
| client_nom | str | - | Oui | Nom client, max 200 caracteres |
| client_adresse | str | - | Oui | Adresse complete |
| client_telephone | Optional[str] | None | Non | Max 20 caracteres |
| client_email | Optional[str] | None | Non | Max 200 caracteres |
| description | str | - | Oui | Description de l'intervention |
| date_souhaitee | Optional[date] | None | Non | Date souhaitee par le client |
| date_planifiee | Optional[date] | None | Non | Date planifiee |
| heure_debut | Optional[time] | None | Non | Heure debut prevue |
| heure_fin | Optional[time] | None | Non | Heure fin prevue |
| heure_debut_reelle | Optional[time] | None | Non | Heure debut effective |
| heure_fin_reelle | Optional[time] | None | Non | Heure fin effective |
| travaux_realises | Optional[str] | None | Non | Description travaux effectues |
| anomalies | Optional[str] | None | Non | Problemes non resolus |
| chantier_origine_id | Optional[int] | None | Non | FK chantiers (optionnel, post-livraison) |
| rapport_genere | bool | False | Non | Rapport PDF genere ou non |
| rapport_url | Optional[str] | None | Non | URL du rapport PDF |
| created_by | int | - | Oui | ID utilisateur createur |
| created_at | datetime | utcnow() | Non | Horodatage creation |
| updated_at | datetime | utcnow() | Non | Derniere modification |
| deleted_at | Optional[datetime] | None | Non | Suppression logique |
| deleted_by | Optional[int] | None | Non | Qui a supprime |

**Methodes cles** :
- `planifier(date_planifiee, heure_debut, heure_fin)` - Planifie l'intervention
- `demarrer(heure_debut_reelle)` - Demarre sur le terrain
- `terminer(heure_fin_reelle, travaux_realises, anomalies)` - Termine avec bilan
- `annuler()` - Annule l'intervention
- `marquer_rapport_genere(rapport_url)` - Marque le rapport PDF comme genere (INT-14)
- `modifier_priorite(nouvelle_priorite)` - Change la priorite
- `modifier_client(nom, adresse, telephone, email)` - Met a jour infos client

**Proprietes calculees** :
- `est_active` - True si A_PLANIFIER, PLANIFIEE ou EN_COURS
- `est_modifiable` - False uniquement pour ANNULEE
- `duree_prevue_minutes` - Duree prevue en minutes
- `duree_reelle_minutes` - Duree effective en minutes
- `horaires_str` - Plage horaire formatee (HH:MM - HH:MM)

### 2.2 AffectationIntervention (INT-10, INT-17)

**Fichier** : `backend/modules/interventions/domain/entities/affectation_intervention.py`

| Champ | Type | Defaut | Notes |
|-------|------|--------|-------|
| id | Optional[int] | None | Cle primaire |
| intervention_id | int | - | FK interventions (requis) |
| utilisateur_id | int | - | FK users (technicien ou sous-traitant) |
| est_principal | bool | False | Technicien principal de l'intervention |
| commentaire | Optional[str] | None | Note sur l'affectation |
| created_by | int | - | Qui a cree l'affectation |
| created_at / updated_at | datetime | utcnow() | Horodatages |
| deleted_at / deleted_by | Optional | None | Suppression logique |

**Contrainte** : UNIQUE (intervention_id, utilisateur_id) WHERE deleted_at IS NULL

**Guideline** : 1-2 techniciens par intervention (courte duree).

### 2.3 InterventionMessage (INT-11, INT-12, INT-15)

**Fichier** : `backend/modules/interventions/domain/entities/intervention_message.py`

| Champ | Type | Defaut | Notes |
|-------|------|--------|-------|
| id | Optional[int] | None | Cle primaire |
| intervention_id | int | - | FK interventions (requis) |
| auteur_id | int | - | FK users (0 = messages systeme) |
| type_message | TypeMessage | - | COMMENTAIRE, PHOTO, ACTION, SYSTEME |
| contenu | str | - | Contenu du message (requis) |
| photos_urls | List[str] | [] | URLs des photos jointes |
| metadata | Optional[dict] | None | Donnees JSON supplementaires |
| inclure_rapport | bool | True | Inclus dans le rapport PDF (INT-15) |
| created_at | datetime | utcnow() | Horodatage |
| deleted_at / deleted_by | Optional | None | Suppression logique |

**TypeMessage (enum)** :
| Valeur | Description | inclure_rapport par defaut |
|--------|-------------|---------------------------|
| COMMENTAIRE | Texte de chat (INT-12) | True |
| PHOTO | Photo avec description (INT-11) | True |
| ACTION | Action systeme (demarrage, signature) | False |
| SYSTEME | Message systeme (changement statut) | False |

**Factory methods** :
- `creer_commentaire(intervention_id, auteur_id, contenu)` - Message texte
- `creer_photo(intervention_id, auteur_id, description, photos_urls)` - Photo
- `creer_action(intervention_id, auteur_id, action, metadata)` - Action (inclure_rapport=False)
- `creer_systeme(intervention_id, message)` - Systeme (auteur_id=0, inclure_rapport=False)

### 2.4 SignatureIntervention (INT-13, INT-14)

**Fichier** : `backend/modules/interventions/domain/entities/signature_intervention.py`

| Champ | Type | Defaut | Notes |
|-------|------|--------|-------|
| id | Optional[int] | None | Cle primaire |
| intervention_id | int | - | FK interventions (requis) |
| type_signataire | TypeSignataire | - | CLIENT ou TECHNICIEN |
| nom_signataire | str | - | Nom du signataire (requis) |
| signature_data | str | - | Base64 ou URL de l'image signature (requis) |
| utilisateur_id | Optional[int] | None | FK users (requis si TECHNICIEN) |
| ip_address | Optional[str] | None | Adresse IP (tracabilite) |
| user_agent | Optional[str] | None | Navigateur (tracabilite) |
| latitude | Optional[float] | None | Geolocalisation GPS |
| longitude | Optional[float] | None | Geolocalisation GPS |
| signed_at | datetime | utcnow() | Horodatage signature |
| deleted_at / deleted_by | Optional | None | Suppression logique |

**Contraintes** :
- Une seule signature client par intervention (index unique partiel)
- Un technicien ne peut signer qu'une fois par intervention
- Pour TECHNICIEN : utilisateur_id obligatoire

**Factory methods** :
- `creer_signature_client(intervention_id, nom_client, signature_data, ip_address, latitude, longitude)`
- `creer_signature_technicien(intervention_id, utilisateur_id, nom_technicien, signature_data, ip_address, latitude, longitude)`

**Proprietes** :
- `a_geolocalisation` - True si latitude et longitude presentes
- `horodatage_str` - Format "DD/MM/YYYY a HH:MM"

---

## 3. MACHINE A ETATS - STATUTS

### Diagramme de transitions

```
┌──────────────────────────────────────────────────────────────────┐
│ INT-05: Cycle de vie Intervention                                │
└──────────────────────────────────────────────────────────────────┘

  A_PLANIFIER ──(planifier)──> PLANIFIEE ──(demarrer)──> EN_COURS
       │                          │                         │
       │                          │ (replanifier)           │
       │                          └────> A_PLANIFIER        │
       │                          │                         │
       │ (annuler)                │ (annuler)               │ (terminer)
       v                          v                         v
   ANNULEE                     ANNULEE                   TERMINEE
                                                            │
                                                            │ (annuler)
                                                            v
                                                         ANNULEE
```

### Proprietes par statut

| Statut | Label | Couleur | est_active | est_modifiable | Etats suivants |
|--------|-------|---------|-----------|----------------|----------------|
| A_PLANIFIER | "A planifier" | #F59E0B | true | true | PLANIFIEE, ANNULEE |
| PLANIFIEE | "Planifiee" | #3B82F6 | true | true | EN_COURS, A_PLANIFIER, ANNULEE |
| EN_COURS | "En cours" | #10B981 | true | true | TERMINEE, ANNULEE |
| TERMINEE | "Terminee" | #6B7280 | false | false | Aucun (etat final) |
| ANNULEE | "Annulee" | #EF4444 | false | false | Aucun (etat final) |

### Regles metier des transitions

- **planifier** : Necessite date_planifiee. heure_debut et heure_fin optionnels. Peut affecter des techniciens en meme temps.
- **demarrer** : Enregistre heure_debut_reelle (auto si non fournie).
- **terminer** : Peut renseigner heure_fin_reelle, travaux_realises et anomalies.
- **annuler** : Possible depuis A_PLANIFIER, PLANIFIEE et EN_COURS.
- **replanifier** : PLANIFIEE peut revenir a A_PLANIFIER.
- TERMINEE et ANNULEE sont des **etats finaux** (aucune transition sortante).

---

## 4. TYPES ET PRIORITES

### Types d'intervention (INT-01 a INT-17)

| Valeur | Label | Couleur | Description |
|--------|-------|---------|-------------|
| SAV | "SAV" | #8B5CF6 | Service apres-vente |
| MAINTENANCE | "Maintenance" | #3B82F6 | Maintenance preventive/curative |
| DEPANNAGE | "Depannage" | #EF4444 | Reparation d'urgence |
| LEVEE_RESERVES | "Levee de reserves" | #F59E0B | Post-reception, levee des reserves |
| AUTRE | "Autre" | #6B7280 | Autre type |

### Priorites (INT-04)

| Valeur | Label | Couleur | Ordre | Comparable |
|--------|-------|---------|-------|-----------|
| BASSE | "Basse" | #6B7280 | 1 | Oui (operateurs < et <=) |
| NORMALE | "Normale" | #3B82F6 | 2 | |
| HAUTE | "Haute" | #F59E0B | 3 | |
| URGENTE | "Urgente" | #EF4444 | 4 | |

---

## 5. FLUX DE CREATION

### Donnees requises (CreateInterventionDTO)

```
type_intervention: TypeIntervention (requis)
priorite: PrioriteIntervention (defaut: NORMALE)
client_nom: str (1-200 caracteres)
client_adresse: str (min 1 caractere)
client_telephone: Optional[str] (max 20)
client_email: Optional[str] (max 200)
description: str (min 1 caractere)
date_souhaitee: Optional[date]
chantier_origine_id: Optional[int]  // Optionnel, pour SAV post-livraison
```

### Generation du code

**Format** : `INT-YYYY-NNNN`
- YYYY = annee en cours
- NNNN = numero sequentiel sur 4 chiffres (zero-padded)
- Sequence : INT-2026-0001, INT-2026-0002, ..., INT-2026-9999

**Logique** : Compte les interventions existantes de l'annee en cours, incremente de 1.

### Resultat

- Statut initial : A_PLANIFIER
- Code genere automatiquement
- Evenement `InterventionCreee` emis

---

## 6. FLUX DE PLANIFICATION ET EXECUTION

### Planification (PlanifierInterventionDTO)

```
date_planifiee: date (requis)
heure_debut: Optional[time]
heure_fin: Optional[time]      // Validation: heure_fin > heure_debut
techniciens_ids: List[int] = []  // Affectation simultanee possible
```

- Transition : A_PLANIFIER → PLANIFIEE
- Les techniciens fournis sont affectes en meme temps
- Evenement `InterventionPlanifiee` emis

### Demarrage (DemarrerInterventionDTO)

```
heure_debut_reelle: Optional[time]  // Auto-set a l'heure courante si non fourni
```

- Transition : PLANIFIEE → EN_COURS
- Evenement `InterventionDemarree` emis

### Fin (TerminerInterventionDTO)

```
heure_fin_reelle: Optional[time]
travaux_realises: Optional[str]    // Description des travaux effectues
anomalies: Optional[str]          // Problemes non resolus
```

- Transition : EN_COURS → TERMINEE
- Evenement `InterventionTerminee` emis

---

## 7. AFFECTATION DES TECHNICIENS

### Entite AffectationIntervention (INT-10, INT-17)

**Technicien principal** : Un seul technicien principal par intervention (flag `est_principal`).

**Sous-traitants** (INT-17) : Pas de distinction de role dans l'entite. Les sous-traitants sont affectes via le meme mecanisme que les techniciens internes.

### Endpoints

| Methode | Endpoint | Action |
|---------|----------|--------|
| POST | `/interventions/{id}/techniciens` | Affecter un technicien |
| GET | `/interventions/{id}/techniciens` | Lister les techniciens affectes |
| DELETE | `/interventions/{id}/techniciens/{affectation_id}` | Retirer (soft delete) |

### Requete d'affectation

```
utilisateur_id: int (requis)
est_principal: bool (defaut: false)
commentaire: Optional[str]
```

### Contraintes

- Unicite partielle : un utilisateur ne peut etre affecte qu'une fois par intervention (WHERE deleted_at IS NULL)
- Guideline design : 1-2 techniciens par intervention (pas de limite technique stricte)
- Evenements : `TechnicienAffecte` et `TechnicienDesaffecte`

---

## 8. FIL D'ACTIVITE ET MESSAGERIE

### Types de messages (INT-11, INT-12)

Le fil d'activite centralise toutes les interactions sur une intervention :

| Type | Icone | Auteur | Contenu | Rapport |
|------|-------|--------|---------|---------|
| COMMENTAIRE | Chat | Utilisateur | Texte libre (INT-12) | Inclus par defaut |
| PHOTO | Camera | Utilisateur | Description + URLs photos | Inclus par defaut |
| ACTION | Systeme | Utilisateur | Demarrage, signature, etc. | Exclu par defaut |
| SYSTEME | Info | Systeme (id=0) | Changement statut, etc. | Exclu par defaut |

### Selection pour le rapport (INT-15)

Chaque message a un flag `inclure_rapport` (boolean, defaut True pour COMMENTAIRE et PHOTO).

**Toggle** : `PATCH /interventions/{id}/messages/{msg_id}/rapport?inclure=true|false`

Cela permet au conducteur de selectionner precisement quels messages apparaitront dans le PV client final.

### Endpoints messages

| Methode | Endpoint | Action |
|---------|----------|--------|
| POST | `/interventions/{id}/messages` | Ajouter un message |
| GET | `/interventions/{id}/messages` | Lister (filtre type_message, limit/offset) |
| PATCH | `/interventions/{id}/messages/{msg_id}/rapport` | Toggle inclusion rapport |

---

## 9. SIGNATURE CLIENT ET TECHNICIEN

### Mecanisme (INT-13)

La signature est capturee sur mobile (dessin manuscrit) et stockee en **Base64** ou URL.

**Tracabilite complete** :
- `ip_address` : Adresse IP du terminal (capturee automatiquement depuis request.client.host)
- `user_agent` : Navigateur/OS du terminal
- `latitude` / `longitude` : Geolocalisation GPS (si autorisee)
- `signed_at` : Horodatage UTC precis

### Types de signataires

| Type | Contrainte | utilisateur_id |
|------|-----------|----------------|
| CLIENT | 1 seule signature client par intervention | Non requis |
| TECHNICIEN | 1 signature par technicien par intervention | Requis |

### Endpoints signatures

| Methode | Endpoint | Action |
|---------|----------|--------|
| POST | `/interventions/{id}/signatures` | Ajouter une signature |
| GET | `/interventions/{id}/signatures` | Lister les signatures |

### Corps de la requete

```json
{
  "type_signataire": "client",
  "nom_signataire": "M. Dupont",
  "signature_data": "data:image/png;base64,iVBOR...",
  "latitude": 48.8566,
  "longitude": 2.3522
}
```

### Valeur probante

La combinaison signature manuscrite + horodatage + geolocalisation + IP constitue un ensemble de preuves pour le PV client.

---

## 10. RAPPORT PDF - PV CLIENT

### Concept (INT-14)

Le rapport PDF genere constitue le **Proces-Verbal (PV) client** de l'intervention. Il synthethise toutes les informations de l'intervention dans un document formel.

### Contenu du rapport

1. **En-tete** : Code intervention, type, priorite, dates
2. **Informations client** : Nom, adresse, telephone, email
3. **Details intervention** : Description, dates prevues/reelles, durees
4. **Travaux realises** : Description complete
5. **Anomalies** : Problemes non resolus
6. **Messages selectionnes** : Uniquement ceux avec `inclure_rapport=True` (INT-15)
7. **Signatures** :
   - Signature client avec horodatage, geolocalisation, IP
   - Signature(s) technicien avec horodatage, geolocalisation, IP

### Declenchement

```python
intervention.marquer_rapport_genere(rapport_url)
# → rapport_genere = True
# → rapport_url = URL du PDF stocke
# → Evenement RapportGenere emis
```

### Selection des messages (INT-15)

Le repository expose `list_for_rapport(intervention_id)` qui retourne uniquement les messages non supprimes avec `inclure_rapport=True`. Cela permet un controle fin du contenu du PV.

---

## 11. PERMISSIONS ET ROLES

### Matrice d'acces

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|-----------|---------------|-----------|
| Creer intervention | Oui | Oui | Non | Non |
| Planifier | Oui | Oui | Non | Non |
| Demarrer | Oui | Oui | Oui (si affecte) | Non |
| Terminer | Oui | Oui | Oui (si affecte) | Non |
| Annuler | Oui | Oui | Non | Non |
| Affecter technicien | Oui | Oui | Non | Non |
| Ajouter message | Oui | Oui | Oui | Oui (si affecte) |
| Signer (technicien) | - | - | Oui (si affecte) | Oui (si affecte) |
| Signer (client) | - | Capture sur mobile du client | - | - |
| Generer rapport | Oui | Oui | Non | Non |
| Supprimer | Oui | Oui | Non | Non |

---

## 12. EVENEMENTS DOMAINE

**Fichier** : `backend/modules/interventions/domain/events/intervention_events.py`

| Evenement | Champs | Declencheur |
|-----------|--------|-------------|
| **InterventionCreee** | intervention_id, code, type_intervention, priorite, client_nom, created_by | Creation |
| **InterventionPlanifiee** | intervention_id, code, date_planifiee, heure_debut, heure_fin, techniciens_ids | Planification |
| **InterventionDemarree** | intervention_id, code, technicien_id, heure_debut_reelle | Demarrage terrain |
| **InterventionTerminee** | intervention_id, code, heure_fin_reelle, travaux_realises, anomalies | Fin intervention |
| **InterventionAnnulee** | intervention_id, code, annule_par | Annulation |
| **TechnicienAffecte** | intervention_id, utilisateur_id, est_principal, affecte_par | Affectation |
| **TechnicienDesaffecte** | intervention_id, utilisateur_id, desaffecte_par | Retrait |
| **SignatureAjoutee** | intervention_id, type_signataire, nom_signataire | Signature |
| **RapportGenere** | intervention_id, code, rapport_url, genere_par | PDF genere |
| **MessageAjoute** | intervention_id, message_id, type_message, auteur_id | Nouveau message |

Tous les evenements sont des **frozen dataclasses** avec horodatage automatique.

---

## 13. API REST - ENDPOINTS

**Base** : `/api/interventions`

### CRUD

| Methode | Endpoint | Description | Statut retour |
|---------|----------|-------------|---------------|
| POST | `/interventions` | Creer intervention (INT-03) | 201 |
| GET | `/interventions` | Lister avec filtres et pagination (INT-02) | 200 |
| GET | `/interventions/{id}` | Detail intervention (INT-04) | 200 |
| PATCH | `/interventions/{id}` | Mettre a jour | 200 |
| DELETE | `/interventions/{id}` | Suppression logique | 204 |

**Parametres de liste** : statut, priorite, type_intervention, date_debut, date_fin, limit, offset

### Actions de transition

| Methode | Endpoint | Transition |
|---------|----------|-----------|
| POST | `/interventions/{id}/planifier` | A_PLANIFIER → PLANIFIEE |
| POST | `/interventions/{id}/demarrer` | PLANIFIEE → EN_COURS |
| POST | `/interventions/{id}/terminer` | EN_COURS → TERMINEE |
| POST | `/interventions/{id}/annuler` | Actif → ANNULEE |

### Techniciens

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/interventions/{id}/techniciens` | Affecter |
| GET | `/interventions/{id}/techniciens` | Lister affectations |
| DELETE | `/interventions/{id}/techniciens/{affectation_id}` | Retirer |

### Messages

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/interventions/{id}/messages` | Ajouter message |
| GET | `/interventions/{id}/messages` | Lister (filtre type, pagination) |
| PATCH | `/interventions/{id}/messages/{msg_id}/rapport` | Toggle rapport |

### Signatures

| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/interventions/{id}/signatures` | Ajouter signature |
| GET | `/interventions/{id}/signatures` | Lister signatures |

**Total : 16 endpoints**

---

## 14. ARCHITECTURE TECHNIQUE

### Clean Architecture

```
interventions/
├── domain/
│   ├── entities/
│   │   ├── intervention.py                 # Entite principale
│   │   ├── affectation_intervention.py     # Affectations techniciens
│   │   ├── intervention_message.py         # Messages / fil activite
│   │   └── signature_intervention.py       # Signatures client/technicien
│   ├── value_objects/
│   │   ├── statut_intervention.py          # Machine a etats
│   │   ├── type_intervention.py            # 5 types
│   │   └── priorite_intervention.py        # 4 priorites
│   ├── events/
│   │   └── intervention_events.py          # 10 evenements domaine
│   └── repositories/
│       ├── intervention_repository.py      # Interface abstraite
│       ├── affectation_intervention_repository.py
│       ├── intervention_message_repository.py
│       └── signature_intervention_repository.py
├── application/
│   ├── dtos/
│   │   └── intervention_dtos.py            # DTOs entree/sortie
│   └── use_cases/
│       ├── intervention_use_cases.py       # CRUD + transitions
│       ├── technicien_use_cases.py         # Affectation/desaffectation
│       ├── message_use_cases.py            # Messages + toggle rapport
│       └── signature_use_cases.py          # Signatures
└── infrastructure/
    └── persistence/
        └── models.py                       # Modeles SQLAlchemy
```

### Schema base de donnees

**Tables** : interventions, affectations_interventions, interventions_messages, interventions_signatures

**Index notables** :
- `ix_interventions_date_statut` (date_planifiee, statut)
- `ix_interventions_statut_priorite_date` (statut, priorite, date_planifiee)
- `ix_interventions_deleted_statut` (deleted_at, statut)
- `ix_interventions_messages_chrono` (intervention_id, created_at)
- `ix_interventions_messages_rapport` partiel (intervention_id, inclure_rapport) WHERE deleted_at IS NULL AND inclure_rapport = true
- `ix_interventions_signatures_client_unique` UNIQUE partiel WHERE type_signataire = 'client' AND deleted_at IS NULL

### Soft delete

Toutes les entites supportent la suppression logique avec `deleted_at` / `deleted_by`. Les requetes filtrent par defaut `WHERE deleted_at IS NULL`.

---

## 15. ETAT DU FRONTEND

### Composant existant

**Fichier** : `frontend/src/components/chantiers/MesInterventions.tsx`

Ce composant affiche les interventions d'un utilisateur dans le detail d'un chantier :
- Plage temporelle : 12 mois passe a 12 mois futur
- Separation : interventions a venir / passees
- Affichage : date + plage horaire (HH:MM - HH:MM)
- Mise en evidence des interventions du jour
- Charge via `planningService.getAffectations()`

### Frontend a developper

Le backend est **entierement implemente** (4 entites, 16 endpoints, 10 evenements). Le frontend reste a developper pour :

- **Page dediee interventions** : Liste avec filtres, creation, detail
- **Formulaire creation** : Type, priorite, client, adresse, description
- **Fiche intervention** : Detail complet avec onglets
- **Planning technicien** : Vue hebdomadaire (INT-06)
- **Fil d'activite** : Chat + photos + actions
- **Capture signature** : Canvas tactile + geolocalisation
- **Generation rapport** : Bouton + visualisation PDF

---

## 16. SCENARIOS DE TEST

### Tests unitaires recommandes

| # | Scenario | Resultat attendu |
|---|----------|-----------------|
| 1 | Creer intervention SAV sans chantier origine | OK, code INT-YYYY-NNNN genere, statut A_PLANIFIER |
| 2 | Creer intervention avec chantier_origine_id | OK, FK renseignee |
| 3 | Planifier avec date + horaires + techniciens | Statut PLANIFIEE, affectations creees |
| 4 | Demarrer sans heure_debut_reelle | OK, auto-set a l'heure courante |
| 5 | Terminer avec travaux et anomalies | Statut TERMINEE, champs renseignes |
| 6 | Annuler depuis EN_COURS | Statut ANNULEE |
| 7 | Tenter transition TERMINEE → autre | Erreur (etat final) |
| 8 | Affecter meme technicien 2 fois | Erreur (contrainte unicite) |
| 9 | Signer client 2 fois | Erreur (une seule signature client) |
| 10 | Toggle inclure_rapport sur message ACTION | OK, flag modifie |
| 11 | Generer rapport apres signatures | rapport_genere=True, rapport_url renseignee |
| 12 | Suppression logique | deleted_at renseigne, invisible dans listes |

---

## 17. EVOLUTIONS FUTURES

| Evolution | Description | Priorite |
|-----------|-------------|----------|
| Frontend complet | Pages dediees interventions (liste, creation, detail, planning) | Haute |
| Capture signature canvas | Composant React pour dessin tactile | Haute |
| Generation PDF reelle | Integration WeasyPrint ou equivalent | Moyenne |
| Notifications push | Handler pour InterventionPlanifiee → notification technicien | Moyenne |
| Geolocalisation automatique | Capture GPS automatique au demarrage/fin | Basse |
| Photos inline | Upload direct dans le fil d'activite | Basse |

---

## 18. REFERENCES CDC

| Section | Fonctionnalites | Status |
|---------|----------------|--------|
| INT-01 | Onglet dedie planning | Backend OK, Frontend partiel |
| INT-02 | Liste interventions | Backend OK |
| INT-03 | Creation intervention | Backend OK |
| INT-04 | Fiche intervention | Backend OK |
| INT-05 | Gestion statuts (5 etats) | Backend OK |
| INT-06 | Planning hebdomadaire | Backend OK |
| INT-07 | Blocs horaires colores | Value objects OK |
| INT-08 | Interventions multiples/jour | Backend OK |
| INT-10 | Affectation techniciens | Backend OK |
| INT-11 | Fil d'activite | Backend OK |
| INT-12 | Chat / messagerie | Backend OK |
| INT-13 | Signature client mobile | Backend OK |
| INT-14 | Rapport PDF | Backend OK (flag + URL) |
| INT-15 | Selection messages rapport | Backend OK |
| INT-17 | Affectation sous-traitant | Backend OK |

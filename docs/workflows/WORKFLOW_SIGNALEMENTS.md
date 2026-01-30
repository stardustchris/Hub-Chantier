# Workflow Signalements - Hub Chantier

> Document cree le 30 janvier 2026
> Analyse complete du workflow de gestion des signalements terrain

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entites et objets metier](#2-entites-et-objets-metier)
3. [Machine a etats - Statuts](#3-machine-a-etats---statuts)
4. [Priorites et SLA](#4-priorites-et-sla)
5. [Flux de creation d'un signalement](#5-flux-de-creation-dun-signalement)
6. [Flux de traitement](#6-flux-de-traitement)
7. [Systeme d'escalade](#7-systeme-descalade)
8. [Systeme de reponses](#8-systeme-de-reponses)
9. [Recherche et filtrage](#9-recherche-et-filtrage)
10. [Statistiques et tableaux de bord](#10-statistiques-et-tableaux-de-bord)
11. [Permissions et roles](#11-permissions-et-roles)
12. [Evenements domaine](#12-evenements-domaine)
13. [API REST - Endpoints](#13-api-rest---endpoints)
14. [Architecture technique](#14-architecture-technique)
15. [Scenarios de test](#15-scenarios-de-test)
16. [Evolutions futures](#16-evolutions-futures)
17. [References CDC](#17-references-cdc)

---

## 1. VUE D'ENSEMBLE

### Objectif du module

Le module Signalements permet aux equipes terrain de remonter des problemes, incidents ou observations directement depuis le chantier. Chaque signalement suit un cycle de vie structure avec suivi des delais (SLA), escalade automatique et systeme de reponses.

### Flux global simplifie

```
Compagnon detecte un probleme sur chantier
    |
    v
[CREATION] Signalement avec titre, description, priorite, photo, localisation
    |
    v
[OUVERT] --> Le chef de chantier est notifie
    |
    +--> [Assignation] --> [EN_COURS] Le responsable traite
    |                          |
    |                          v
    |                   [TRAITE] avec commentaire obligatoire
    |                          |
    |                          v
    |                   [CLOTURE] Validation finale
    |
    +--> [Escalade automatique si SLA depasse]
         50% temps --> Chef de chantier
         100% temps --> Conducteur de travaux
         200% temps --> Admin
```

### Fonctionnalites couvertes (CDC Section 10)

| ID | Fonctionnalite | Description |
|----|----------------|-------------|
| SIG-01 | Creation signalement | Formulaire complet avec photo et localisation |
| SIG-02 | Consultation detail | Vue detaillee d'un signalement |
| SIG-03 | Liste par chantier | Liste filtrable des signalements |
| SIG-04 | Modification / Assignation | Mise a jour et assignation responsable |
| SIG-05 | Suppression | Suppression (admin/conducteur uniquement) |
| SIG-06 | Photo jointe | URL photo attachee au signalement |
| SIG-07 | Reponses / Commentaires | Fil de discussion avec marquage resolution |
| SIG-08 | Marquage traite | Transition vers TRAITE avec commentaire obligatoire |
| SIG-09 | Cloture | Fermeture definitive du signalement |
| SIG-10 | Recherche plein texte | Recherche dans titre et description |
| SIG-14 | Niveaux de priorite | 4 niveaux avec SLA associe |
| SIG-15 | Date resolution souhaitee | Date limite personnalisable |
| SIG-16 | Detection retards | Alertes visuelles pour signalements en retard |
| SIG-17 | Escalade | Remontee hierarchique automatique selon seuils |
| SIG-18 | Statistiques | Tableau de bord avec KPI |
| SIG-19 | Filtres avances | Par statut, priorite, dates, createur, assigne |
| SIG-20 | Export / Historique | Consultation historique |

---

## 2. ENTITES ET OBJETS METIER

### 2.1 Entite Signalement

**Fichier** : `backend/modules/signalements/domain/entities/signalement.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `chantier_id` | int | Oui | Chantier associe (FK) |
| `titre` | str | Oui | Titre du signalement (non vide apres trim) |
| `description` | str | Oui | Description detaillee (non vide apres trim) |
| `priorite` | Priorite | Non | Niveau de priorite (defaut: MOYENNE) |
| `statut` | StatutSignalement | Auto | Statut courant (defaut: OUVERT) |
| `cree_par` | int | Oui | ID de l'utilisateur createur |
| `assigne_a` | int | Non | ID de l'utilisateur assigne |
| `date_resolution_souhaitee` | datetime | Non | Date limite souhaitee (SIG-15) |
| `date_traitement` | datetime | Auto | Date de passage a TRAITE |
| `date_cloture` | datetime | Auto | Date de cloture |
| `commentaire_traitement` | str | Conditionnel | Commentaire obligatoire au traitement (SIG-08) |
| `photo_url` | str | Non | URL de la photo jointe (SIG-06) |
| `localisation` | str | Non | Localisation sur le chantier |
| `nb_escalades` | int | Auto | Nombre d'escalades effectuees (SIG-16/17) |
| `derniere_escalade_at` | datetime | Auto | Date de derniere escalade |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de derniere modification |

**Proprietes calculees** :

| Propriete | Type | Calcul |
|-----------|------|--------|
| `est_en_retard` | bool | `now > date_limite_traitement` si OUVERT/EN_COURS |
| `date_limite_traitement` | datetime | `date_resolution_souhaitee` si definie, sinon `created_at + priorite.delai_traitement` |
| `pourcentage_temps_ecoule` | float | `(now - created_at) / (date_limite - created_at) * 100` |
| `niveau_escalade_requis` | str | "chef_chantier" / "conducteur" / "admin" selon % |
| `temps_restant` | timedelta | `date_limite - now` (negatif si retard) |
| `temps_restant_formatte` | str | "Xj Yh", "Xh Ymin" ou "En retard de Xh" |

### 2.2 Entite Reponse

**Fichier** : `backend/modules/signalements/domain/entities/reponse.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `signalement_id` | int | Oui | Signalement parent (FK) |
| `contenu` | str | Oui | Texte de la reponse (non vide apres trim) |
| `auteur_id` | int | Oui | ID de l'auteur |
| `photo_url` | str | Non | Photo jointe a la reponse |
| `est_resolution` | bool | Non | Marque la reponse comme resolution (SIG-07) |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |

### 2.3 Value Objects

#### StatutSignalement

**Fichier** : `backend/modules/signalements/domain/value_objects/statut_signalement.py`

| Valeur | Label | Couleur | Icone | Actif | Resolu | Modifiable |
|--------|-------|---------|-------|-------|--------|------------|
| `OUVERT` | "Ouvert" | Rouge | alert-circle | Oui | Non | Oui |
| `EN_COURS` | "En cours" | Orange | clock | Oui | Non | Oui |
| `TRAITE` | "Traite" | Bleu | check | Non | Oui | Oui |
| `CLOTURE` | "Cloture" | Vert | check-circle | Non | Oui | Non |

#### Priorite

**Fichier** : `backend/modules/signalements/domain/value_objects/priorite.py`

| Valeur | Label | SLA | Couleur | Icone |
|--------|-------|-----|---------|-------|
| `CRITIQUE` | "Critique (4h)" | 4 heures | Rouge | - |
| `HAUTE` | "Haute (24h)" | 24 heures | Orange | - |
| `MOYENNE` | "Moyenne (48h)" | 48 heures | Jaune | - |
| `BASSE` | "Basse (72h)" | 72 heures | Vert | - |

---

## 3. MACHINE A ETATS - STATUTS

### 3.1 Diagramme de transitions

```
                    +-----------+
                    |           |
         +--------->  OUVERT   <---------+
         |          |           |         |
         |          +-----+-----+         |
         |                |               |
         |       assigner |               | reouvrir
         |                v               | (exceptionnel,
         |          +-----------+         |  admin only)
         |          |           |         |
         +--------- EN_COURS   |         |
         reouvrir   |           |         |
                    +-----+-----+         |
                          |               |
              marquer_traite              |
              (commentaire                |
               obligatoire)               |
                          v               |
                    +-----------+         |
                    |           |---------+
                    |  TRAITE   |  reouvrir
                    |           |
                    +-----+-----+
                          |
                    cloturer
                    (chef+/admin)
                          v
                    +-----------+
                    |           |
                    |  CLOTURE  |----> reouvrir (admin/conducteur only)
                    |           |      ---> retour OUVERT
                    +-----------+
```

### 3.2 Regles de transition

| Depuis | Vers | Condition | Action declenchee |
|--------|------|-----------|-------------------|
| OUVERT | EN_COURS | `assigner(user_id)` | Assignation automatique, notif |
| OUVERT | TRAITE | `marquer_traite(commentaire)` | Commentaire requis |
| EN_COURS | TRAITE | `marquer_traite(commentaire)` | Commentaire requis, date_traitement |
| EN_COURS | OUVERT | `reouvrir()` | Reset assignation |
| TRAITE | CLOTURE | `cloturer()` | date_cloture, role chef+ requis |
| TRAITE | OUVERT | `reouvrir()` | Reset exceptionnel |
| CLOTURE | OUVERT | `reouvrir()` | Role admin/conducteur uniquement |

### 3.3 Contraintes metier

- **Commentaire obligatoire** : Le passage a TRAITE exige un `commentaire_traitement` non vide
- **Pas de saut** : EN_COURS ne peut pas passer directement a CLOTURE (doit passer par TRAITE)
- **Reopening** : Un signalement CLOTURE ne peut etre rouvert que par admin/conducteur
- **Modification** : Un signalement CLOTURE ne peut plus etre modifie

---

## 4. PRIORITES ET SLA

### 4.1 Delais contractuels

Le SLA (Service Level Agreement) definit le temps maximum entre la creation du signalement et son traitement :

```
CRITIQUE  ----[4h]-------> Traitement attendu
HAUTE     --------[24h]----------> Traitement attendu
MOYENNE   ----------------[48h]-----------------> Traitement attendu (defaut)
BASSE     ----------------------------[72h]--------------------> Traitement attendu
```

### 4.2 Calcul de la date limite

```python
# Regle de calcul :
if date_resolution_souhaitee is not None:
    date_limite = date_resolution_souhaitee  # SIG-15 : priorite a la date manuelle
else:
    date_limite = created_at + priorite.delai_traitement
```

**Explication** : Si un chef de chantier definit explicitement une date de resolution (SIG-15), celle-ci prevaut sur le SLA automatique. Sinon, le delai est calcule a partir de la priorite.

### 4.3 Pourcentage de temps ecoule

```python
pourcentage = (now - created_at) / (date_limite - created_at) * 100

# Exemples pour un signalement CRITIQUE cree a 08:00 :
# - 09:00 (1h ecoulee) : 25%
# - 10:00 (2h ecoulee) : 50%  --> Alerte chef
# - 12:00 (4h ecoulee) : 100% --> Escalade conducteur
# - 16:00 (8h ecoulee) : 200% --> Escalade admin
```

### 4.4 Affichage du temps restant

| Condition | Format | Exemple |
|-----------|--------|---------|
| Restant > 1 jour | "Xj Yh" | "2j 5h" |
| Restant < 1 jour | "Xh Ymin" | "3h 45min" |
| Retard | "En retard de Xh" | "En retard de 2h" |
| Plus de retard | "En retard de Xj Yh" | "En retard de 1j 8h" |

---

## 5. FLUX DE CREATION D'UN SIGNALEMENT

### 5.1 Diagramme de sequence

```
Compagnon              Frontend              Backend              BDD
    |                      |                     |                  |
    |  Detecte probleme    |                     |                  |
    |  Ouvre formulaire    |                     |                  |
    |--------------------->|                     |                  |
    |                      |                     |                  |
    |  Remplit :           |                     |                  |
    |  - Chantier (auto)   |                     |                  |
    |  - Titre             |                     |                  |
    |  - Description       |                     |                  |
    |  - Priorite          |                     |                  |
    |  - Photo (optionnel) |                     |                  |
    |  - Localisation      |                     |                  |
    |--------------------->|                     |                  |
    |                      |                     |                  |
    |                      | POST /signalements  |                  |
    |                      |-------------------->|                  |
    |                      |                     | Validation       |
    |                      |                     | titre non vide   |
    |                      |                     | description non  |
    |                      |                     | vide             |
    |                      |                     |----------------->|
    |                      |                     |  INSERT          |
    |                      |                     |<-----------------|
    |                      |                     |                  |
    |                      |                     | Publish:         |
    |                      |                     | SignalementCreated|
    |                      |                     | Event            |
    |                      |<--------------------|                  |
    |                      | SignalementDTO      |                  |
    |<---------------------|                     |                  |
    |  Confirmation        |                     |                  |
```

### 5.2 Donnees du formulaire de creation

```typescript
interface SignalementCreateDTO {
  chantier_id: number       // Requis - chantier actif du compagnon
  titre: string             // Requis - titre court du probleme
  description: string       // Requis - description detaillee
  priorite?: string         // Optionnel - defaut "moyenne"
  assigne_a?: number        // Optionnel - assignation immediate
  date_resolution_souhaitee?: string  // Optionnel - date ISO (SIG-15)
  photo_url?: string        // Optionnel - URL de la photo (SIG-06)
  localisation?: string     // Optionnel - zone sur le chantier
}
```

### 5.3 Validations

| Champ | Regle | Message erreur |
|-------|-------|----------------|
| `titre` | Non vide apres trim | "Le titre est obligatoire" |
| `description` | Non vide apres trim | "La description est obligatoire" |
| `chantier_id` | Chantier existant | "Chantier introuvable" |
| `priorite` | Valeur enum valide | "Priorite invalide" |
| `assigne_a` | Utilisateur existant (si fourni) | "Utilisateur introuvable" |

---

## 6. FLUX DE TRAITEMENT

### 6.1 Assignation (OUVERT --> EN_COURS)

```
Chef/Conducteur/Admin
    |
    | POST /signalements/{id}/assigner?assigne_a=42
    |
    v
Backend :
    1. Verifie que le signalement existe
    2. Verifie le role (chef_chantier / conducteur / admin)
    3. Appelle signalement.assigner(user_id)
        -> statut passe de OUVERT a EN_COURS
        -> assigne_a = user_id
    4. Sauvegarde en BDD
    5. Publie SignalementAssigned event
    |
    v
Resultat : Le responsable est assigne, SLA continue de courir
```

### 6.2 Marquage traite (EN_COURS --> TRAITE)

```
Responsable/Chef/Admin
    |
    | POST /signalements/{id}/traiter
    | Body: { "commentaire": "Fuite reparee, joint remplace" }
    |
    v
Backend :
    1. Verifie que le signalement existe
    2. Verifie le role (chef_chantier / conducteur / admin)
    3. Verifie que le commentaire est non vide
    4. Appelle signalement.marquer_traite(commentaire)
        -> statut passe a TRAITE
        -> date_traitement = now
        -> commentaire_traitement = commentaire
    5. Sauvegarde en BDD
    6. Publie SignalementStatusChanged event
    |
    v
Resultat : Le signalement est marque comme traite, en attente de cloture
```

**Regle metier** : Le commentaire de traitement est **obligatoire**. Il explique ce qui a ete fait pour resoudre le probleme. C'est la trace de la resolution.

### 6.3 Cloture (TRAITE --> CLOTURE)

```
Chef/Conducteur/Admin
    |
    | POST /signalements/{id}/cloturer
    |
    v
Backend :
    1. Verifie que le signalement est en statut TRAITE
    2. Verifie le role (chef_chantier / conducteur / admin)
    3. Appelle signalement.cloturer()
        -> statut passe a CLOTURE
        -> date_cloture = now
    4. Sauvegarde en BDD
    5. Publie SignalementClosedEvent
    |
    v
Resultat : Le signalement est definitivement ferme
           Plus modifiable (sauf reopening exceptionnel)
```

### 6.4 Reouverture (CLOTURE --> OUVERT)

```
Admin/Conducteur uniquement
    |
    | POST /signalements/{id}/reouvrir
    |
    v
Backend :
    1. Verifie que le signalement est en statut CLOTURE (ou TRAITE)
    2. Verifie le role (admin / conducteur uniquement)
    3. Appelle signalement.reouvrir()
        -> statut revient a OUVERT
        -> Reset : le SLA ne repart pas (created_at inchange)
    4. Sauvegarde en BDD
    |
    v
Resultat : Le signalement est rouvert pour re-traitement
           Cas d'usage : probleme non resolu, recidive
```

---

## 7. SYSTEME D'ESCALADE

### 7.1 Principe

**Fichier** : `backend/modules/signalements/domain/services/escalade_service.py`

L'escalade est **lazy** (evaluee paresseusement) : elle est calculee a chaque consultation du signalement, pas par un cron periodique. Le `pourcentage_temps_ecoule` est recalcule en temps reel.

### 7.2 Seuils d'escalade

```
Temps ecoule    Action                          Destinataire
  0%  -------- Creation ----------------------- Createur
 50%  -------- Alerte 1er niveau --------------- Chef de chantier
100%  -------- Escalade 2eme niveau ------------ Conducteur de travaux
200%  -------- Escalade critique --------------- Admin
```

### 7.3 Exemple concret

```
Signalement HAUTE priorite (SLA = 24h) cree le Lundi 08:00

Lundi 20:00 (12h = 50%)
  --> Indicateur visuel ORANGE dans l'interface
  --> niveau_escalade_requis = "chef_chantier"
  --> Le chef de chantier voit une alerte

Mardi 08:00 (24h = 100%)
  --> Indicateur visuel ROUGE
  --> niveau_escalade_requis = "conducteur"
  --> Le conducteur de travaux est alerte

Mercredi 08:00 (48h = 200%)
  --> Indicateur visuel ROUGE FONCE / CLIGNOTANT
  --> niveau_escalade_requis = "admin"
  --> L'administrateur est alerte
  --> nb_escalades incremente
```

### 7.4 Service d'escalade

```python
class EscaladeService:
    """Evalue les escalades pour une liste de signalements."""

    SEUILS = {
        "chef_chantier": 50.0,
        "conducteur": 100.0,
        "admin": 200.0
    }

    def determiner_escalades(signalements) -> List[EscaladeInfo]:
        """Retourne la liste des signalements necessitant une escalade."""

    def calculer_prochaine_escalade(signalement) -> (niveau, datetime):
        """Calcule quand la prochaine escalade aura lieu."""

    def generer_message_escalade(escalade, chantier_nom) -> str:
        """Genere un message d'alerte pour l'escalade."""

    def get_statistiques_escalade(signalements) -> dict:
        """Statistiques d'escalade : total, par niveau, taux."""
```

**EscaladeInfo** (dataclass) :

| Champ | Type | Description |
|-------|------|-------------|
| `signalement` | Signalement | Le signalement concerne |
| `niveau` | str | "chef_chantier" / "conducteur" / "admin" |
| `pourcentage_temps` | float | Pourcentage de temps ecoule |
| `destinataires_roles` | List[str] | Roles qui doivent etre alertes |

### 7.5 Implementation actuelle vs. evolution prevue

| Aspect | Actuel | Evolution prevue |
|--------|--------|-----------------|
| **Declenchement** | Lazy (calcul a la consultation) | Cron periodique (toutes les 15min) |
| **Notification** | Indicateur visuel dans l'UI | Push notification + email |
| **Historique** | `nb_escalades` + `derniere_escalade_at` | Table `escalades` dediee |
| **Acquittement** | Pas d'acquittement | Bouton "J'ai vu" |

> **Note** : L'implementation actuelle est fonctionnelle pour un usage quotidien.
> L'escalade est visible dans l'interface (indicateurs visuels colores) et les statistiques.
> Le passage a un systeme proactif (cron + push) est prevu en phase 2.

---

## 8. SYSTEME DE REPONSES

### 8.1 Fil de discussion (SIG-07)

Chaque signalement dispose d'un fil de discussion permettant aux differents intervenants de communiquer.

```
Signalement #42 "Fuite toiture batiment B"
    |
    +-- Reponse 1 (Compagnon) : "La fuite est au niveau du joint de dilatation"
    |   [Photo jointe]
    |
    +-- Reponse 2 (Chef) : "Equipe etancheite prevue demain matin"
    |
    +-- Reponse 3 (Chef) : "Reparation effectuee, joint remplace"
    |   [Marquee comme RESOLUTION]  <-- est_resolution = true
    |
    +-- Reponse 4 (Conducteur) : "Validation OK, cloture"
```

### 8.2 Reponse de resolution

Une reponse peut etre marquee comme **resolution** (`est_resolution = true`). Cette reponse est celle qui decrit la solution apportee au probleme. Il n'y a qu'une seule reponse de resolution attendue par signalement.

Le repository expose la methode `find_resolution(signalement_id)` pour retrouver directement la reponse de resolution.

### 8.3 Endpoints reponses

| Methode | Path | Description |
|---------|------|-------------|
| POST | `/signalements/{id}/reponses` | Ajouter une reponse |
| GET | `/signalements/{id}/reponses` | Lister les reponses (paginee) |
| PUT | `/signalements/reponses/{id}` | Modifier une reponse |
| DELETE | `/signalements/reponses/{id}` | Supprimer une reponse |

### 8.4 Permissions sur les reponses

| Action | Admin/Conducteur | Chef chantier | Compagnon |
|--------|------------------|---------------|-----------|
| Creer | Oui | Oui | Oui |
| Modifier | Toutes | Les siennes | Les siennes |
| Supprimer | Toutes | Les siennes | Les siennes |
| Marquer resolution | Oui | Oui | Non |

---

## 9. RECHERCHE ET FILTRAGE

### 9.1 Recherche plein texte (SIG-10)

La recherche s'effectue sur le **titre** et la **description** du signalement. Le backend utilise une requete SQL LIKE/ILIKE pour la correspondance.

```
GET /signalements?query=fuite+toiture
```

### 9.2 Filtres disponibles (SIG-19, SIG-20)

```typescript
interface SignalementSearchParams {
  query?: string              // Texte libre (titre, description)
  chantier_id?: number        // Filtre par chantier
  chantier_ids?: number[]     // Filtre par plusieurs chantiers
  statut?: string             // OUVERT, EN_COURS, TRAITE, CLOTURE
  priorite?: string           // CRITIQUE, HAUTE, MOYENNE, BASSE
  date_debut?: string         // Date creation >= (ISO)
  date_fin?: string           // Date creation <= (ISO)
  cree_par?: number           // Filtre par createur
  assigne_a?: number          // Filtre par responsable assigne
  en_retard_only?: boolean    // Uniquement les signalements en retard
  skip?: number               // Pagination - offset
  limit?: number              // Pagination - limit
}
```

### 9.3 Tri par defaut

Les signalements sont tries par :
1. **Priorite** (critique en premier) via un `CASE WHEN` SQL
2. **Date de creation** (plus recent en premier) en secondaire

### 9.4 Alertes retard (SIG-16)

Un endpoint dedie retourne les signalements en retard :

```
GET /signalements/alertes/en-retard?chantier_id=1
```

Le filtre `en_retard_only=true` dans la recherche permet aussi de les retrouver.

---

## 10. STATISTIQUES ET TABLEAUX DE BORD

### 10.1 Endpoint statistiques (SIG-18)

```
GET /signalements/stats/global?chantier_id=1&date_debut=2026-01-01&date_fin=2026-01-31
```

### 10.2 Donnees retournees

```typescript
interface SignalementStatsResponse {
  total: number              // Nombre total de signalements
  par_statut: {              // Repartition par statut
    ouvert: number
    en_cours: number
    traite: number
    cloture: number
  }
  par_priorite: {            // Repartition par priorite
    critique: number
    haute: number
    moyenne: number
    basse: number
  }
  en_retard: number          // Nombre en retard (SLA depasse)
  traites_cette_semaine: number  // Signalements traites cette semaine
  temps_moyen_resolution: number | null  // En heures (moyenne)
  taux_resolution: number    // Pourcentage (0-100)
}
```

### 10.3 Composant frontend

**Fichier** : `frontend/src/components/signalements/SignalementStats.tsx`

Le tableau de bord affiche :
- **Compteurs** : Total, ouverts, en cours, en retard
- **Repartition par priorite** : Barres colorees
- **Repartition par statut** : Camembert ou barres
- **KPI** : Taux de resolution, temps moyen de resolution
- **Tendance** : Signalements traites cette semaine

---

## 11. PERMISSIONS ET ROLES

### 11.1 Matrice de permissions

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|-----------|---------------|-----------|
| Creer signalement | Tous chantiers | Tous chantiers | Ses chantiers | Ses chantiers |
| Voir signalement | Tous | Tous | Ses chantiers | Les siens |
| Modifier signalement | Tous | Tous | Ses chantiers | Les siens (non clos) |
| Supprimer signalement | Oui | Oui | Non | Non |
| Assigner responsable | Oui | Oui | Ses chantiers | Non |
| Marquer traite | Oui | Oui | Ses chantiers | Non |
| Cloturer | Oui | Oui | Ses chantiers | Non |
| Reouvrir (depuis CLOTURE) | Oui | Oui | Non | Non |
| Voir statistiques | Tous | Tous | Ses chantiers | Non |

### 11.2 Regles de verification

```python
def peut_modifier(user_id: int, user_role: str) -> bool:
    """Un signalement peut etre modifie par :
    - L'admin ou le conducteur (toujours)
    - Le chef de chantier (son perimetre)
    - Le createur (si statut != CLOTURE)
    """
    if user_role in ('admin', 'conducteur'):
        return True
    if user_role == 'chef_chantier':
        return True  # + verification perimetre dans le use case
    return user_id == self.cree_par and self.statut != StatutSignalement.CLOTURE

def peut_cloturer(user_role: str) -> bool:
    """Seuls admin, conducteur et chef de chantier peuvent cloturer."""
    return user_role in ('admin', 'conducteur', 'chef_chantier')
```

---

## 12. EVENEMENTS DOMAINE

### 12.1 Liste des evenements

**Fichier** : `backend/modules/signalements/domain/events/signalement_events.py`

| Evenement | Declencheur | Donnees |
|-----------|-------------|---------|
| `SignalementCreated` | Creation | signalement_id, chantier_id, titre, priorite, cree_par |
| `SignalementUpdated` | Modification | signalement_id, chantier_id, updated_by, changes |
| `SignalementAssigned` | Assignation | signalement_id, chantier_id, assigne_a, assigned_by |
| `SignalementStatusChanged` | Changement statut | signalement_id, ancien_statut, nouveau_statut, changed_by, commentaire |
| `SignalementEscalated` | Escalade | signalement_id, niveau_escalade, pourcentage_temps, destinataires |
| `ReponseAdded` | Nouvelle reponse | reponse_id, signalement_id, auteur_id, est_resolution |

### 12.2 DomainEvent (extends shared)

| Classe | Type d'evenement |
|--------|-----------------|
| `SignalementCreatedEvent` | "signalement.created" |
| `SignalementUpdatedEvent` | "signalement.updated" |
| `SignalementClosedEvent` | "signalement.closed" |

### 12.3 Publication

L'evenement `SignalementCreatedEvent` est publie apres le commit en base dans le endpoint de creation (`signalement_routes.py`). Les autres evenements sont prepares mais leur publication depend de l'integration avec le bus d'evenements global.

---

## 13. API REST - ENDPOINTS

### 13.1 Signalements

**Router** : `/signalements`

| Methode | Path | Body/Query | Reponse | Feature |
|---------|------|------------|---------|---------|
| POST | `/` | SignalementCreateRequest | 201 SignalementResponse | SIG-01 |
| GET | `/{id}` | - | SignalementResponse | SIG-02 |
| GET | `/chantier/{chantier_id}` | ?skip, limit, statut, priorite | SignalementListResponse | SIG-03 |
| GET | `/` | ?query, chantier_id, statut, priorite, dates, en_retard_only | SignalementListResponse | SIG-10/19/20 |
| PUT | `/{id}` | SignalementUpdateRequest | SignalementResponse | SIG-04 |
| DELETE | `/{id}` | - | 204 No Content | SIG-05 |
| POST | `/{id}/assigner` | ?assigne_a | SignalementResponse | SIG-04 |
| POST | `/{id}/traiter` | MarquerTraiteRequest | SignalementResponse | SIG-08 |
| POST | `/{id}/cloturer` | - | SignalementResponse | SIG-09 |
| POST | `/{id}/reouvrir` | - | SignalementResponse | - |
| GET | `/stats/global` | ?chantier_id, date_debut, date_fin | SignalementStatsResponse | SIG-18 |
| GET | `/alertes/en-retard` | ?chantier_id, skip, limit | SignalementListResponse | SIG-16 |

### 13.2 Reponses

| Methode | Path | Body/Query | Reponse | Feature |
|---------|------|------------|---------|---------|
| POST | `/{id}/reponses` | ReponseCreateRequest | ReponseResponse | SIG-07 |
| GET | `/{id}/reponses` | ?skip, limit | ReponseListResponse | SIG-07 |
| PUT | `/reponses/{id}` | ReponseUpdateRequest | ReponseResponse | - |
| DELETE | `/reponses/{id}` | - | 204 No Content | - |

### 13.3 Schemas Pydantic

**SignalementCreateRequest** :
```python
{
    "chantier_id": int,
    "titre": str,
    "description": str,
    "priorite": Optional[str],        # default "moyenne"
    "assigne_a": Optional[int],
    "date_resolution_souhaitee": Optional[datetime],
    "photo_url": Optional[str],
    "localisation": Optional[str]
}
```

**MarquerTraiteRequest** :
```python
{
    "commentaire": str  # Obligatoire, non vide
}
```

**SignalementResponse** (enrichi) :
```python
{
    "id": int,
    "chantier_id": int,
    "titre": str,
    "description": str,
    "priorite": str, "priorite_label": str, "priorite_couleur": str,
    "statut": str, "statut_label": str, "statut_couleur": str,
    "cree_par": int, "cree_par_nom": str,
    "assigne_a": Optional[int], "assigne_a_nom": Optional[str],
    "date_resolution_souhaitee": Optional[datetime],
    "date_traitement": Optional[datetime],
    "date_cloture": Optional[datetime],
    "commentaire_traitement": Optional[str],
    "photo_url": Optional[str],
    "localisation": Optional[str],
    "created_at": datetime,
    "updated_at": datetime,
    "est_en_retard": bool,
    "temps_restant": Optional[str],
    "pourcentage_temps": float,
    "nb_reponses": int,
    "nb_escalades": int
}
```

---

## 14. ARCHITECTURE TECHNIQUE

### 14.1 Structure des fichiers

```
backend/modules/signalements/
|
+-- domain/
|   +-- entities/
|   |   +-- signalement.py          # Entite principale
|   |   +-- reponse.py              # Entite reponse
|   +-- value_objects/
|   |   +-- statut_signalement.py   # Enum statuts + transitions
|   |   +-- priorite.py             # Enum priorites + SLA
|   +-- repositories/
|   |   +-- signalement_repository.py  # Interface abstraite
|   |   +-- reponse_repository.py      # Interface abstraite
|   +-- services/
|   |   +-- escalade_service.py     # Logique d'escalade
|   +-- events/
|       +-- signalement_events.py   # Dataclass events
|       +-- signalement_created.py  # DomainEvent
|       +-- signalement_updated.py  # DomainEvent
|       +-- signalement_closed.py   # DomainEvent
|
+-- application/
|   +-- use_cases/
|   |   +-- signalement_use_cases.py  # 12 use cases signalements
|   |   +-- reponse_use_cases.py      # 4 use cases reponses
|   +-- dtos/
|       +-- signalement_dtos.py       # 7 DTOs signalements
|       +-- reponse_dtos.py           # 5 DTOs reponses
|
+-- adapters/
|   +-- controllers/
|       +-- signalement_controller.py # Orchestrateur (16 methodes)
|
+-- infrastructure/
    +-- persistence/
    |   +-- models.py                 # SQLAlchemy models
    |   +-- sqlalchemy_signalement_repository.py
    |   +-- sqlalchemy_reponse_repository.py
    +-- web/
        +-- signalement_routes.py     # FastAPI router
        +-- dependencies.py           # Injection de dependances
```

### 14.2 Tables base de donnees

**Table `signalements`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| chantier_id | INTEGER | FK chantiers, CASCADE |
| titre | VARCHAR | NOT NULL |
| description | TEXT | NOT NULL |
| priorite | ENUM | NOT NULL |
| statut | ENUM | NOT NULL |
| cree_par | INTEGER | FK users |
| assigne_a | INTEGER | FK users, nullable |
| date_resolution_souhaitee | DATETIME | nullable |
| date_traitement | DATETIME | nullable |
| date_cloture | DATETIME | nullable |
| commentaire_traitement | TEXT | nullable |
| photo_url | VARCHAR | nullable |
| localisation | VARCHAR | nullable |
| nb_escalades | INTEGER | default 0 |
| derniere_escalade_at | DATETIME | nullable |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes : `chantier_id`, `cree_par`, `assigne_a`

**Table `reponses_signalements`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| signalement_id | INTEGER | FK signalements, CASCADE |
| contenu | TEXT | NOT NULL |
| auteur_id | INTEGER | FK users |
| photo_url | VARCHAR | nullable |
| est_resolution | BOOLEAN | default false |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes : `signalement_id`, `auteur_id`

> Note : La suppression d'un signalement supprime en cascade toutes ses reponses.

### 14.3 Frontend - Composants

**Fichier** : `frontend/src/components/signalements/`

| Composant | Responsabilite |
|-----------|---------------|
| `SignalementList.tsx` | Liste avec filtres et pagination |
| `SignalementCard.tsx` | Carte individuelle (priorite, statut, temps) |
| `SignalementModal.tsx` | Creation / modification |
| `SignalementDetail.tsx` | Vue detaillee complete |
| `SignalementFilters.tsx` | Barre de filtres (statut, priorite, recherche, dates) |
| `SignalementStats.tsx` | Tableau de bord statistiques |
| `TraiterModal.tsx` | Modal de traitement (commentaire obligatoire) |
| `ReponsesSection.tsx` | Fil de discussion avec reponses |

**Services** : `frontend/src/services/signalements.ts` (14 fonctions API)

**Types** : `frontend/src/types/signalements.ts` (interfaces + constantes couleurs/labels)

---

## 15. SCENARIOS DE TEST

### Scenario 1 : Cycle de vie complet

```
GIVEN un compagnon "Carlos DE OLIVEIRA COVAS" affecte au chantier "Villa Duplex"
WHEN il cree un signalement "Fuite toiture batiment B" avec priorite HAUTE
THEN le signalement est cree en statut OUVERT
AND le SLA est de 24h

WHEN le chef de chantier assigne le signalement a "Sebastien ACHKAR"
THEN le statut passe a EN_COURS

WHEN Sebastien marque le signalement comme traite avec "Joint remplace"
THEN le statut passe a TRAITE
AND date_traitement est renseignee
AND commentaire_traitement = "Joint remplace"

WHEN le conducteur cloture le signalement
THEN le statut passe a CLOTURE
AND date_cloture est renseignee
```

### Scenario 2 : Escalade automatique

```
GIVEN un signalement CRITIQUE (SLA 4h) cree a 08:00
WHEN on consulte a 10:00 (2h = 50%)
THEN pourcentage_temps_ecoule = 50
AND niveau_escalade_requis = "chef_chantier"
AND indicateur visuel ORANGE

WHEN on consulte a 12:00 (4h = 100%)
THEN pourcentage_temps_ecoule = 100
AND niveau_escalade_requis = "conducteur"
AND est_en_retard = true
AND indicateur visuel ROUGE

WHEN on consulte a 16:00 (8h = 200%)
THEN pourcentage_temps_ecoule = 200
AND niveau_escalade_requis = "admin"
AND indicateur visuel ROUGE FONCE
```

### Scenario 3 : Date resolution souhaitee (SIG-15)

```
GIVEN un signalement priorite BASSE (SLA theorique 72h)
WHEN le chef definit date_resolution_souhaitee = demain 17:00
THEN la date limite = demain 17:00 (pas 72h)
AND le SLA effectif est reduit
AND les seuils d'escalade sont recalcules sur cette date
```

### Scenario 4 : Fil de reponses

```
GIVEN un signalement ouvert #42
WHEN un compagnon ajoute une reponse avec photo
THEN nb_reponses incremente a 1

WHEN le chef ajoute une reponse marquee "resolution"
THEN la reponse est stockee avec est_resolution = true

WHEN on demande find_resolution(42)
THEN on obtient la reponse du chef
```

### Scenario 5 : Traitement sans commentaire (erreur)

```
GIVEN un signalement EN_COURS
WHEN on tente POST /signalements/{id}/traiter avec commentaire vide
THEN HTTP 400 Bad Request
AND le statut reste EN_COURS
```

### Scenario 6 : Suppression (permission)

```
GIVEN un signalement cree par un compagnon
WHEN le compagnon tente DELETE /signalements/{id}
THEN HTTP 403 Forbidden (seuls admin/conducteur peuvent supprimer)

WHEN un admin tente DELETE /signalements/{id}
THEN HTTP 204 No Content
AND toutes les reponses associees sont supprimees en cascade
```

### Scenario 7 : Recherche et filtres

```
GIVEN 10 signalements dont 3 en retard et 2 priorite CRITIQUE
WHEN on cherche GET /signalements?en_retard_only=true
THEN on obtient les 3 signalements en retard

WHEN on cherche GET /signalements?priorite=critique&statut=ouvert
THEN on obtient les signalements CRITIQUE et OUVERTS
AND ils sont tries par priorite puis date (plus recent d'abord)
```

---

## 16. EVOLUTIONS FUTURES

| Evolution | Description | Impact |
|-----------|-------------|--------|
| **Escalade proactive** | Cron toutes les 15min + push notifications | Necessiterait un service de notifications |
| **Escalade par email** | Notification email aux responsables | Integration SMTP |
| **Acquittement escalade** | Bouton "J'ai vu" pour acquitter l'alerte | Nouveau champ + UI |
| **Geolocalisation** | Coordonnees GPS + carte | Integration map |
| **Photos multiples** | Plusieurs photos par signalement | Champ `photo_urls[]` ou table dediee |
| **Modeles de signalement** | Templates pre-remplis par type (securite, qualite) | Nouvelle entite template |
| **Export PDF** | Generation de rapport PDF | Integration PDF |
| **Soft delete** | Suppression logique au lieu de physique | Ajout `deleted_at` |
| **Historique modifications** | Audit trail des changements | Table `signalement_history` |
| **Notifications in-app** | Toast temps reel sur changement de statut | Integration WebSocket |

---

## 17. REFERENCES CDC

| Section CDC | Description | Fonctionnalites |
|-------------|-------------|-----------------|
| Section 10 | Signalements terrain | SIG-01 a SIG-20 |
| Section 3 | Gestion utilisateurs | Roles et permissions |
| Section 4 | Gestion chantiers | `chantier_id` FK |
| Section 2 | Dashboard | Compteurs signalements |

### Fichiers sources principaux

| Fichier | Lignes | Role |
|---------|--------|------|
| `backend/modules/signalements/domain/entities/signalement.py` | ~200 | Entite + logique metier |
| `backend/modules/signalements/domain/entities/reponse.py` | ~60 | Entite reponse |
| `backend/modules/signalements/domain/value_objects/statut_signalement.py` | ~80 | Machine a etats |
| `backend/modules/signalements/domain/value_objects/priorite.py` | ~50 | SLA |
| `backend/modules/signalements/domain/services/escalade_service.py` | ~100 | Escalade |
| `backend/modules/signalements/application/use_cases/signalement_use_cases.py` | ~300 | 12 use cases |
| `backend/modules/signalements/application/use_cases/reponse_use_cases.py` | ~100 | 4 use cases |
| `backend/modules/signalements/infrastructure/web/signalement_routes.py` | ~250 | Routes API |
| `frontend/src/types/signalements.ts` | ~100 | Types TS |
| `frontend/src/services/signalements.ts` | ~150 | Client API |
| `frontend/src/components/signalements/` | 8 composants | UI |

---

**Document genere automatiquement par analyse du code source.**
**Dernier audit : 30 janvier 2026**

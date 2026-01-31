# Workflow Gestion Financiere et Budgetaire - Hub Chantier

> Document cree le 31 janvier 2026
> Specification complete du workflow financier (module 17 - CDC Section 17)
> Statut : SPECS READY — implementation a venir

---

## TABLE DES MATIERES

1. [Vue d'ensemble](#1-vue-densemble)
2. [Entites et objets metier](#2-entites-et-objets-metier)
3. [Machine a etats - Achats](#3-machine-a-etats---achats)
4. [Machine a etats - Situations de travaux](#4-machine-a-etats---situations-de-travaux)
5. [Flux Budget](#5-flux-budget)
6. [Flux Achats et bons de commande](#6-flux-achats-et-bons-de-commande)
7. [Flux Situations de travaux](#7-flux-situations-de-travaux)
8. [Flux Avenants budgetaires](#8-flux-avenants-budgetaires)
9. [Integration couts automatiques](#9-integration-couts-automatiques)
10. [Tableau de bord financier](#10-tableau-de-bord-financier)
11. [Alertes et notifications](#11-alertes-et-notifications)
12. [Referentiel fournisseurs](#12-referentiel-fournisseurs)
13. [Export comptable](#13-export-comptable)
14. [Permissions et roles](#14-permissions-et-roles)
15. [Evenements domaine](#15-evenements-domaine)
16. [API REST - Endpoints](#16-api-rest---endpoints)
17. [Architecture technique](#17-architecture-technique)
18. [Scenarios de test](#18-scenarios-de-test)
19. [Evolutions futures](#19-evolutions-futures)
20. [References CDC](#20-references-cdc)

---

## 1. VUE D'ENSEMBLE

### Objectif du module

Le module Financier centralise le suivi economique des chantiers de Greg Construction. Il permet de :
- Definir et suivre les budgets previsionnels par lots
- Gerer les achats fournisseurs avec workflow de validation
- Produire les situations de travaux mensuelles (base de facturation)
- Visualiser la sante financiere de chaque chantier en temps reel
- Alerter automatiquement en cas de depassement budgetaire

### Contexte Greg Construction

- 20 employes, 4.3M EUR CA annuel
- 4-6 chantiers simultanes (gros oeuvre)
- Devise unique : EUR
- Comptabilite externalisee (export CSV vers comptable)
- Pas d'ERP integre (saisie manuelle, pas d'import PDF)

### Flux global simplifie

```
Admin/Conducteur cree le budget du chantier (par lots)
    |
    v
Chef/Conducteur cree des demandes d'achat
    |
    v
[DEMANDE] --> Montant >= seuil ?
    |                |
    NON              OUI
    |                |
    v                v
[VALIDE]     Conducteur/Admin valide
(auto)              |
    |          +----+----+
    |          |         |
    v       VALIDE    REFUSE
    |          |      (+ motif)
    v          v
Commande fournisseur
    |
    v
Livraison → [LIVRE]
    |
    v
Facture fournisseur → [FACTURE] (definitif)
    |
    v
Imputation sur lot budgetaire (Realise += montant)
    |
    v
Dashboard KPI mis a jour automatiquement
```

### Flux situations de travaux

```
Conducteur prepare la situation mensuelle
    |
    v
[BROUILLON] --> Saisie avancement par lot
    |
    v
Admin/Direction valide
    |
    +-- [EN_VALIDATION] --> OK ? --> [EMISE] --> PDF genere + envoi client
    |                        |
    |                       NON --> Retour BROUILLON
    |
    v
Client valide --> [VALIDEE]
    |
    v
Admin cree facture --> [FACTUREE] (definitif)
```

### Fonctionnalites couvertes (CDC Section 17)

| ID | Fonctionnalite | Description |
|----|----------------|-------------|
| FIN-01 | Onglet Budget par chantier | Accessible depuis la fiche chantier |
| FIN-02 | Budget previsionnel par lots | Decomposition arborescente code lot / libelle / unite / PU |
| FIN-03 | Affectation budgets aux taches | Liaison taches <-> lignes budgetaires |
| FIN-04 | Avenants budgetaires | Modification contractuelle avec impact budget revise |
| FIN-05 | Saisie achats / bons de commande | Creation avec fournisseur, lot, montant HT/TTC |
| FIN-06 | Validation hierarchique achats | Approbation si montant > seuil configurable |
| FIN-07 | Situations de travaux | Workflow 5 etapes, generation PDF |
| FIN-08 | Facturation client | Factures/acomptes depuis situations validees |
| FIN-09 | Suivi couts main-d'oeuvre | Integration heures validees x taux horaire |
| FIN-10 | Suivi couts materiel | Integration reservations logistique x tarif |
| FIN-11 | Tableau de bord financier | KPI + graphiques Budget/Engage/Realise |
| FIN-12 | Alertes depassements | Notifications push sur seuils configurables |
| FIN-13 | Export comptable | CSV avec codes analytiques chantier |
| FIN-14 | Referentiel fournisseurs | CRUD fournisseurs (raison sociale, SIRET, type) |
| FIN-15 | Historique et tracabilite | Journal modifications budgetaires |

---

## 2. ENTITES ET OBJETS METIER

### 2.1 Entite Budget

**Fichier prevu** : `backend/modules/financier/domain/entities/budget.py`

Un budget est le conteneur financier d'un chantier. Il regroupe les lignes budgetaires (lots).

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `chantier_id` | int | Oui | FK vers chantier (1 budget par chantier) |
| `montant_initial_ht` | Decimal | Calcule | Somme des lignes budgetaires |
| `montant_avenants_ht` | Decimal | Calcule | Somme des avenants |
| `montant_revise_ht` | Decimal | Calcule | Initial + Avenants |
| `retenue_garantie_pct` | Decimal | Oui | 0%, 5% ou 10% (defaut 5%) |
| `seuil_alerte_pct` | Decimal | Oui | Seuil alerte depassement (defaut 110%) |
| `seuil_validation_achat` | Decimal | Oui | Montant HT declenchant validation (defaut 5000) |
| `created_by` | int | Oui | FK vers utilisateur createur |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |

**Proprietes calculees** :

| Propriete | Formule | Description |
|-----------|---------|-------------|
| `total_engage` | Somme achats valides/commandes/livres/factures | Total engage |
| `total_realise` | Somme achats factures + couts MO + couts materiel | Total realise |
| `reste_a_faire` | montant_revise_ht - total_realise | Reste a depenser |
| `ecart` | total_realise - montant_revise_ht | Positif = depassement |
| `marge_estimee` | montant_revise_ht - (total_realise + reste_a_faire_estime) | Marge prevue |
| `taux_engagement` | total_engage / montant_revise_ht * 100 | % engage |
| `taux_realisation` | total_realise / montant_revise_ht * 100 | % realise |
| `en_depassement` | (total_engage + reste_a_faire) > montant_revise_ht * seuil | Booleen alerte |

**Methodes cles** :
- `ajouter_ligne(ligne)` : Ajoute un lot budgetaire, recalcule montant_initial
- `supprimer_ligne(ligne_id)` : Supprime un lot (si aucun achat lie)
- `appliquer_avenant(avenant)` : Applique un avenant, recalcule montant_revise
- `verifier_seuil_alerte()` : Retourne True si depassement detecte

### 2.2 Entite LigneBudgetaire

**Fichier prevu** : `backend/modules/financier/domain/entities/ligne_budgetaire.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `budget_id` | int | Oui | FK vers budget |
| `parent_id` | int | Non | FK vers ligne parente (arborescence) |
| `code_lot` | str | Oui | Code unique dans le budget (ex: LOT-01, LOT-02-MACON) |
| `libelle` | str | Oui | Description du poste |
| `unite` | UniteMesure | Oui | m2, m3, forfait, kg, heure, ml, u |
| `quantite_prevue` | Decimal | Oui | Volume budgete |
| `prix_unitaire_ht` | Decimal | Oui | Cout unitaire HT |
| `total_prevu_ht` | Decimal | Calcule | quantite x prix_unitaire |
| `ordre` | int | Auto | Ordre d'affichage |
| `tache_id` | int | Non | FK optionnelle vers tache (FIN-03) |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |

**Proprietes calculees** :

| Propriete | Formule | Description |
|-----------|---------|-------------|
| `engage` | Somme achats lies en statut >= VALIDE | Montant engage sur ce lot |
| `realise` | Somme achats FACTURE lies | Montant realise sur ce lot |
| `reste_a_faire` | total_prevu_ht - realise | Reste |
| `ecart` | realise - total_prevu_ht | Depassement si > 0 |
| `taux_consommation` | realise / total_prevu_ht * 100 | % consomme |

**Validations** :
- `code_lot` : unique au sein du budget, pattern `^[A-Z0-9\-]+$`, max 30 chars
- `quantite_prevue` : >= 0
- `prix_unitaire_ht` : >= 0
- `libelle` : non vide, max 200 chars

### 2.3 Entite Achat

**Fichier prevu** : `backend/modules/financier/domain/entities/achat.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `chantier_id` | int | Oui | FK vers chantier |
| `fournisseur_id` | int | Oui | FK vers fournisseur |
| `ligne_budgetaire_id` | int | Non | FK vers lot budgetaire |
| `type_achat` | TypeAchat | Oui | MATERIAU / MATERIEL / SOUS_TRAITANCE / SERVICE |
| `libelle` | str | Oui | Description de l'achat |
| `quantite` | Decimal | Oui | Quantite commandee |
| `unite` | UniteMesure | Oui | Unite de mesure |
| `prix_unitaire_ht` | Decimal | Oui | Cout unitaire HT |
| `total_ht` | Decimal | Calcule | quantite x prix_unitaire_ht |
| `taux_tva` | TauxTVA | Oui | 20%, 10%, 5.5%, 0% |
| `total_ttc` | Decimal | Calcule | total_ht x (1 + taux_tva) |
| `date_commande` | date | Oui | Date du bon de commande |
| `date_livraison_prevue` | date | Non | Echeance livraison |
| `statut` | StatutAchat | Auto | DEMANDE / VALIDE / REFUSE / COMMANDE / LIVRE / FACTURE |
| `motif_refus` | str | Conditionnel | Motif si refuse |
| `numero_facture` | str | Non | Reference facture fournisseur |
| `commentaire` | str | Non | Notes complementaires |
| `demandeur_id` | int | Oui | FK vers utilisateur demandeur |
| `valideur_id` | int | Non | FK vers utilisateur valideur |
| `validated_at` | datetime | Non | Date de validation |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |

**Methodes cles** :
- `valider(valideur_id)` : DEMANDE → VALIDE
- `refuser(valideur_id, motif)` : DEMANDE → REFUSE
- `commander()` : VALIDE → COMMANDE
- `livrer()` : COMMANDE → LIVRE
- `facturer(numero_facture)` : LIVRE → FACTURE (definitif)
- `necessite_validation(seuil)` : retourne total_ht >= seuil
- `est_modifiable()` : retourne statut != FACTURE

### 2.4 Entite Avenant

**Fichier prevu** : `backend/modules/financier/domain/entities/avenant.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `budget_id` | int | Oui | FK vers budget |
| `numero` | int | Auto | Numero sequentiel par budget (AV-01, AV-02...) |
| `motif` | str | Oui | Raison de l'avenant |
| `montant_ht` | Decimal | Oui | Montant HT (positif = ajout, negatif = reduction) |
| `date_avenant` | date | Oui | Date de l'avenant |
| `created_by` | int | Oui | FK vers utilisateur createur |
| `created_at` | datetime | Auto | Date de creation |

**Validations** :
- `motif` : non vide, max 500 chars
- `montant_ht` : non nul (peut etre negatif pour moins-values)
- `numero` : auto-incremente par budget

### 2.5 Entite SituationTravaux

**Fichier prevu** : `backend/modules/financier/domain/entities/situation_travaux.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `budget_id` | int | Oui | FK vers budget |
| `numero` | str | Auto | Numerotation auto (SIT-2026-01) |
| `periode_debut` | date | Oui | Debut de la periode |
| `periode_fin` | date | Oui | Fin de la periode |
| `statut` | StatutSituation | Auto | BROUILLON / EN_VALIDATION / EMISE / VALIDEE / FACTUREE |
| `montant_cumule_precedent_ht` | Decimal | Calcule | Cumul des situations precedentes |
| `montant_periode_ht` | Decimal | Calcule | Somme des lignes de cette situation |
| `montant_cumule_total_ht` | Decimal | Calcule | Precedent + Periode |
| `retenue_garantie_ht` | Decimal | Calcule | Cumul total x taux retenue |
| `montant_a_facturer_ht` | Decimal | Calcule | Periode - retenue prorata |
| `taux_tva` | TauxTVA | Oui | Taux TVA applicable |
| `montant_a_facturer_ttc` | Decimal | Calcule | A facturer HT x (1 + TVA) |
| `document_id` | int | Non | FK vers GED si PDF genere |
| `created_by` | int | Oui | FK vers utilisateur createur |
| `validated_by` | int | Non | FK vers valideur interne |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |

### 2.6 Entite LigneSituation

**Fichier prevu** : `backend/modules/financier/domain/entities/ligne_situation.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `situation_id` | int | Oui | FK vers situation |
| `ligne_budgetaire_id` | int | Oui | FK vers lot budgetaire |
| `avancement_pct` | Decimal | Oui | % avancement cumule (0-100) |
| `avancement_precedent_pct` | Decimal | Calcule | % de la situation precedente |
| `montant_marche_ht` | Decimal | Calcule | Total prevu HT du lot |
| `montant_cumule_ht` | Decimal | Calcule | Marche x avancement_pct / 100 |
| `montant_precedent_ht` | Decimal | Calcule | Marche x avancement_precedent / 100 |
| `montant_periode_ht` | Decimal | Calcule | Cumule - Precedent |

**Validations** :
- `avancement_pct` : 0 <= valeur <= 100
- `avancement_pct` >= `avancement_precedent_pct` (pas de regression)

### 2.7 Entite Fournisseur

**Fichier prevu** : `backend/modules/financier/domain/entities/fournisseur.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `raison_sociale` | str | Oui | Nom officiel |
| `type_fournisseur` | TypeFournisseur | Oui | NEGOCE / LOUEUR / SOUS_TRAITANT / SERVICE |
| `siret` | str | Non | Numero SIRET (14 chiffres) |
| `adresse` | str | Non | Adresse complete |
| `contact_principal` | str | Non | Nom du contact |
| `telephone` | str | Non | Numero direct |
| `email` | str | Non | Email de contact |
| `conditions_paiement` | str | Non | Ex: "30 jours fin de mois" |
| `notes` | str | Non | Informations complementaires |
| `actif` | bool | Auto | Actif ou archive (defaut: true) |
| `created_at` | datetime | Auto | Date de creation |
| `updated_at` | datetime | Auto | Date de modification |

**Validations** :
- `raison_sociale` : non vide, max 200 chars
- `siret` : si fourni, exactement 14 chiffres (pattern `^\d{14}$`)
- `email` : si fourni, format email valide
- `telephone` : si fourni, pattern telephone francais

### 2.8 Entite JournalFinancier

**Fichier prevu** : `backend/modules/financier/domain/entities/journal_financier.py`

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | int | Auto | Identifiant unique |
| `budget_id` | int | Oui | FK vers budget |
| `type_operation` | TypeOperation | Oui | CREATION_LIGNE / MODIFICATION_LIGNE / SUPPRESSION_LIGNE / AVENANT / ACHAT_CREE / ACHAT_VALIDE / ACHAT_REFUSE / SITUATION_CREEE / SITUATION_EMISE / ... |
| `entite_type` | str | Oui | Nom de l'entite concernee |
| `entite_id` | int | Oui | ID de l'entite concernee |
| `description` | str | Oui | Description lisible de l'operation |
| `donnees_avant` | JSON | Non | Snapshot avant modification |
| `donnees_apres` | JSON | Non | Snapshot apres modification |
| `auteur_id` | int | Oui | FK vers utilisateur |
| `created_at` | datetime | Auto | Timestamp de l'operation |

### 2.9 Value Objects

#### StatutAchat

**Fichier prevu** : `backend/modules/financier/domain/value_objects/statut_achat.py`

| Valeur | Label | Couleur | Engage | Realise | Final |
|--------|-------|---------|--------|---------|-------|
| `DEMANDE` | "Demande" | #FFC107 (jaune) | Non | Non | Non |
| `VALIDE` | "Valide" | #4CAF50 (vert) | Oui | Non | Non |
| `REFUSE` | "Refuse" | #F44336 (rouge) | Non | Non | Oui |
| `COMMANDE` | "Commande" | #2196F3 (bleu) | Oui | Non | Non |
| `LIVRE` | "Livre" | #9C27B0 (violet) | Oui | Non | Non |
| `FACTURE` | "Facture" | #424242 (gris fonce) | Oui | Oui | Oui |

> **Engage** = compte dans le total engage du lot
> **Realise** = compte dans le total realise du lot
> **Final** = aucune modification possible

#### StatutSituation

**Fichier prevu** : `backend/modules/financier/domain/value_objects/statut_situation.py`

| Valeur | Label | Couleur | Final |
|--------|-------|---------|-------|
| `BROUILLON` | "Brouillon" | #FFC107 (jaune) | Non |
| `EN_VALIDATION` | "En validation" | #FF9800 (orange) | Non |
| `EMISE` | "Emise" | #2196F3 (bleu) | Non |
| `VALIDEE` | "Validee" | #4CAF50 (vert) | Non |
| `FACTUREE` | "Facturee" | #424242 (gris fonce) | Oui |

#### TypeAchat

| Valeur | Label | Exemples |
|--------|-------|----------|
| `MATERIAU` | "Materiau" | Beton, acier, parpaings, sable |
| `MATERIEL` | "Materiel" | Location grue, nacelle |
| `SOUS_TRAITANCE` | "Sous-traitance" | Electricien, plombier |
| `SERVICE` | "Service" | Bureau d'etude, geometre |

#### TypeFournisseur

| Valeur | Label |
|--------|-------|
| `NEGOCE` | "Negoce materiaux" |
| `LOUEUR` | "Loueur" |
| `SOUS_TRAITANT` | "Sous-traitant" |
| `SERVICE` | "Service" |

#### TauxTVA

| Valeur | Label | Taux | Usage BTP courant |
|--------|-------|------|-------------------|
| `TVA_20` | "20%" | 0.20 | Neuf, materiel |
| `TVA_10` | "10%" | 0.10 | Renovation, main-d'oeuvre |
| `TVA_5_5` | "5.5%" | 0.055 | Amelioration energetique |
| `TVA_0` | "0%" | 0.00 | Exonere (DOM-TOM, export) |

#### UniteMesure

Reutilise le value object existant du module Taches, etendu si necessaire :

| Valeur | Label |
|--------|-------|
| `M2` | "m2" |
| `M3` | "m3" |
| `ML` | "ml" |
| `KG` | "kg" |
| `UNITE` | "u" |
| `HEURE` | "heure" |
| `FORFAIT` | "forfait" |

---

## 3. MACHINE A ETATS - ACHATS

### 3.1 Diagramme de transitions

```
                    +-------------+
                    |             |
                    |  DEMANDE    |
                    |  (jaune)    |
                    +------+------+
                           |
              +------------+------------+
              |            |            |
         valider()    refuser()    [auto-valider]
         (si >= seuil) (+ motif)   (si < seuil)
              |            |            |
              v            v            v
        +-----------+ +-----------+
        |           | |           |
        |  VALIDE   | |  REFUSE   |
        |  (vert)   | |  (rouge)  |
        +-----------+ +-----------+
              |            (final)
              |
         commander()
              |
              v
        +-----------+
        |           |
        | COMMANDE  |
        |  (bleu)   |
        +-----------+
              |
         livrer()
              |
              v
        +-----------+
        |           |
        |  LIVRE    |
        | (violet)  |
        +-----------+
              |
     facturer(numero)
              |
              v
        +-----------+
        |           |
        | FACTURE   |
        | (gris)    |
        +-----------+
           (final)
```

### 3.2 Regles de transition

| Depuis | Vers | Action | Qui | Condition |
|--------|------|--------|-----|-----------|
| DEMANDE | VALIDE | `valider(valideur_id)` | Conducteur/Admin | Si montant >= seuil |
| DEMANDE | VALIDE | auto-validation | Systeme | Si montant < seuil |
| DEMANDE | REFUSE | `refuser(valideur_id, motif)` | Conducteur/Admin | — |
| VALIDE | COMMANDE | `commander()` | Chef/Conducteur/Admin | — |
| COMMANDE | LIVRE | `livrer()` | Chef/Conducteur/Admin | — |
| LIVRE | FACTURE | `facturer(numero)` | Conducteur/Admin | numero_facture requis |
| REFUSE | — | Etat final | — | Pas de retour |
| FACTURE | — | Etat final | — | Aucune modification |

### 3.3 Auto-validation

```python
# Dans CreateAchatUseCase :
if achat.total_ht < budget.seuil_validation_achat:
    achat.valider(demandeur_id)  # Auto-validation immediate
    # Pas de notification au conducteur
else:
    # Statut reste DEMANDE
    # Notification push au conducteur pour validation
    publish(AchatDemandeEvent(...))
```

### 3.4 Verrouillage apres facturation

```python
def facturer(self, numero_facture: str) -> None:
    if self.statut != StatutAchat.LIVRE:
        raise TransitionStatutInvalideError("Seul un achat LIVRE peut etre facture")
    if not numero_facture or not numero_facture.strip():
        raise ValueError("Le numero de facture est obligatoire")
    self.statut = StatutAchat.FACTURE
    self.numero_facture = numero_facture.strip()
    self.updated_at = datetime.now()
    # A partir de ce point, aucune modification n'est autorisee
```

---

## 4. MACHINE A ETATS - SITUATIONS DE TRAVAUX

### 4.1 Diagramme de transitions

```
        +--------------+
        |              |
        |  BROUILLON   |
        |   (jaune)    |
        +------+-------+
               |
          soumettre()
               |
               v
        +--------------+
        |              |
        | EN_VALIDATION|
        |   (orange)   |
        +------+-------+
               |
        +------+------+
        |             |
   valider()     rejeter()
        |             |
        v             v
  +-----------+  +-----------+
  |           |  |           |
  |  EMISE    |  | BROUILLON |
  |  (bleu)   |  |  (retour) |
  +-----------+  +-----------+
        |
  valider_client()
        |
        v
  +-----------+
  |           |
  | VALIDEE   |
  |  (vert)   |
  +-----------+
        |
  facturer()
        |
        v
  +-----------+
  |           |
  | FACTUREE  |
  |  (gris)   |
  +-----------+
     (final)
```

### 4.2 Regles de transition

| Depuis | Vers | Action | Qui |
|--------|------|--------|-----|
| BROUILLON | EN_VALIDATION | `soumettre()` | Conducteur |
| EN_VALIDATION | EMISE | `valider_interne(valideur_id)` | Admin |
| EN_VALIDATION | BROUILLON | `rejeter(motif)` | Admin |
| EMISE | VALIDEE | `valider_client()` | Admin (apres retour client) |
| VALIDEE | FACTUREE | `facturer()` | Admin |
| FACTUREE | — | Etat final | — |

### 4.3 Regles metier

- Une seule situation BROUILLON ou EN_VALIDATION a la fois par budget
- L'avancement ne peut pas regresser par rapport a la situation precedente
- La generation PDF se fait a la transition vers EMISE
- Le PDF est automatiquement archive dans la GED du chantier
- La numerotation est sequentielle par chantier et par annee (SIT-2026-01, SIT-2026-02...)

---

## 5. FLUX BUDGET

### 5.1 Creation d'un budget

```
Conducteur/Admin     Frontend              Backend                   BDD
      |                  |                     |                       |
      | Ouvre fiche       |                     |                       |
      | chantier          |                     |                       |
      |  onglet Budget    |                     |                       |
      |----------------->|                     |                       |
      |                  | GET /financier/      |                       |
      |                  | chantiers/{id}/budget|                       |
      |                  |-------------------->|                       |
      |                  |                     | Budget existe ?        |
      |                  |                     |---------------------->|
      |                  |                     |<----------------------|
      |                  |                     |                       |
      |                  |<--------------------|                       |
      |                  | 404 (pas de budget)  |                       |
      |                  | ou 200 (budget)      |                       |
      |                  |                     |                       |
      | Si 404 :          |                     |                       |
      | Clic "Creer       |                     |                       |
      | budget"           |                     |                       |
      |----------------->|                     |                       |
      |                  | POST /financier/     |                       |
      |                  | chantiers/{id}/budget|                       |
      |                  |-------------------->|                       |
      |                  |                     | Verif :                |
      |                  |                     | - Chantier existe      |
      |                  |                     | - Pas de budget existant|
      |                  |                     | - User a le droit      |
      |                  |                     |                       |
      |                  |                     | INSERT budget          |
      |                  |                     |---------------------->|
      |                  |                     |<----------------------|
      |                  |                     |                       |
      |                  |                     | Publish                |
      |                  |                     | BudgetCreatedEvent     |
      |                  |<--------------------|                       |
      |<-----------------|                     |                       |
      | Budget vide cree  |                     |                       |
```

### 5.2 Ajout de lignes budgetaires

```
Conducteur/Admin     Frontend              Backend                   BDD
      |                  |                     |                       |
      | Clic "Ajouter    |                     |                       |
      | un lot"           |                     |                       |
      |----------------->|                     |                       |
      |                  | Modal formulaire :   |                       |
      |                  | - Code lot           |                       |
      |                  | - Libelle            |                       |
      |                  | - Unite              |                       |
      |                  | - Quantite           |                       |
      |                  | - Prix unitaire HT   |                       |
      |                  |                     |                       |
      | Remplit et        |                     |                       |
      | valide            |                     |                       |
      |----------------->|                     |                       |
      |                  | POST /financier/     |                       |
      |                  | budgets/{id}/lignes  |                       |
      |                  |-------------------->|                       |
      |                  |                     | Verif :                |
      |                  |                     | - Code lot unique      |
      |                  |                     | - Quantite >= 0        |
      |                  |                     | - PU >= 0              |
      |                  |                     |                       |
      |                  |                     | INSERT ligne           |
      |                  |                     | UPDATE budget totaux   |
      |                  |                     | INSERT journal         |
      |                  |                     |---------------------->|
      |                  |<--------------------|                       |
      |<-----------------|                     |                       |
      | Ligne ajoutee,    |                     |                       |
      | totaux mis a jour |                     |                       |
```

### 5.3 Structure arborescente

Les lots peuvent avoir des sous-lots via `parent_id` :

```
LOT-01  Gros oeuvre                    150 000 EUR HT
  LOT-01-FOND  Fondations              40 000 EUR HT
  LOT-01-MURS  Murs porteurs           60 000 EUR HT
  LOT-01-DALL  Dalles                   50 000 EUR HT
LOT-02  Charpente                       80 000 EUR HT
LOT-03  Couverture                      35 000 EUR HT
LOT-04  Sous-traitance electricite      25 000 EUR HT
```

Les lots parents ont un `total_prevu_ht` egal a la somme de leurs sous-lots.

---

## 6. FLUX ACHATS ET BONS DE COMMANDE

### 6.1 Diagramme de sequence — creation achat

```
Chef/Conducteur      Frontend              Backend                   BDD
      |                  |                     |                       |
      | Clic "Nouvel     |                     |                       |
      | achat"            |                     |                       |
      |----------------->|                     |                       |
      |                  | Modal formulaire :   |                       |
      |                  | - Type (materiau...) |                       |
      |                  | - Fournisseur (liste)|                       |
      |                  | - Lot budgetaire     |                       |
      |                  | - Libelle            |                       |
      |                  | - Quantite + unite   |                       |
      |                  | - PU HT              |                       |
      |                  | - TVA (20/10/5.5/0)  |                       |
      |                  | - Date commande      |                       |
      |                  | - Date livraison     |                       |
      |                  | - Commentaire        |                       |
      |                  |                     |                       |
      | Remplit et        |                     |                       |
      | valide            |                     |                       |
      |----------------->|                     |                       |
      |                  | POST /financier/     |                       |
      |                  | achats               |                       |
      |                  |-------------------->|                       |
      |                  |                     | Verif :                |
      |                  |                     | 1. Fournisseur actif   |
      |                  |                     | 2. Chantier existe     |
      |                  |                     | 3. Lot existe (si lie) |
      |                  |                     | 4. Montants positifs   |
      |                  |                     |                       |
      |                  |                     | total_ht >= seuil ?    |
      |                  |                     |   OUI -> DEMANDE       |
      |                  |                     |   NON -> VALIDE (auto) |
      |                  |                     |                       |
      |                  |                     | INSERT achat           |
      |                  |                     | INSERT journal         |
      |                  |                     |---------------------->|
      |                  |                     |                       |
      |                  |                     | Si DEMANDE :           |
      |                  |                     | Publish                |
      |                  |                     | AchatDemandeEvent      |
      |                  |                     | -> Notif conducteur    |
      |                  |<--------------------|                       |
      |<-----------------|                     |                       |
      | Achat cree        |                     |                       |
```

### 6.2 Validation d'un achat

```
Conducteur/Admin     Frontend              Backend
      |                  |                     |
      | Voit notification |                     |
      | "Achat 12 500 EUR |                     |
      |  en attente"      |                     |
      |----------------->|                     |
      |                  | GET /financier/      |
      |                  | achats/en-attente    |
      |                  |-------------------->|
      |                  |<--------------------|
      |                  | Liste achats DEMANDE |
      |                  |                     |
      | Clic sur achat    |                     |
      | puis "Valider"    |                     |
      |----------------->|                     |
      |                  | POST /financier/     |
      |                  | achats/{id}/valider  |
      |                  |-------------------->|
      |                  |                     | Verif :
      |                  |                     | - Statut == DEMANDE
      |                  |                     | - User est Conducteur/Admin
      |                  |                     |
      |                  |                     | UPDATE statut -> VALIDE
      |                  |                     | SET valideur_id, validated_at
      |                  |                     | INSERT journal
      |                  |                     |
      |                  |                     | Publish AchatValideEvent
      |                  |                     | -> Notif au demandeur
      |                  |<--------------------|
      |<-----------------|                     |
```

### 6.3 Progression des statuts apres validation

Apres validation, le chef de chantier ou conducteur fait progresser l'achat :

```
POST /financier/achats/{id}/commander    → VALIDE -> COMMANDE
POST /financier/achats/{id}/livrer       → COMMANDE -> LIVRE
POST /financier/achats/{id}/facturer     → LIVRE -> FACTURE (+ numero_facture dans body)
```

Chaque transition publie un evenement et inscrit une entree au journal.

---

## 7. FLUX SITUATIONS DE TRAVAUX

### 7.1 Diagramme de sequence — creation et soumission

```
Conducteur           Frontend              Backend                   BDD
      |                  |                     |                       |
      | Clic "Nouvelle   |                     |                       |
      | situation"        |                     |                       |
      |----------------->|                     |                       |
      |                  | POST /financier/     |                       |
      |                  | budgets/{id}/        |                       |
      |                  | situations           |                       |
      |                  |-------------------->|                       |
      |                  |                     | Verif :                |
      |                  |                     | - Pas de situation     |
      |                  |                     |   BROUILLON existante  |
      |                  |                     | - Budget existe        |
      |                  |                     |                       |
      |                  |                     | Recupere derniere      |
      |                  |                     | situation (avancements)|
      |                  |                     |                       |
      |                  |                     | Cree situation         |
      |                  |                     | BROUILLON avec lignes  |
      |                  |                     | pre-remplies           |
      |                  |                     | (avancement precedent) |
      |                  |                     |---------------------->|
      |                  |<--------------------|                       |
      |<-----------------|                     |                       |
      |                  |                     |                       |
      | Saisie avancement |                     |                       |
      | par lot :          |                     |                       |
      | LOT-01: 45% -> 60%|                     |                       |
      | LOT-02: 30% -> 50%|                     |                       |
      |----------------->|                     |                       |
      |                  | PUT /financier/      |                       |
      |                  | situations/{id}/     |                       |
      |                  | lignes               |                       |
      |                  |-------------------->|                       |
      |                  |                     | Verif :                |
      |                  |                     | - avancement >= prec.  |
      |                  |                     | - avancement <= 100%   |
      |                  |                     |                       |
      |                  |                     | UPDATE lignes          |
      |                  |                     | Recalcul montants      |
      |                  |                     |---------------------->|
      |                  |<--------------------|                       |
      |<-----------------|                     |                       |
      |                  |                     |                       |
      | Clic "Soumettre"  |                     |                       |
      |----------------->|                     |                       |
      |                  | POST /financier/     |                       |
      |                  | situations/{id}/     |                       |
      |                  | soumettre            |                       |
      |                  |-------------------->|                       |
      |                  |                     | BROUILLON ->           |
      |                  |                     | EN_VALIDATION          |
      |                  |                     |                       |
      |                  |                     | Publish                |
      |                  |                     | SituationSoumiseEvent  |
      |                  |                     | -> Notif Admin         |
      |                  |<--------------------|                       |
      |<-----------------|                     |                       |
```

### 7.2 Validation et emission

```
Admin                Frontend              Backend
      |                  |                     |
      | Voit notification |                     |
      | "Situation SIT-   |                     |
      |  2026-03 a valider"|                    |
      |                  |                     |
      | Verifie les       |                     |
      | avancements       |                     |
      |                  |                     |
      | Option A :        |                     |
      | "Valider"         |                     |
      |----------------->|                     |
      |                  | POST /financier/     |
      |                  | situations/{id}/     |
      |                  | valider              |
      |                  |-------------------->|
      |                  |                     | EN_VALIDATION -> EMISE |
      |                  |                     | Generation PDF         |
      |                  |                     | Archivage dans GED     |
      |                  |                     | Publish SituationEmise |
      |                  |<--------------------|
      |<-----------------|                     |
      |                  |                     |
      | Option B :        |                     |
      | "Rejeter"         |                     |
      |----------------->|                     |
      |                  | POST /financier/     |
      |                  | situations/{id}/     |
      |                  | rejeter              |
      |                  | body: { motif: "..." }|
      |                  |-------------------->|
      |                  |                     | EN_VALIDATION ->       |
      |                  |                     | BROUILLON (retour)     |
      |                  |                     | Publish SituationRejet |
      |                  |<--------------------|
      |<-----------------|                     |
```

### 7.3 Validation client et facturation

```
Admin                Frontend              Backend
      |                  |                     |
      | Client a signe   |                     |
      | la situation      |                     |
      |                  |                     |
      | Clic "Valider     |                     |
      |  client"          |                     |
      |----------------->|                     |
      |                  | POST /situations/   |
      |                  | {id}/valider-client  |
      |                  |-------------------->|
      |                  |                     | EMISE -> VALIDEE       |
      |                  |<--------------------|
      |                  |                     |
      | Clic "Facturer"   |                     |
      |----------------->|                     |
      |                  | POST /situations/   |
      |                  | {id}/facturer        |
      |                  |-------------------->|
      |                  |                     | VALIDEE -> FACTUREE    |
      |                  |                     | (definitif)            |
      |                  |<--------------------|
      |<-----------------|                     |
```

### 7.4 Contenu du PDF genere

```
+----------------------------------------------------------+
| GREG CONSTRUCTION                                        |
| 123 rue du Batiment, 73000 Chambery                      |
| SIRET : 123 456 789 00012                                |
+----------------------------------------------------------+
|                                                          |
| SITUATION DE TRAVAUX N° SIT-2026-03                      |
| Periode : 01/03/2026 au 31/03/2026                       |
|                                                          |
| Chantier : 2026-01-MONTMELIAN                            |
| Client : SCI Les Terrasses                               |
| Adresse : 42 avenue de la Gare, 73800 Montmelian         |
|                                                          |
+------+------------------+--------+--------+---------+----+
| Lot  | Designation      | Marche | Avanc. | Cumule  | Periode |
+------+------------------+--------+--------+---------+---------+
| 01   | Gros oeuvre       | 150000 |  60.0% |  90000  |  22500  |
| 02   | Charpente         |  80000 |  50.0% |  40000  |  16000  |
| 03   | Couverture        |  35000 |  20.0% |   7000  |   7000  |
| 04   | Electricite ST    |  25000 |   0.0% |      0  |      0  |
+------+------------------+--------+--------+---------+---------+
|      | TOTAL HT          | 290000 |        | 137000  |  45500  |
+------+------------------+--------+--------+---------+---------+
|                                                          |
| Cumul precedent HT :                          91 500 EUR |
| Travaux periode HT :                          45 500 EUR |
| Cumul total HT :                             137 000 EUR |
|                                                          |
| Retenue de garantie 5% (sur cumul) :          -6 850 EUR |
|                                                          |
| NET A FACTURER HT :                          38 650 EUR  |
| TVA 10% :                                      3 865 EUR |
| NET A FACTURER TTC :                          42 515 EUR |
|                                                          |
+----------------------------------------------------------+
| Conducteur : _______________  Client : _________________ |
+----------------------------------------------------------+
```

---

## 8. FLUX AVENANTS BUDGETAIRES

### 8.1 Creation d'un avenant

```
Conducteur/Admin     Frontend              Backend
      |                  |                     |
      | Clic "Ajouter    |                     |
      | un avenant"       |                     |
      |----------------->|                     |
      |                  | Modal :              |
      |                  | - Motif (obligatoire)|
      |                  | - Montant HT (+/-)   |
      |                  | - Date               |
      |                  |                     |
      | Remplit et        |                     |
      | valide            |                     |
      |----------------->|                     |
      |                  | POST /financier/     |
      |                  | budgets/{id}/        |
      |                  | avenants             |
      |                  |-------------------->|
      |                  |                     | INSERT avenant         |
      |                  |                     | (numero auto AV-01)   |
      |                  |                     | UPDATE budget :        |
      |                  |                     |   montant_avenants +=  |
      |                  |                     |   montant_ht           |
      |                  |                     |   montant_revise =     |
      |                  |                     |   initial + avenants   |
      |                  |                     | INSERT journal         |
      |                  |                     |                       |
      |                  |                     | Verif seuil alerte     |
      |                  |                     | (budget revise change) |
      |                  |                     |                       |
      |                  |                     | Publish AvenantCreeEvent|
      |                  |<--------------------|
      |<-----------------|                     |
```

### 8.2 Impact sur le budget

```
Budget initial :     290 000 EUR HT  (somme des lots)
Avenant AV-01 :     + 15 000 EUR HT  (travaux supplementaires fondations)
Avenant AV-02 :     -  3 000 EUR HT  (moins-value couverture)
                    ─────────────────
Budget revise :      302 000 EUR HT
```

Les avenants ne modifient pas les lignes budgetaires existantes. Ils impactent uniquement le `montant_revise_ht` du budget global, ce qui modifie les seuils d'alerte et la marge estimee.

---

## 9. INTEGRATION COUTS AUTOMATIQUES

### 9.1 Couts main-d'oeuvre (FIN-09)

Le module financier consomme les donnees du module Feuilles d'Heures via EventBus.

```
Module Pointages                    Module Financier
      |                                    |
      | FeuilleHeuresValideeEvent          |
      |  - chantier_id                     |
      |  - user_id                         |
      |  - heures_normales                 |
      |  - heures_sup                      |
      |  - metier                          |
      |----------------------------------->|
      |                                    |
      |                        Lookup taux horaire par metier
      |                        dans table taux_horaires :
      |                        - Macon : 35 EUR/h
      |                        - Coffreur : 37 EUR/h
      |                        - Ferrailleur : 36 EUR/h
      |                        - Grutier : 42 EUR/h
      |                        - Chef equipe : 45 EUR/h
      |                                    |
      |                        Cout = heures x taux
      |                        Heures sup = heures_sup x taux x 1.25
      |                                    |
      |                        INSERT cout_main_oeuvre
      |                        UPDATE budget.total_realise
      |                                    |
```

**Table taux_horaires** :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | int | PK |
| `metier` | str | Code metier (MACON, COFFREUR, etc.) |
| `taux_horaire_ht` | Decimal | Taux horaire normal HT |
| `taux_majoration_sup` | Decimal | Multiplicateur heures sup (defaut 1.25) |
| `date_effet` | date | Date d'effet du taux |
| `actif` | bool | Taux courant |

### 9.2 Couts materiel (FIN-10)

Le module financier consomme les donnees du module Logistique.

```
Module Logistique                   Module Financier
      |                                    |
      | ReservationValideeEvent            |
      |  - ressource_id                    |
      |  - chantier_id                     |
      |  - date_reservation                |
      |  - heure_debut                     |
      |  - heure_fin                       |
      |----------------------------------->|
      |                                    |
      |                        Lookup tarif ressource
      |                        dans table tarifs_materiel :
      |                        - Grue 40T : 800 EUR/jour
      |                        - Mini-pelle : 350 EUR/jour
      |                        - Nacelle : 200 EUR/jour
      |                                    |
      |                        Cout = duree_heures / 8 x tarif_jour
      |                        (prorata si < journee complete)
      |                                    |
      |                        INSERT cout_materiel
      |                        UPDATE budget.total_realise
      |                                    |
```

**Table tarifs_materiel** :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | int | PK |
| `ressource_id` | int | FK vers logistique.ressources (optionnel) |
| `categorie` | str | Categorie de materiel |
| `libelle` | str | Description |
| `tarif_journalier_ht` | Decimal | Tarif par jour HT |
| `date_effet` | date | Date d'effet |
| `actif` | bool | Tarif courant |

### 9.3 Recapitulatif des sources de couts

| Source | Type | Automatique | Impacte |
|--------|------|-------------|---------|
| Achats FACTURE | Montant total HT | Non (saisie manuelle, progression statuts) | Engage + Realise |
| Achats VALIDE/COMMANDE/LIVRE | Montant total HT | Non | Engage uniquement |
| Heures validees | Heures x taux horaire | Oui (via EventBus) | Realise |
| Reservations materiel | Duree x tarif journalier | Oui (via EventBus) | Realise |

---

## 10. TABLEAU DE BORD FINANCIER

### 10.1 Disposition (mobile-first)

L'onglet Budget d'un chantier affiche le tableau de bord suivant :

```
+----------------------------------------------------------+
|  BUDGET CHANTIER : 2026-01-MONTMELIAN                    |
+----------------------------------------------------------+
|                                                          |
|  +-----------+  +-----------+  +-----------+  +--------+ |
|  | Budget    |  | Engage    |  | Realise   |  | Marge  | |
|  | revise    |  |           |  |           |  | estim. | |
|  |           |  |           |  |           |  |        | |
|  | 302 000 EUR  | 185 000 EUR  | 137 000 EUR  | 28 500 | |
|  |           |  | 61% [===] |  | 45% [===] |  | 9.4%   | |
|  | vert      |  | vert      |  | vert      |  | vert   | |
|  +-----------+  +-----------+  +-----------+  +--------+ |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  BUDGET / ENGAGE / REALISE PAR LOT                       |
|                                                          |
|  LOT-01 Gros oeuvre                                      |
|  Budget  [████████████████████████████] 150 000          |
|  Engage  [████████████████████       ] 112 000           |
|  Realise [████████████               ]  78 000           |
|                                                          |
|  LOT-02 Charpente                                        |
|  Budget  [████████████████████████████]  80 000          |
|  Engage  [██████████████████████████████████] 95 000 !!  |
|  Realise [████████████████           ]  52 000           |
|                                                          |
|  LOT-03 Couverture                                       |
|  Budget  [████████████████████████████]  35 000          |
|  Engage  [████████                   ]  12 000           |
|  Realise [████                       ]   7 000           |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  REPARTITION DES COUTS          COURBE EN S              |
|                                                          |
|     [Donut chart]                 [Line chart]           |
|   MO 42%  |  Mat 31%          Physique --- Financier     |
|   ST 18%  |  Equip 9%                                   |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  DERNIERS ACHATS                                         |
|  ┌──────────────────────────────────────────────────┐    |
|  │ Beton C25/30 - Vicat SA - 12 500 EUR - COMMANDE │    |
|  │ Acier HA10 - SteelFrance - 8 200 EUR - LIVRE    │    |
|  │ Coffrage - LoxamRent - 3 500 EUR - FACTURE      │    |
|  └──────────────────────────────────────────────────┘    |
|                                                          |
|  DERNIERES SITUATIONS                                    |
|  ┌──────────────────────────────────────────────────┐    |
|  │ SIT-2026-03 - 45 500 EUR - 31/03 - EMISE        │    |
|  │ SIT-2026-02 - 38 200 EUR - 28/02 - FACTUREE     │    |
|  └──────────────────────────────────────────────────┘    |
|                                                          |
+----------------------------------------------------------+
```

### 10.2 Couleurs des cartes KPI

| Condition | Couleur | Icone |
|-----------|---------|-------|
| Taux < 80% du budget | #4CAF50 (vert) | Check |
| Taux entre 80% et 100% | #FF9800 (orange) | Warning |
| Taux > 100% du budget | #F44336 (rouge) | Alert |
| Marge > 10% | #4CAF50 (vert) | TrendUp |
| Marge entre 5% et 10% | #FF9800 (orange) | TrendFlat |
| Marge < 5% | #F44336 (rouge) | TrendDown |

### 10.3 Endpoint dashboard

```
GET /api/financier/chantiers/{chantier_id}/dashboard
```

**Reponse** :

```typescript
interface DashboardFinancier {
  budget_revise_ht: number
  total_engage: number
  total_realise: number
  marge_estimee: number
  taux_engagement: number      // %
  taux_realisation: number     // %
  taux_marge: number           // %
  en_alerte: boolean
  lots: LotResume[]            // Pour barres groupees
  repartition_couts: {        // Pour donut
    main_oeuvre: number
    materiaux: number
    sous_traitance: number
    materiel: number
  }
  courbe_s: {                  // Pour line chart
    mois: string[]
    avancement_physique: number[]   // %
    avancement_financier: number[]  // %
  }
  derniers_achats: AchatResume[]        // 5 derniers
  dernieres_situations: SituationResume[] // 3 dernieres
}
```

---

## 11. ALERTES ET NOTIFICATIONS

### 11.1 Types d'alertes

| Alerte | Condition | Destinataire | Canal |
|--------|-----------|-------------|-------|
| Depassement lot | engage_lot > budget_lot * seuil | Conducteur + Admin | Push + in-app |
| Depassement global | (engage + raf) > budget_revise * seuil | Admin | Push + in-app |
| Achat en attente validation | Achat DEMANDE cree, montant >= seuil | Conducteur + Admin | Push |
| Achat valide | Achat passe de DEMANDE a VALIDE | Demandeur | Push |
| Achat refuse | Achat passe de DEMANDE a REFUSE | Demandeur | Push |
| Situation soumise | Situation passe a EN_VALIDATION | Admin | Push |
| Situation rejetee | Situation retourne a BROUILLON | Conducteur createur | Push |
| Marge critique | Marge estimee < 5% | Admin | Push + in-app |

### 11.2 Seuils configurables

| Parametre | Defaut | Configurable par |
|-----------|--------|-----------------|
| Seuil alerte depassement | 110% (budget + 10%) | Budget (par chantier) |
| Seuil validation achat | 5 000 EUR HT | Budget (par chantier) |
| Seuil marge critique | 5% | Global (config app) |

### 11.3 Integration EventBus

Les alertes sont declenchees par les use cases via le bus d'evenements :

```python
# Dans UpdateBudgetUseCase, apres recalcul :
if budget.en_depassement:
    EventBus.publish(DepassementBudgetEvent(
        budget_id=budget.id,
        chantier_id=budget.chantier_id,
        taux_engagement=budget.taux_engagement,
        montant_engage=budget.total_engage,
        montant_budget=budget.montant_revise_ht
    ))
```

Le handler de notifications (module notifications) ecoute ces evenements et genere les push via Firebase.

---

## 12. REFERENTIEL FOURNISSEURS

### 12.1 Flux CRUD

```
GET    /api/financier/fournisseurs              → Liste (filtre type, actif, recherche)
POST   /api/financier/fournisseurs              → Creation (Admin uniquement)
GET    /api/financier/fournisseurs/{id}          → Detail
PUT    /api/financier/fournisseurs/{id}          → Modification (Admin uniquement)
DELETE /api/financier/fournisseurs/{id}          → Archivage (actif=false, Admin uniquement)
```

### 12.2 Regles

- Un fournisseur ne peut pas etre supprime physiquement (soft delete via `actif=false`)
- Les fournisseurs archives n'apparaissent plus dans les listes de selection
- Les achats existants conservent leur reference au fournisseur (meme archive)
- Le SIRET est optionnel mais s'il est fourni, il doit etre valide (14 chiffres)
- Le conducteur peut consulter les fournisseurs mais pas les modifier

### 12.3 Recherche et filtres

| Filtre | Type | Description |
|--------|------|-------------|
| `q` | string | Recherche full-text (raison_sociale, contact) |
| `type` | enum | NEGOCE / LOUEUR / SOUS_TRAITANT / SERVICE |
| `actif` | bool | true (defaut) / false / null (tous) |
| `limit` | int | Pagination (defaut 50) |
| `offset` | int | Offset pagination |

---

## 13. EXPORT COMPTABLE

### 13.1 Format du fichier CSV

```csv
date_piece;code_journal;numero_piece;code_compte;libelle;debit;credit;code_analytique
2026-03-15;HA;ACH-0042;401000;Vicat SA - Beton C25/30;0.00;12500.00;2026-01-MONTMELIAN
2026-03-15;HA;ACH-0042;601100;Achat beton;12500.00;0.00;2026-01-MONTMELIAN
2026-03-31;VE;SIT-2026-03;411000;SCI Les Terrasses;42515.00;0.00;2026-01-MONTMELIAN
2026-03-31;VE;SIT-2026-03;704000;Travaux de construction;0.00;38650.00;2026-01-MONTMELIAN
2026-03-31;VE;SIT-2026-03;445710;TVA collectee 10%;0.00;3865.00;2026-01-MONTMELIAN
```

### 13.2 Colonnes

| Colonne | Description |
|---------|-------------|
| `date_piece` | Date de l'operation (format AAAA-MM-JJ) |
| `code_journal` | HA (achats) / VE (ventes) |
| `numero_piece` | Reference unique (ACH-NNNN ou SIT-AAAA-NN) |
| `code_compte` | Numero de compte comptable |
| `libelle` | Description de l'ecriture |
| `debit` | Montant debit |
| `credit` | Montant credit |
| `code_analytique` | Code chantier pour affectation analytique |

### 13.3 Endpoint

```
GET /api/financier/export?chantier_id=1&date_debut=2026-01-01&date_fin=2026-03-31&format=csv
```

Reponse : fichier CSV en telechargement direct (`Content-Type: text/csv`).

Le format Excel (`.xlsx`) est aussi supporte via le parametre `format=xlsx`.

### 13.4 Comptes comptables utilises

| Compte | Libelle | Utilisation |
|--------|---------|-------------|
| 401000 | Fournisseurs | Credit lors achat |
| 411000 | Clients | Debit lors facturation |
| 601100 | Achats materiaux | Debit achat materiau |
| 602000 | Achats sous-traitance | Debit achat ST |
| 606100 | Location materiel | Debit location |
| 621000 | Services exterieurs | Debit achat service |
| 641000 | Main-d'oeuvre | Debit cout MO |
| 704000 | Travaux | Credit facturation client |
| 445710 | TVA collectee | Credit TVA vente |
| 445660 | TVA deductible | Debit TVA achat |

---

## 14. PERMISSIONS ET ROLES

### 14.1 Matrice complete

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|------------|---------------|-----------|
| **Budget** | | | | |
| Voir budget | ✅ tous | ✅ ses chantiers | ✅ ses chantiers | ❌ |
| Creer budget | ✅ | ✅ ses chantiers | ❌ | ❌ |
| Modifier lignes budget | ✅ | ✅ ses chantiers | ❌ | ❌ |
| Supprimer ligne budget | ✅ | ✅ ses chantiers | ❌ | ❌ |
| **Avenants** | | | | |
| Voir avenants | ✅ | ✅ ses chantiers | ✅ ses chantiers | ❌ |
| Creer avenant | ✅ | ✅ ses chantiers | ❌ | ❌ |
| **Achats** | | | | |
| Creer demande achat | ✅ | ✅ | ✅ | ❌ |
| Voir ses achats | ✅ | ✅ | ✅ | ❌ |
| Voir achats chantier | ✅ | ✅ ses chantiers | ❌ | ❌ |
| Valider achat > seuil | ✅ | ✅ | ❌ | ❌ |
| Refuser achat | ✅ | ✅ | ❌ | ❌ |
| Progresser statut | ✅ | ✅ | ✅ (ses achats) | ❌ |
| **Situations** | | | | |
| Creer situation | ✅ | ✅ ses chantiers | ❌ | ❌ |
| Soumettre situation | ✅ | ✅ (createur) | ❌ | ❌ |
| Valider situation | ✅ | ❌ | ❌ | ❌ |
| Rejeter situation | ✅ | ❌ | ❌ | ❌ |
| Valider client | ✅ | ❌ | ❌ | ❌ |
| Facturer | ✅ | ❌ | ❌ | ❌ |
| **Fournisseurs** | | | | |
| Voir fournisseurs | ✅ | ✅ | ❌ | ❌ |
| Gerer fournisseurs | ✅ | ❌ | ❌ | ❌ |
| **Export** | | | | |
| Export comptable | ✅ | ❌ | ❌ | ❌ |
| **Dashboard** | | | | |
| Voir dashboard | ✅ | ✅ ses chantiers | ✅ ses chantiers | ❌ |

### 14.2 Securite

| Code | Regle | Endpoint |
|------|-------|----------|
| FIN-SEC-01 | Budget accessible uniquement aux affectes au chantier | Tous GET /budgets |
| FIN-SEC-02 | Achats : proprietaire ou role superieur | GET /achats/{id} |
| FIN-SEC-03 | Validation : Conducteur/Admin uniquement | POST /achats/{id}/valider |
| FIN-SEC-04 | Situations : Admin uniquement pour validation/rejet | POST /situations/{id}/valider |
| FIN-SEC-05 | Export : Admin uniquement | GET /export |
| FIN-SEC-06 | Fournisseurs : CRUD Admin, lecture Conducteur | /fournisseurs |

---

## 15. EVENEMENTS DOMAINE

### 15.1 Liste des evenements

**Fichier prevu** : `backend/modules/financier/domain/events/financier_events.py`

| Evenement | Donnees | Declencheur |
|-----------|---------|-------------|
| `BudgetCreatedEvent` | budget_id, chantier_id, created_by | Creation budget |
| `LigneBudgetaireAjouteeEvent` | budget_id, ligne_id, code_lot, total_ht | Ajout ligne |
| `LigneBudgetaireModifieeEvent` | budget_id, ligne_id, ancien_total, nouveau_total | Modification ligne |
| `LigneBudgetaireSupprimeeEvent` | budget_id, ligne_id, code_lot | Suppression ligne |
| `AvenantCreeEvent` | budget_id, avenant_id, numero, montant_ht, motif | Creation avenant |
| `AchatDemandeEvent` | achat_id, chantier_id, demandeur_id, total_ht, fournisseur_nom | Achat cree >= seuil |
| `AchatValideEvent` | achat_id, demandeur_id, valideur_id, total_ht | Achat valide |
| `AchatRefuseEvent` | achat_id, demandeur_id, valideur_id, motif | Achat refuse |
| `AchatFactureEvent` | achat_id, chantier_id, total_ht, numero_facture | Achat facture |
| `SituationSoumiseEvent` | situation_id, budget_id, montant_periode_ht, created_by | Soumission validation |
| `SituationEmiseEvent` | situation_id, budget_id, montant_periode_ht, document_id | Validation + PDF |
| `SituationRejeteeEvent` | situation_id, budget_id, motif, created_by | Rejet par admin |
| `SituationFactureeEvent` | situation_id, budget_id, montant_ttc | Facturation definitive |
| `DepassementBudgetEvent` | budget_id, chantier_id, taux_engagement, montant_engage, montant_budget | Seuil depasse |
| `MargeAlertEvent` | budget_id, chantier_id, taux_marge | Marge < seuil critique |

### 15.2 Evenements consommes (depuis autres modules)

| Evenement source | Module source | Usage dans financier |
|-----------------|---------------|---------------------|
| `FeuilleHeuresValideeEvent` | Pointages | Calcul cout main-d'oeuvre |
| `ReservationValideeEvent` | Logistique | Calcul cout materiel |
| `ChantierStatusChangedEvent` | Chantiers | Bloquer operations si chantier ferme |

---

## 16. API REST - ENDPOINTS

### 16.1 Budget

**Router** : `/api/financier`

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| GET | `/chantiers/{id}/budget` | Affecte au chantier | Recuperer budget complet | FIN-01 |
| POST | `/chantiers/{id}/budget` | Conducteur/Admin | Creer budget | FIN-01 |
| GET | `/chantiers/{id}/dashboard` | Affecte au chantier | Dashboard financier | FIN-11 |

### 16.2 Lignes budgetaires

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| POST | `/budgets/{id}/lignes` | Conducteur/Admin | Ajouter ligne | FIN-02 |
| PUT | `/budgets/{id}/lignes/{lid}` | Conducteur/Admin | Modifier ligne | FIN-02 |
| DELETE | `/budgets/{id}/lignes/{lid}` | Conducteur/Admin | Supprimer ligne | FIN-02 |

### 16.3 Avenants

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| GET | `/budgets/{id}/avenants` | Affecte | Liste avenants | FIN-04 |
| POST | `/budgets/{id}/avenants` | Conducteur/Admin | Creer avenant | FIN-04 |

### 16.4 Achats

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| POST | `/achats` | Chef/Conducteur/Admin | Creer achat | FIN-05 |
| GET | `/achats` | Selon role | Liste achats (filtres) | FIN-05 |
| GET | `/achats/en-attente` | Conducteur/Admin | File de validation | FIN-06 |
| GET | `/achats/{id}` | Proprietaire/Superieur | Detail achat | FIN-05 |
| PUT | `/achats/{id}` | Proprietaire (si modifiable) | Modifier achat | FIN-05 |
| POST | `/achats/{id}/valider` | Conducteur/Admin | Valider achat | FIN-06 |
| POST | `/achats/{id}/refuser` | Conducteur/Admin | Refuser (+ motif) | FIN-06 |
| POST | `/achats/{id}/commander` | Chef/Conducteur/Admin | Passer en commande | FIN-05 |
| POST | `/achats/{id}/livrer` | Chef/Conducteur/Admin | Marquer livre | FIN-05 |
| POST | `/achats/{id}/facturer` | Conducteur/Admin | Facturer (+ numero) | FIN-05 |

### 16.5 Situations de travaux

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| GET | `/budgets/{id}/situations` | Affecte | Liste situations | FIN-07 |
| POST | `/budgets/{id}/situations` | Conducteur/Admin | Creer situation | FIN-07 |
| GET | `/situations/{id}` | Affecte | Detail situation + lignes | FIN-07 |
| PUT | `/situations/{id}/lignes` | Conducteur (createur) | Maj avancements | FIN-07 |
| POST | `/situations/{id}/soumettre` | Conducteur (createur) | Soumettre validation | FIN-07 |
| POST | `/situations/{id}/valider` | Admin | Valider + generer PDF | FIN-07 |
| POST | `/situations/{id}/rejeter` | Admin | Rejeter (+ motif) | FIN-07 |
| POST | `/situations/{id}/valider-client` | Admin | Validation client | FIN-07 |
| POST | `/situations/{id}/facturer` | Admin | Facturer | FIN-08 |
| GET | `/situations/{id}/pdf` | Affecte | Telecharger PDF | FIN-07 |

### 16.6 Fournisseurs

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| GET | `/fournisseurs` | Conducteur/Admin | Liste fournisseurs | FIN-14 |
| POST | `/fournisseurs` | Admin | Creer fournisseur | FIN-14 |
| GET | `/fournisseurs/{id}` | Conducteur/Admin | Detail | FIN-14 |
| PUT | `/fournisseurs/{id}` | Admin | Modifier | FIN-14 |
| DELETE | `/fournisseurs/{id}` | Admin | Archiver (actif=false) | FIN-14 |

### 16.7 Export et historique

| Methode | Path | Auth | Description | Feature |
|---------|------|------|-------------|---------|
| GET | `/export` | Admin | Export comptable CSV/XLSX | FIN-13 |
| GET | `/budgets/{id}/journal` | Conducteur/Admin | Journal modifications | FIN-15 |

### 16.8 Filtres achats

| Parametre | Type | Description |
|-----------|------|-------------|
| `chantier_id` | int | Filtrer par chantier |
| `fournisseur_id` | int | Filtrer par fournisseur |
| `statut` | enum | DEMANDE / VALIDE / COMMANDE / LIVRE / FACTURE |
| `type_achat` | enum | MATERIAU / MATERIEL / SOUS_TRAITANCE / SERVICE |
| `date_debut` | date | Achats depuis cette date |
| `date_fin` | date | Achats jusqu'a cette date |
| `montant_min` | decimal | Montant HT minimum |
| `montant_max` | decimal | Montant HT maximum |
| `q` | string | Recherche texte (libelle, fournisseur) |
| `limit` | int | Pagination (defaut 50) |
| `offset` | int | Offset |

---

## 17. ARCHITECTURE TECHNIQUE

### 17.1 Structure des fichiers

```
backend/modules/financier/
|
+-- domain/
|   +-- entities/
|   |   +-- budget.py               # Entite budget (conteneur)
|   |   +-- ligne_budgetaire.py     # Lot budgetaire
|   |   +-- achat.py                # Achat / bon de commande
|   |   +-- avenant.py              # Avenant budgetaire
|   |   +-- situation_travaux.py    # Situation mensuelle
|   |   +-- ligne_situation.py      # Ligne avancement par lot
|   |   +-- fournisseur.py          # Fournisseur
|   |   +-- journal_financier.py    # Trace audit
|   +-- value_objects/
|   |   +-- statut_achat.py         # Machine a etats achats
|   |   +-- statut_situation.py     # Machine a etats situations
|   |   +-- type_achat.py           # MATERIAU/MATERIEL/ST/SERVICE
|   |   +-- type_fournisseur.py     # NEGOCE/LOUEUR/ST/SERVICE
|   |   +-- taux_tva.py             # 20%/10%/5.5%/0%
|   |   +-- unite_mesure.py         # Reutilise module taches
|   +-- repositories/
|   |   +-- budget_repository.py         # Interface abstraite
|   |   +-- ligne_budgetaire_repository.py
|   |   +-- achat_repository.py
|   |   +-- avenant_repository.py
|   |   +-- situation_repository.py
|   |   +-- fournisseur_repository.py
|   |   +-- journal_repository.py
|   +-- events/
|   |   +-- financier_events.py     # 15 evenements domaine
|   +-- services/
|       +-- calcul_budget_service.py # Calculs financiers purs
|
+-- application/
|   +-- use_cases/
|   |   +-- budget/
|   |   |   +-- create_budget.py
|   |   |   +-- get_budget.py
|   |   |   +-- get_dashboard.py
|   |   +-- lignes/
|   |   |   +-- add_ligne.py
|   |   |   +-- update_ligne.py
|   |   |   +-- delete_ligne.py
|   |   +-- achats/
|   |   |   +-- create_achat.py
|   |   |   +-- validate_achat.py
|   |   |   +-- refuse_achat.py
|   |   |   +-- progress_achat.py    # commander/livrer/facturer
|   |   |   +-- list_achats.py
|   |   |   +-- list_achats_en_attente.py
|   |   +-- avenants/
|   |   |   +-- create_avenant.py
|   |   |   +-- list_avenants.py
|   |   +-- situations/
|   |   |   +-- create_situation.py
|   |   |   +-- update_lignes_situation.py
|   |   |   +-- submit_situation.py
|   |   |   +-- validate_situation.py
|   |   |   +-- reject_situation.py
|   |   |   +-- validate_client.py
|   |   |   +-- facture_situation.py
|   |   |   +-- generate_pdf.py
|   |   +-- fournisseurs/
|   |   |   +-- crud_fournisseur.py  # Create/Read/Update/Archive
|   |   +-- export/
|   |   |   +-- export_comptable.py
|   |   +-- journal/
|   |       +-- list_journal.py
|   +-- dtos/
|   |   +-- budget_dtos.py
|   |   +-- ligne_dtos.py
|   |   +-- achat_dtos.py
|   |   +-- avenant_dtos.py
|   |   +-- situation_dtos.py
|   |   +-- fournisseur_dtos.py
|   |   +-- dashboard_dtos.py
|   |   +-- journal_dtos.py
|   +-- ports/
|       +-- pdf_generator_port.py    # Interface generation PDF
|
+-- adapters/
|   +-- controllers/
|   |   +-- budget_controller.py
|   |   +-- achat_controller.py
|   |   +-- situation_controller.py
|   |   +-- fournisseur_controller.py
|   +-- presenters/
|   |   +-- budget_presenter.py
|   |   +-- dashboard_presenter.py
|   +-- providers/
|       +-- pdf_generator_provider.py
|
+-- infrastructure/
    +-- persistence/
    |   +-- models.py                    # 8 tables SQLAlchemy
    |   +-- sqlalchemy_budget_repository.py
    |   +-- sqlalchemy_ligne_repository.py
    |   +-- sqlalchemy_achat_repository.py
    |   +-- sqlalchemy_avenant_repository.py
    |   +-- sqlalchemy_situation_repository.py
    |   +-- sqlalchemy_fournisseur_repository.py
    |   +-- sqlalchemy_journal_repository.py
    +-- web/
        +-- financier_routes.py          # ~35 endpoints FastAPI
        +-- dependencies.py              # Injection de dependances
```

### 17.2 Tables base de donnees

**Table `budgets`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| chantier_id | INTEGER | FK chantiers, UNIQUE, NOT NULL |
| retenue_garantie_pct | DECIMAL(5,2) | NOT NULL, default 5.00 |
| seuil_alerte_pct | DECIMAL(5,2) | NOT NULL, default 110.00 |
| seuil_validation_achat | DECIMAL(12,2) | NOT NULL, default 5000.00 |
| created_by | INTEGER | FK users, NOT NULL |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes : `UNIQUE(chantier_id)`

**Table `lignes_budgetaires`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| budget_id | INTEGER | FK budgets, NOT NULL, INDEX |
| parent_id | INTEGER | FK lignes_budgetaires, nullable |
| code_lot | VARCHAR(30) | NOT NULL |
| libelle | VARCHAR(200) | NOT NULL |
| unite | ENUM | NOT NULL |
| quantite_prevue | DECIMAL(12,3) | NOT NULL, >= 0 |
| prix_unitaire_ht | DECIMAL(12,2) | NOT NULL, >= 0 |
| total_prevu_ht | DECIMAL(14,2) | NOT NULL (calcule) |
| ordre | INTEGER | NOT NULL, default 0 |
| tache_id | INTEGER | FK taches, nullable |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes : `UNIQUE(budget_id, code_lot)`, `(budget_id, parent_id)`, `(tache_id)`

**Table `achats`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| chantier_id | INTEGER | FK chantiers, NOT NULL, INDEX |
| fournisseur_id | INTEGER | FK fournisseurs, NOT NULL, INDEX |
| ligne_budgetaire_id | INTEGER | FK lignes_budgetaires, nullable, INDEX |
| type_achat | ENUM | NOT NULL |
| libelle | VARCHAR(300) | NOT NULL |
| quantite | DECIMAL(12,3) | NOT NULL, > 0 |
| unite | ENUM | NOT NULL |
| prix_unitaire_ht | DECIMAL(12,2) | NOT NULL, > 0 |
| total_ht | DECIMAL(14,2) | NOT NULL |
| taux_tva | ENUM | NOT NULL |
| total_ttc | DECIMAL(14,2) | NOT NULL |
| date_commande | DATE | NOT NULL |
| date_livraison_prevue | DATE | nullable |
| statut | ENUM | NOT NULL, default 'demande', INDEX |
| motif_refus | TEXT | nullable |
| numero_facture | VARCHAR(100) | nullable |
| commentaire | TEXT | nullable |
| demandeur_id | INTEGER | FK users, NOT NULL, INDEX |
| valideur_id | INTEGER | FK users, nullable |
| validated_at | DATETIME | nullable |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes : `(chantier_id, statut)`, `(fournisseur_id)`, `(demandeur_id, statut)`, `(ligne_budgetaire_id)`

**Table `avenants`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| budget_id | INTEGER | FK budgets, NOT NULL, INDEX |
| numero | INTEGER | NOT NULL |
| motif | VARCHAR(500) | NOT NULL |
| montant_ht | DECIMAL(14,2) | NOT NULL |
| date_avenant | DATE | NOT NULL |
| created_by | INTEGER | FK users, NOT NULL |
| created_at | DATETIME | auto |

Indexes : `UNIQUE(budget_id, numero)`

**Table `situations_travaux`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| budget_id | INTEGER | FK budgets, NOT NULL, INDEX |
| numero | VARCHAR(20) | NOT NULL, UNIQUE |
| periode_debut | DATE | NOT NULL |
| periode_fin | DATE | NOT NULL |
| statut | ENUM | NOT NULL, default 'brouillon', INDEX |
| taux_tva | ENUM | NOT NULL |
| document_id | INTEGER | FK documents, nullable |
| created_by | INTEGER | FK users, NOT NULL |
| validated_by | INTEGER | FK users, nullable |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes : `(budget_id, statut)`, `UNIQUE(numero)`
CHECK : `periode_fin > periode_debut`

**Table `lignes_situations`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| situation_id | INTEGER | FK situations_travaux, NOT NULL, INDEX |
| ligne_budgetaire_id | INTEGER | FK lignes_budgetaires, NOT NULL |
| avancement_pct | DECIMAL(5,2) | NOT NULL, CHECK 0..100 |

Indexes : `UNIQUE(situation_id, ligne_budgetaire_id)`

**Table `fournisseurs`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| raison_sociale | VARCHAR(200) | NOT NULL |
| type_fournisseur | ENUM | NOT NULL |
| siret | VARCHAR(14) | nullable, CHECK pattern |
| adresse | TEXT | nullable |
| contact_principal | VARCHAR(200) | nullable |
| telephone | VARCHAR(20) | nullable |
| email | VARCHAR(200) | nullable |
| conditions_paiement | VARCHAR(200) | nullable |
| notes | TEXT | nullable |
| actif | BOOLEAN | NOT NULL, default true, INDEX |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto |

Indexes : `(type_fournisseur, actif)`, `(raison_sociale)`

**Table `journal_financier`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| budget_id | INTEGER | FK budgets, NOT NULL, INDEX |
| type_operation | VARCHAR(50) | NOT NULL, INDEX |
| entite_type | VARCHAR(50) | NOT NULL |
| entite_id | INTEGER | NOT NULL |
| description | TEXT | NOT NULL |
| donnees_avant | JSON | nullable |
| donnees_apres | JSON | nullable |
| auteur_id | INTEGER | FK users, NOT NULL |
| created_at | DATETIME | auto |

Indexes : `(budget_id, created_at DESC)`, `(auteur_id)`

**Table `taux_horaires`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| metier | VARCHAR(50) | NOT NULL |
| taux_horaire_ht | DECIMAL(8,2) | NOT NULL |
| taux_majoration_sup | DECIMAL(4,2) | NOT NULL, default 1.25 |
| date_effet | DATE | NOT NULL |
| actif | BOOLEAN | NOT NULL, default true |

Indexes : `(metier, actif)`, `UNIQUE(metier, date_effet)`

**Table `tarifs_materiel`** :

| Colonne | Type | Contraintes |
|---------|------|-------------|
| id | INTEGER | PK, auto |
| ressource_id | INTEGER | FK logistique.ressources, nullable |
| categorie | VARCHAR(50) | NOT NULL |
| libelle | VARCHAR(200) | NOT NULL |
| tarif_journalier_ht | DECIMAL(10,2) | NOT NULL |
| date_effet | DATE | NOT NULL |
| actif | BOOLEAN | NOT NULL, default true |

Indexes : `(categorie, actif)`

### 17.3 Frontend - Composants prevus

| Composant | Fichier | Responsabilite |
|-----------|---------|---------------|
| `BudgetTab` | BudgetTab.tsx | Onglet principal dans fiche chantier |
| `BudgetDashboard` | BudgetDashboard.tsx | Cartes KPI + graphiques |
| `KPICard` | KPICard.tsx | Carte indicateur avec couleur seuil |
| `LotBudgetTable` | LotBudgetTable.tsx | Tableau des lots avec Budget/Engage/Realise |
| `LotBudgetForm` | LotBudgetForm.tsx | Modal ajout/modification lot |
| `AchatList` | AchatList.tsx | Liste achats avec filtres |
| `AchatForm` | AchatForm.tsx | Modal creation/modification achat |
| `AchatValidationQueue` | AchatValidationQueue.tsx | File achats en attente |
| `AchatActions` | AchatActions.tsx | Boutons valider/refuser/progresser |
| `SituationList` | SituationList.tsx | Liste situations |
| `SituationForm` | SituationForm.tsx | Saisie avancements par lot |
| `SituationPDFPreview` | SituationPDFPreview.tsx | Previsualisation PDF |
| `AvenantList` | AvenantList.tsx | Liste avenants |
| `AvenantForm` | AvenantForm.tsx | Modal creation avenant |
| `FournisseurList` | FournisseurList.tsx | Referentiel fournisseurs |
| `FournisseurForm` | FournisseurForm.tsx | Modal creation/edition fournisseur |
| `BarChartLots` | BarChartLots.tsx | Graphique barres Budget/Engage/Realise |
| `DonutRepartition` | DonutRepartition.tsx | Donut repartition couts |
| `CourbeSAvancement` | CourbeSAvancement.tsx | Courbe en S physique vs financier |
| `JournalFinancier` | JournalFinancier.tsx | Historique modifications |

**Hooks prevus** :

| Hook | Responsabilite |
|------|---------------|
| `useBudget(chantierId)` | Chargement budget + lignes + KPI |
| `useAchats(filters)` | CRUD achats + filtres + pagination |
| `useAchatsEnAttente()` | File de validation |
| `useSituations(budgetId)` | CRUD situations |
| `useFournisseurs(filters)` | CRUD fournisseurs |
| `useDashboardFinancier(chantierId)` | Donnees dashboard (KPI + graphs) |
| `useJournalFinancier(budgetId)` | Historique modifications |

**Schemas Zod prevus** :

| Schema | Valide |
|--------|--------|
| `ligneBudgetaireSchema` | Code lot, libelle, unite, quantite, PU |
| `achatSchema` | Type, fournisseur, chantier, montants, TVA |
| `avenantSchema` | Motif, montant, date |
| `situationLigneSchema` | Avancement % (0-100) |
| `fournisseurSchema` | Raison sociale, type, SIRET optionnel |
| `exportSchema` | Chantier, dates, format |

---

## 18. SCENARIOS DE TEST

### Scenario 1 : Creation budget et ajout lots

```
GIVEN un chantier "2026-01-MONTMELIAN" sans budget
AND un conducteur affecte a ce chantier

WHEN le conducteur cree un budget
THEN le budget est cree avec retenue 5%, seuil alerte 110%, seuil achat 5000
AND un BudgetCreatedEvent est publie

WHEN le conducteur ajoute 3 lots :
  LOT-01 Gros oeuvre : 100m3 x 1500 EUR = 150 000 EUR
  LOT-02 Charpente : 1 forfait x 80 000 EUR = 80 000 EUR
  LOT-03 Couverture : 350m2 x 100 EUR = 35 000 EUR
THEN montant_initial_ht = 265 000 EUR
AND montant_revise_ht = 265 000 EUR (pas d'avenant)
AND 3 entrees dans le journal financier
```

### Scenario 2 : Achat avec auto-validation (< seuil)

```
GIVEN un budget avec seuil_validation_achat = 5000 EUR
AND un chef de chantier

WHEN le chef cree un achat de 2 500 EUR HT (beton)
THEN l'achat est cree directement en statut VALIDE (auto-validation)
AND aucune notification de validation envoyee
AND le total engage du lot augmente de 2 500 EUR
```

### Scenario 3 : Achat avec validation hierarchique (>= seuil)

```
GIVEN un budget avec seuil_validation_achat = 5000 EUR
AND un chef de chantier "Sebastien"
AND un conducteur "Thomas"

WHEN Sebastien cree un achat de 12 500 EUR HT (acier)
THEN l'achat est cree en statut DEMANDE
AND Thomas recoit une notification push "Achat 12 500 EUR en attente"

WHEN Thomas valide l'achat
THEN le statut passe a VALIDE
AND Sebastien recoit une notification "Achat valide"
AND le total engage du lot augmente de 12 500 EUR
AND valideur_id = Thomas.id, validated_at = now()
```

### Scenario 4 : Refus d'achat

```
GIVEN un achat DEMANDE de 8 000 EUR (sous-traitance electricite)

WHEN le conducteur refuse avec motif "Tarif trop eleve, renegocier"
THEN le statut passe a REFUSE (final)
AND motif_refus = "Tarif trop eleve, renegocier"
AND le demandeur recoit notification "Achat refuse : Tarif trop eleve"
AND le total engage ne change pas
```

### Scenario 5 : Cycle complet achat jusqu'a facturation

```
GIVEN un achat VALIDE de 3 200 EUR pour "Parpaings"

WHEN le chef passe la commande au fournisseur
THEN POST /achats/{id}/commander → statut COMMANDE

WHEN la livraison arrive sur chantier
THEN POST /achats/{id}/livrer → statut LIVRE

WHEN la facture fournisseur arrive (FAC-2026-0142)
THEN POST /achats/{id}/facturer body: {numero_facture: "FAC-2026-0142"}
AND statut = FACTURE (definitif)
AND total_realise du lot augmente de 3 200 EUR
AND aucune modification n'est plus possible sur cet achat
```

### Scenario 6 : Situation de travaux - cycle complet

```
GIVEN un budget avec 3 lots et une situation precedente (SIT-2026-02)
  LOT-01 : avancement precedent 45%
  LOT-02 : avancement precedent 30%
  LOT-03 : avancement precedent 0%

WHEN le conducteur cree une nouvelle situation
THEN SIT-2026-03 est creee en BROUILLON
AND les lignes sont pre-remplies avec avancements precedents

WHEN le conducteur saisit les nouveaux avancements :
  LOT-01 : 60% (etait 45%)
  LOT-02 : 50% (etait 30%)
  LOT-03 : 20% (etait 0%)
THEN les montants periode sont calcules automatiquement

WHEN le conducteur soumet la situation
THEN statut passe a EN_VALIDATION
AND l'admin recoit notification "SIT-2026-03 a valider"

WHEN l'admin valide
THEN statut passe a EMISE
AND un PDF est genere avec le contenu conforme
AND le PDF est archive dans la GED du chantier

WHEN le client signe et retourne la situation
THEN l'admin valide cote client → statut VALIDEE

WHEN l'admin facture
THEN statut passe a FACTUREE (definitif)
```

### Scenario 7 : Rejet de situation

```
GIVEN une situation SIT-2026-04 en statut EN_VALIDATION

WHEN l'admin rejette avec motif "Avancement LOT-02 incoherent"
THEN le statut retourne a BROUILLON
AND le conducteur recoit notification "Situation rejetee"
AND le conducteur peut corriger et resoumettre
```

### Scenario 8 : Avenant budgetaire

```
GIVEN un budget initial de 265 000 EUR

WHEN le conducteur cree un avenant :
  Motif: "Travaux supplementaires fondations suite etude sol"
  Montant: +15 000 EUR
THEN avenant AV-01 cree
AND montant_revise = 265 000 + 15 000 = 280 000 EUR
AND les seuils d'alerte sont recalcules sur le nouveau montant

WHEN le conducteur cree un second avenant :
  Motif: "Moins-value couverture (surface reduite)"
  Montant: -3 000 EUR
THEN avenant AV-02 cree
AND montant_revise = 280 000 - 3 000 = 277 000 EUR
```

### Scenario 9 : Alerte depassement budget

```
GIVEN un budget revise de 277 000 EUR, seuil alerte 110%
AND total engage = 290 000 EUR (> 277 000 x 1.10 = 304 700)
  -- En fait 290 000 < 304 700, pas d'alerte

GIVEN total engage = 310 000 EUR (> 304 700)
THEN DepassementBudgetEvent publie
AND l'admin recoit notification push "Depassement budget chantier MONTMELIAN"
AND la carte KPI "Engage" passe en rouge dans le dashboard
```

### Scenario 10 : Integration couts main-d'oeuvre

```
GIVEN taux horaire macon = 35 EUR/h, majoration sup = 1.25
AND le module Pointages publie FeuilleHeuresValideeEvent :
  chantier_id: 1, user_id: 5, metier: MACON
  heures_normales: 38, heures_sup: 3

THEN le module financier calcule :
  Cout normal = 38 x 35 = 1 330 EUR
  Cout sup = 3 x 35 x 1.25 = 131.25 EUR
  Total = 1 461.25 EUR

AND total_realise du budget augmente de 1 461.25 EUR
```

### Scenario 11 : Permissions

```
GIVEN un compagnon "Carlos"

WHEN Carlos tente GET /financier/chantiers/1/budget
THEN HTTP 403 Forbidden (compagnon n'a pas acces au budget)

WHEN Carlos tente POST /financier/achats
THEN HTTP 403 Forbidden (compagnon ne peut pas creer d'achat)
```

```
GIVEN un chef de chantier "Sebastien" affecte au chantier 1 mais pas au chantier 2

WHEN Sebastien tente GET /financier/chantiers/1/budget
THEN HTTP 200 (son chantier)

WHEN Sebastien tente GET /financier/chantiers/2/budget
THEN HTTP 403 Forbidden (pas son chantier)
```

### Scenario 12 : Verrouillage facturation

```
GIVEN un achat en statut FACTURE avec numero "FAC-2026-0142"

WHEN un utilisateur tente PUT /financier/achats/{id}
THEN HTTP 400 "Achat facture non modifiable"

WHEN un utilisateur tente POST /financier/achats/{id}/livrer
THEN HTTP 400 "Transition invalide depuis statut FACTURE"
```

---

## 19. EVOLUTIONS FUTURES

| Evolution | Description | Impact |
|-----------|-------------|--------|
| **Import factures PDF** | Scan + OCR pour extraire montants automatiquement | Integration service OCR |
| **Previsionnel a terminaison (EAC)** | Estimation automatique du cout final | Calculs predictifs |
| **Cash flow previsionnel** | Projection encaissements vs decaissements | Courbe de tresorerie |
| **Mode hors-ligne** | Consultation budget + saisie achats offline | Service Worker + sync |
| **Multi-devises** | Support EUR, CHF, USD | Taux de change + conversion |
| **Integration ERP** | Synchronisation bidirectionnelle Sage/Cegid | API connecteur |
| **Reception livraisons** | Validation quantite/qualite avec photo | Nouveau workflow |
| **Facturation electronique** | Factur-X / ZUGFeRD conforme | Generation PDF/A-3 |
| **Analytique avancee** | Cout au m2, rentabilite par type de chantier | Reporting BI |

---

## 20. REFERENCES CDC

| Section CDC | Description | Fonctionnalites |
|-------------|-------------|-----------------|
| Section 17 | Gestion Financiere et Budgetaire | FIN-01 a FIN-15 |
| Section 4 | Gestion Chantiers | chantier_id FK, onglet Budget |
| Section 13 | Gestion Taches | tache_id FK (FIN-03) |
| Section 7 | Feuilles d'Heures | Integration couts MO (FIN-09) |
| Section 11 | Logistique | Integration couts materiel (FIN-10) |
| Section 9 | GED | Archivage PDF situations |
| Section 3 | Utilisateurs | Roles et permissions |

### Fichiers de reference existants

| Fichier | Role |
|---------|------|
| `docs/SPECIFICATIONS.md` (Section 17) | Specifications fonctionnelles |
| `backend/modules/taches/domain/value_objects/` | UniteMesure reutilisable |
| `backend/modules/logistique/domain/events/` | Pattern evenements a suivre |
| `backend/modules/pointages/` | Source couts main-d'oeuvre |
| `backend/modules/logistique/` | Source couts materiel |
| `backend/modules/documents/` | GED pour archivage PDF |
| `backend/modules/notifications/` | Handlers push Firebase |

### Migration prevue

| Fichier | Description |
|---------|-------------|
| `backend/migrations/versions/YYYYMMDD_NNNN_financier_schema.py` | Creation 10 tables + indexes |

---

**Document de specification workflow — Module Financier**
**Statut : SPECS READY — Implementation a venir**
**Derniere mise a jour : 31 janvier 2026**

## 17. GESTION FINANCIERE ET BUDGETAIRE

### 17.1 Vue d'ensemble

Le module Financier centralise le suivi economique des chantiers : budgets previsionnels par lots, achats fournisseurs, situations de travaux et analyse de rentabilite. Il s'integre aux modules Chantiers, Taches, Feuilles d'Heures et Logistique pour offrir une vision consolidee couts/avancement.

**Interface moderne** : Dashboard visuel unifie avec graphiques interactifs (courbes d'evolution, camemberts, barres comparatives), alertes en temps reel et indicateurs intelligents. Inspire des meilleures pratiques du marche (Graneet, Kalitics) pour offrir une experience utilisateur competitive.

**Deux points d'acces** :
1. **Vue chantier** : Onglet Budget dans la fiche chantier (pilotage operationnel)
2. **Vue consolidee** : Page Finances globale (vision strategique multi-chantiers)

Cette double approche permet aux conducteurs de piloter chaque chantier finement, et a la direction d'avoir une vision portfolio instantanee de la rentabilite de l'entreprise.

### 17.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| **Phase 1 & 2 - Fondations (COMPLET)** ||||
| FIN-01 | Onglet Budget par chantier | Accessible depuis la fiche chantier, affiche budget + KPI + dernieres operations | ✅ Backend + Frontend |
| FIN-02 | Budget previsionnel par lots | Decomposition arborescente par lots et postes (code lot, libelle, unite, quantite, PU HT) | ✅ Backend + Frontend |
| FIN-04 | Avenants budgetaires | Creation d'avenants avec motif, montant et impact automatique sur budget revise | ✅ Backend + Frontend |
| FIN-05 | Saisie achats / bons de commande | Creation achats avec fournisseur, lot, montant HT, TVA, statut et workflow validation | ✅ Backend + Frontend |
| FIN-06 | Validation hierarchique achats | Approbation requise par Conducteur/Admin si montant > seuil configurable (defaut 5 000 EUR HT) | ✅ Backend + Frontend |
| FIN-07 | Situations de travaux | Creation situations mensuelles basees sur avancement reel, workflow 5 etapes, generation PDF | ✅ Backend + Frontend |
| FIN-08 | Facturation client | Generation factures/acomptes depuis situations validees avec retenue de garantie | ✅ Backend + Frontend |
| FIN-09 | Suivi couts main-d'oeuvre | Integration automatique heures validees (module Pointages) x taux horaire par metier | ✅ Backend + Frontend |
| FIN-10 | Suivi couts materiel | Integration automatique reservations (module Logistique) x tarif journalier | ✅ Backend + Frontend |
| FIN-11 | Tableau de bord financier | Dashboard unifie avec 5 KPI, graphiques interactifs, alertes visibles, dernieres operations | ✅ Backend + Frontend |
| FIN-12 | Alertes depassements | Banniere visible + notifications push si (Engage + Reste a faire) > Budget x seuil (110%) | ✅ Backend + Frontend |
| FIN-14 | Referentiel fournisseurs | Gestion fournisseurs (raison sociale, type, SIRET, contact, conditions paiement) | ✅ Backend + Frontend |
| FIN-15 | Historique et tracabilite | Journal complet des modifications budgetaires avec auteur, date et motif | ✅ Backend + Frontend |
| **Phase 3 - UX Moderne & Intelligence (EN COURS)** ||||
| FIN-16 | Indicateur "Reste a depenser" | Carte KPI Budget - Engage - Realise avec jauge visuelle et alerte si negatif | 🚧 Specs ready |
| FIN-17 | Graphique evolution temporelle | Courbe comparative Budget/Engage/Realise sur timeline du chantier (mensuel) | 🚧 Specs ready |
| FIN-18 | Graphique repartition lots | Camembert interactif montrant % budget par lot avec drill-down details | 🚧 Specs ready |
| FIN-19 | Graphique barres comparatives | Barres empilees Prevu/Engage/Realise par lot avec code couleur depassements | 🚧 Specs ready |
| FIN-20 | Vue consolidee multi-chantiers | Page Finances avec tableau comparatif tous chantiers + KPI globaux entreprise | 🚧 Specs ready |
| FIN-21 | Suggestions intelligentes | Algorithme detectant anomalies et proposant actions (avenant, optimisation, alerte) | 🚧 Specs ready |
| FIN-22 | Indicateurs predictifs | Burn rate, projection fin chantier, avancement physique vs financier | 🚧 Specs ready |
| **Phase 4 - Integration & Exports (FUTUR)** ||||
| FIN-03 | Affectation budgets aux taches | Liaison optionnelle taches <-> lignes budgetaires pour suivi avancement financier | 🔮 Phase 4 |
| FIN-13 | Export comptable | Generation CSV/Excel avec codes analytiques chantier, compatible logiciels comptables | 🔮 Phase 4 |
| FIN-23 | Integration ERP | Synchronisation bidirectionnelle avec logiciels comptables (Sage, Cegid, QuadraExpert) | 🔮 Phase 4 |

### 17.3 Structure d'un budget

| Champ | Type | Description |
|-------|------|-------------|
| Code lot | Texte | Ex: LOT-01, LOT-02-MACON |
| Libelle | Texte | Description du poste |
| Unite | Liste | m2, m3, forfait, kg, heure, ml, u |
| Quantite prevue | Nombre | Volume budgete |
| Prix unitaire HT | Montant | Cout unitaire hors taxe |
| Total prevu HT | Calcule | Quantite x Prix unitaire |
| Engage | Montant | Somme bons de commande valides sur ce lot |
| Realise | Montant | Somme factures recues sur ce lot |
| Reste a faire | Calcule | Total prevu - Realise |
| Ecart | Calcule | Realise - Total prevu (positif = depassement) |

### 17.4 Tableau de bord financier

Le tableau de bord s'affiche dans l'onglet Budget de chaque chantier. Design moderne inspire de Graneet/Kalitics : **toutes les informations essentielles visibles en un ecran sans navigation**.

#### 17.4.1 SECTION 1 - Banniere alertes (conditionnelle)

Affichee uniquement si alertes actives. Positionnee en haut pour visibilite maximale.

```
┌────────────────────────────────────────────────────┐
│ ⚠️ 2 alertes budgetaires                          │
│ • Lot 2 - Gros oeuvre: Depassement prevu +12%     │
│ • Achat #245 en attente validation depuis 5j      │
│ [Voir toutes les alertes]                         │
└────────────────────────────────────────────────────┘
```

**UX** : Fond orange clair, bordure gauche orange foncee, bouton cliquable vers AlertesPanel.

---

#### 17.4.2 SECTION 2 - Cartes KPI (5 cartes)

Grille responsive : 5 colonnes desktop, 2 colonnes tablette, 1 colonne mobile.

| Indicateur | Formule | Visualisation | Couleur seuil |
|------------|---------|---------------|---------------|
| **Budget revise HT** | Budget initial + Avenants | Montant + badge "Initial: XXX EUR" | Bleu neutre |
| **Engage** | Somme bons de commande valides | Montant + jauge circulaire % | Orange > 90%, Rouge > 100% |
| **Realise** | Somme factures + couts MO + couts materiel | Montant + jauge circulaire % | Orange > 90%, Rouge > 100% |
| **Reste a depenser** ⭐ | Budget revise - Engage - Realise | Montant + jauge circulaire % | Rouge si negatif |
| **Marge estimee** | ((Budget revise - Realise) / Budget revise) x 100 | Pourcentage + trend icon | Rouge < 5%, Orange < 10% |

**Design** :
- Jauge circulaire SVG (arc 270°) pour Engage/Realise/Reste
- Icone trending-up/down pour Marge
- Animation transition sur changement valeur
- Badge "Initial" sous Budget revise si avenants existent

---

#### 17.4.3 SECTION 3 - Graphiques interactifs (2 colonnes)

**Colonne gauche : Evolution temporelle**

```
┌─────────────────────────────────────┐
│ Evolution financiere                │
│                                     │
│ [Graphique courbes - Recharts]     │
│  Axe X: Mois (depuis debut chantier│
│  Axe Y: Montants EUR                │
│  Courbe bleue: Prevu (budget lisse) │
│  Courbe orange: Engage cumule       │
│  Courbe verte: Realise cumule       │
│                                     │
│ Legende interactive + tooltip hover│
└─────────────────────────────────────┘
```

**Donnees** : Agregation mensuelle depuis `chantier.date_debut` jusqu'a aujourd'hui + projection jusqu'a `date_fin_prevue`.

**Colonne droite : Repartition par lot**

```
┌─────────────────────────────────────┐
│ Repartition budget par lot          │
│                                     │
│ [Graphique camembert - Recharts]   │
│  Secteurs colores par lot           │
│  Labels: Code lot + % du total      │
│  Tooltip: Libelle + montant EUR     │
│                                     │
│ Click secteur → Drill-down details │
└─────────────────────────────────────┘
```

**Alternative tablette/mobile** : Barres horizontales empilees au lieu de camembert.

---

#### 17.4.4 SECTION 4 - Graphique barres comparatives

```
┌──────────────────────────────────────────────────────┐
│ Comparaison Prevu / Engage / Realise par lot        │
│                                                      │
│ [Graphique barres groupees - Recharts]              │
│  Axe X: Code lot                                     │
│  Axe Y: Montants EUR                                 │
│  Barre bleue: Total prevu HT                         │
│  Barre orange: Engage                                │
│  Barre verte: Realise                                │
│                                                      │
│  Surlignage rouge si Realise > Prevu                 │
└──────────────────────────────────────────────────────┘
```

**UX** : Click sur barre → Ouvre modal details du lot.

---

#### 17.4.5 SECTION 5 - Top 5 lots (tableau resume)

Tableau compact affichant les 5 lots les plus importants (tri par `total_prevu_ht DESC`).

| Code | Libelle | Budget | Engage | Realise | Reste | Status |
|------|---------|--------|--------|---------|-------|--------|
| LOT-01 | Gros oeuvre | 120k | 95k | 80k | 40k | 🟢 OK |
| LOT-02 | Fondations | 80k | 82k | 70k | 10k | 🟠 Alerte |
| ... | ... | ... | ... | ... | ... | ... |

**UX** : Bouton "Voir tous les lots (12)" en bas du tableau → Ouvre modal LotsBudgetairesTable complet.

---

#### 17.4.6 SECTION 6 - Dernieres operations (2 colonnes)

**Colonne gauche : 5 derniers achats**

| Date | Libelle | Fournisseur | Montant | Statut |
|------|---------|-------------|---------|--------|
| 31/01 | Beton C25/30 | Cemex | 12 500 EUR | ✅ Livre |
| ... | ... | ... | ... | ... |

**Colonne droite : 3 dernieres situations**

| N° | Date | Montant | Statut |
|----|------|---------|--------|
| SIT-2026-03 | 30/01 | 45 000 EUR | ✅ Validee |
| ... | ... | ... | ... |

**UX** : Click ligne → Ouvre modal details (AchatModal ou SituationDetail).

---

#### 17.4.7 SECTION 7 - Actions rapides

Boutons en bas de page pour actions frequentes :

```
[+ Ajouter lot]  [+ Nouvel achat]  [+ Creer avenant]  [+ Nouvelle situation]  [📊 Export]
```

**UX** : Boutons outlined avec icones, espaces equidistants, responsive (empilement mobile).

---

#### 17.4.8 Navigation secondaire (onglets)

Les 8 sous-sections (Lots, Achats, Avenants, Situations, Factures, Couts MO, Couts Materiel, Alertes) restent accessibles via onglets pour consultation detaillee, mais **ne sont plus la vue par defaut**.

**Principe** : Dashboard = synthese actionable, Onglets = details exhaustifs.

### 17.5 Workflow situation de travaux

Une situation de travaux est un document contractuel recapitulant l'avancement des travaux sur une periode donnee (generalement mensuelle) et servant de base a la facturation.

#### 17.5.1 Etapes du workflow

| Etape | Responsable | Actions | Statut |
|-------|-------------|---------|--------|
| 1. Preparation | Conducteur | Saisie avancement par lot, calcul montant periode | Brouillon |
| 2. Validation interne | Admin/Direction | Verification coherence, correction si besoin | En validation |
| 3. Emission client | Conducteur | Generation PDF, envoi email client | Emise |
| 4. Validation client | — | Signature/validation du montant par le client | Validee |
| 5. Facturation | Admin | Creation facture, marquage "Facturee" | Facturee |

#### 17.5.2 Contenu du document PDF

- En-tete : Logo Greg Construction, coordonnees, numero situation (SIT-AAAA-NN)
- Client : Nom maitre d'ouvrage, projet, adresse chantier
- Tableau recapitulatif : Lot | Montant marche | % avancement | Montant periode | Montant cumule
- Totaux : Cumul precedent + Periode = Cumul total
- Retenue de garantie (parametrable : 0%, 5% ou 10%)
- Montant a facturer HT / TVA / TTC
- Signatures : Conducteur + Client

### 17.6 Gestion des achats

#### 17.6.1 Structure d'un achat

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| Type | Liste | Oui | Materiau / Materiel / Sous-traitance / Service |
| Fournisseur | Reference | Oui | Choix dans le referentiel fournisseurs |
| Chantier | Reference | Oui | Affectation au projet |
| Lot budgetaire | Reference | Non | Liaison avec la ligne de budget |
| Libelle | Texte | Oui | Description de l'achat |
| Quantite | Nombre | Oui | Quantite commandee |
| Unite | Liste | Oui | m2, kg, unite, forfait, ml, m3 |
| Prix unitaire HT | Montant | Oui | Cout unitaire hors taxe |
| Total HT | Calcule | — | Quantite x Prix unitaire |
| TVA | Taux | Oui | 20%, 10%, 5.5%, 0% |
| Total TTC | Calcule | — | Total HT x (1 + TVA) |
| Date commande | Date | Oui | Date du bon de commande |
| Date livraison prevue | Date | Non | Echeance de livraison |
| Statut | Liste | Oui | Demande / Valide / Commande / Livre / Facture |
| N facture fournisseur | Texte | Non | Reference facture fournisseur |
| Commentaire | Texte | Non | Notes complementaires |

#### 17.6.2 Workflow validation achats

- Montant >= seuil configurable (defaut 5 000 EUR HT) : approbation Conducteur/Admin requise
- Montant < seuil : passage direct au statut "Valide"
- Statut "Facture" est definitif (aucune modification autorisee ensuite)

Etapes si validation requise :

1. Chef de chantier cree la demande d'achat → Statut "Demande"
2. Conducteur recoit notification push pour validation
3. Conducteur approuve → Statut "Valide" → Chef peut passer commande
4. Conducteur refuse → Statut "Refuse" + motif → Chef doit modifier

### 17.7 Referentiel fournisseurs

| Champ | Type | Description |
|-------|------|-------------|
| Raison sociale | Texte | Nom officiel de l'entreprise |
| Type | Liste | Negoce materiaux / Loueur / Sous-traitant / Service |
| SIRET | Texte | Numero identification (14 chiffres) |
| Adresse | Texte | Adresse complete |
| Contact principal | Texte | Nom du commercial/responsable |
| Telephone | Texte | Numero direct |
| Email | Email | Adresse de contact |
| Conditions paiement | Texte | Ex: 30 jours fin de mois |
| Notes | Texte | Informations complementaires |
| Actif | Booleen | Fournisseur actif ou archive |

### 17.8 Matrice des droits - Financier

| Action | Admin | Conducteur | Chef chantier | Compagnon |
|--------|-------|------------|---------------|-----------|
| Voir budget chantier | ✅ | ✅ (ses chantiers) | ✅ (ses chantiers) | ❌ |
| Modifier budget | ✅ | ✅ (ses chantiers) | ❌ | ❌ |
| Creer avenant | ✅ | ✅ (ses chantiers) | ❌ | ❌ |
| Creer demande achat | ✅ | ✅ | ✅ | ❌ |
| Valider achat > seuil | ✅ | ✅ | ❌ | ❌ |
| Voir tous les achats | ✅ | ✅ (ses chantiers) | ✅ (ses achats) | ❌ |
| Creer situation travaux | ✅ | ✅ | ❌ | ❌ |
| Valider situation | ✅ | ❌ | ❌ | ❌ |
| Exporter comptabilite | ✅ | ❌ | ❌ | ❌ |
| Gerer fournisseurs | ✅ | ✅ (lecture) | ❌ | ❌ |

### 17.9 Regles metier

- Tous les montants sont saisis en HT ; TVA calculee automatiquement selon taux configurable par categorie
- Un achat est lie a un seul chantier
- Les situations de travaux sont numerotees automatiquement par chantier (SIT-2026-01, SIT-2026-02...)
- Les situations ne peuvent etre generees qu'apres validation des avancements (lien module Taches)
- L'alerte depassement se declenche si : (Engage + Reste a faire estime) > (Budget revise x seuil configurable)
- La retenue de garantie est parametrable par chantier (0%, 5% ou 10%)
- Les couts main-d'oeuvre sont calcules automatiquement depuis le module Feuilles d'Heures (heures validees x taux horaire metier)
- Les couts materiel sont calcules depuis le module Logistique (reservations x tarif journalier)
- L'export comptable genere un fichier CSV avec codes analytiques chantier pour lettrage comptable
- Tout document financier (situation, facture) est automatiquement reference dans la GED du chantier
- Journal d'audit : chaque modification budgetaire enregistre auteur + timestamp + motif
- Notifications push aux responsables lors de depassement ou validation requise

### 17.10 Integrations avec modules existants

| Module source | Donnees exploitees | Usage financier |
|---------------|-------------------|-----------------|
| Chantiers | ID chantier, nom, maitre d'ouvrage, dates | Rattachement budget, en-tete situations |
| Taches | Avancement %, heures realisees | Calcul avancement situations, courbe en S |
| Feuilles d'Heures (Pointages) | Heures validees par employe/chantier | Cout main-d'oeuvre = heures x taux horaire metier |
| Logistique | Reservations materiel par chantier | Cout materiel = jours reservation x tarif journalier |
| Documents (GED) | Stockage fichiers | Archivage automatique situations PDF et factures |
| Notifications | Push Firebase | Alertes depassement, validation requise |

### 17.11 Vue consolidee multi-chantiers (FIN-20)

**Objectif** : Offrir a la direction et aux conducteurs une vision portfolio instantanee de la sante financiere de tous les chantiers en cours.

**Route** : `/finances` (nouvelle page au meme niveau que `/dashboard`, `/chantiers`, etc.)

**Cible utilisateurs** : Admin (tous chantiers), Conducteur (ses chantiers uniquement)

#### 17.11.1 Structure de la page

**Section 1 : KPI globaux entreprise** (4 cartes)

| Indicateur | Calcul | Usage |
|------------|--------|-------|
| Total Budget Chantiers | Somme budgets revises de tous chantiers actifs | Vision capacite totale |
| Total Engage | Somme engagements tous chantiers | Tresorerie previsionnelle |
| Total Realise | Somme depenses reelles tous chantiers | Flux sortants cumules |
| Marge Moyenne | Moyenne ponderee marges par chantier | Rentabilite globale |

**Section 2 : Tableau comparatif chantiers**

Tableau interactif avec colonnes :

| Colonne | Description | Tri | Filtres |
|---------|-------------|-----|---------|
| Chantier | Nom + code | Alphabetique | Recherche texte |
| Budget Revise | Montant HT | Numerique | — |
| Engage | Montant + % vs budget | Numerique | Alerte si > 90% |
| Realise | Montant + % vs budget | Numerique | Alerte si > 100% |
| Reste a depenser | Montant + couleur | Numerique | Rouge si negatif |
| Marge % | Pourcentage | Numerique | Rouge < 5%, Orange < 10% |
| Alertes | Badge nombre + severity | Nombre | Filtre "Alertes actives" |
| Statut | Ouvert / En cours / Reception / Ferme | — | Filtre multi-select |

**UX** :
- Click ligne → Redirection vers `/chantiers/:id` (onglet Budget)
- Tri multi-colonnes (comme Excel)
- Export CSV/Excel du tableau
- Pagination si > 20 chantiers

**Section 3 : Top/Flop chantiers** (2 colonnes)

**Colonne gauche : Top 3 chantiers rentables**

Classement par marge % decroissante :

```
🥇 Chantier Montmelian - Marge 18.5% (Budget 450k EUR)
🥈 Chantier Albertville - Marge 15.2% (Budget 320k EUR)
🥉 Chantier Chambery - Marge 12.8% (Budget 680k EUR)
```

**Colonne droite : Top 3 chantiers en derive**

Classement par depassement % decroissant :

```
⚠️ Chantier Saint-Jean - Depassement +22% (Alerte critique)
⚠️ Chantier Aix-les-Bains - Depassement +15% (Alerte haute)
⚠️ Chantier Modane - Engage 98% pour 60% realise
```

**UX** : Click → Drill-down vers chantier concern

**Section 4 : Graphiques analytiques** (2 colonnes)

**Colonne gauche : Evolution mensuelle globale**

Graphique courbes empilees montrant l'evolution du cumul Budget/Engage/Realise sur 12 derniers mois.

**Colonne droite : Repartition par statut**

Camembert montrant la repartition du budget total par statut de chantier :
- En cours (70%)
- En reception (20%)
- Ouvert (10%)

#### 17.11.2 Backend - Use Case

**Use Case** : `GetVueConsolideeFinancesUseCase`

**Input** : `user_id` (pour filtrage selon role)

**Output** :
```python
{
  "kpi_globaux": {
    "total_budget_revise": Decimal,
    "total_engage": Decimal,
    "total_realise": Decimal,
    "marge_moyenne_pct": Decimal
  },
  "chantiers": [
    {
      "id": int,
      "nom": str,
      "code": str,
      "budget_revise_ht": Decimal,
      "engage": Decimal,
      "pct_engage": Decimal,
      "realise": Decimal,
      "pct_realise": Decimal,
      "reste_a_depenser": Decimal,
      "marge_pct": Decimal,
      "nb_alertes": int,
      "statut": StatutChantier
    }
  ],
  "top_rentables": List[ChantierFinancierSummary],
  "top_derives": List[ChantierFinancierSummary]
}
```

**Regles** :
- Admin voit tous les chantiers
- Conducteur voit uniquement ses chantiers (via `affectations`)
- Seuls les chantiers actifs (statut != ferme) sont inclus par defaut
- Filtre optionnel "Inclure chantiers fermes" pour historique

#### 17.11.3 Permissions

| Role | Acces vue consolidee | Perimetre |
|------|---------------------|-----------|
| Admin | ✅ | Tous chantiers |
| Conducteur | ✅ | Ses chantiers uniquement |
| Chef chantier | ❌ | — (vue chantier uniquement) |
| Compagnon | ❌ | — |

### 17.12 Intelligence et suggestions (FIN-21, FIN-22)

**Objectif** : Transformer le module financier d'un outil de reporting en assistant intelligent proposant des actions predictives.

#### 17.12.1 Indicateurs predictifs (FIN-22)

**1. Burn Rate (Rythme de consommation)**

**Formule** :
```python
duree_ecoulee_mois = (date.today() - chantier.date_debut).days / 30
burn_rate_mensuel = total_realise / duree_ecoulee_mois if duree_ecoulee_mois > 0 else 0
budget_moyen_mensuel = montant_revise_ht / chantier.duree_prevue_mois
ecart_burn_rate_pct = ((burn_rate_mensuel - budget_moyen_mensuel) / budget_moyen_mensuel) * 100
```

**Affichage** :
```
Rythme de depense : 45 000 EUR/mois (Budget moyen : 38 000 EUR/mois)
⚠️ Rythme +18% superieur a la moyenne
```

**Seuil alerte** : Burn rate > 120% du budget moyen

---

**2. Projection fin de chantier**

**Formule** :
```python
if burn_rate_mensuel > 0:
    mois_restants_budgetaires = reste_a_depenser / burn_rate_mensuel
    date_epuisement_budget = date.today() + timedelta(days=mois_restants_budgetaires * 30)

    # Comparer avec date_fin_prevue
    if date_epuisement_budget < chantier.date_fin_prevue:
        alerte_projection = True
        deficit_prevu = (chantier.date_fin_prevue - date_epuisement_budget).days / 30 * burn_rate_mensuel
```

**Affichage** :
```
⚠️ Projection : Budget epuise le 15/03/2026
   Fin chantier prevue : 30/04/2026
   Deficit estime : 67 500 EUR

💡 Suggestion : Creer un avenant de +70k EUR ou reduire le rythme de depense de 25%
```

---

**3. Avancement physique vs financier**

**Formule** :
```python
# Integration module Taches
avancement_physique_pct = (nb_taches_terminees / nb_taches_total) * 100
avancement_financier_pct = (total_realise / montant_revise_ht) * 100
ecart_pct = avancement_financier_pct - avancement_physique_pct
```

**Affichage** :
```
Graphique double jauge :
┌─────────────────────────────┐
│ Avancement physique :  48%  │ 🟢🟢🟢🟢🟢⚪⚪⚪⚪⚪
│ Avancement financier : 65%  │ 🟠🟠🟠🟠🟠🟠🟠⚪⚪⚪
│                             │
│ ⚠️ Ecart : +17 points        │
│ Vous depensez plus vite     │
│ que vous n'avancez          │
└─────────────────────────────┘
```

**Seuil alerte** : Ecart > 15 points

---

#### 17.12.2 Suggestions intelligentes (FIN-21)

**Algorithme de detection d'anomalies et proposition d'actions**

**Cas 1 : Depassement imminent**

**Condition** :
```python
if pct_engage > 95 and pct_realise < 60:
    suggestion = "CREATE_AVENANT"
```

**Affichage** :
```
┌───────────────────────────────────────────────┐
│ 💡 Suggestion                                 │
│                                               │
│ Vous avez engage 97% du budget alors que     │
│ seulement 58% du chantier est realise.       │
│                                               │
│ Action recommandee : Creer un avenant de     │
│ +45 000 EUR pour securiser la fin du chantier│
│                                               │
│ [Creer avenant]  [Ignorer]                   │
└───────────────────────────────────────────────┘
```

---

**Cas 2 : Achat non impute**

**Condition** :
```python
achats_sans_lot = Achat.query.filter(
    Achat.chantier_id == chantier_id,
    Achat.lot_budgetaire_id.is_(None),
    Achat.statut == StatutAchat.VALIDE
).count()

if achats_sans_lot > 0:
    suggestion = "IMPUTE_ACHATS"
```

**Affichage** :
```
⚠️ 3 achats valides ne sont pas imputes a un lot budgetaire
   Impact : Le tableau de bord ne reflete pas la realite des engagements

   [Voir les achats]  [Imputer maintenant]
```

---

**Cas 3 : Marge faible detectable tot**

**Condition** :
```python
if pct_realise < 30 and marge_estimee_pct < 8:
    suggestion = "OPTIMIZE_COSTS"
```

**Affichage** :
```
⚠️ Alerte marge precoce

   Marge estimee : 6.2% (objectif entreprise : 12%)
   Le chantier n'est qu'a 28% de realisation, vous pouvez encore agir.

   Pistes d'optimisation :
   • Negocier prix fournisseurs restants (economie potentielle : 8k EUR)
   • Reduire heures supplementaires (economie potentielle : 5k EUR)
   • Sous-traiter moins (economie potentielle : 12k EUR)

   [Voir details]
```

---

**Cas 4 : Situation en retard**

**Condition** :
```python
derniere_situation = Situation.query.filter(...).order_by(desc(created_at)).first()
if derniere_situation:
    jours_depuis = (date.today() - derniere_situation.created_at.date()).days
    if jours_depuis > 35:  # > 1 mois
        suggestion = "CREATE_SITUATION"
```

**Affichage** :
```
💰 Opportunite de tresorerie

   Derniere situation emise : il y a 42 jours
   Montant realise depuis : 38 500 EUR

   [Creer situation S-04]
```

---

**Cas 5 : Burn rate excessif**

**Condition** :
```python
if ecart_burn_rate_pct > 30:
    suggestion = "REDUCE_BURN_RATE"
```

**Affichage** :
```
🔥 Rythme de depense trop eleve

   Vous depensez 52 000 EUR/mois vs budget moyen de 38 000 EUR/mois (+37%)
   A ce rythme, le budget sera epuise dans 4.2 mois (fin prevue dans 7 mois)

   Actions possibles :
   • Reporter achats non urgents (22k EUR identifies)
   • Reduire effectif (2 compagnons → economie 8k EUR/mois)
   • Renogocier planning client (delai +2 mois)

   [Voir planning]  [Voir achats]
```

---

#### 17.12.3 Implementation technique - IA Gemini Flash

**Choix technologique** : **Google Gemini 1.5 Flash**

**Justification** :
- ✅ **Gratuit** : 1500 requetes/jour (tier gratuit largement suffisant pour Hub-Chantier)
- ✅ **Excellente qualite** : Niveau GPT-4o-mini, superieur aux modeles locaux legers
- ✅ **Rapide** : Latence 400ms (meilleure que modeles locaux)
- ✅ **Simple** : Integration via google-generativeai (1 pip install)
- ✅ **Fiable** : API stable Google, SLA 99.9%
- ✅ **Evolutif** : Passage au tier payant transparent si croissance (0.35 USD/1M tokens input)

**Alternatives evaluees** :
- Ollama + Qwen 2.5 7B (100% local, mais latence 500ms et RAM 8GB requise)
- Groq + Llama 3.1 (ultra-rapide 100ms, mais rate limit strict 30 req/min)
- Mistral Large (EU RGPD, mais 3 EUR/mois vs gratuit Gemini)

**Confidentialite** :
- Donnees anonymisees avant envoi (noms chantiers/clients remplaces par codes)
- Transmission KPI uniquement (pas de donnees brutes sensibles)
- Option desactivable par parametre utilisateur (opt-in)

**Cout estime** :
- 20 chantiers x 2 consultations/jour = 40 req/jour
- **0 EUR/mois** (tier gratuit 1500 req/jour)
- Meme en depassant (100 req/jour) : ~0.80 EUR/mois

---

#### 17.12.4 Backend - Architecture d'implementation

**Stack technique** :

```python
# requirements.txt
google-generativeai>=0.4.0

# .env
GEMINI_API_KEY=your_key_here  # Cle gratuite : https://ai.google.dev/
GEMINI_ENABLED=true            # Activation globale
```

**Structure fichiers** :

```
backend/modules/financier/application/intelligence/
├── __init__.py
├── ai_suggestion_engine.py           # Moteur principal IA
├── suggestion_service.py             # Service orchestrateur
├── providers/
│   ├── __init__.py
│   ├── gemini_provider.py            # Provider Gemini Flash
│   └── fallback_provider.py          # Fallback regles algorithmiques
├── prompts/
│   ├── system_prompt.txt             # Prompt systeme (role expert BTP)
│   └── user_prompt_template.txt     # Template prompt utilisateur
└── models/
    └── suggestion.py                 # Entities/DTOs suggestions
```

**Provider Gemini** :

```python
# backend/modules/financier/application/intelligence/providers/gemini_provider.py
import google.generativeai as genai
from typing import Dict
import json

class GeminiProvider:
    """Provider Gemini Flash pour suggestions intelligentes"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.3,  # Peu de creativite (fiabilite)
                "max_output_tokens": 800,
                "response_mime_type": "application/json"
            }
        )

    async def generate_suggestions(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Dict:
        """
        Genere suggestions via Gemini Flash

        Args:
            system_prompt: Role du modele (expert BTP)
            user_prompt: Donnees financieres + contexte chantier

        Returns:
            JSON structure avec suggestions + metadata
        """
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = await self.model.generate_content_async(full_prompt)

        return json.loads(response.text)
```

**Prompt Systeme** :

```
Tu es un expert en gestion financiere de chantiers BTP.
Ton role est d'analyser les donnees budgetaires d'un chantier et de proposer
des actions concretes et actionnables pour optimiser la rentabilite.

Regles :
- Sois concis (2-3 phrases max par suggestion)
- Propose uniquement des actions realisables
- Quantifie l'impact financier quand possible
- Priorise par urgence (CRITICAL > WARNING > INFO)
- Utilise un ton professionnel mais accessible
- Reponds UNIQUEMENT en JSON (pas de texte avant/apres)

Format JSON attendu :
{
  "suggestions": [
    {
      "type": "CREATE_AVENANT|IMPUTE_ACHATS|OPTIMIZE_COSTS|CREATE_SITUATION|REDUCE_BURN_RATE",
      "severity": "CRITICAL|WARNING|INFO",
      "titre": "Titre court (5-8 mots)",
      "description": "Description actionable (2-3 phrases)",
      "impact_estime_eur": 12345.67,
      "actions": [
        {"label": "Action principale", "primary": true}
      ]
    }
  ]
}
```

---

#### 17.12.5 Backend - Use Case GetSuggestionsFinancieresUseCase

**Input** : `chantier_id`

**Output** :
```python
{
  "suggestions": [
    {
      "type": "CREATE_AVENANT" | "IMPUTE_ACHATS" | "OPTIMIZE_COSTS" | "CREATE_SITUATION" | "REDUCE_BURN_RATE",
      "severity": "INFO" | "WARNING" | "CRITICAL",
      "titre": str,
      "description": str,
      "impact_estime_eur": Optional[Decimal],
      "actions": [
        {
          "label": str,
          "action": str,  # URL ou handler
          "primary": bool
        }
      ]
    }
  ],
  "indicateurs_predictifs": {
    "burn_rate_mensuel": Decimal,
    "budget_moyen_mensuel": Decimal,
    "ecart_burn_rate_pct": Decimal,
    "date_epuisement_budget": Optional[date],
    "deficit_prevu_eur": Optional[Decimal],
    "avancement_physique_pct": Decimal,
    "avancement_financier_pct": Decimal,
    "ecart_avancement_pct": Decimal
  }
}
```

**Workflow** :

1. Recuperer donnees financieres (dashboard KPI, achats, situations)
2. Calculer indicateurs predictifs (burn rate, projection, avancement)
3. **Si GEMINI_ENABLED=true** :
   - Anonymiser donnees (remplacer noms par codes)
   - Construire prompt utilisateur avec KPI + contexte
   - Appeler Gemini Flash via provider
   - Parser reponse JSON
4. **Fallback si erreur ou GEMINI_ENABLED=false** :
   - Utiliser regles algorithmiques (detection basee sur seuils)
   - Generer suggestions avec templates texte fixes
5. Filtrer + trier suggestions (max 3, severity DESC)
6. Retourner JSON avec suggestions + indicateurs

**Resilience** :
- Timeout Gemini : 10 secondes
- Retry : 2 tentatives avec exponential backoff (1s, 2s)
- Fallback systematique regles algorithmiques si echec IA
- Logging erreurs pour monitoring

**Route API** :

```
GET /api/financier/chantiers/{chantier_id}/suggestions

Response 200 OK :
{
  "suggestions": [...],
  "indicateurs_predictifs": {...}
}

Response 500 (fallback actif) :
{
  "suggestions": [...],  # Generes par regles algorithmiques
  "ai_available": false,
  "fallback_mode": "algorithmic"
}
```

---

#### 17.12.6 Frontend - Composant SuggestionsPanel

**Emplacement** : `frontend/src/components/financier/SuggestionsPanel.tsx`

**Integration** : Section 1 du BudgetDashboard (avant les KPI cards)

**Affichage** :

```tsx
<div className="space-y-3">
  {suggestions.map(suggestion => (
    <div
      key={suggestion.id}
      className={`border-l-4 p-4 rounded-lg ${severityColors[suggestion.severity]}`}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {severityIcons[suggestion.severity]}
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-1">
            {suggestion.titre}
          </h4>
          <p className="text-sm text-gray-700 mb-3">
            {suggestion.description}
          </p>
          {suggestion.impact_estime_eur && (
            <p className="text-xs text-gray-500 mb-2">
              Impact estime : {formatEUR(suggestion.impact_estime_eur)}
            </p>
          )}
          <div className="flex gap-2">
            {suggestion.actions.map(action => (
              <button
                key={action.label}
                onClick={() => handleAction(action)}
                className={action.primary ? 'btn-primary' : 'btn-secondary'}
              >
                {action.label}
              </button>
            ))}
            <button
              onClick={() => dismissSuggestion(suggestion.id)}
              className="btn-ghost"
            >
              Ignorer
            </button>
          </div>
        </div>
      </div>
    </div>
  ))}
</div>
```

**Severite** :
- CRITICAL : Bordure rouge, icone AlertTriangle
- WARNING : Bordure orange, icone AlertCircle
- INFO : Bordure bleue, icone Info

**Regles d'affichage** :
- Maximum 3 suggestions affichees simultanement (tri par severity DESC)
- Les suggestions peuvent etre "acquittees" (dismissed) par l'utilisateur
- Suggestions dismissees stockees en localStorage (24h)
- Historique des suggestions dans journal d'audit backend

---
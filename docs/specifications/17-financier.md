## 17. GESTION FINANCIERE ET BUDGETAIRE

### 17.1 Vue d'ensemble

Le module Financier centralise le suivi economique des chantiers : budgets previsionnels par lots, achats fournisseurs, situations de travaux et analyse de rentabilite. Il s'integre aux modules Chantiers, Taches, Feuilles d'Heures et Logistique pour offrir une vision consolidee couts/avancement. Accessible depuis un onglet dedie sur chaque fiche chantier, il permet a la direction et aux conducteurs de piloter la marge en temps reel.

### 17.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| FIN-01 | Onglet Budget par chantier | Accessible depuis la fiche chantier, affiche budget + KPI + dernieres operations | ✅ Backend + Frontend |
| FIN-02 | Budget previsionnel par lots | Decomposition arborescente par lots et postes (code lot, libelle, unite, quantite, PU HT) | ✅ Backend + Frontend |
| FIN-03 | Affectation budgets aux taches | Liaison optionnelle taches <-> lignes budgetaires pour suivi avancement financier | 🔮 Phase 3 |
| FIN-04 | Avenants budgetaires | Creation d'avenants avec motif, montant et impact automatique sur budget revise | 🔮 Phase 2 |
| FIN-05 | Saisie achats / bons de commande | Creation achats avec fournisseur, lot, montant HT, TVA, statut et workflow validation | ✅ Backend + Frontend |
| FIN-06 | Validation hierarchique achats | Approbation requise par Conducteur/Admin si montant > seuil configurable (defaut 5 000 EUR HT) | ✅ Backend + Frontend |
| FIN-07 | Situations de travaux | Creation situations mensuelles basees sur avancement reel, workflow 5 etapes, generation PDF | 🔮 Phase 2 |
| FIN-08 | Facturation client | Generation factures/acomptes depuis situations validees avec retenue de garantie | 🔮 Phase 2 |
| FIN-09 | Suivi couts main-d'oeuvre | Integration automatique heures validees (module Pointages) x taux horaire par metier | 🔮 Phase 2 (champ taux_horaire ajouté sur users) |
| FIN-10 | Suivi couts materiel | Integration automatique reservations (module Logistique) x tarif journalier | 🔮 Phase 2 (champ tarif_journalier ajouté sur ressources) |
| FIN-11 | Tableau de bord financier | Cartes KPI + graphiques comparatifs Budget/Engage/Realise + dernieres operations | ✅ Backend + Frontend |
| FIN-12 | Alertes depassements | Notifications push si (Engage + Reste a faire) > Budget x seuil (defaut 110%) | ✅ Backend (DepassementBudgetEvent) |
| FIN-13 | Export comptable | Generation CSV/Excel avec codes analytiques chantier, compatible logiciels comptables | 🔮 Phase 3 |
| FIN-14 | Referentiel fournisseurs | Gestion fournisseurs (raison sociale, type, SIRET, contact, conditions paiement) | ✅ Backend + Frontend |
| FIN-15 | Historique et tracabilite | Journal complet des modifications budgetaires avec auteur, date et motif | ✅ Backend + Frontend |

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

Le tableau de bord s'affiche dans l'onglet Budget de chaque chantier. Mobile-first, optimise pour consultation rapide sur le terrain.

#### 17.4.1 Zone superieure - Cartes KPI

| Indicateur | Formule | Couleur seuil |
|------------|---------|---------------|
| Budget revise HT | Budget initial + Avenants | — |
| Engage | Somme bons de commande valides | Orange > 90% budget |
| Realise | Somme factures + couts MO + couts materiel | Rouge > 100% budget |
| Marge estimee | Budget revise - (Realise + Reste a faire estime) | Rouge < 5% |

Chaque carte affiche le montant principal, le delta vs budget et une icone couleur (vert/orange/rouge).

#### 17.4.2 Zone centrale - Graphiques

- **Barres groupees par lot** : Budget / Engage / Realise avec surlignage rouge sur depassements
- **Donut repartition** : Couts par categorie (Main-d'oeuvre, Materiaux, Sous-traitance, Materiel)
- **Courbe en S** : Avancement physique (% taches) vs avancement financier (% realise/budget)

#### 17.4.3 Zone inferieure - Dernieres operations

- 5 derniers achats avec montant, fournisseur, statut
- 3 dernieres situations emises avec montant, date, statut paiement

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

---
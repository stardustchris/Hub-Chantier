## 18. GESTION DES DEVIS

### 18.1 Vue d'ensemble

Le module Gestion des Devis permet de créer, chiffrer, versionner et suivre les devis clients depuis la phase commerciale jusqu'à l'acceptation. Une fois accepté et signé, le devis peut être converti automatiquement en chantier avec transfert du budget détaillé, des lots et des sous-détails vers les modules Financier (§17) et Planning (§5).

Le module intègre des outils avancés de métrés numériques sur plans PDF, un système complet de consultations sous-traitants, et la gestion de bibliothèques de prix personnalisables avec import de bases externes (Batiprix, etc.). Il supporte un usage hors-ligne pour la consultation et la saisie partielle, avec synchronisation automatique des modifications.

Ce module se positionne **en amont** du cycle de vie actuel de Hub Chantier, couvrant la phase commerciale avant la création du chantier.

### 18.2 Fonctionnalités

| ID   | Fonctionnalité                              | Description                                                                 | Status |
|------|---------------------------------------------|-----------------------------------------------------------------------------|--------|
| DEV-01  | Bibliothèque d'articles et bordereaux       | Base de données d'articles (matériaux, main-d'œuvre, sous-traitance) avec prix unitaires, unités, codes et composants détaillés | 🔮     |
| DEV-02  | Import bibliothèques externes                | Import CSV/Excel ou connexion API vers bases standards (Batiprix 80 000+ ouvrages, etc.) pour prix marché actualisés mensuellement | 🔮     |
| DEV-03  | Création devis structuré                    | Arborescence par lots/chapitres/lignes avec quantités, prix unitaires et totaux automatiques | 🔮     |
| DEV-04  | Métrés numériques 2D intégrés               | Outils de mesure directe (longueur, surface, comptage) sur plans PDF du module Plans (§9), avec transfert automatique quantités et verrouillage | 🔮     |
| DEV-05  | Détail déboursés avancés                    | Breakdown par ligne : main-d'œuvre (heures × taux), matériaux, sous-traitance, matériel, frais avec calcul automatique prix de revient | 🔮     |
| DEV-06  | Gestion marges et coefficients              | Application de marges globales/par lot/par ligne, coefficients déboursés secs et prix de vente, avec règle de priorité (ligne > lot > global) | 🔮     |
| DEV-07  | Insertion multimédia                        | Ajout photos, fiches techniques ou documents par ligne/lot pour enrichissement visuel du devis client | 🔮     |
| DEV-08  | Variantes et révisions                      | Création de versions alternatives (économique/standard/premium) ou révisions avec comparatif détaillé automatique (écarts quantités/montants/marges) | 🔮     |
| DEV-09  | Gestion consultations sous-traitants        | Création packages par lot, envoi email automatisé avec plans/annexes, tracking réponses et dates limites | 🔮     |
| DEV-10  | Réception et comparaison offres             | Import offres reçues, tableau comparatif normalisé (prix, délais, conditions) avec sélection gagnante et mise à jour automatique déboursé lot | 🔮     |
| DEV-11  | Personnalisation présentation               | Modèles de mise en page configurables (avec/sans détail déboursés, avec/sans multimédia, avec/sans composants) | 🔮     |
| DEV-12  | Génération PDF devis                        | Export PDF professionnel avec entête personnalisé, conditions générales, annexes et multimédia intégré | 🔮     |
| DEV-13  | Envoi par email intégré                     | Envoi direct depuis l'app avec tracking ouverture/clics et lien signature sécurisé | 🔮     |
| DEV-14  | Signature électronique client               | Intégration signature simple (dessin tactile ou upload scan) avec validation légale horodatée et auditée | 🔮     |
| DEV-15  | Suivi statut devis                          | Workflow complet : Brouillon / En validation / Envoyé / Vu / En négociation / Accepté / Refusé / Perdu / Expiré | 🔮     |
| DEV-16  | Conversion en chantier                      | Transformation automatique devis accepté → création chantier avec budget, lots, déboursés et planning initial | 🔮     |
| DEV-17  | Tableau de bord devis                       | Vue liste/kanban des devis en cours par statut, client, montant, avec KPI pipeline commercial et alertes délais | 🔮     |
| DEV-18  | Historique modifications                    | Journal complet des changements avec auteur, timestamp, type modification et valeurs avant/après | 🔮     |
| DEV-19  | Recherche et filtres                        | Filtres avancés par client, date, montant, statut, commercial assigné, lot, marge | 🔮     |
| DEV-20  | Accès hors-ligne                            | Consultation/modification devis brouillons et métrés simples, synchronisation à la reconnexion avec gestion conflits | 🔮     |
| DEV-21  | Import DPGF automatique                     | Import fichier DPGF (Décomposition Prix Global Forfaitaire) Excel/CSV/PDF des appels d'offres avec mapping colonnes et pré-remplissage lots/lignes | 🔮     |
| DEV-22  | Retenue de garantie                         | Paramétrage retenue de garantie par devis (0%, 5%, 10%) avec affichage dans PDF client et report automatique lors conversion chantier | 🔮     |
| DEV-23  | Génération attestation TVA                  | Création automatique attestation TVA réglementaire selon taux appliqué (5.5% rénovation énergétique, 10% rénovation, 20% standard) | 🔮     |
| DEV-24  | Relances automatiques                       | Notifications push/email automatiques si délai de réponse dépassé (configurable : 7j, 15j, 30j) avec historique relances | 🔮     |
| DEV-25  | Frais de chantier                           | Ajout compte prorata, frais généraux, installations de chantier avec répartition globale ou par lot | 🔮     |

### 18.3 Déboursé sec et pilotage des marges

Le **déboursé sec** est l'indicateur central du chiffrage BTP. Il représente l'ensemble des coûts directs nécessaires à l'exécution des travaux, sans intégrer les frais de structure ni la marge bénéficiaire.

#### 18.3.1 Composantes du déboursé sec

| Composante | Description | Exemple |
|------------|-------------|---------|
| Main-d'œuvre | Heures × taux horaire par métier | 40h × 45€/h = 1 800€ |
| Matériaux | Quantité × prix unitaire achat | 50m² × 35€/m² = 1 750€ |
| Matériel | Location ou amortissement équipements | Bétonnière : 120€ |
| Sous-traitance | Montant forfaitaire ou métré sous-traitant | Électricité : 8 500€ |
| Déplacements | Frais de déplacement ressources | 3 jours × 65€ = 195€ |

#### 18.3.2 Formules de calcul

```
Déboursé sec = Σ (quantité composant × prix unitaire composant)
Prix de revient = Déboursé sec × (1 + coefficient frais généraux)
Prix de vente HT = Prix de revient × (1 + taux de marge)
Prix de vente TTC = Prix de vente HT × (1 + taux TVA applicable)
```

**Exemple concret - Lot maçonnerie** :

| Composant | Quantité | Prix unitaire | Montant |
|-----------|----------|---------------|---------|
| Maçon (MOE) | 120 h | 42€/h | 5 040€ |
| Parpaings | 800 u | 3,50€/u | 2 800€ |
| Mortier | 2 m³ | 85€/m³ | 170€ |
| **Déboursé sec lot** | | | **8 010€** |
| Frais généraux (12%) | | | 961€ |
| **Prix de revient** | | | **8 971€** |
| Marge (18%) | | | 1 615€ |
| **Prix de vente HT** | | | **10 586€** |
| TVA (20%) | | | 2 117€ |
| **Prix de vente TTC** | | | **12 703€** |

#### 18.3.3 Pilotage des marges multi-niveaux

Les marges sont pilotables à chaque niveau de la hiérarchie du devis avec règle de priorité :

| Niveau | Scope | Exemple | Priorité |
|--------|-------|---------|----------|
| Par ligne | Marge sur une ligne individuelle | Câble 3G2.5 : 10% | 1 (max) |
| Par lot | Marge spécifique à un lot | Lot électricité : 22% | 2 |
| Par type de débours | Marge différenciée selon nature | MOE : 20%, Matériaux : 12%, ST : 8% | 3 |
| Global | Marge par défaut sur tout le devis | 15% sur l'ensemble | 4 (min) |

**Règle de priorité** : Ligne > Lot > Type de débours > Global.

**Vues** :
- **Vue Débours** (interne uniquement) : Affiche coûts bruts (déboursé sec, prix de revient, marges détaillées)
- **Vue Vente** (PDF client) : Affiche uniquement prix commerciaux (prix de vente HT, TVA, TTC) sans révéler marges ni déboursés

### 18.4 Workflow du devis

| Étape | Responsable | Actions | Statut | Transitions |
|-------|-------------|---------|--------|-------------|
| 1. Création | Conducteur / Commercial | Création depuis template ou vierge, ajout lots/lignes | 🔵 Brouillon | → En validation |
| 2. Chiffrage | Conducteur | Saisie déboursés, métrés, ajustement marges | 🔵 Brouillon | → En validation |
| 3. Validation interne | Admin / Direction | Vérification marges minimales, cohérence prix | 🟡 En validation | → Approuvé / → Brouillon |
| 4. Génération PDF | Conducteur | PDF professionnel vue Vente uniquement | 🟢 Approuvé | → Envoyé |
| 5. Envoi client | Conducteur / Commercial | Email avec lien visibilité + signature | 🔵 Envoyé | → Vu |
| 6. Consultation | Client | Ouverture email/PDF (tracking) | 🟣 Vu | → En négociation / Accepté / Refusé |
| 7. Négociation | Conducteur + Client | Échanges, modifications, variantes | 🟠 En négociation | → Envoyé (nouvelle version) |
| 8. Acceptation | Client | Signature électronique | ✅ Accepté | → Conversion chantier |
| 9. Refus/Perte | Client / Interne | Motif obligatoire pour reporting | ❌ Refusé / Perdu | Final |
| 10. Expiration | Automatique | Si date validité dépassée sans réponse | ⏰ Expiré | → En négociation |

### 18.5 Matrice des droits - Devis

| Action | Admin | Conducteur | Commercial | Chef chantier | Compagnon |
|--------|-------|------------|------------|---------------|-----------|
| Créer devis | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier devis (Brouillon) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Valider devis (< 50k€) | ✅ | ✅ | ✅ | ❌ | ❌ |
| Valider devis (≥ 50k€) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Envoyer devis au client | ✅ | ✅ | ✅ | ❌ | ❌ |
| Voir tous les devis | ✅ | ✅ (ses chantiers) | ✅ (tous) | ❌ | ❌ |
| Gérer bibliothèque de prix | ✅ | ❌ | ❌ | ❌ | ❌ |
| Import bibliothèques externes | ✅ | ❌ | ❌ | ❌ | ❌ |
| Réaliser métrés numériques | ✅ | ✅ | ✅ | ✅ | ❌ |
| Gérer consultations ST | ✅ | ✅ | ❌ | ❌ | ❌ |
| Import DPGF | ✅ | ✅ | ✅ | ❌ | ❌ |
| Convertir en chantier | ✅ | ✅ | ❌ | ❌ | ❌ |
| Voir déboursés et marges | ✅ | ✅ | ✅ | ❌ | ❌ |

**Note** : Le rôle **Commercial** doit être ajouté au module Utilisateurs (§3).

### 18.6 Règles métier

- Accès complet réservé aux rôles Commercial/Conducteur/Administrateur
- Un devis ne peut être envoyé que s'il a été validé en validation interne (marge minimale vérifiée)
- La marge minimale par défaut est configurable au niveau entreprise (défaut 12%)
- La validation Direction est requise si montant total HT ≥ seuil configurable (défaut 50 000€)
- Le statut "Expiré" est déclenché automatiquement à la date de validité
- Les montants sont toujours saisis en HT ; TVA calculée automatiquement
- Le versioning conserve chaque état du devis (impossible de supprimer une version)
- Le PDF client ne contient jamais les déboursés secs ni les marges détaillées
- Les quantités issues de métrés numériques sont verrouillables pour éviter modifications accidentelles
- La conversion en chantier nécessite un devis en statut "Accepté" et signé
- La conversion transfère automatiquement lots/budget/déboursés vers module Financier (§17)
- Notification push/email aux commerciaux sur changement statut, signature, réception offre
- Relances automatiques configurables si délai de réponse dépassé (défaut : J+7, J+15, J+30)
- La signature électronique est horodatée, auditée et conservée pour valeur probante (conforme eIDAS)

### 18.7 Intégrations avec modules existants

| Module | Données exploitées | Usage dans Devis | Type intégration |
|--------|-------------------|------------------|------------------|
| §4 Chantiers | ID chantier, nom, dates | Association devis → chantier | EntityInfoService |
| §5 Planning | — | Création tâches lors conversion | Domain Event `DevisAccepteEvent` |
| §9 GED (Plans) | Plans PDF, échelle | Métrés numériques 2D | Domain Event `MetrageExtractedEvent` |
| §9 GED (Documents) | Stockage fichiers | Photos/fiches techniques, archivage PDF signés | EntityInfoService |
| §17 Financier | — | Génération budget chantier lors conversion | Domain Event `DevisAccepteEvent` |
| §20 Sous-Traitants | Référentiel ST, spécialités | Consultations ST, sélection offres | EntityInfoService |

### 18.8 Roadmap d'implémentation

Le module Devis est découpé en 4 phases successives (total 188 jours ≈ 9 mois).

#### Phase 1 : MVP Commercial (40 jours ~ 2 mois)

Bibliothèque interne, création structurée, déboursés avancés, marges, génération PDF, envoi email, suivi statuts, dashboard basique.

**Livrable** : Devis PDF professionnel avec déboursés, marges, envoi email et suivi.

#### Phase 2 : Automatisation (50 jours ~ 2.5 mois)

Variantes, personnalisation PDF, signature électronique, conversion chantier, historique, recherche, retenue garantie, attestation TVA, relances auto, frais chantier.

**Livrable** : Workflow complet Devis → Signature → Chantier avec budget.

#### Phase 3 : Productivité++ (45 jours ~ 2 mois)

Import bibliothèques externes (Batiprix), multimédia, consultations ST, comparaison offres, import DPGF, dashboard avancé.

**Livrable** : Réponse rapide aux marchés publics + consultations ST optimisées.

#### Phase 4 : Premium (53 jours ~ 2.5 mois)

Métrés numériques 2D intégrés, mode hors-ligne, optimisations performances.

**Livrable** : Fonctionnalités premium différenciantes (Autodesk Takeoff, Procore).

**Calendrier recommandé** :
```
FÉV - MARS 2026 : Module 17 (Financier)
AVRIL - MAI 2026 : Module 18 Phase 1 (MVP)
JUIN - JUIL 2026 : Module 18 Phase 2 (Automatisation)
SEPT - OCT 2026 : Module 18 Phase 3 (Productivité)
NOV - DÉC 2026 : Module 18 Phase 4 (Premium)
```

---
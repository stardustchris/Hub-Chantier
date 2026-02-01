## 13. GESTION DES TACHES

### 13.1 Vue d'ensemble

Le module Taches permet de creer des listes de travaux structurees par chantier avec un systeme de taches/sous-taches hierarchiques, une bibliotheque de modeles reutilisables, et un suivi d'avancement en temps reel avec code couleur.

### 13.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| TAC-01 | Onglet Taches par chantier | Accessible depuis la fiche chantier | ✅ |
| TAC-02 | Structure hierarchique | Taches parentes + sous-taches imbriquees | ✅ |
| TAC-03 | Chevrons repliables | ▼ / > pour afficher/masquer | ✅ |
| TAC-04 | Bibliotheque de modeles | Templates reutilisables avec sous-taches | ✅ |
| TAC-05 | Creation depuis modele | Importer un modele dans un chantier | ✅ |
| TAC-06 | Creation manuelle | Tache personnalisee libre | ✅ |
| TAC-07 | Bouton + Ajouter | Creation rapide de tache | ✅ |
| TAC-08 | Date d'echeance | Deadline pour la tache | ✅ |
| TAC-09 | Unite de mesure | m², litre, unite, ml, kg, m³... | ✅ |
| TAC-10 | Quantite estimee | Volume/quantite prevu | ✅ |
| TAC-11 | Heures estimees | Temps prevu pour realisation | ✅ |
| TAC-12 | Heures realisees | Temps effectivement passe | ✅ |
| TAC-13 | Statuts tache | A faire ☐ / Termine ✅ | ✅ |
| TAC-14 | Barre de recherche | Filtrer par mot-cle | ✅ |
| TAC-15 | Reorganiser les taches | Drag & drop pour reordonner | ✅ |
| TAC-16 | Export rapport PDF | Recapitulatif des taches | ✅ |
| TAC-17 | Vue mobile | Consultation et mise a jour (responsive) | ✅ |
| TAC-18 | Feuilles de taches | Declaration quotidienne travail realise | ✅ |
| TAC-19 | Validation conducteur | Valide le travail declare | ✅ |
| TAC-20 | Code couleur avancement | Vert/Jaune/Rouge selon progression | ✅ |

**Module COMPLET** - Backend + Frontend implementes (20/20 fonctionnalites)

### 13.3 Modeles de taches - Gros Oeuvre

| Nom | Description | Unite |
|-----|-------------|-------|
| Coffrage voiles | Mise en place des banches, reglage d'aplomb, serrage | m² |
| Ferraillage plancher | Pose des armatures, ligatures, verification enrobages | kg |
| Coulage beton | Preparation, vibration, talochage, cure | m³ |
| Decoffrage | Retrait des banches, nettoyage, stockage | m² |
| Pose predalles | Manutention, calage, etaiement provisoire | m² |
| Reservations | Mise en place des reservations techniques | unite |
| Traitement reprise | Preparation surfaces, application produit adherence | ml |

### 13.4 Codes couleur - Avancement

| Couleur | Condition | Signification |
|---------|-----------|---------------|
| 🟢 Vert | Heures realisees <= 80% estimees | Dans les temps |
| 🟡 Jaune | Heures realisees entre 80% et 100% | Attention, limite proche |
| 🔴 Rouge | Heures realisees > estimees | Depassement, retard |
| ⚪ Gris | Heures realisees = 0 | Non commence |

---
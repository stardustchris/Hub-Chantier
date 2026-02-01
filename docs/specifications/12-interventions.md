## 12. GESTION DES INTERVENTIONS

### 12.1 Vue d'ensemble

Le module Interventions est dedie a la gestion des interventions ponctuelles (SAV, maintenance, depannages, levee de reserves) distinctes des chantiers de longue duree. Il dispose d'un planning specifique et permet la generation de rapports d'intervention signes.

### 12.2 Difference Chantier vs Intervention

| Critere | Chantier | Intervention |
|---------|----------|--------------|
| Duree | Longue (semaines/mois) | Courte (heures/jours) |
| Equipe | Multiple collaborateurs | 1-2 techniciens |
| Recurrence | Continue | Ponctuelle |
| Usage | Gros oeuvre, construction | SAV, maintenance, depannage |
| Livrable | Suivi global projet | Rapport d'intervention signe |

### 12.3 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| INT-01 | Onglet dedie Planning | 3eme onglet Gestion des interventions | ✅ |
| INT-02 | Liste des interventions | Tableau Chantier/Client/Adresse/Statut | ✅ |
| INT-03 | Creation intervention | Bouton + pour nouvelle intervention | ✅ |
| INT-04 | Fiche intervention | Client, adresse, contact, description, priorite | ✅ |
| INT-05 | Statuts intervention | A planifier / Planifiee / En cours / Terminee / Annulee | ✅ |
| INT-06 | Planning hebdomadaire | Utilisateurs en lignes, jours en colonnes | ✅ |
| INT-07 | Blocs intervention colores | Format HH:MM - HH:MM - Code - Nom client | ✅ |
| INT-08 | Multi-interventions/jour | Plusieurs par utilisateur | ✅ |
| INT-09 | Toggle Afficher les taches | Activer/desactiver l'affichage | ✅ |
| INT-10 | Affectation technicien | Drag & drop ou via modal | ✅ |
| INT-11 | Fil d'actualite | Timeline actions, photos, commentaires | ✅ |
| INT-12 | Chat intervention | Discussion instantanee equipe | ✅ |
| INT-13 | Signature client | Sur mobile avec stylet/doigt | ✅ |
| INT-14 | Rapport PDF | Generation automatique avec tous les details | ⏳ Infra |
| INT-15 | Selection posts pour rapport | Choisir les elements a inclure | ⏳ Infra |
| INT-16 | Generation mobile | Creer le PDF depuis l'application | ⏳ Infra |
| INT-17 | Affectation sous-traitants | Prestataires externes (PLB, CFA...) | ✅ |

### 12.4 Contenu du rapport PDF

| Section | Contenu |
|---------|---------|
| En-tete | Logo entreprise, N° intervention, Date generation |
| Client | Nom, Adresse complete, Contact, Telephone |
| Intervenant(s) | Nom(s) du/des technicien(s) affectes |
| Horaires | Heure debut, heure fin, duree totale |
| Description | Motif de l'intervention |
| Travaux realises | Detail des actions effectuees |
| Photos | Avant / Pendant / Apres (selectionnees) |
| Anomalies | Problemes constates non resolus |
| Signatures | Client + Technicien avec horodatage |

---
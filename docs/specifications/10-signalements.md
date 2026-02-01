## 10. SIGNALEMENTS

### 10.1 Vue d'ensemble

Le module Signalements permet de signaler des urgences, problemes ou informations importantes avec un systeme de fil de conversation type chat, de statuts ouvert/ferme, et d'alertes automatiques pour les signalements non traites. Les signalements sont rattaches a un chantier et generent des notifications push avec escalade hierarchique.

### 10.2 Fonctionnalites de base

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| SIG-01 | Rattachement chantier | Signalement obligatoirement lie a un projet | ✅ |
| SIG-02 | Liste chronologique | Affichage par date de creation | ✅ |
| SIG-03 | Indicateur statut | 🟢 Ouvert / 🔴 Ferme | ✅ |
| SIG-04 | Photo chantier | Vignette d'identification visuelle | ✅ |
| SIG-05 | Horodatage | Date + heure de creation | ✅ |
| SIG-06 | Fil de conversation | Mode chat pour echanges multiples | ✅ |
| SIG-07 | Statut ferme avec badge | Ce signalement a ete ferme le [date] | ✅ |
| SIG-08 | Ajout photo/video | Dans les reponses du fil | ✅ |
| SIG-09 | Signature dans reponses | Validation des actions correctives | ✅ |
| SIG-10 | Bouton Publier | Envoyer une reponse dans le fil | ✅ |
| SIG-11 | Historique | X a ajoute un signalement sur Y le [date] | ✅ |
| SIG-12 | Bouton + (FAB) | Creation rapide sur mobile | ✅ |
| SIG-13 | Notifications push | Alerte temps reel a la creation | ⏳ Infra |

### 10.3 Fonctionnalites d'alertes et escalade

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| SIG-14 | Priorite signalement | 4 niveaux : Critique / Haute / Moyenne / Basse | ✅ |
| SIG-15 | Date resolution souhaitee | Echeance optionnelle fixee par le createur | ✅ |
| SIG-16 | Alertes retard | Notification si signalement non traite dans les delais | ⏳ Infra |
| SIG-17 | Escalade automatique | Remontee hierarchique progressive | ⏳ Infra |
| SIG-18 | Tableau de bord alertes | Vue des signalements en retard (Admin/Conducteur) | ✅ |
| SIG-19 | Filtres avances | Par chantier, statut, periode, priorite (Admin/Conducteur) | ✅ |
| SIG-20 | Vue globale | Tous les signalements tous chantiers (Admin/Conducteur) | ✅ |

### 10.4 Delais d'escalade par defaut

Si aucune date de resolution n'est fixee, les delais par defaut s'appliquent :

| Priorite | Delai alerte | Couleur | Cas d'usage |
|----------|--------------|---------|-------------|
| Critique | 4h | 🔴 Rouge | Securite, arret chantier |
| Haute | 24h | 🟠 Orange | Probleme technique bloquant |
| Moyenne | 48h | 🟡 Jaune | Approvisionnement, qualite |
| Basse | 72h | 🔵 Bleu | Information, amelioration |

### 10.5 Regles d'escalade

Un signalement est considere "en retard" si :
- Une date de resolution est fixee ET la date actuelle depasse cette echeance
- OU aucune date n'est fixee ET le delai par defaut (selon priorite) est depasse depuis la derniere activite

Notifications d'escalade :

| Declencheur | Destinataires | Canal |
|-------------|---------------|-------|
| 50% du delai ecoule | Createur + Chef de chantier | Push |
| 100% du delai (en retard) | + Conducteur de travaux | Push + Email |
| 200% du delai (critique) | + Administrateur | Push + Email + SMS |

### 10.6 Cas d'usage

| Type | Exemple | Priorite |
|------|---------|----------|
| Urgence securite | Echafaudage instable zone B - STOP travaux | Critique |
| Probleme technique | Fuite reseau eau potable niveau -1 | Haute |
| Approvisionnement | Rupture stock ferraille HA12, livraison retardee | Moyenne |
| Qualite | Non-conformite beton livre (slump trop eleve) | Haute |
| Incident | Bris de cable sur grue tour, arret maintenance | Haute |
| Information | Visite client prevue demain 10h - preparer zone A | Basse |

### 10.7 Matrice des droits - Signalements

| Action | Admin | Conducteur | Chef de Chantier | Compagnon |
|--------|-------|------------|------------------|-----------|
| Voir signalements (global) | ✅ | ✅ | ❌ | ❌ |
| Voir signalements (ses chantiers) | ✅ | ✅ | ✅ | ✅ |
| Creer un signalement | ✅ | ✅ | ✅ | ✅ |
| Repondre dans le fil | ✅ | ✅ | ✅ | ✅ |
| Ajouter photo/video | ✅ | ✅ | ✅ | ✅ |
| Signer une reponse | ✅ | ✅ | ✅ | ❌ |
| Fermer un signalement | ✅ | ✅ | ✅ | ❌ |
| Rouvrir un signalement | ✅ | ✅ | ❌ | ❌ |
| Supprimer un signalement | ✅ | ✅ | ❌ | ❌ |
| Filtres avances | ✅ | ✅ | ❌ | ❌ |

### 10.8 Vues par role

**Admin / Conducteur** : Vue globale avec filtres (chantier, statut, periode, priorite) + tableau de bord des alertes

**Chef de Chantier / Compagnon** : Vue par chantier uniquement (onglet Signalements de la fiche chantier)

---
## 11. LOGISTIQUE - GESTION DU MATERIEL

### 11.1 Vue d'ensemble

Le module Logistique permet de gerer les engins et gros materiel de l'entreprise avec un systeme de reservation par chantier, validation hierarchique optionnelle et visualisation calendrier. Chaque ressource dispose de son planning propre.

### 11.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| LOG-01 | Referentiel materiel | Liste des engins disponibles (Admin uniquement) | ✅ Backend + Frontend |
| LOG-02 | Fiche ressource | Nom, code, photo, couleur, plage horaire par defaut | ✅ Backend + Frontend |
| LOG-03 | Planning par ressource | Vue calendrier hebdomadaire 7 jours | ✅ Backend + Frontend |
| LOG-04 | Navigation semaine | < [Semaine X] > avec 3 semaines visibles | ✅ Backend + Frontend |
| LOG-05 | Axe horaire vertical | 08:00 → 18:00 (configurable) | ✅ Frontend |
| LOG-06 | Blocs reservation colores | Par demandeur avec nom complet (ex: "Jean DUPONT") | ✅ Frontend + Backend |
| LOG-07 | Demande de reservation | Depuis mobile ou web | ✅ Backend + Frontend |
| LOG-08 | Selection chantier | Association obligatoire au projet | ✅ Backend |
| LOG-09 | Selection creneau | Date + heure debut / heure fin | ✅ Backend + Frontend |
| LOG-10 | Option validation N+1 | Activation/desactivation par ressource | ✅ Backend |
| LOG-11 | Workflow validation | Demande 🟡 → Chef valide → Confirme 🟢 | ✅ Backend + Frontend |
| LOG-12 | Statuts reservation | En attente 🟡 / Validee 🟢 / Refusee 🔴 | ✅ Backend + Frontend |
| LOG-13 | Notification demande | Push au valideur (chef/conducteur) | ✅ Firebase FCM |
| LOG-14 | Notification decision | Push au demandeur | ✅ Firebase FCM |
| LOG-15 | Rappel J-1 | Notification veille de reservation | ✅ APScheduler |
| LOG-16 | Motif de refus | Champ texte optionnel | ✅ Backend + Frontend |
| LOG-17 | Conflit de reservation | Alerte si creneau deja occupe | ✅ Backend |
| LOG-18 | Historique par ressource | Journal complet des reservations | ✅ Backend + Frontend |
| LOG-19 | Selecteur de ressource | Dropdown pour choisir quelle ressource afficher | ✅ Frontend |
| LOG-20 | Vue "Toutes les ressources" | Affichage empile de toutes les ressources avec leurs plannings | ✅ Frontend |
| LOG-21 | Basculement vue globale/detaillee | Bouton "Voir en detail →" pour passer d'une ressource a sa vue detaillee | ✅ Frontend |
| LOG-22 | Enrichissement noms utilisateurs | Affichage "Prenom NOM" au lieu de "User #X" dans les reservations | ✅ Backend |
| LOG-23 | Persistence selection ressource | Conservation de la ressource selectionnee lors de navigation entre onglets | ✅ Frontend |

### 11.3 Types de ressources (Greg Constructions)

| Categorie | Exemples | Validation |
|-----------|----------|------------|
| Engins de levage | Grue mobile, Manitou, Nacelle, Chariot elevateur | N+1 requis |
| Engins de terrassement | Mini-pelle, Pelleteuse, Compacteur, Dumper | N+1 requis |
| Vehicules | Camion benne, Fourgon, Vehicule utilitaire | Optionnel |
| Gros outillage | Betonniere, Vibrateur, Pompe a beton | Optionnel |
| Equipements | Echafaudage, Etais, Banches, Coffrages | N+1 requis |

### 11.4 Matrice des droits - Logistique

| Action | Admin | Conducteur | Chef | Compagnon |
|--------|-------|------------|------|-----------|
| Creer ressource | ✅ | ❌ | ❌ | ❌ |
| Modifier ressource | ✅ | ❌ | ❌ | ❌ |
| Supprimer ressource | ✅ | ❌ | ❌ | ❌ |
| Voir planning ressource | ✅ | ✅ | ✅ | ✅ |
| Demander reservation | ✅ | ✅ | ✅ | ✅ |
| Valider/Refuser | ✅ | ✅ | ✅ | ❌ |

---
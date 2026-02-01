## 5. PLANNING OPERATIONNEL

### 5.1 Vue d'ensemble

Le Planning Operationnel permet d'affecter les collaborateurs aux chantiers avec une vue multi-perspective (Chantiers, Utilisateurs, Interventions), un groupement par metier avec badges colores, et une synchronisation temps reel mobile. Les affectations sont visualisees sous forme de blocs colores indiquant les horaires et le chantier.

### 5.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| PLN-01 | 2 onglets de vue | [Chantiers] [Utilisateurs] | ✅ |
| PLN-02 | Onglet Utilisateurs par defaut | Vue ressource comme vue principale | ✅ |
| PLN-03 | Bouton + Creer | Creation rapide d'affectation en haut a droite | ✅ |
| PLN-04 | Dropdown filtre utilisateurs | Utilisateurs planifies / Non planifies / Tous | ✅ |
| PLN-05 | Dropdown filtre chantier | Filtrer par chantier (simplifie vs entonnoir) | ✅ |
| PLN-06 | Toggle weekend | Afficher/masquer samedi-dimanche (simplifie) | ✅ |
| PLN-07 | Filtres par metier | Filtrage par badges metier | ✅ |
| PLN-08 | Selecteur periode | Vue semaine uniquement (mois/trimestre: future) | ✅ |
| PLN-09 | Navigation temporelle | Semaine < [Aujourd'hui] > Semaine | ✅ |
| PLN-10 | Indicateur semaine | Numero et dates de la semaine affichee | ✅ |
| PLN-11 | Badge non planifies | Compteur des ressources non affectees | ✅ |
| PLN-12 | Groupement par metier | Arborescence repliable par type d'utilisateur | ✅ |
| PLN-13 | Badges metier colores | Employe, Charpentier, Couvreur, Electricien, Sous-traitant... | ✅ |
| PLN-14 | Chevrons repliables | ▼ / > pour afficher/masquer les groupes | ✅ |
| PLN-15 | Avatar utilisateur | Cercle avec initiales + code couleur personnel | ✅ |
| PLN-16 | Bouton duplication | Dupliquer les affectations vers semaine suivante | ✅ |
| PLN-17 | Blocs affectation colores | Couleur = chantier (coherence visuelle globale) | ✅ |
| PLN-18 | Format bloc | HH:MM - HH:MM + icone note + Nom chantier | ✅ |
| PLN-19 | Icone note dans bloc | 📝 Indicateur de commentaire sur l'affectation | ✅ |
| PLN-20 | Multi-affectations/jour | Plusieurs blocs possibles par utilisateur par jour | ✅ |
| PLN-21 | Colonnes jours | Lundi 21 juil. / Mardi 22 juil. etc. | ✅ |
| PLN-22 | Filtres metiers | Filtrage par selection de metiers | ✅ |
| PLN-23 | Notification push | Alerte a chaque nouvelle affectation | ⏳ Infra |
| PLN-24 | Mode Offline | Consultation planning sans connexion | ⏳ Infra |
| PLN-25 | Notes privees | Commentaires visibles uniquement par l'affecte | ✅ |
| PLN-26 | Bouton appel | Icone telephone sur hover utilisateur | ✅ |
| PLN-27 | Drag & Drop | Deplacer les blocs pour modifier les affectations | ✅ |
| PLN-28 | Double-clic creation | Double-clic cellule vide → creation affectation | ✅ |

**Legende**: ✅ Complet | ⏳ Infra = Infrastructure requise

**Notes d'implementation**:
- PLN-05 simplifie : dropdown chantier au lieu d'icone entonnoir avec modal
- PLN-06 simplifie : toggle weekend au lieu d'icone engrenage avec parametres
- PLN-22 : filtre par metiers via panel depliable (pas barre de recherche texte)

### 5.3 Badges metiers (Groupement)

| Badge | Couleur | Description |
|-------|---------|-------------|
| Employe | 🔵 Bleu fonce | Compagnons internes polyvalents |
| Charpentier | 🟢 Vert | Specialistes bois et charpente |
| Couvreur | 🟠 Orange | Specialistes toiture |
| Electricien | 🟣 Magenta/Rose | Specialistes electricite |
| Sous-traitant | 🔴 Rouge/Corail | Prestataires externes |
| Macon | 🟤 Marron | Specialistes maconnerie (Greg) |
| Coffreur | 🟡 Jaune | Specialistes coffrage (Greg) |
| Ferrailleur | ⚫ Gris fonce | Specialistes ferraillage (Greg) |
| Grutier | 🩵 Cyan | Conducteurs d'engins (Greg) |

### 5.4 Structure d'une affectation

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| Utilisateur | Reference | Oui | Compagnon ou sous-traitant affecte |
| Chantier | Reference | Oui | Chantier d'affectation |
| Date | Date | Oui | Jour de l'affectation |
| Heure debut | HH:MM | Non | Heure de prise de poste |
| Heure fin | HH:MM | Non | Heure de fin de journee |
| Note | Texte | Non | Commentaire prive pour l'affecte |
| Recurrence | Option | Non | Unique / Repeter (jours selectionnes) |

### 5.5 Matrice des droits - Planning

| Action | Admin | Conducteur | Chef | Compagnon |
|--------|-------|------------|------|-----------|
| Voir planning global | ✅ | ✅ | ❌ | ❌ |
| Voir planning ses chantiers | ✅ | ✅ | ✅ | ❌ |
| Voir son planning personnel | ✅ | ✅ | ✅ | ✅ |
| Creer affectation | ✅ | ✅ | ❌ | ❌ |
| Modifier affectation | ✅ | ✅ | ❌ | ❌ |
| Supprimer affectation | ✅ | ✅ | ❌ | ❌ |
| Ajouter note | ✅ | ✅ | ✅ | ❌ |
| Dupliquer affectations | ✅ | ✅ | ❌ | ❌ |

### 5.6 Vue Mobile

Sur mobile, le planning s'affiche avec une navigation par jour (L M M J V S D) et deux onglets [Chantiers] et [Utilisateurs]. La vue Chantiers liste les chantiers avec leurs collaborateurs affectes. La vue Utilisateurs liste les collaborateurs avec leurs affectations. Chaque affectation peut etre supprimee via le bouton ✕. Le FAB (+) permet de creer une nouvelle affectation.

---
## 3. GESTION DES UTILISATEURS

### 3.1 Vue d'ensemble

Le module Utilisateurs permet de gerer l'ensemble des collaborateurs (employes et sous-traitants) avec un systeme de roles et permissions granulaires. Chaque utilisateur dispose d'une fiche complete avec photo, couleur d'identification et informations de contact.

### 3.2 Fonctionnalites

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| USR-01 | Ajout illimite | Nombre d'utilisateurs non plafonne | ✅ |
| USR-02 | Photo de profil | Upload d'une photo personnelle | ✅ |
| USR-03 | Couleur utilisateur | Palette 16 couleurs pour identification visuelle | ✅ |
| USR-04 | Statut Active/Desactive | Toggle pour activer/desactiver l'acces | ✅ |
| USR-05 | Type utilisateur | Employe ou Sous-traitant | ✅ |
| USR-06 | Role | Administrateur / Conducteur / Chef de Chantier / Compagnon | ✅ |
| USR-07 | Code utilisateur | Matricule optionnel pour export paie | ✅ |
| USR-08 | Numero mobile | Format international avec selecteur pays | ✅ |
| USR-09 | Navigation precedent/suivant | Parcourir les fiches utilisateurs | ✅ |
| USR-10 | Revocation instantanee | Desactivation sans suppression des donnees historiques | ✅ |
| USR-11 | Metier/Specialite | Classification par corps de metier | ✅ |
| USR-12 | Email professionnel | Adresse email (requis pour l'authentification) | ✅ |
| USR-13 | Coordonnees d'urgence | Contact en cas d'accident | ✅ |
| USR-14 | Invitation utilisateur | Envoi email invitation avec lien activation compte | ✅ |
| USR-15 | Reset password | Reinitialisation mot de passe via email avec token | ✅ |
| USR-16 | Change password | Modification mot de passe depuis parametres compte | ✅ |
| USR-17 | Statut is_active | Activation/desactivation compte apres invitation | ✅ |

### 3.3 Authentification et securite

| ID | Fonctionnalite | Description | Status |
|----|----------------|-------------|--------|
| AUTH-01 | Login email/password | Connexion avec email professionnel et mot de passe | ✅ |
| AUTH-02 | JWT tokens | Authentification par tokens (access + refresh) | ✅ |
| AUTH-03 | Invitation utilisateur | Admin envoie invitation avec lien activation 7j | ✅ |
| AUTH-04 | Acceptation invitation | Utilisateur cree mot de passe et active compte | ✅ |
| AUTH-05 | Reset password request | Demande reinitialisation avec envoi email token | ✅ |
| AUTH-06 | Reset password | Reinitialisation avec token valide 1h | ✅ |
| AUTH-07 | Change password | Modification depuis parametres (mot de passe actuel requis) | ✅ |
| AUTH-08 | Email verification | Templates HTML pour invitation, reset, verification | ✅ |
| AUTH-09 | Token expiration | Tokens invitation (7j), reset (1h) avec validation | ✅ |
| AUTH-10 | Password strength | Validation force mot de passe (8+ car, maj, min, chiffre) | ✅ |
| AUTH-11 | Droit a l'oubli RGPD | Suppression definitive donnees utilisateur (Art. 17 RGPD) | ✅ |

**AUTH-11 - Détails technique** :
- Endpoint: `DELETE /api/auth/users/{user_id}/gdpr`
- Permissions: Admin ou utilisateur lui-même uniquement
- Action: Hard delete définitif de toutes les données personnelles
- Conformité: RGPD Article 17 (Right to erasure)
- Auditabilité: Horodatage de suppression retourné

### 3.4 Matrice des roles et permissions

| Role | Web | Mobile | Perimetre | Droits principaux |
|------|-----|--------|-----------|-------------------|
| Administrateur | ✅ | ✅ | Global | Tous droits, configuration systeme, invitation utilisateurs |
| Conducteur | ✅ | ✅ | Ses chantiers | Planification, validation, export |
| Chef de Chantier | ❌ | ✅ | Ses chantiers assignes | Saisie, consultation, publication |
| Compagnon | ❌ | ✅ | Planning perso | Consultation, saisie heures |

### 3.5 Palette de couleurs utilisateurs

16 couleurs disponibles pour l'identification visuelle des utilisateurs. Ces couleurs sont utilisees de maniere coherente dans tout l'ecosysteme : planning, feuilles d'heures, fil d'actualite, affectations.

| Couleur | Code | Couleur | Code |
|---------|------|---------|------|
| Rouge | `#E74C3C` | Bleu fonce | `#2C3E50` |
| Orange | `#E67E22` | Bleu clair | `#3498DB` |
| Jaune | `#F1C40F` | Cyan | `#1ABC9C` |
| Vert clair | `#2ECC71` | Violet | `#9B59B6` |
| Vert fonce | `#27AE60` | Rose | `#E91E63` |
| Marron | `#795548` | Gris | `#607D8B` |
| Corail | `#FF7043` | Indigo | `#3F51B5` |
| Magenta | `#EC407A` | Lime | `#CDDC39` |

---
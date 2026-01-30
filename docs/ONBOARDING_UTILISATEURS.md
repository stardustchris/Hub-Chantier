# Onboarding Utilisateurs Hub Chantier

**Date** : 30 janvier 2026
**Auteur** : Claude Sonnet 4.5

---

## 🎯 Vue d'ensemble

Ce document décrit les 3 parcours d'onboarding disponibles dans Hub Chantier pour créer et activer un compte utilisateur.

---

## 📋 Parcours 1 : Auto-registration (Compagnon)

**Utilisé pour** : Compagnons qui s'inscrivent eux-mêmes

### Étapes

1. **L'utilisateur accède à la page d'inscription**
   - URL : `https://hub-chantier.fr/register`
   - Accessible publiquement (pas d'authentification requise)

2. **L'utilisateur remplit le formulaire**
   - Email professionnel (obligatoire)
   - Mot de passe (8+ car, majuscule, minuscule, chiffre)
   - Nom + Prénom
   - Code utilisateur (optionnel, ex: "PM001")
   - Téléphone (optionnel)

3. **Validation et création automatique**
   - Le système vérifie :
     - ✅ Email unique (pas déjà utilisé)
     - ✅ Code utilisateur unique (si fourni)
     - ✅ Force du mot de passe
   - Le compte est créé avec :
     - Rôle par défaut : `COMPAGNON` (sécurité)
     - Statut : `actif` (utilisable immédiatement)

4. **Token JWT généré automatiquement**
   - L'utilisateur reçoit un token JWT
   - Cookie HttpOnly sécurisé stocké
   - Redirection automatique vers le dashboard

### ✅ Avantages

- Rapide et autonome
- Aucune intervention admin requise
- Utilisable immédiatement

### ⚠️ Limitations

- Rôle fixé à COMPAGNON (ne peut pas s'auto-promouvoir admin)
- Pas de vérification email (Phase 2)

### 💻 Code d'exemple

**Endpoint** : `POST /api/auth/register`

```json
{
  "email": "pierre.martin@gregconstruction.fr",
  "password": "MonMotDePasse123",
  "nom": "Martin",
  "prenom": "Pierre",
  "code_utilisateur": "PM001",
  "telephone": "0612345678"
}
```

**Réponse** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "42",
    "email": "pierre.martin@gregconstruction.fr",
    "nom": "Martin",
    "prenom": "Pierre",
    "role": "compagnon",
    "is_active": true
  }
}
```

---

## 📧 Parcours 2 : Invitation par Admin/Conducteur (Recommandé)

**Utilisé pour** : Chefs de chantier, Conducteurs, Admins

### Étapes

#### Partie 1 : L'admin envoie l'invitation

1. **L'admin/conducteur se connecte**
   - URL : `https://hub-chantier.fr/login`
   - Rôle requis : `admin` ou `conducteur`

2. **L'admin accède à la gestion des utilisateurs**
   - Menu : "Administration" → "Gestion Utilisateurs"
   - Bouton : "Inviter un utilisateur"

3. **L'admin remplit le formulaire d'invitation**
   - Email du nouvel utilisateur (obligatoire)
   - Nom + Prénom
   - **Rôle** : `admin`, `conducteur`, `chef_chantier`, ou `compagnon`
   - Type : `employe`, `interimaire`, ou `sous_traitant`
   - Code utilisateur (optionnel)
   - Métier (optionnel, ex: "Maçon", "Chef de chantier")

4. **Le système crée le compte et envoie l'email**
   - Compte créé avec statut `inactif` (is_active=False)
   - Token d'invitation généré (UUID sécurisé)
   - Expiration : 7 jours
   - Email HTML professionnel envoyé avec :
     - Nom de l'inviteur (ex: "Jean Dupont vous a invité...")
     - Lien d'activation : `https://hub-chantier.fr/invite?token=XXX`
     - Instructions claires

#### Partie 2 : L'utilisateur accepte l'invitation

5. **L'utilisateur reçoit l'email d'invitation**
   - Objet : "Invitation à rejoindre Hub Chantier"
   - Template HTML professionnel
   - Lien cliquable valide 7 jours

6. **L'utilisateur clique sur le lien**
   - Redirection vers : `/invite?token=XXX`
   - Page d'acceptation d'invitation affichée

7. **L'utilisateur définit son mot de passe**
   - Saisie du nouveau mot de passe
   - Confirmation du mot de passe
   - Acceptation des CGU (optionnel)

8. **Activation du compte**
   - Le système valide :
     - ✅ Token valide et non expiré
     - ✅ Force du mot de passe
   - Le compte passe à `is_active=True`
   - Token d'invitation invalidé (usage unique)
   - Redirection vers la page de connexion

9. **L'utilisateur se connecte**
   - Login avec email + mot de passe défini
   - Accès au dashboard avec son rôle assigné

### ✅ Avantages

- **Contrôle total** : Admin choisit le rôle et les permissions
- **Sécurité** : L'utilisateur définit son propre mot de passe
- **Traçabilité** : On sait qui a invité qui
- **Professionnel** : Email HTML avec branding

### 🎯 Cas d'usage

- Nouveau chef de chantier embauché
- Promotion d'un compagnon vers chef de chantier
- Ajout d'un conducteur de travaux
- Création d'un compte admin

### 💻 Code d'exemple

#### Étape 1 : Admin envoie l'invitation

**Endpoint** : `POST /api/auth/invite`

**Headers** :
```
Authorization: Bearer ADMIN_TOKEN
```

**Body** :
```json
{
  "email": "sophie.bernard@gregconstruction.fr",
  "nom": "Bernard",
  "prenom": "Sophie",
  "role": "chef_chantier",
  "type_utilisateur": "employe",
  "code_utilisateur": "SB001",
  "metier": "Chef de chantier"
}
```

**Réponse** :
```json
{
  "message": "Invitation envoyée à sophie.bernard@gregconstruction.fr"
}
```

#### Étape 2 : Utilisateur accepte

**Endpoint** : `POST /api/auth/accept-invitation`

**Body** :
```json
{
  "token": "invite_abc123def456...",
  "password": "MonNouveauMotDePasse123"
}
```

**Réponse** :
```json
{
  "message": "Invitation acceptée, votre compte est maintenant actif"
}
```

---

## 🔐 Parcours 3 : Création manuelle par API (Avancé)

**Utilisé pour** : Intégrations systèmes, scripts, migration de données

### Étapes

1. **L'admin appelle l'API de création**
   - Endpoint : `POST /api/users` (nécessite rôle admin)
   - Fourni : Email, nom, prénom, rôle, mot de passe temporaire

2. **L'admin communique les identifiants**
   - Envoi manuel par email sécurisé
   - SMS ou appel téléphonique
   - Remise en main propre

3. **L'utilisateur se connecte avec le mot de passe temporaire**
   - Login classique

4. **L'utilisateur change son mot de passe**
   - Via : Paramètres → Sécurité → "Changer mon mot de passe"
   - Endpoint : `POST /api/auth/change-password`

### ⚠️ Limitations

- Pas d'email automatique
- Communication manuelle des identifiants (risque sécurité)
- Nécessite une étape supplémentaire (changement mot de passe)

### 💡 Recommandation

**Utiliser le Parcours 2 (Invitation)** à la place pour plus de sécurité et de professionnalisme.

---

## 📊 Tableau comparatif

| Critère | Auto-registration | Invitation Admin | Création API manuelle |
|---------|-------------------|------------------|----------------------|
| **Public cible** | Compagnons | Chefs, Conducteurs, Admins | Scripts, migrations |
| **Rôle assigné** | COMPAGNON uniquement | Tous les rôles | Tous les rôles |
| **Mot de passe** | Défini par l'utilisateur | Défini par l'utilisateur | Temporaire fourni |
| **Email envoyé** | Non (Phase 2) | Oui (invitation HTML) | Non (manuel) |
| **Activation** | Immédiate | Après acceptation | Immédiate |
| **Sécurité** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **UX** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

---

## 🎯 Workflows recommandés par profil

### Compagnon (Ouvrier terrain)

**Recommandation** : Parcours 1 (Auto-registration)

**Raison** :
- Autonome et rapide
- Pas d'intervention admin nécessaire
- Rôle COMPAGNON suffisant pour accès terrain

**Instructions à communiquer** :
1. "Rendez-vous sur hub-chantier.fr/register"
2. "Inscrivez-vous avec votre email professionnel"
3. "Vous pourrez pointer immédiatement"

---

### Chef de chantier

**Recommandation** : Parcours 2 (Invitation)

**Raison** :
- Nécessite le rôle `chef_chantier` (pas possible en auto-registration)
- Professionnel et sécurisé
- Traçabilité de qui a créé le compte

**Workflow** :
1. Admin/Conducteur envoie invitation avec rôle `chef_chantier`
2. Chef reçoit email professionnel
3. Chef définit son mot de passe
4. Chef accède aux fonctionnalités de gestion d'équipe

---

### Conducteur de travaux

**Recommandation** : Parcours 2 (Invitation)

**Raison** :
- Nécessite le rôle `conducteur` (haut niveau de permissions)
- Doit être validé par admin
- Accès complet à la gestion de chantiers

**Workflow** :
1. Admin envoie invitation avec rôle `conducteur`
2. Conducteur accepte et définit mot de passe
3. Conducteur peut à son tour inviter des utilisateurs

---

### Administrateur

**Recommandation** : Parcours 2 (Invitation) par un autre admin

**Raison** :
- Rôle le plus sensible (accès complet)
- Doit être créé par un admin existant
- Double validation

**Workflow** :
1. Admin existant envoie invitation avec rôle `admin`
2. Nouvel admin accepte
3. Droits complets activés

---

### Intérimaire / Sous-traitant

**Recommandation** : Parcours 2 (Invitation) avec type spécifique

**Raison** :
- Permet de spécifier `type_utilisateur=interimaire` ou `sous_traitant`
- Facilite le suivi RH
- Peut avoir un rôle temporaire limité

**Workflow** :
1. Admin envoie invitation avec :
   - Rôle : `compagnon` (généralement)
   - Type : `interimaire` ou `sous_traitant`
   - Durée : Compte peut être désactivé après mission

---

## 🔄 Récupération de mot de passe oublié

Si un utilisateur oublie son mot de passe :

1. **Page de login** : Clic sur "Mot de passe oublié ?"
2. **Saisie email** : L'utilisateur entre son email
3. **Email de réinitialisation** :
   - Template HTML professionnel
   - Lien : `https://hub-chantier.fr/reset-password?token=XXX`
   - Expiration : 1 heure
4. **Définition nouveau mot de passe** :
   - L'utilisateur clique sur le lien
   - Saisit un nouveau mot de passe
   - Validation et redirection vers login

**Endpoint** : `POST /api/auth/reset-password/request`

**Sécurité** :
- Retourne toujours succès (évite énumération des comptes)
- Token à usage unique
- Expiration courte (1h)
- Rate limiting (3 req/min)

---

## 📧 Templates d'emails

### Email d'invitation

**Sujet** : "Invitation à rejoindre Hub Chantier - Greg Construction"

**Contenu** :
```
Bonjour Sophie Bernard,

Jean Dupont vous a invité à rejoindre Hub Chantier, l'outil de gestion
de chantiers de Greg Construction.

Votre rôle : Chef de chantier

Pour activer votre compte, cliquez sur le lien ci-dessous :
[Accepter l'invitation]

Ce lien est valide pendant 7 jours.

Si vous n'avez pas demandé cette invitation, ignorez cet email.

Cordialement,
L'équipe Hub Chantier
```

### Email de réinitialisation

**Sujet** : "Réinitialisation de votre mot de passe Hub Chantier"

**Contenu** :
```
Bonjour,

Nous avons reçu une demande de réinitialisation de mot de passe
pour votre compte Hub Chantier.

Pour définir un nouveau mot de passe, cliquez sur le lien ci-dessous :
[Réinitialiser mon mot de passe]

Ce lien est valide pendant 1 heure.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
Votre mot de passe actuel reste inchangé.

Cordialement,
L'équipe Hub Chantier
```

---

## 🛡️ Sécurité et bonnes pratiques

### Pour les administrateurs

✅ **À faire** :
- Utiliser le parcours invitation pour tous les rôles sensibles
- Vérifier l'identité avant d'envoyer une invitation
- Désactiver les comptes des employés partis
- Monitorer les connexions suspectes

❌ **À éviter** :
- Créer des comptes admin en masse
- Communiquer des mots de passe par email non chiffré
- Réutiliser les mêmes mots de passe temporaires
- Laisser des comptes inactifs actifs

### Pour les utilisateurs

✅ **À faire** :
- Utiliser un mot de passe unique et fort
- Changer régulièrement son mot de passe
- Ne jamais partager ses identifiants
- Signaler toute activité suspecte

❌ **À éviter** :
- Utiliser le même mot de passe que d'autres services
- Noter son mot de passe sur papier
- Laisser sa session ouverte sur ordinateur partagé
- Cliquer sur des liens suspects dans les emails

---

## 📞 Support

### FAQ

**Q : Je n'ai pas reçu l'email d'invitation, que faire ?**
R : Vérifiez vos spams. Si toujours rien, contactez l'admin qui vous a invité pour renvoyer l'invitation.

**Q : Le lien d'invitation a expiré, que faire ?**
R : Contactez l'admin pour qu'il renvoie une nouvelle invitation.

**Q : Je veux changer mon mot de passe, comment faire ?**
R : Une fois connecté, allez dans Paramètres → Sécurité → "Changer mon mot de passe".

**Q : Je veux inviter un nouveau compagnon, ai-je les droits ?**
R : Seuls les Admin et Conducteurs peuvent inviter des utilisateurs.

**Q : Puis-je changer le rôle d'un utilisateur ?**
R : Oui, via l'interface d'administration (Admin ou Conducteur uniquement).

---

## 🎯 Checklist onboarding

### Pour l'administrateur

- [ ] Identifier le profil utilisateur (compagnon, chef, conducteur, admin)
- [ ] Choisir le parcours approprié (auto-registration ou invitation)
- [ ] Si invitation : remplir les informations correctement (email, rôle, etc.)
- [ ] Vérifier que l'email d'invitation est envoyé
- [ ] Suivre que l'utilisateur a bien accepté l'invitation
- [ ] Vérifier la première connexion de l'utilisateur

### Pour l'utilisateur invité

- [ ] Vérifier la réception de l'email d'invitation
- [ ] Vérifier l'expéditeur (noreply@hub-chantier.fr)
- [ ] Cliquer sur le lien dans les 7 jours
- [ ] Définir un mot de passe fort (8+ car, maj, min, chiffre)
- [ ] Confirmer le mot de passe
- [ ] Se connecter avec les nouveaux identifiants
- [ ] Explorer l'interface et les fonctionnalités

---

**Version** : 1.0 (30 janvier 2026)
**Statut** : ✅ Workflow complet implémenté

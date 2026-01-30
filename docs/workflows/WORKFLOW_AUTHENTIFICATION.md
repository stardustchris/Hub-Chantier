# Workflow Authentification Hub Chantier - Audit & Gap Analysis

**Date** : 30 janvier 2026
**Auteur** : Claude Sonnet 4.5

---

## 🎯 Objectif

Audit complet du workflow d'authentification actuel et identification des fonctionnalités manquantes pour permettre un parcours utilisateur complet.

---

## ✅ FONCTIONNALITÉS EXISTANTES

### Backend (Module `auth`)

#### 1. **Login** ✅
- **Fichier** : `backend/modules/auth/application/use_cases/login.py`
- **Fonctionnalités** :
  - Authentification par email + mot de passe
  - Vérification du hash BCrypt
  - Génération de token JWT
  - Vérification du statut actif du compte
  - Event `UserLoggedInEvent` publié
- **Exceptions** :
  - `InvalidCredentialsError` : Email ou mot de passe incorrect
  - `UserInactiveError` : Compte désactivé

#### 2. **Register** ✅
- **Fichier** : `backend/modules/auth/application/use_cases/register.py`
- **Fonctionnalités** :
  - Création de compte utilisateur
  - Validation email unique
  - Validation code utilisateur unique
  - Validation force du mot de passe (8+ caractères, majuscule, minuscule, chiffre)
  - Hash BCrypt du mot de passe
  - Rôle par défaut : `COMPAGNON` (sécurité)
  - Génération automatique de token JWT
  - Event `UserCreatedEvent` publié
- **Exceptions** :
  - `EmailAlreadyExistsError`
  - `CodeAlreadyExistsError`
  - `WeakPasswordError`

#### 3. **Get Current User** ✅
- **Fichier** : `backend/modules/auth/application/use_cases/get_current_user.py`
- Récupère l'utilisateur connecté depuis le token JWT

#### 4. **Update User** ✅
- **Fichier** : `backend/modules/auth/application/use_cases/update_user.py`
- Modification des informations utilisateur (nom, prénom, téléphone, etc.)

#### 5. **Deactivate User** ✅
- **Fichier** : `backend/modules/auth/application/use_cases/deactivate_user.py`
- Désactivation d'un compte (soft delete)

#### 6. **List Users** ✅
- **Fichier** : `backend/modules/auth/application/use_cases/list_users.py`
- Listage des utilisateurs (admin)

#### 7. **API Keys** ✅
- **Fichiers** :
  - `create_api_key.py` - Génération de clés API
  - `list_api_keys.py` - Liste des clés
  - `revoke_api_key.py` - Révocation
- Pour authentification systèmes externes

#### 8. **RGPD** ✅
- **Fichiers** :
  - `get_consents.py` - Récupération des consentements
  - `update_consents.py` - Mise à jour des consentements
  - `export_user_data.py` - Export des données personnelles

---

### Frontend (React + TypeScript)

#### 1. **Page de Login** ✅
- **Fichier** : `frontend/src/pages/LoginPage.tsx`
- **Fonctionnalités** :
  - Formulaire email + mot de passe
  - Validation Zod côté client
  - Gestion des erreurs
  - Loading state
  - Redirection après succès

#### 2. **Auth Context** ✅
- **Fichier** : `frontend/src/contexts/AuthContext.tsx`
- Gestion de l'état d'authentification global

#### 3. **Auth Service** ✅
- **Fichier** : `frontend/src/services/auth.ts`
- Appels API login/register/logout

---

## ❌ FONCTIONNALITÉS MANQUANTES

### 🔴 Critiques (Bloquantes)

#### 1. **Reset Password / Mot de passe oublié**
**Status** : ❌ NON IMPLÉMENTÉ

**Besoin** :
- Use Case backend `request_password_reset.py`
  - Génère un token de réinitialisation (UUID + expiration 1h)
  - Envoie email avec lien de reset
  - Stocke le token en DB avec expiration

- Use Case backend `reset_password.py`
  - Valide le token
  - Hash le nouveau mot de passe
  - Met à jour l'utilisateur
  - Invalide tous les tokens existants

- Page frontend `ResetPasswordPage.tsx`
  - Formulaire "Mot de passe oublié ?"
  - Saisie email
  - Page de réinitialisation avec token

- Email template
  - Template HTML pour email de reset
  - Lien vers `hub-chantier.fr/reset-password?token=XXX`

**Référence CDC** : Section 15.1 - Authentification

---

#### 2. **Invitation Utilisateur**
**Status** : ❌ NON IMPLÉMENTÉ

**Besoin** :
- Use Case backend `invite_user.py`
  - Création d'un compte pré-rempli (email, nom, prénom, rôle)
  - Génération d'un token d'invitation (UUID + expiration 7 jours)
  - Envoi email d'invitation
  - Statut compte : `PENDING_ACTIVATION`

- Use Case backend `accept_invitation.py`
  - Valide le token d'invitation
  - Active le compte
  - Permet à l'utilisateur de définir son mot de passe

- Page frontend `AcceptInvitationPage.tsx`
  - Formulaire de définition de mot de passe
  - Validation du token
  - Acceptation CGU

- Email template invitation
  - Lien vers `hub-chantier.fr/invite?token=XXX`

- Interface admin pour envoyer invitations
  - Formulaire dans la gestion des utilisateurs

**Référence CDC** : Section 3 - Gestion des Utilisateurs (USR-01 à USR-13)

---

#### 3. **Change Password (Utilisateur connecté)**
**Status** : ❌ NON IMPLÉMENTÉ

**Besoin** :
- Use Case backend `change_password.py`
  - Vérification ancien mot de passe
  - Validation nouveau mot de passe (force)
  - Hash et mise à jour
  - Invalidation anciens tokens (optionnel)

- Page frontend `SettingsPage.tsx` (section Sécurité)
  - Formulaire changement de mot de passe
  - Ancien mot de passe
  - Nouveau mot de passe
  - Confirmation

**Référence CDC** : Section 15.1 - Authentification

---

### 🟡 Importantes (Recommandées)

#### 4. **Email Verification (Confirmation email)**
**Status** : ❌ NON IMPLÉMENTÉ

**Besoin** :
- Après register, envoyer email de confirmation
- Token de vérification email
- Use Case `verify_email.py`
- Compte actif seulement après vérification email
- Badge "Email vérifié" dans l'interface

**Impact** : Sécurité, réduction spam, validation identité

---

#### 5. **2FA (Authentification à 2 facteurs)**
**Status** : ❌ NON IMPLÉMENTÉ

**Besoin** :
- Support TOTP (Google Authenticator, Authy)
- Use Cases :
  - `enable_2fa.py` - Génère QR code
  - `verify_2fa.py` - Validation du code 6 chiffres
  - `disable_2fa.py` - Désactivation
- Page frontend de configuration 2FA
- Backup codes de récupération

**Référence CDC** : Section 15.1 - Authentification (mentionné dans specs)

---

#### 6. **SMS OTP Login**
**Status** : ❌ NON IMPLÉMENTÉ

**Besoin** :
- Alternative au mot de passe
- Use Cases :
  - `send_otp_sms.py` - Envoi code 6 chiffres par SMS
  - `verify_otp_sms.py` - Vérification code
- Intégration API SMS (Twilio, OVH, etc.)
- Stockage numéros de téléphone vérifiés

**Référence CDC** : Section 15.1 - "La connexion s'effectue de manière sécurisée par SMS (code OTP)"

---

#### 7. **Session Management**
**Status** : ⚠️ PARTIEL (JWT uniquement)

**Besoin actuel** :
- JWT stocké côté client (localStorage/sessionStorage)
- Expiration token configurable
- Refresh token automatique

**Améliorations recommandées** :
- Use Case `refresh_token.py`
- Refresh token (durée 30 jours)
- Access token court (15 min)
- Rotation automatique
- Révocation refresh tokens
- Liste des sessions actives (devices)
- Déconnexion à distance

---

#### 8. **Account Lockout (Verrouillage après échecs)**
**Status** : ❌ NON IMPLÉMENTÉ

**Besoin** :
- Après N tentatives échouées (ex: 5) → verrouillage 15 min
- Stockage nombre de tentatives par utilisateur
- Reset automatique après délai
- Notification email en cas de tentatives suspectes

**Sécurité** : Protection contre brute force

---

#### 9. **Audit Log Authentification**
**Status** : ⚠️ PARTIEL (Event `UserLoggedInEvent` existe)

**Besoin complet** :
- Log toutes les tentatives de connexion (réussite/échec)
- Stockage :
  - IP address
  - User agent
  - Timestamp
  - Résultat (succès/échec/raison)
  - Géolocalisation (optionnel)
- Interface admin pour consulter logs
- Alertes activité suspecte

---

### 🟢 Nice to Have (Optionnelles)

#### 10. **Social Login (Google, Microsoft)**
**Status** : ❌ NON IMPLÉMENTÉ

OAuth2 avec providers externes (Google Workspace, Microsoft 365)

---

#### 11. **Magic Link Login (Sans mot de passe)**
**Status** : ❌ NON IMPLÉMENTÉ

Envoi lien temporaire par email pour connexion directe

---

#### 12. **Remember Me (Rester connecté)**
**Status** : ⚠️ PARTIEL (frontend uniquement)

Prolongation session avec cookie sécurisé long terme

---

## 📊 MATRICE DE PRIORITÉ

| Fonctionnalité | Statut | Priorité | Effort | Impact |
|----------------|--------|----------|--------|--------|
| **Reset Password** | ❌ | 🔴 CRITIQUE | 2j | Bloquant UX |
| **Invitation Utilisateur** | ❌ | 🔴 CRITIQUE | 3j | Bloquant onboarding |
| **Change Password** | ❌ | 🔴 CRITIQUE | 1j | Sécurité |
| **Email Verification** | ❌ | 🟡 IMPORTANT | 2j | Sécurité |
| **2FA** | ❌ | 🟡 IMPORTANT | 3j | Sécurité |
| **SMS OTP** | ❌ | 🟡 IMPORTANT | 2j | CDC spec |
| **Session Management** | ⚠️ | 🟡 IMPORTANT | 2j | UX |
| **Account Lockout** | ❌ | 🟡 IMPORTANT | 1j | Sécurité |
| **Audit Logs** | ⚠️ | 🟡 IMPORTANT | 2j | Compliance |
| **Social Login** | ❌ | 🟢 NICE | 3j | Confort |
| **Magic Link** | ❌ | 🟢 NICE | 2j | UX |
| **Remember Me** | ⚠️ | 🟢 NICE | 1j | UX |

**Total effort critique** : 6 jours
**Total effort important** : 12 jours
**Total complet** : 21 jours

---

## 🚀 WORKFLOW ACTUEL (Réalisable)

### ✅ Ce qui fonctionne AUJOURD'HUI

#### Scénario 1 : Auto-registration (Compagnon)
1. Utilisateur va sur `/register`
2. Remplit le formulaire (email, mot de passe, nom, prénom)
3. Compte créé avec rôle `COMPAGNON`
4. Token JWT généré automatiquement
5. Redirection vers dashboard

**Limites** :
- ❌ Pas de vérification email
- ❌ Rôle fixé à COMPAGNON (sécurisé mais limitant)
- ❌ Pas d'invitation par admin

---

#### Scénario 2 : Login classique
1. Utilisateur va sur `/login`
2. Saisit email + mot de passe
3. Authentification réussie
4. Token JWT stocké
5. Redirection vers dashboard

**Limites** :
- ❌ Pas de "Mot de passe oublié"
- ❌ Pas de 2FA
- ❌ Pas de SMS OTP

---

#### Scénario 3 : Création admin (via API)
1. Admin appelle `POST /api/users` (nécessite privilèges admin)
2. Crée un compte avec n'importe quel rôle
3. Définit un mot de passe temporaire
4. Communique les identifiants à l'utilisateur (email manuel)

**Limites** :
- ❌ Pas d'email automatique
- ❌ Utilisateur ne peut pas définir son propre mot de passe
- ❌ Pas de token d'invitation

---

## 🎯 WORKFLOW IDÉAL (Avec fonctionnalités manquantes)

### 🔴 Prérequis : Implémenter les 3 fonctionnalités critiques

1. **Reset Password**
2. **Invitation Utilisateur**
3. **Change Password**

---

### ✅ Workflow Complet Post-implémentation

#### Parcours Nouveau Compagnon (Auto-registration)
1. Va sur `/register`
2. Crée son compte → Email de confirmation envoyé
3. Clique sur lien de vérification
4. Email vérifié → Compte actif
5. Login → Dashboard

#### Parcours Nouveau Chef/Conducteur (Invitation)
1. **Admin** :
   - Va dans Gestion Utilisateurs
   - Clique "Inviter un utilisateur"
   - Remplit : email, nom, prénom, rôle
   - Clique "Envoyer invitation"

2. **Utilisateur** :
   - Reçoit email d'invitation
   - Clique sur le lien
   - Page `/invite?token=XXX`
   - Définit son mot de passe
   - Accepte les CGU
   - Compte activé
   - Redirection vers dashboard

#### Mot de passe oublié
1. Page `/login` → "Mot de passe oublié ?"
2. Saisit son email
3. Reçoit email de reset
4. Clique sur lien → `/reset-password?token=XXX`
5. Définit nouveau mot de passe
6. Confirmation → Redirection `/login`

#### Changement de mot de passe (sécurité)
1. Utilisateur connecté → Paramètres
2. Section "Sécurité"
3. "Changer mon mot de passe"
4. Saisit ancien + nouveau
5. Validation → Déconnexion forcée (sécurité)
6. Reconnexion avec nouveau mot de passe

---

## 📋 RECOMMANDATIONS

### Phase 1 : MVP Authentification (1-2 semaines)
✅ **Implémenter les 3 critiques** :
1. Reset Password (2j)
2. Invitation Utilisateur (3j)
3. Change Password (1j)

→ **Total : 6 jours** = Workflow utilisateur complet

---

### Phase 2 : Sécurité Renforcée (2-3 semaines)
✅ **Implémenter les importantes** :
1. Email Verification (2j)
2. Account Lockout (1j)
3. Session Management amélioré (2j)
4. Audit Logs complets (2j)

→ **Total : 7 jours** = Sécurité production-ready

---

### Phase 3 : Fonctionnalités Avancées (optionnel)
✅ **Si budget disponible** :
1. 2FA (3j)
2. SMS OTP (2j) - Requis par CDC
3. Social Login (3j)

---

## 🔐 NOTES SÉCURITÉ

### Bonnes pratiques actuelles ✅
- ✅ Hash BCrypt pour mots de passe
- ✅ Validation force mot de passe (8+ car, maj, min, chiffre)
- ✅ JWT avec expiration
- ✅ Vérification compte actif
- ✅ Rôle COMPAGNON par défaut (sécurité)
- ✅ Event sourcing (UserLoggedInEvent, UserCreatedEvent)

### À améliorer 🔧
- ⚠️ Pas de rate limiting (brute force possible)
- ⚠️ Pas de lockout après échecs
- ⚠️ Tokens JWT non révocables (problème si compromis)
- ⚠️ Pas de rotation refresh tokens
- ⚠️ Pas d'audit logs détaillés

---

## 📞 CONCLUSION

**Statut actuel** : ⚠️ **FONCTIONNEL MAIS INCOMPLET**

Hub Chantier dispose d'une **base solide** d'authentification (login/register/JWT), mais **manque de fonctionnalités essentielles** pour un workflow utilisateur complet en production :

### ❌ Bloquants critiques
1. **Pas de récupération mot de passe** → Utilisateurs bloqués définitivement si oubli
2. **Pas d'invitation admin** → Impossible de créer des comptes Chef/Conducteur proprement
3. **Pas de changement mot de passe** → Problème sécurité si mot de passe compromis

### 🎯 Action Immédiate Recommandée
**Implémenter Phase 1 (6 jours)** pour débloquer le workflow complet.

Sans ces 3 fonctionnalités, **l'onboarding utilisateur est incomplet** et nécessite des workarounds manuels peu professionnels (envoi manuel d'identifiants, impossibilité de reset password).

---

**Prochaine étape** : Créer les issues GitHub pour Phase 1 ?

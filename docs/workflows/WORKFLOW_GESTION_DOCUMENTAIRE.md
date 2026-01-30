# Workflow : Gestion Documentaire (GED)

**Complexité** : ⭐⭐⭐⭐ (Élevée)
**Module** : `backend/modules/documents`
**Date** : 30 janvier 2026
**Statut** : ✅ Documenté

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Acteurs et permissions](#2-acteurs-et-permissions)
3. [Entités métier](#3-entités-métier)
4. [Workflows détaillés](#4-workflows-détaillés)
5. [Arborescence standard](#5-arborescence-standard)
6. [Contrôle d'accès](#6-contrôle-daccès)
7. [Interactions avec autres modules](#7-interactions-avec-autres-modules)
8. [Architecture technique](#8-architecture-technique)
9. [Scénarios de test](#9-scénarios-de-test)
10. [Points d'attention](#10-points-dattention)

---

## 1. Vue d'ensemble

### 1.1 Définition

La **Gestion Électronique de Documents (GED)** permet de stocker, organiser, partager et sécuriser tous les documents liés aux chantiers : plans, photos, PV de réception, PPSPS, comptes-rendus, etc.

Le module s'organise en 3 niveaux :

```
┌─────────────────────────────────────────────────────────────┐
│  CHANTIER                                                    │
│  "Villa Duplex - Montmélian"                                │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  DOSSIER (arborescence hiérarchique)                    │ │
│  │  01-Plans / 02-Administratif / 03-Sécurité / ...       │ │
│  │                                                          │ │
│  │  ┌─────────────────────────────────────────────────────┐│ │
│  │  │  DOCUMENT (fichier physique)                        ││ │
│  │  │  Plan-RDC-v3.pdf  │  12 Mo  │  Conducteur only     ││ │
│  │  └─────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  AUTORISATION (permission nominative)                   │ │
│  │  "Sébastien ACHKAR peut LIRE le dossier 03-Sécurité"  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Objectifs métier

| Objectif | Description |
|----------|-------------|
| **Centralisation** | Un seul endroit pour tous les documents d'un chantier |
| **Traçabilité** | Savoir qui a uploadé quoi, quand, avec quel niveau d'accès |
| **Conformité BTP** | Conservation des documents légaux (PPSPS, DOE, PV réception) pendant 10 ans |
| **Sécurité** | Contrôler finement qui peut voir/modifier/supprimer chaque document |
| **Productivité** | Recherche rapide, prévisualisation, téléchargement groupé |

### 1.3 Références CDC

| CDC ID | Fonctionnalité | Implémenté |
|--------|----------------|------------|
| GED-01 | Structure arborescente par chantier | ✅ |
| GED-02 | Arborescence standard (7 dossiers types) | ✅ |
| GED-03 | Liste documents avec pagination | ✅ |
| GED-04 | Niveaux d'accès hiérarchiques | ✅ |
| GED-05 | Autorisations nominatives | ✅ |
| GED-06 | Upload multi-fichiers (max 10) | ✅ |
| GED-07 | Limite taille (10 Go/fichier) | ✅ |
| GED-08 | Versioning documents | ✅ |
| GED-09 | Drag & drop upload | ✅ |
| GED-12 | Types supportés (PDF, Image, Excel, Word, Vidéo) | ✅ |
| GED-13 | Renommer, déplacer, changer accès | ✅ |
| GED-16 | Téléchargement ZIP multi-documents | ✅ |
| GED-17 | Prévisualisation (PDF, images, vidéo) | ✅ |

---

## 2. Acteurs et permissions

### 2.1 Matrice de permissions

| Action | Compagnon | Chef chantier | Conducteur | Admin |
|--------|:---------:|:-------------:|:----------:|:-----:|
| Voir documents (niveau Compagnon) | ✅ | ✅ | ✅ | ✅ |
| Voir documents (niveau Chef) | ❌ | ✅ | ✅ | ✅ |
| Voir documents (niveau Conducteur) | ❌ | ❌ | ✅ | ✅ |
| Voir documents (niveau Admin) | ❌ | ❌ | ❌ | ✅ |
| Uploader un document | ❌ | ✅ | ✅ | ✅ |
| Modifier (renommer, déplacer) | ❌ | ✅ | ✅ | ✅ |
| Supprimer | ❌ | ❌ | ✅ | ✅ |
| Créer un dossier | ❌ | ✅ | ✅ | ✅ |
| Gérer les autorisations | ❌ | ❌ | ✅ | ✅ |
| Télécharger | ✅ (si accès) | ✅ | ✅ | ✅ |
| Prévisualiser | ✅ (si accès) | ✅ | ✅ | ✅ |

**Exception** : Un compagnon peut accéder à un document/dossier au-dessus de son niveau si une **autorisation nominative** lui a été accordée (GED-05, GED-15).

---

## 3. Entités métier

### 3.1 Document

**Fichier** : `backend/modules/documents/domain/entities/document.py`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | int | Identifiant unique |
| `chantier_id` | int | Chantier propriétaire |
| `dossier_id` | int | Dossier parent |
| `nom` | str | Nom affiché (peut être renommé) |
| `nom_original` | str | Nom du fichier uploadé (conservé) |
| `chemin_stockage` | str | Chemin physique sur le serveur |
| `taille` | int | Taille en octets (max 10 Go) |
| `mime_type` | str | Type MIME (application/pdf, image/png...) |
| `type_document` | TypeDocument | Catégorie auto-détectée |
| `niveau_acces` | NiveauAcces | Qui peut voir ce document |
| `uploaded_by` | int | Utilisateur qui a uploadé |
| `description` | str | Description optionnelle |
| `version` | int | Numéro de version (incrémenté) |

**Méthodes** : `peut_acceder(role)`, `renommer(nom)`, `deplacer(dossier_id)`, `changer_niveau_acces(niveau)`, `incrementer_version()`

**Constantes** : `MAX_TAILLE_FICHIER = 10 Go`, `MAX_FICHIERS_UPLOAD = 10`

### 3.2 Dossier

**Fichier** : `backend/modules/documents/domain/entities/dossier.py`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | int | Identifiant unique |
| `chantier_id` | int | Chantier propriétaire |
| `nom` | str | Nom du dossier |
| `type_dossier` | DossierType | Type standard ou CUSTOM |
| `niveau_acces` | NiveauAcces | Qui peut voir ce dossier |
| `parent_id` | int (nullable) | Dossier parent (arborescence) |
| `ordre` | int | Ordre d'affichage |

**Méthodes** : `peut_acceder(role)`, `renommer(nom)`, `deplacer(parent_id)`, `changer_niveau_acces(niveau)`

### 3.3 Autorisation nominative

**Fichier** : `backend/modules/documents/domain/entities/autorisation.py`

| Champ | Type | Description |
|-------|------|-------------|
| `id` | int | Identifiant |
| `user_id` | int | Bénéficiaire |
| `type_autorisation` | TypeAutorisation | LECTURE, ECRITURE ou ADMIN |
| `dossier_id` | int (XOR document_id) | Cible : dossier OU document |
| `document_id` | int (XOR dossier_id) | Cible : dossier OU document |
| `accorde_par` | int | Qui a accordé la permission |
| `expire_at` | datetime (nullable) | Date d'expiration (optionnelle) |

**3 niveaux d'autorisation** :

| Type | Lecture | Modification | Suppression |
|------|:------:|:----------:|:---------:|
| LECTURE | ✅ | ❌ | ❌ |
| ECRITURE | ✅ | ✅ | ❌ |
| ADMIN | ✅ | ✅ | ✅ |

---

## 4. Workflows détaillés

### 4.1 Upload d'un document

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌─────────┐
│ Utilisateur  │────►│ FileUploadZone   │────►│ POST /documents/ │────►│ Stockage│
│ (drag & drop │     │ (validation      │     │ dossiers/{id}/   │     │ local   │
│  ou clic)    │     │  taille+type)    │     │ documents        │     │         │
└──────────────┘     └──────────────────┘     └──────────────────┘     └─────────┘
                                                      │
                                                      ▼
                                              ┌──────────────┐
                                              │ Validations  │
                                              │ 1. Taille    │
                                              │ 2. Extension │
                                              │ 3. MIME type │
                                              │ 4. Doublon   │
                                              │ 5. Droits    │
                                              └──────┬───────┘
                                                     │ OK
                                                     ▼
                                              ┌──────────────┐
                                              │ Sauvegarde   │
                                              │ fichier +    │
                                              │ métadonnées  │
                                              └──────┬───────┘
                                                     │
                                                     ▼
                                              DocumentUploadedEvent
```

**Requête** (multipart/form-data) :

```http
POST /api/documents/dossiers/15/documents
Content-Type: multipart/form-data
Authorization: Bearer <token>

--boundary
Content-Disposition: form-data; name="file"; filename="Plan-RDC-v3.pdf"
Content-Type: application/pdf
[contenu binaire]
--boundary
Content-Disposition: form-data; name="description"
Plan du rez-de-chaussée - version finale
--boundary
Content-Disposition: form-data; name="niveau_acces"
conducteur
--boundary--
```

**Validations appliquées** :

| Validation | Règle | Erreur |
|-----------|-------|--------|
| Taille | <= 10 Go par fichier | `FileTooLargeError` |
| Extension | PDF, PNG, JPG, GIF, WEBP, XLS, XLSX, CSV, DOC, DOCX, ODT, MP4, AVI, MOV, MKV, WEBM | `InvalidFileTypeError` |
| MIME type | Vérifié côté serveur (pas confiance au Content-Type client) | `InvalidFileTypeError` |
| Doublon nom | Si même nom dans le dossier → suffixe `_1`, `_2`... | Auto-résolu |
| Droits | L'uploadeur doit avoir accès ECRITURE au dossier | `AccessDeniedError` |

**Stockage physique** : `uploads/chantiers/{chantier_id}/dossiers/{dossier_id}/{uuid8}_{filename}`

Le nom de fichier est sanitisé (caractères spéciaux retirés) et un UUID 8 caractères est ajouté pour éviter les collisions.

### 4.2 Téléchargement groupé (ZIP)

```http
POST /api/documents/download-zip
Content-Type: application/json
Authorization: Bearer <token>

{
  "document_ids": [1, 5, 12, 34, 67]
}
```

**Limites** : Maximum 100 documents par téléchargement ZIP.

### 4.3 Prévisualisation

```http
GET /api/documents/documents/42/preview
```

| Type | Prévisualisable | Condition |
|------|:--------------:|-----------|
| PDF | ✅ | Toujours |
| Image (PNG, JPG, GIF, WEBP) | ✅ | Taille < 10 Mo |
| Vidéo (MP4, AVI, MOV) | ✅ | Toujours (streaming) |
| Excel, Word | ❌ | Téléchargement uniquement |

### 4.4 Gestion des autorisations

**Accorder une autorisation nominative** :

```http
POST /api/documents/autorisations
Content-Type: application/json

{
  "user_id": 7,
  "type_autorisation": "lecture",
  "dossier_id": 15,
  "expire_at": "2026-06-30T23:59:59Z"
}
```

**Logique de contrôle d'accès (par ordre de priorité)** :

```
1. L'utilisateur est l'uploadeur du document → ACCÈS
2. L'utilisateur a une autorisation nominative valide → selon type (LECTURE/ECRITURE/ADMIN)
3. Sinon → vérifier niveau_acces du document/dossier vs rôle utilisateur
4. Admin → accès à tout
```

---

## 5. Arborescence standard

### 5.1 Structure par défaut (GED-02)

Lors de la création d'un chantier, l'arborescence standard peut être initialisée :

```
📁 Villa Duplex - Montmélian
│
├── 📁 01 - Plans                    (niveau: CHEF_CHANTIER)
│   └── Plans architecte, plans béton, plans réseaux...
│
├── 📁 02 - Administratif            (niveau: CONDUCTEUR)
│   └── Marché, avenants, assurances, CCTP...
│
├── 📁 03 - Sécurité                 (niveau: CHEF_CHANTIER)
│   └── PPSPS, PGC, registres, habilitations...
│
├── 📁 04 - Qualité                  (niveau: CHEF_CHANTIER)
│   └── Fiches contrôle, PV essais, non-conformités...
│
├── 📁 05 - Photos                   (niveau: COMPAGNON)
│   └── Photos chantier, avancement, réserves...
│
├── 📁 06 - Comptes-rendus           (niveau: CHEF_CHANTIER)
│   └── CR réunions, CR chantier, notes internes...
│
└── 📁 07 - Livraisons               (niveau: CHEF_CHANTIER)
    └── Bons de livraison, bons de commande...
```

**Endpoint d'initialisation** :

```http
POST /api/documents/chantiers/28/init-arborescence
```

→ Crée les 7 dossiers types avec niveaux d'accès par défaut.

### 5.2 Dossiers personnalisés

En plus des dossiers standards, des dossiers CUSTOM peuvent être créés librement :

```http
POST /api/documents/dossiers
Content-Type: application/json

{
  "chantier_id": 28,
  "nom": "DOE (Dossier des Ouvrages Exécutés)",
  "type_dossier": "custom",
  "niveau_acces": "conducteur",
  "parent_id": null
}
```

---

## 6. Contrôle d'accès

### 6.1 Niveaux hiérarchiques

```
┌─────────────────────────────────────────────────────────┐
│               HIÉRARCHIE D'ACCÈS                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  COMPAGNON ──────── Peut voir : COMPAGNON                │
│      │                                                   │
│      ▼                                                   │
│  CHEF_CHANTIER ──── Peut voir : COMPAGNON + CHEF         │
│      │                                                   │
│      ▼                                                   │
│  CONDUCTEUR ─────── Peut voir : COMPAGNON + CHEF + COND. │
│      │                                                   │
│      ▼                                                   │
│  ADMIN ──────────── Peut voir : TOUT                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Cas concret

```
Sébastien ACHKAR (compagnon) :
  ✅ 05-Photos (niveau COMPAGNON) → visible
  ❌ 01-Plans (niveau CHEF_CHANTIER) → invisible
  ❌ 02-Administratif (niveau CONDUCTEUR) → invisible

  MAIS si le conducteur lui accorde une autorisation nominative LECTURE
  sur 01-Plans → ✅ visible (l'autorisation nominative prime)
```

---

## 7. Interactions avec autres modules

| Module | Interaction |
|--------|-------------|
| **Chantiers** | Dossiers rattachés au chantier, cascade delete |
| **Formulaires** | Export PDF → stocké en GED |
| **Signalements** | Photos rattachées via URL |
| **Planning** | Pas d'interaction directe |
| **Pointages** | Pas d'interaction directe |

---

## 8. Architecture technique

```
backend/modules/documents/
├── domain/
│   ├── entities/          document.py, dossier.py, autorisation.py
│   ├── value_objects/     type_document.py, dossier_type.py, niveau_acces.py
│   ├── repositories/      document_repo.py, dossier_repo.py, autorisation_repo.py
│   ├── services/          file_storage_service.py (interface)
│   └── events/            document_uploaded.py, document_deleted.py
├── application/
│   ├── dtos/              document_dtos.py, dossier_dtos.py, autorisation_dtos.py
│   └── use_cases/         document_use_cases.py (571 lignes), dossier_use_cases.py, autorisation_use_cases.py
├── adapters/
│   ├── controllers/       document_controller.py
│   └── providers/         local_file_storage.py (implémentation locale)
└── infrastructure/
    ├── persistence/       models.py, sqlalchemy_*_repository.py
    └── web/               document_routes.py (400+ lignes), dependencies.py
```

**API Endpoints résumés** :

| Méthode | Endpoint | Action |
|---------|----------|--------|
| POST | `/documents/dossiers` | Créer dossier |
| GET | `/documents/chantiers/{id}/arborescence` | Arborescence complète |
| POST | `/documents/chantiers/{id}/init-arborescence` | Initialiser dossiers types |
| POST | `/documents/dossiers/{id}/documents` | Uploader document |
| GET | `/documents/documents/{id}` | Métadonnées document |
| GET | `/documents/documents/{id}/download` | Télécharger |
| GET | `/documents/documents/{id}/preview` | Prévisualiser |
| POST | `/documents/download-zip` | Télécharger en ZIP |
| PUT | `/documents/documents/{id}` | Modifier (nom, accès, dossier) |
| DELETE | `/documents/documents/{id}` | Supprimer |
| POST | `/documents/autorisations` | Accorder autorisation |
| DELETE | `/documents/autorisations/{id}` | Révoquer autorisation |

---

## 9. Scénarios de test

```python
def test_upload_document_success(client):
    """Upload PDF dans un dossier existant."""
    response = client.post("/api/documents/dossiers/15/documents",
        files={"file": ("plan.pdf", b"...", "application/pdf")},
        data={"description": "Plan RDC", "niveau_acces": "chef_chantier"})
    assert response.status_code == 201
    assert response.json()["type_document"] == "pdf"

def test_upload_fichier_trop_gros(client):
    """Fichier > 10 Go → refusé."""
    big_file = b"x" * (10 * 1024**3 + 1)
    response = client.post("/api/documents/dossiers/15/documents",
        files={"file": ("big.pdf", big_file, "application/pdf")})
    assert response.status_code == 400  # FileTooLargeError

def test_acces_niveau_insuffisant(client):
    """Compagnon ne peut pas voir un dossier niveau Conducteur."""
    # Login as compagnon
    response = client.get("/api/documents/documents/42")
    assert response.status_code == 403  # AccessDeniedError

def test_autorisation_nominative_prime(client):
    """Autorisation nominative donne accès malgré niveau insuffisant."""
    # Accorder LECTURE à Sébastien (compagnon) sur dossier Plans
    client.post("/api/documents/autorisations", json={
        "user_id": 7, "type_autorisation": "lecture", "dossier_id": 15})
    # Sébastien peut maintenant voir
    response = client_compagnon.get("/api/documents/documents/42")
    assert response.status_code == 200

def test_download_zip_max_100(client):
    """ZIP limité à 100 documents."""
    response = client.post("/api/documents/download-zip",
        json={"document_ids": list(range(1, 102))})
    assert response.status_code == 400
```

---

## 10. Points d'attention

### 10.1 Stockage

| Point | État actuel | Évolution prévue |
|-------|------------|------------------|
| **Stockage fichiers** | Local (`uploads/`) | Migration S3/Azure Blob |
| **Suppression** | Hard delete (fichier + BDD) | Soft delete + archivage prévu |
| **Backup** | Non automatisé | À implémenter |

### 10.2 Sécurité

| Point | Mitigation |
|-------|-----------|
| Path traversal | Sanitisation nom fichier + UUID |
| Upload malveillant | Vérification MIME côté serveur |
| Accès non autorisé | Double vérification : niveau hiérarchique + autorisation nominative |
| Fichiers sensibles | Niveaux d'accès par défaut selon type de dossier |

### 10.3 Conformité BTP

| Obligation | Implémentation |
|-----------|----------------|
| Conservation PPSPS | Dossier 03-Sécurité, niveau CHEF_CHANTIER |
| Conservation DOE | Dossier personnalisé, niveau CONDUCTEUR |
| Archivage 10 ans | Soft delete prévu (données conservées) |
| Traçabilité | `uploaded_by` + `uploaded_at` sur chaque document |

---

**Auteur** : Claude Opus 4.5
**Date dernière mise à jour** : 30 janvier 2026
**Version** : 1.0
**Statut** : ✅ Complet

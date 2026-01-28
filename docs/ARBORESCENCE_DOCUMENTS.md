# 📁 Arborescence Documents - Comment ça marche ?

## 🤔 Pourquoi initialiser au lieu d'afficher directement ?

### Sans initialisation (mauvaise approche)
```
Chantier XYZ
└── (vide) ← L'utilisateur doit tout créer manuellement
```

**Problèmes** :
- ❌ Chaque conducteur crée sa propre organisation
- ❌ Pas de standardisation entre chantiers
- ❌ Risque d'oublier des dossiers obligatoires
- ❌ Permissions à configurer manuellement pour chaque dossier

### Avec initialisation (bonne approche)
```
Chantier XYZ
├── 📐 Plans (Conducteur+)
├── 📋 Administratif (Chef+)
├── 🦺 Sécurité (Tous)
├── ✅ Qualité (Chef+)
├── 📷 Photos (Tous)
├── 📝 Comptes-rendus (Chef+)
└── 📦 Livraisons (Chef+)
```

**Avantages** :
- ✅ Structure standardisée conforme aux normes BTP
- ✅ Permissions pré-configurées selon le rôle
- ✅ Dossiers obligatoires (Sécurité, PPSPS, etc.)
- ✅ Gain de temps : 1 clic au lieu de 10 minutes de configuration

---

## 🎯 Arborescence Standard du BTP

L'arborescence est définie dans le backend :
`backend/modules/documents/application/use_cases/init_arborescence.py`

### Structure créée automatiquement :

```
Chantier "Villa Moderne"
│
├── 📐 01 - Plans                                    [Conducteur+]
│   ├── Plans d'exécution
│   ├── Plans techniques
│   └── Plans de récolement
│
├── 📋 02 - Administratif                            [Chef de chantier+]
│   ├── Permis de construire
│   ├── Contrats
│   ├── Devis
│   └── Factures
│
├── 🦺 03 - Sécurité                                 [Tous - Obligatoire]
│   ├── PPSPS (Plan Prévention Sécurité)
│   ├── Registre de sécurité
│   ├── Fiches de risques
│   └── Photos EPI (Équipements Protection)
│
├── ✅ 04 - Qualité                                  [Chef de chantier+]
│   ├── PV de réception
│   ├── Fiches d'autocontrôle
│   └── Attestations de conformité
│
├── 📷 05 - Photos                                   [Tous]
│   ├── Avancement hebdomadaire
│   ├── Photos techniques
│   └── Avant/Après
│
├── 📝 06 - Comptes-rendus                          [Chef de chantier+]
│   ├── Réunions de chantier
│   ├── Visites OPC
│   └── Points techniques
│
└── 📦 07 - Livraisons                              [Chef de chantier+]
    ├── Bons de livraison
    ├── Bordereaux
    └── Récépissés
```

### Niveaux d'accès par dossier

| Dossier | Compagnon | Chef | Conducteur | Admin |
|---------|-----------|------|------------|-------|
| Plans | ❌ Non | ❌ Non | ✅ Oui | ✅ Oui |
| Administratif | ❌ Non | ✅ Oui | ✅ Oui | ✅ Oui |
| **Sécurité** | ✅ **Tous** | ✅ **Tous** | ✅ **Tous** | ✅ **Tous** |
| Qualité | ❌ Non | ✅ Oui | ✅ Oui | ✅ Oui |
| Photos | ✅ Oui | ✅ Oui | ✅ Oui | ✅ Oui |
| Comptes-rendus | ❌ Non | ✅ Oui | ✅ Oui | ✅ Oui |
| Livraisons | ❌ Non | ✅ Oui | ✅ Oui | ✅ Oui |

---

## 📊 Exemple de données créées

### 1. Initialisation de l'arborescence

**Action** : Clic sur "Initialiser l'arborescence standard"

**Ce qui se passe** :
```sql
-- Création des 7 dossiers racine
INSERT INTO dossiers (nom, type_dossier, niveau_acces, chantier_id) VALUES
('01 - Plans', '01_plans', 'conducteur', 9),
('02 - Administratif', '02_administratif', 'chef_chantier', 9),
('03 - Sécurité', '03_securite', 'compagnon', 9),
...
```

**Résultat** :
```
✅ 7 dossiers créés
✅ Permissions configurées
✅ Structure prête à l'emploi
```

### 2. Ajout de documents de démo

Pour avoir des données de test, le script `seed_documents_demo.py` ajoute :

#### Dans "Plans" :
```
📄 Plan masse chantier.pdf (2.3 MB)
📄 Plan facade principale.dwg (1.2 MB)
📄 Détails techniques fondations.pdf (3.3 MB)
```

#### Dans "Sécurité" :
```
📄 PPSPS Version 2.pdf (4.4 MB)
📄 Registre sécurité chantier.xlsx (229 KB)
📄 Photos EPI équipes.jpg (3.3 MB)
```

#### Dans "Photos" :
```
📄 Avancement semaine 12.jpg (5.4 MB)
🎬 Pose première pierre.mp4 (43.5 MB)
📄 Charpente terminée.jpg (4.4 MB)
```

---

## 🔄 Workflow complet

### Étape 1 : Chantier sans documents
```
Documents
└── "Sélectionnez un chantier"
```

### Étape 2 : Sélection d'un chantier
```
Documents - CONGES - Conges payes
└── "Aucun dossier"
    └── [Bouton: Initialiser l'arborescence standard]
```

### Étape 3 : Après initialisation
```
Documents - CONGES - Conges payes

Dossiers:                           Total documents: 0
├── 📐 Plans              [Cond.]   Taille totale: 0 o
├── 📋 Administratif      [Chef]
├── 🦺 Sécurité          [Tous]
├── ✅ Qualité           [Chef]
├── 📷 Photos            [Tous]
├── 📝 Comptes-rendus    [Chef]
└── 📦 Livraisons        [Chef]
```

### Étape 4 : Clic sur un dossier (ex: Plans)
```
Documents - CONGES - Conges payes

Dossiers (colonne gauche)           Documents (colonne droite)
├── 📐 Plans ← SÉLECTIONNÉ          
├── 📋 Administratif                📄 (Aucun document)
├── 🦺 Sécurité                     "Sélectionnez un dossier"
...                                  ou uploadez des fichiers
```

### Étape 5 : Upload d'un document
```
[Zone de drop]
"Glissez vos fichiers ici ou cliquez pour parcourir"

→ Upload → Document ajouté à "Plans"

Documents:
└── 📄 Plan masse.pdf
    Ajouté il y a 2 min par Admin
    2.3 MB
```

---

## 💡 Cas d'usage réels

### Conducteur de travaux
**Besoin** : Nouveau chantier "Immeuble R+3"
1. Sélectionne le chantier
2. Clic "Initialiser l'arborescence"
3. **→ Structure complète en 2 secondes**
4. Upload directement les plans dans "Plans"
5. Upload PPSPS dans "Sécurité"

**Sans initialisation** :
- 15 minutes à créer manuellement 7 dossiers
- Risque d'oublier "Sécurité" (obligatoire !)
- Permissions à configurer dossier par dossier

### Chef de chantier
**Besoin** : Accéder aux documents du chantier
1. Sélectionne le chantier
2. **Structure déjà créée par le conducteur**
3. Peut directement :
   - Consulter les plans
   - Ajouter photos d'avancement
   - Uploader comptes-rendus réunions

### Compagnon
**Besoin** : Consulter le PPSPS
1. Sélectionne le chantier
2. Clique sur "🦺 Sécurité"
3. **Accès autorisé** (niveau_acces = 'compagnon')
4. Télécharge le PPSPS

**Tentative accès "Plans"** :
- ❌ Dossier invisible (niveau_acces = 'conducteur')
- Protection automatique

---

## 🔐 Sécurité et Permissions

### Principe de base
Chaque dossier a un **niveau d'accès minimum** :

```typescript
type NiveauAcces = 'compagnon' | 'chef_chantier' | 'conducteur' | 'admin'
```

### Hiérarchie des droits
```
Admin > Conducteur > Chef de chantier > Compagnon
```

### Exemples

**Compagnon "Pierre" tente d'accéder** :
- ✅ Sécurité (niveau: compagnon) → **Autorisé**
- ✅ Photos (niveau: compagnon) → **Autorisé**
- ❌ Plans (niveau: conducteur) → **Interdit (invisible)**

**Chef "Marie" tente d'accéder** :
- ✅ Sécurité → **Autorisé**
- ✅ Administratif (niveau: chef_chantier) → **Autorisé**
- ❌ Plans (niveau: conducteur) → **Interdit**

**Conducteur "Thomas" tente d'accéder** :
- ✅ Tous les dossiers → **Autorisé**
- ✅ Peut créer sous-dossiers dans "Plans"

---

## 🚀 Pour tester avec des données

### Option 1 : Initialisation + Upload manuel
1. Sélectionnez un chantier
2. Clic "Initialiser l'arborescence standard"
3. Clic sur un dossier (ex: Sécurité)
4. Glissez-déposez un fichier PDF

### Option 2 : Script de démonstration (recommandé)
```bash
cd backend
python scripts/seed_documents_demo.py
```

**Ce script crée** :
- ✅ 20+ documents de démonstration
- ✅ Dans tous les types de dossiers
- ✅ Avec données réalistes (noms, tailles, types)
- ✅ Prêt à tester immédiatement

**Résultat** :
```
📁 Plans (3 documents)
├── Plan masse chantier.pdf
├── Plan facade principale.dwg
└── Détails techniques fondations.pdf

📁 Sécurité (3 documents)
├── PPSPS Version 2.pdf
├── Registre sécurité chantier.xlsx
└── Photos EPI équipes.jpg

📁 Photos (3 documents)
├── Avancement semaine 12.jpg
├── Pose première pierre.mp4
└── Charpente terminée.jpg

... etc
```

---

## 📝 Résumé

| Question | Réponse |
|----------|---------|
| **Pourquoi initialiser ?** | Structure standardisée + permissions automatiques |
| **C'est obligatoire ?** | Non, mais fortement recommandé |
| **Peut-on personnaliser ?** | Oui, après initialisation (bouton "+ Nouveau") |
| **Les permissions ?** | Configurées automatiquement selon le type de dossier |
| **Combien de temps ?** | 2 secondes vs 15 minutes en manuel |
| **Conforme BTP ?** | Oui, structure basée sur normes construction |

---

**🎯 Conclusion** : L'initialisation de l'arborescence standardise l'organisation documentaire, assure la conformité réglementaire, et fait gagner un temps précieux aux équipes terrain.

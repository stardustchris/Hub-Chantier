# Guide de Publication PyPI - Hub Chantier SDK Python

**Version** : 1.0.0
**Date** : 2026-01-29
**Status** : ✅ Package construit et prêt

---

## 📦 Packages Construits

```
dist/
├── hub_chantier-1.0.0.tar.gz          (11 KB - source distribution)
└── hub_chantier-1.0.0-py3-none-any.whl (12 KB - wheel)
```

**Build effectué avec** : `python -m build`

---

## 🔐 Prérequis Publication

### 1. Compte PyPI

Créer un compte sur :
- **Production** : https://pypi.org/account/register/
- **Test** : https://test.pypi.org/account/register/ (pour tester)

### 2. Token API PyPI

1. Se connecter sur https://pypi.org
2. Aller dans **Account Settings** > **API tokens**
3. Créer un token avec scope **"Entire account"** ou **"hub-chantier project"**
4. Copier le token (commence par `pypi-...`)

### 3. Configurer Twine

Créer `~/.pypirc` :

```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
repository = https://test.pypi.org/legacy/
```

**⚠️ IMPORTANT** : Ne JAMAIS commit ce fichier dans Git !

```bash
chmod 600 ~/.pypirc
```

---

## 🧪 Publication Test (Recommandé)

### Étape 1 : Publier sur TestPyPI

```bash
cd /home/user/Hub-Chantier/sdk/python

# Vérifier les packages
twine check dist/*

# Uploader sur TestPyPI
twine upload --repository testpypi dist/*
```

### Étape 2 : Tester l'Installation

```bash
# Installer depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ hub-chantier

# Tester import
python -c "from hub_chantier import HubChantierClient; print('✅ OK')"
```

### Étape 3 : Vérifier la Page PyPI

Visiter : https://test.pypi.org/project/hub-chantier/

---

## 🚀 Publication Production

### ⚠️ CHECKLIST PRÉ-PUBLICATION

- [ ] **Version unique** : Vérifier que 1.0.0 n'existe pas déjà
- [ ] **Tests passent** : `pytest tests/ -v` (7/7 tests OK)
- [ ] **Qualité code** : `flake8` + `mypy` (0 erreur)
- [ ] **README complet** : Instructions installation/usage
- [ ] **CHANGELOG à jour** : Version 1.0.0 documentée
- [ ] **License** : Fichier LICENSE présent
- [ ] **Tests manuels** : SDK testé en conditions réelles

### Commandes Publication

```bash
cd /home/user/Hub-Chantier/sdk/python

# 1. Vérifier les packages
twine check dist/*

# 2. Uploader sur PyPI
twine upload dist/*

# Ou avec confirmation interactive
twine upload --verbose dist/*
```

**Sortie attendue** :
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading hub_chantier-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.0/12.0 kB • 00:00
Uploading hub_chantier-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.0/11.0 kB • 00:00

View at:
https://pypi.org/project/hub-chantier/1.0.0/
```

### Vérification Post-Publication

```bash
# 1. Attendre 1-2 minutes (propagation CDN)

# 2. Installer depuis PyPI
pip install hub-chantier

# 3. Tester
python -c "from hub_chantier import HubChantierClient; print('✅ SDK installé')"

# 4. Vérifier page PyPI
# https://pypi.org/project/hub-chantier/
```

---

## 📝 Publication Versions Suivantes

### 1. Modifier la Version

**Fichier** : `setup.py` ligne 13

```python
setup(
    name="hub-chantier",
    version="1.0.1",  # Incrémenter
    ...
)
```

**Conventions** : [Semantic Versioning](https://semver.org/)
- **MAJOR** (1.x.x) : Breaking changes
- **MINOR** (x.1.x) : Nouvelles features (backward-compatible)
- **PATCH** (x.x.1) : Bug fixes

### 2. Mettre à Jour CHANGELOG

Ajouter entrée pour la nouvelle version.

### 3. Reconstruire

```bash
# Nettoyer anciens builds
rm -rf dist/ build/ *.egg-info

# Reconstruire
python -m build
```

### 4. Republier

```bash
twine upload dist/*
```

---

## 🛠️ Troubleshooting

### Erreur : "Package already exists"

**Cause** : Version déjà publiée sur PyPI
**Solution** : Incrémenter version dans `setup.py`

```python
version="1.0.1",  # Au lieu de 1.0.0
```

### Erreur : "Invalid credentials"

**Cause** : Token PyPI incorrect ou expiré
**Solution** : Regénérer token sur pypi.org et mettre à jour `~/.pypirc`

### Erreur : "Package name already taken"

**Cause** : `hub-chantier` déjà utilisé par quelqu'un d'autre
**Solution** : Choisir nom alternatif (ex: `hub-chantier-btp`, `hubchantier`)

### Erreur : "Description content type missing"

**Cause** : setup.py incomplet
**Solution** : Déjà corrigé dans notre setup.py (ligne 18)

```python
long_description_content_type="text/markdown",
```

---

## 📊 Monitoring Post-Publication

### Stats PyPI

Visiter : https://pypistats.org/packages/hub-chantier

Métriques disponibles :
- Téléchargements par jour/mois
- Versions Python utilisées
- Systèmes d'exploitation
- Pays d'origine

### Badges README

Ajouter dans `README.md` :

```markdown
[![PyPI version](https://badge.fury.io/py/hub-chantier.svg)](https://badge.fury.io/py/hub-chantier)
[![Downloads](https://pepy.tech/badge/hub-chantier)](https://pepy.tech/project/hub-chantier)
```

---

## 🔒 Sécurité

### Protéger le Token PyPI

```bash
# Ne JAMAIS commit .pypirc
echo "~/.pypirc" >> ~/.gitignore

# Permissions restrictives
chmod 600 ~/.pypirc
```

### Scanner Dépendances

```bash
# Vérifier vulnérabilités
pip install safety
safety check -r requirements.txt
```

### Signer les Releases

```bash
# Avec GPG (optionnel)
twine upload --sign dist/*
```

---

## 📧 Support Post-Publication

**Issues** : https://github.com/hub-chantier/sdk-python/issues
**Email** : support@hub-chantier.fr
**Documentation** : https://docs.hub-chantier.fr

---

## ✅ Checklist Complète

### Pré-Publication
- [x] Package construit (`python -m build`)
- [x] Tests unitaires passent (7/7)
- [x] Qualité code validée (flake8 + mypy)
- [x] Documentation complète (README.md)
- [x] Code review effectuée (9.5/10)
- [x] setup.py configuré
- [x] requirements.txt à jour
- [ ] LICENSE ajouté (TODO)
- [ ] Compte PyPI créé
- [ ] Token API configuré

### Publication Test
- [ ] Publié sur test.pypi.org
- [ ] Installation testée depuis TestPyPI
- [ ] Imports fonctionnels

### Publication Production
- [ ] Publié sur pypi.org
- [ ] Installation testée depuis PyPI
- [ ] Page PyPI vérifiée
- [ ] Annonce dans CHANGELOG
- [ ] Tag Git créé (`v1.0.0`)

---

**Préparé par** : Claude Code
**Date** : 2026-01-29
**Session** : https://claude.ai/code/session_011u3yRrSvnWiaaZPEQvnBg6

#!/usr/bin/env python3
"""
Script de migration SPECIFICATIONS.md vers architecture modulaire.
Extrait chaque module dans un fichier séparé dans docs/specifications/
"""

import re
from pathlib import Path

# Chemins
SPECS_FILE = Path("docs/SPECIFICATIONS.md")
OUTPUT_DIR = Path("docs/specifications")
BACKUP_FILE = Path("docs/SPECIFICATIONS.md.backup")

def backup_original():
    """Créer une sauvegarde du fichier original."""
    print(f"📦 Sauvegarde de {SPECS_FILE} vers {BACKUP_FILE}")
    content = SPECS_FILE.read_text(encoding='utf-8')
    BACKUP_FILE.write_text(content, encoding='utf-8')
    print(f"✅ Sauvegarde créée")

def parse_specifications():
    """Parse le fichier SPECIFICATIONS.md et extrait les sections."""
    content = SPECS_FILE.read_text(encoding='utf-8')

    # Extraire l'entête (avant la table des matières)
    header_match = re.search(r'^(.*?)(?=## TABLE DES MATIERES)', content, re.DOTALL)
    header = header_match.group(1).strip() if header_match else ""

    # Extraire la table des matières
    toc_match = re.search(r'## TABLE DES MATIERES(.*?)(?=^---)', content, re.DOTALL | re.MULTILINE)
    toc = toc_match.group(0).strip() if toc_match else ""

    # Trouver toutes les sections principales (## 1. INTRODUCTION, ## 2. TABLEAU, etc.)
    sections = []
    pattern = r'^## (\d+)\. (.+?)$'

    lines = content.split('\n')
    current_section = None
    current_content = []

    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match:
            # Sauvegarder la section précédente
            if current_section:
                sections.append({
                    'number': current_section['number'],
                    'title': current_section['title'],
                    'content': '\n'.join(current_content).strip()
                })

            # Démarrer nouvelle section
            current_section = {
                'number': match.group(1),
                'title': match.group(2)
            }
            current_content = [line]
        elif current_section:
            current_content.append(line)

    # Ajouter la dernière section
    if current_section:
        sections.append({
            'number': current_section['number'],
            'title': current_section['title'],
            'content': '\n'.join(current_content).strip()
        })

    return header, toc, sections

def sanitize_filename(title):
    """Convertit un titre en nom de fichier valide."""
    # Mapping spécial pour les titres connus
    mappings = {
        'INTRODUCTION': '01-introduction',
        'TABLEAU DE BORD & FEED D\'ACTUALITES': '02-tableau-de-bord',
        'TABLEAU DE BORD & FEED DACTUALITES': '02-tableau-de-bord',
        'GESTION DES UTILISATEURS': '03-utilisateurs',
        'GESTION DES CHANTIERS': '04-chantiers',
        'PLANNING OPERATIONNEL': '05-planning-operationnel',
        'PLANNING DE CHARGE': '06-planning-charge',
        'FEUILLES D\'HEURES': '07-feuilles-heures',
        'FEUILLES DHEURES': '07-feuilles-heures',
        'FORMULAIRES CHANTIER': '08-formulaires',
        'GESTION DOCUMENTAIRE (GED)': '09-ged',
        'SIGNALEMENTS': '10-signalements',
        'LOGISTIQUE - GESTION DU MATERIEL': '11-logistique',
        'GESTION DES INTERVENTIONS': '12-interventions',
        'GESTION DES TACHES': '13-taches',
        'INTEGRATIONS': '14-integrations',
        'SECURITE ET CONFORMITE': '15-securite',
        'GLOSSAIRE': '19-glossaire',
        'GESTION FINANCIERE ET BUDGETAIRE': '17-financier',
        'GESTION DES DEVIS': '18-devis',
    }

    title_upper = title.upper().strip()
    if title_upper in mappings:
        return mappings[title_upper]

    # Sinon, générer automatiquement
    filename = title.lower()
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[\s_]+', '-', filename)
    return filename

def write_module_files(sections):
    """Écrit chaque section dans son propre fichier."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    files_created = []

    for section in sections:
        filename = sanitize_filename(section['title'])
        # Ajouter le numéro si pas déjà présent
        if not filename.startswith(section['number'].zfill(2)):
            filename = f"{section['number'].zfill(2)}-{filename}"

        filename = f"{filename}.md"
        filepath = OUTPUT_DIR / filename

        print(f"📝 Création de {filepath}")
        filepath.write_text(section['content'], encoding='utf-8')

        files_created.append({
            'number': section['number'],
            'title': section['title'],
            'filename': filename
        })

    return files_created

def create_index(header, toc, files_created):
    """Crée le nouveau fichier SPECIFICATIONS.md (index)."""

    # Créer la nouvelle table des matières avec liens
    new_toc_lines = []
    for file_info in files_created:
        title = file_info['title']
        filename = file_info['filename']
        new_toc_lines.append(f"{file_info['number']}. [{title}](./specifications/{filename})")

    new_content = f"""{header}

## TABLE DES MATIERES

{chr(10).join(new_toc_lines)}

---

## 📚 Organisation de la documentation

Ce document est l'index principal du Cahier des Charges Fonctionnel de Hub Chantier.

Chaque module est documenté dans un fichier séparé dans le dossier `specifications/` :

- **Modules opérationnels** (1-15) : Fonctionnalités principales de l'application
- **Module 17** : Gestion Financière et Budgétaire
- **Module 18** : Gestion des Devis (phase commerciale)
- **Module 19** : Glossaire des termes métier BTP

### Structure des fichiers

```
docs/
├── SPECIFICATIONS.md (ce fichier - index principal)
└── specifications/
    ├── 01-introduction.md
    ├── 02-tableau-de-bord.md
    ├── 03-utilisateurs.md
    ├── 04-chantiers.md
    ├── 05-planning-operationnel.md
    ├── 06-planning-charge.md
    ├── 07-feuilles-heures.md
    ├── 08-formulaires.md
    ├── 09-ged.md
    ├── 10-signalements.md
    ├── 11-logistique.md
    ├── 12-interventions.md
    ├── 13-taches.md
    ├── 14-integrations.md
    ├── 15-securite.md
    ├── 17-financier.md
    ├── 18-devis.md
    └── 19-glossaire.md
```

### Avantages de cette architecture

- ✅ Fichiers < 200 lignes chacun (très lisibles)
- ✅ Édition parallèle possible (plusieurs développeurs)
- ✅ Git diff plus précis (1 module = 1 fichier)
- ✅ Navigation rapide (1 clic par module)
- ✅ Scalable jusqu'à 100+ modules

---

## 🔗 Références complémentaires

- [Architecture Clean](./architecture/CLEAN_ARCHITECTURE.md)
- [Guide de déploiement](./DEPLOYMENT.md)
- [Setup local](./LOCAL_SETUP.md)
- [Onboarding utilisateurs](./ONBOARDING_UTILISATEURS.md)

---

*Greg Constructions - Cahier des Charges Fonctionnel v2.2 - Janvier 2026*
"""

    print(f"📄 Création du nouveau SPECIFICATIONS.md (index)")
    SPECS_FILE.write_text(new_content, encoding='utf-8')

def main():
    print("🚀 Migration SPECIFICATIONS.md vers architecture modulaire")
    print("=" * 70)

    # 1. Sauvegarde
    backup_original()
    print()

    # 2. Parse
    print("📖 Analyse du fichier SPECIFICATIONS.md...")
    header, toc, sections = parse_specifications()
    print(f"✅ Trouvé {len(sections)} sections")
    print()

    # 3. Écrire les fichiers modules
    print("📝 Création des fichiers modules...")
    files_created = write_module_files(sections)
    print(f"✅ {len(files_created)} fichiers créés")
    print()

    # 4. Créer le nouvel index
    print("📄 Création du nouveau SPECIFICATIONS.md (index)...")
    create_index(header, toc, files_created)
    print("✅ Index créé")
    print()

    print("=" * 70)
    print("✅ Migration terminée avec succès !")
    print()
    print(f"📦 Sauvegarde disponible : {BACKUP_FILE}")
    print(f"📁 Fichiers modules : {OUTPUT_DIR}/")
    print(f"📄 Nouvel index : {SPECS_FILE}")
    print()
    print("🔍 Vérifiez les fichiers avant de committer :")
    print(f"   git diff {SPECS_FILE}")
    print(f"   ls -lh {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()

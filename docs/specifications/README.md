# Spécifications Hub Chantier - Modules

Ce dossier contient la documentation détaillée de chaque module de Hub Chantier.

## 📋 Structure

Chaque module est documenté dans un fichier séparé :

| Fichier | Module | Taille | Description |
|---------|--------|--------|-------------|
| `01-introduction.md` | Introduction | 35 lignes | Contexte, objectifs, périmètre fonctionnel |
| `02-tableau-de-bord.md` | Tableau de Bord | 155 lignes | Dashboard + Feed social |
| `03-utilisateurs.md` | Utilisateurs | 75 lignes | Gestion comptes, rôles, permissions |
| `04-chantiers.md` | Chantiers | 125 lignes | Création et suivi projets construction |
| `05-planning-operationnel.md` | Planning Opérationnel | 89 lignes | Affectation équipes aux chantiers |
| `06-planning-charge.md` | Planning de Charge | 51 lignes | Vision capacitaire par métier |
| `07-feuilles-heures.md` | Feuilles d'Heures | 65 lignes | Saisie et validation temps travail |
| `08-formulaires.md` | Formulaires | 34 lignes | Templates personnalisables |
| `09-ged.md` | GED | 57 lignes | Gestion documentaire |
| `10-signalements.md` | Signalements | 93 lignes | Communication urgence et suivi problèmes |
| `11-logistique.md` | Logistique | 55 lignes | Réservation engins et matériel |
| `12-interventions.md` | Interventions | 52 lignes | Gestion SAV et maintenance |
| `13-taches.md` | Tâches | 54 lignes | Gestion travaux et avancement |
| `14-integrations.md` | Intégrations | 87 lignes | APIs et connexions externes |
| `15-securite.md` | Sécurité | 58 lignes | Conformité et protection données |
| `17-financier.md` | Financier | 183 lignes | Budgets, achats, situations travaux |
| `18-devis.md` | Devis | 195 lignes | Phase commerciale, chiffrage, conversion |
| `19-glossaire.md` | Glossaire | 39 lignes | Termes métier BTP |

**Total** : ~1 600 lignes réparties sur 18 fichiers (vs 1 fichier monolithique de 1 572 lignes)

## ✅ Avantages de cette architecture

- **Lisibilité** : Fichiers < 200 lignes chacun (très lisibles)
- **Édition parallèle** : Plusieurs développeurs peuvent travailler simultanément
- **Git diff précis** : 1 module = 1 fichier = commits ciblés
- **Navigation rapide** : 1 clic par module depuis l'index
- **Scalabilité** : Architecture extensible jusqu'à 100+ modules

## 🔗 Navigation

Pour accéder à un module, ouvrir le fichier correspondant ou utiliser l'index principal :

📄 [../SPECIFICATIONS.md](../SPECIFICATIONS.md) (index avec liens)

## 📐 Conventions

- **Numérotation** : `NN-nom-module.md` (ex: `18-devis.md`)
- **Titre H2** : Chaque fichier commence par `## NN. TITRE MODULE`
- **Sections H3** : Sous-sections numérotées (ex: `### 18.1 Vue d'ensemble`)
- **Références croisées** : Utiliser `§NN` pour référencer un autre module (ex: "voir §17 Financier")

## 🔄 Mise à jour

Lors de l'ajout d'un nouveau module :

1. Créer le fichier `docs/specifications/NN-nom.md`
2. Ajouter le lien dans `docs/SPECIFICATIONS.md` (table des matières)
3. Utiliser le pattern de numérotation cohérent

## 📊 Statistiques

- **18 modules** documentés
- **~1 600 lignes** au total
- **Taille moyenne** : ~90 lignes/module
- **Taille max** : 195 lignes (Module 18 - Devis)
- **Taille min** : 34 lignes (Module 8 - Formulaires)

---

*Dernière mise à jour : 1er février 2026*

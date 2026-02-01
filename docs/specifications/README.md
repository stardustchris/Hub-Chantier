# Spécifications Hub Chantier - Modules

Ce dossier contient la documentation détaillée de chaque module de Hub Chantier.

## 📋 Structure

Chaque module est documenté dans un fichier séparé :

| Fichier | Module | Taille | Description |
|---------|--------|--------|-------------|
| `01-introduction.md` | Introduction | ~40 lignes | Contexte, objectifs, périmètre fonctionnel |
| `02-tableau-de-bord.md` | Tableau de Bord | ~190 lignes | Dashboard + Feed social |
| `03-utilisateurs.md` | Utilisateurs | ~90 lignes | Gestion comptes, rôles, permissions |
| `04-chantiers.md` | Chantiers | ~150 lignes | Création et suivi projets construction |
| `05-planning-operationnel.md` | Planning Opérationnel | ~100 lignes | Affectation équipes aux chantiers |
| `06-planning-charge.md` | Planning de Charge | ~60 lignes | Vision capacitaire par métier |
| `07-feuilles-heures.md` | Feuilles d'Heures | ~80 lignes | Saisie et validation temps travail |
| `08-formulaires.md` | Formulaires | ~40 lignes | Templates personnalisables |
| `09-ged.md` | GED | ~70 lignes | Gestion documentaire |
| `10-signalements.md` | Signalements | ~110 lignes | Communication urgence et suivi problèmes |
| `11-logistique.md` | Logistique | ~65 lignes | Réservation engins et matériel |
| `12-interventions.md` | Interventions | ~60 lignes | Gestion SAV et maintenance |
| `13-taches.md` | Tâches | ~65 lignes | Gestion travaux et avancement |
| `14-integrations.md` | Intégrations | ~100 lignes | APIs et connexions externes |
| `15-securite.md` | Sécurité | ~70 lignes | Conformité et protection données |
| `17-financier.md` | Financier | ~350 lignes | Budgets, achats, situations travaux |
| `18-connecteurs-webhooks-pennylane-silae.md` | Webhooks | ~120 lignes | Intégration Pennylane (compta) & Silae (paie) |
| `20-devis.md` | **Devis** | **195 lignes** | **Phase commerciale, chiffrage, conversion** |
| `21-glossaire.md` | Glossaire | ~45 lignes | Termes métier BTP |

**Total** : ~2 050 lignes réparties sur 19 fichiers (vs 1 fichier monolithique de 2 354 lignes)

## ✅ Avantages de cette architecture

- **Lisibilité** : Fichiers < 400 lignes chacun (très lisibles)
- **Édition parallèle** : Plusieurs développeurs peuvent travailler simultanément
- **Git diff précis** : 1 module = 1 fichier = commits ciblés
- **Navigation rapide** : 1 clic par module depuis l'index
- **Scalabilité** : Architecture extensible jusqu'à 100+ modules

## 🆕 Nouveau Module 20 : Gestion des Devis

Le Module 20 couvre la **phase commerciale** en amont du cycle de vie actuel de Hub Chantier :

### Fonctionnalités clés (25 features)

- **Métrés numériques 2D** : Mesure directe sur plans PDF (game changer)
- **Consultations sous-traitants** : Workflow complet envoi/réception/comparaison offres
- **Import DPGF** : Réponse rapide aux appels d'offres publics
- **Variantes de devis** : Économique/Standard/Premium avec comparatif automatique
- **Bibliothèque de prix** : Import Batiprix (80 000+ ouvrages)
- **Déboursés secs avancés** : Pilotage marges multi-niveaux
- **Signature électronique** : Validation client conforme eIDAS
- **Conversion automatique** : Devis accepté → Chantier + Budget + Planning

### Roadmap implémentation

- **Phase 1** (40j) : MVP commercial (bibliothèque, déboursés, PDF)
- **Phase 2** (50j) : Automatisation (signature, conversion chantier)
- **Phase 3** (45j) : Productivité (Batiprix, DPGF, consultations ST)
- **Phase 4** (53j) : Premium (métrés 2D, hors-ligne)

**Total** : 188 jours (9 mois)

## 🔗 Navigation

Pour accéder à un module, ouvrir le fichier correspondant ou utiliser l'index principal :

📄 [../SPECIFICATIONS.md](../SPECIFICATIONS.md) (index avec liens)

## 📐 Conventions

- **Numérotation** : `NN-nom-module.md` (ex: `20-devis.md`)
- **Titre H2** : Chaque fichier commence par `## NN. TITRE MODULE`
- **Sections H3** : Sous-sections numérotées (ex: `### 20.1 Vue d'ensemble`)
- **Références croisées** : Utiliser `§NN` pour référencer un autre module (ex: "voir §17 Financier")

## 🔄 Mise à jour

Lors de l'ajout d'un nouveau module :

1. Créer le fichier `docs/specifications/NN-nom.md`
2. Ajouter le lien dans `docs/SPECIFICATIONS.md` (table des matières)
3. Utiliser le pattern de numérotation cohérent
4. Mettre à jour ce README.md

## 📊 Statistiques

- **19 modules** documentés (dont 1 nouveau : Devis)
- **~2 050 lignes** au total
- **Taille moyenne** : ~110 lignes/module
- **Taille max** : 350 lignes (Module 17 - Financier)
- **Taille min** : 40 lignes (Module 8 - Formulaires)

---

*Dernière mise à jour : 1er février 2026 - Version 2.3*

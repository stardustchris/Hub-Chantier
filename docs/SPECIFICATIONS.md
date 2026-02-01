# GREG CONSTRUCTIONS

**Gros Oeuvre - Batiment**

## CAHIER DES CHARGES FONCTIONNEL

Application SaaS de Gestion de Chantiers

**Version 2.2 - Janvier 2026**

---

## TABLE DES MATIERES

1. [INTRODUCTION](./specifications/01-introduction.md)
2. [TABLEAU DE BORD & FEED D'ACTUALITES](./specifications/02-tableau-de-bord.md)
3. [GESTION DES UTILISATEURS](./specifications/03-utilisateurs.md)
4. [GESTION DES CHANTIERS](./specifications/04-chantiers.md)
5. [PLANNING OPERATIONNEL](./specifications/05-planning-operationnel.md)
6. [PLANNING DE CHARGE](./specifications/06-planning-charge.md)
7. [FEUILLES D'HEURES](./specifications/07-feuilles-heures.md)
8. [FORMULAIRES CHANTIER](./specifications/08-formulaires.md)
9. [GESTION DOCUMENTAIRE (GED)](./specifications/09-ged.md)
10. [SIGNALEMENTS](./specifications/10-signalements.md)
11. [LOGISTIQUE - GESTION DU MATERIEL](./specifications/11-logistique.md)
12. [GESTION DES INTERVENTIONS](./specifications/12-interventions.md)
13. [GESTION DES TACHES](./specifications/13-taches.md)
14. [INTEGRATIONS](./specifications/14-integrations.md)
15. [SECURITE ET CONFORMITE](./specifications/15-securite.md)
17. [GESTION FINANCIERE ET BUDGETAIRE](./specifications/17-financier.md)
18. [GESTION DES DEVIS](./specifications/18-devis.md)
19. [GLOSSAIRE](./specifications/19-glossaire.md)

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

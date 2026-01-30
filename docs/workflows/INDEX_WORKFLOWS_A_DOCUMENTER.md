# Index des Workflows à Documenter - Hub Chantier

**Date** : 30 janvier 2026
**Auteur** : Claude Sonnet 4.5

---

## 🎯 Objectif

Liste exhaustive des workflows métier de Hub Chantier nécessitant une documentation pour assurer la cohérence, faciliter la maintenance et l'onboarding des développeurs.

---

## ✅ WORKFLOWS DÉJÀ DOCUMENTÉS

| Workflow | Fichier | Statut | Complétude |
|----------|---------|--------|------------|
| **Authentification** | `WORKFLOW_AUTHENTIFICATION.md` | ✅ Complet | 100% - Audit + Gap Analysis |
| **Feuilles d'Heures (données)** | `WORKFLOW_FEUILLES_HEURES.md` | ✅ Complet | 100% - Diagnostic données + Fix |
| **Refactoring Pointages** | `REFACTORING_POINTAGES_ARCHITECTURE.md` | ✅ Complet | 100% - Clean Architecture |
| **Nettoyage Données** | `NETTOYAGE_DONNEES_DEMO.md` | ✅ Complet | 100% - Suppression mocks |
| **Planning Opérationnel** | `WORKFLOW_PLANNING_OPERATIONNEL.md` | ✅ Complet | 100% - Affectations, absences, drag&drop, conflits |
| **Cycle de Vie Chantier** | `WORKFLOW_CYCLE_VIE_CHANTIER.md` | ✅ Complet | 100% - Machine à états, création, transitions, RGPD |
| **Validation Feuilles d'Heures** | `WORKFLOW_VALIDATION_FEUILLES_HEURES.md` | ✅ Complet | 100% - Workflow validation, signature manuscrite, verrouillage mensuel, export paie |
| **Gestion Documentaire (GED)** | `WORKFLOW_GESTION_DOCUMENTAIRE.md` | ✅ Complet | 100% - Upload, arborescence, permissions, versionnage, prévisualisation |
| **Formulaires Dynamiques** | `WORKFLOW_FORMULAIRES_DYNAMIQUES.md` | ✅ Complet | 100% - Templates, machine à états, auto-fill, signature, export PDF |
| **Signalements** | `WORKFLOW_SIGNALEMENTS.md` | ✅ Complet | 100% - Machine à états, SLA, escalade, réponses, statistiques |
| **Logistique Matériel** | `WORKFLOW_LOGISTIQUE_MATERIEL.md` | ✅ Complet | 100% - Catalogue, réservation, validation N+1, conflits, calendrier |
| **Planning de Charge** | `WORKFLOW_PLANNING_CHARGE.md` | ✅ Complet | 100% - Taux occupation, besoins, capacité, métiers, footer |

---

## 🔴 WORKFLOWS CRITIQUES (Haute Priorité)

### 1. **Planning Opérationnel** ✅ DOCUMENTÉ
**Module** : `backend/modules/planning/`

**Workflow à documenter** :
- Affectation d'un compagnon à un chantier
- Gestion des absences (CONGES, MALADIE, FORMATION, RTT)
- Drag & Drop des affectations
- Gestion des conflits (double affectation)
- Synchronisation Planning → Feuilles d'Heures (FDH-10)
- Navigation hebdomadaire
- Filtres par chantier/utilisateur/métier
- Notifications d'affectation

**Enjeux** :
- ❌ Cœur métier de l'application
- ❌ Interaction complexe avec pointages
- ❌ Règles métier critiques (heures prévues, conflits)
- ❌ Module de référence pour Clean Architecture

**Complexité** : ⭐⭐⭐⭐⭐ (Très élevée)

**Fichier recommandé** : `WORKFLOW_PLANNING_OPERATIONNEL.md`

---

### 2. **Cycle de Vie d'un Chantier** ✅ DOCUMENTÉ
**Module** : `backend/modules/chantiers/`

**Workflow à documenter** :
1. **Création** :
   - Saisie des informations (code, nom, adresse, dates)
   - Affectation conducteur de travaux
   - Affectation chef de chantier
   - Définition heures estimées
   - Upload photo de couverture
   - Géolocalisation (latitude/longitude)

2. **Gestion en Cours** :
   - Modification des informations
   - Ajout de contacts (maître d'ouvrage, architecte)
   - Gestion des dossiers (GED)
   - Gestion des documents
   - Création de formulaires chantier

3. **Statuts** :
   - Ouvert → En cours → Réceptionné → Fermé
   - Règles de transition
   - Impact sur planning/pointages

4. **Archivage/Suppression** :
   - Soft delete (deleted_at)
   - Conservation des données historiques
   - Restrictions (pointages existants, etc.)

**Enjeux** :
- ❌ Entité centrale de l'application
- ❌ Multiples interactions (planning, pointages, documents, formulaires)
- ❌ Règles métier de statuts

**Complexité** : ⭐⭐⭐⭐ (Élevée)

**Fichier recommandé** : `WORKFLOW_CYCLE_VIE_CHANTIER.md`

---

### 3. **Validation Feuilles d'Heures** ✅ DOCUMENTÉ
**Module** : `backend/modules/pointages/`

**Workflow à documenter** :
1. **Saisie Compagnon** :
   - Création pointages depuis planning (FDH-10)
   - Saisie manuelle heures normales/sup
   - Modification avant signature
   - Signature électronique

2. **Workflow de Validation** :
   - Soumission par compagnon (BROUILLON → SOUMIS)
   - Validation chef de chantier (SOUMIS → VALIDE)
   - Rejet avec commentaire (SOUMIS → BROUILLON)
   - Verrouillage après validation

3. **Calculs Paie** :
   - Variables de paie (primes, indemnités)
   - Export pour logiciel paie
   - Récapitulatifs mensuels

**Enjeux** :
- ❌ Workflow multi-étapes critique
- ❌ Statuts et transitions complexes
- ❌ Notifications à chaque étape
- ❌ Calculs paie sensibles

**Complexité** : ⭐⭐⭐⭐⭐ (Très élevée)

**Fichier recommandé** : `WORKFLOW_VALIDATION_FEUILLES_HEURES.md`

---

## 🟡 WORKFLOWS IMPORTANTS (Priorité Moyenne)

### 4. **Gestion Documentaire (GED)** ✅ DOCUMENTÉ
**Module** : `backend/modules/documents/`

**Workflow documenté** : `WORKFLOW_GESTION_DOCUMENTAIRE.md`
- Structure arborescente (7 dossiers standards), upload (10GB max), permissions 4 niveaux
- Versionnage, prévisualisation, téléchargement ZIP, audit trail

**Complexité** : ⭐⭐⭐⭐ (Élevée)

---

### 5. **Formulaires Chantier Dynamiques** ✅ DOCUMENTÉ
**Module** : `backend/modules/formulaires/`

**Workflow documenté** : `WORKFLOW_FORMULAIRES_DYNAMIQUES.md`
- Templates (8 catégories, 21 types de champs), machine à états (BROUILLON→SOUMIS→VALIDÉ→ARCHIVÉ)
- Auto-fill GPS/date/user, signature manuscrite, photos géolocalisées, export PDF

**Complexité** : ⭐⭐⭐⭐ (Élevée)

---

### 6. **Signalements / Memos** ✅ DOCUMENTÉ
**Module** : `backend/modules/signalements/`

**Workflow documenté** : `WORKFLOW_SIGNALEMENTS.md`
- Machine à états (OUVERT→EN_COURS→TRAITÉ→CLÔTURÉ), 4 priorités avec SLA (4h/24h/48h/72h)
- Escalade lazy (50%→chef, 100%→conducteur, 200%→admin), fil de réponses, statistiques

**Complexité** : ⭐⭐⭐ (Moyenne)

---

### 7. **Logistique - Réservation Matériel** ✅ DOCUMENTÉ
**Module** : `backend/modules/logistique/`

**Workflow documenté** : `WORKFLOW_LOGISTIQUE_MATERIEL.md`
- Catalogue (5 catégories), réservation (EN_ATTENTE→VALIDÉE/REFUSÉE/ANNULÉE)
- Validation N+1 configurable, détection conflits, calendrier 7 jours, rappel J-1

**Complexité** : ⭐⭐⭐ (Moyenne)

---

### 8. **Planning de Charge** ✅ DOCUMENTÉ
**Module** : `backend/modules/planning/` (sous-module charge)

**Workflow documenté** : `WORKFLOW_PLANNING_CHARGE.md`
- Vue tabulaire chantiers x semaines, taux d'occupation (5 niveaux), 9 types de métiers
- Besoins manuels, capacité auto (35h/sem), footer "À recruter" / "À placer"

**Complexité** : ⭐⭐⭐⭐ (Élevée)

---

## 🟢 WORKFLOWS SECONDAIRES (Basse Priorité)

### 9. **Interventions SAV**
**Module** : `backend/modules/interventions/`

**Workflow** : Gestion interventions ponctuelles post-livraison

**Complexité** : ⭐⭐ (Faible)

---

### 10. **Gestion des Tâches**
**Module** : `backend/modules/taches/`

**Workflow** : Todo list par chantier avec affectations

**Complexité** : ⭐⭐ (Faible)

---

### 11. **Dashboard & Feed Social**
**Module** : `backend/modules/dashboard/`

**Workflow** : Publication posts, likes, commentaires, ciblage

**Complexité** : ⭐⭐⭐ (Moyenne)

---

### 12. **Notifications**
**Module** : `backend/modules/notifications/`

**Workflow** : Push, email, SMS selon types d'événements

**Complexité** : ⭐⭐⭐ (Moyenne)

---

## 📊 MATRICE DE PRIORISATION

| # | Workflow | Priorité | Complexité | Impact Business | Effort | Statut |
|---|----------|----------|------------|-----------------|--------|--------|
| 1 | **Planning Opérationnel** | ✅ FAIT | ⭐⭐⭐⭐⭐ | 🔥 CRITIQUE | 3j | ✅ Complet (WORKFLOW_PLANNING_OPERATIONNEL.md) |
| 2 | **Cycle Vie Chantier** | ✅ FAIT | ⭐⭐⭐⭐ | 🔥 CRITIQUE | 2j | ✅ Complet (WORKFLOW_CYCLE_VIE_CHANTIER.md) |
| 3 | **Validation Feuilles Heures** | ✅ FAIT | ⭐⭐⭐⭐⭐ | 🔥 CRITIQUE | 3j | ✅ Complet (WORKFLOW_VALIDATION_FEUILLES_HEURES.md) |
| 4 | **GED** | ✅ FAIT | ⭐⭐⭐⭐ | ⚠️ IMPORTANT | 2j | ✅ Complet (WORKFLOW_GESTION_DOCUMENTAIRE.md) |
| 5 | **Formulaires Dynamiques** | ✅ FAIT | ⭐⭐⭐⭐ | ⚠️ IMPORTANT | 2j | ✅ Complet (WORKFLOW_FORMULAIRES_DYNAMIQUES.md) |
| 6 | **Signalements** | ✅ FAIT | ⭐⭐⭐ | ⚠️ IMPORTANT | 1j | ✅ Complet (WORKFLOW_SIGNALEMENTS.md) |
| 7 | **Logistique** | ✅ FAIT | ⭐⭐⭐ | ⚠️ IMPORTANT | 1j | ✅ Complet (WORKFLOW_LOGISTIQUE_MATERIEL.md) |
| 8 | **Planning Charge** | ✅ FAIT | ⭐⭐⭐⭐ | ⚠️ IMPORTANT | 2j | ✅ Complet (WORKFLOW_PLANNING_CHARGE.md) |
| 9 | **Interventions** | 🟢 NICE | ⭐⭐ | ℹ️ UTILE | 0.5j | ❌ À faire |
| 10 | **Tâches** | 🟢 NICE | ⭐⭐ | ℹ️ UTILE | 0.5j | ❌ À faire |
| 11 | **Dashboard/Feed** | 🟢 NICE | ⭐⭐⭐ | ℹ️ UTILE | 1j | ❌ À faire |
| 12 | **Notifications** | 🟢 NICE | ⭐⭐⭐ | ℹ️ UTILE | 1j | ❌ À faire |
| | **Authentification** | ✅ FAIT | ⭐⭐⭐⭐ | 🔥 CRITIQUE | 2j | ✅ Complet |
| | **Feuilles Heures (saisie)** | ✅ FAIT | ⭐⭐⭐⭐ | 🔥 CRITIQUE | 1j | ✅ Complet |

**Total effort workflows critiques** : 8 jours
**Total effort workflows importants** : 8 jours
**Total effort complet** : 21 jours

---

## 🎯 ROADMAP DE DOCUMENTATION RECOMMANDÉE

### Sprint 1 : Workflows Critiques (1 semaine)
1. **Planning Opérationnel** (3j) - Cœur métier
2. **Cycle Vie Chantier** (2j) - Entité centrale
3. **Validation Feuilles Heures** (3j) - Compléter existant

**Livrable** : 3 workflows critiques documentés

---

### Sprint 2 : Workflows Importants (1 semaine)
4. **GED** (2j)
5. **Formulaires Dynamiques** (2j)
6. **Signalements** (1j)
7. **Logistique** (1j)
8. **Planning Charge** (2j)

**Livrable** : 5 workflows métier documentés

---

### Sprint 3 : Workflows Secondaires (0.5 semaine)
9-12. **Interventions, Tâches, Dashboard, Notifications** (4j)

**Livrable** : Documentation complète

---

## 📝 TEMPLATE DE WORKFLOW RECOMMANDÉ

Chaque workflow devrait inclure :

```markdown
# Workflow [NOM DU WORKFLOW]

## 🎯 Objectif
Description concise du workflow

## 👥 Acteurs
- Admin
- Conducteur de travaux
- Chef de chantier
- Compagnon
- Système (automatisations)

## 📋 Prérequis
- Modules/données nécessaires
- Permissions requises

## 🔄 Étapes du Workflow

### Étape 1 : [Nom]
**Acteur** : Qui
**Action** : Quoi
**Validation** : Critères
**Exception** : Gestion erreurs

[...]

## 🎨 Diagrammes
- Diagramme de séquence
- Diagramme d'états
- Schéma d'architecture

## 🔗 Interactions avec Autres Modules
- Planning → Pointages
- Chantiers → Documents
- [...]

## ⚠️ Règles Métier
- Contraintes
- Validations
- Calculs

## 🧪 Scénarios de Test
- Happy path
- Edge cases
- Erreurs

## 📊 Métriques & KPIs
- Temps moyen
- Taux de succès
- Volumétrie

## ❌ Points d'Attention
- Bugs connus
- Limitations
- Évolutions futures
```

---

## 🚀 BÉNÉFICES ATTENDUS

### Pour les Développeurs
- ✅ Onboarding accéléré (50% temps en moins)
- ✅ Compréhension globale des interactions
- ✅ Réduction bugs (règles métier claires)
- ✅ Facilitation refactoring

### Pour le Projet
- ✅ Documentation vivante et à jour
- ✅ Traçabilité des décisions métier
- ✅ Base pour tests automatisés
- ✅ Référence pour évolutions futures

### Pour le Business
- ✅ Validation workflow avec client
- ✅ Formation utilisateurs facilitée
- ✅ Support technique amélioré
- ✅ Évolutivité maîtrisée

---

## 📞 CONCLUSION

**Statut actuel** : 12 workflows documentés sur 16 (75%)

**Fait** :
1. ✅ **3 workflows critiques** documentés (Planning, Cycle Vie Chantier, Validation FdH)
2. ✅ **5 workflows importants** documentés (GED, Formulaires, Signalements, Logistique, Planning Charge)
3. ✅ **4 workflows supports** documentés (Authentification, Feuilles Heures données, Refactoring, Nettoyage)

**Reste à faire** :
1. Finaliser les **4 workflows secondaires** (Sprint 3 - Interventions, Tâches, Dashboard, Notifications)

**ROI** : 20 jours d'investissement → Gain estimé 50j/an (réduction bugs, onboarding, support)

---

**Prochaine action recommandée** : Commencer le Sprint 3 par les workflows secondaires (Interventions, Tâches, Dashboard, Notifications) ?

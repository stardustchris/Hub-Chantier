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
| **Feuilles d'Heures** | `WORKFLOW_FEUILLES_HEURES.md` | ✅ Complet | 100% - Workflow + Fix |
| **Refactoring Pointages** | `REFACTORING_POINTAGES_ARCHITECTURE.md` | ✅ Complet | 100% - Clean Architecture |
| **Nettoyage Données** | `NETTOYAGE_DONNEES_DEMO.md` | ✅ Complet | 100% - Suppression mocks |

---

## 🔴 WORKFLOWS CRITIQUES (Haute Priorité)

### 1. **Planning Opérationnel** 🔴 URGENT
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

### 2. **Cycle de Vie d'un Chantier** 🔴 URGENT
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

### 3. **Validation Feuilles d'Heures** 🔴 URGENT
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

### 4. **Gestion Documentaire (GED)**
**Module** : `backend/modules/documents/`

**Workflow à documenter** :
- Structure arborescente (Chantiers → Dossiers → Documents)
- Upload de fichiers (types autorisés, taille max)
- Gestion des versions
- Permissions d'accès (rôles)
- Tags et recherche
- Prévisualisation (PDF, images)
- Partage avec externes
- Signature électronique documents

**Enjeux** :
- ⚠️ Compliance légale (conservation documents BTP)
- ⚠️ Volumétrie importante (photos, plans, PV)
- ⚠️ Sécurité (documents sensibles)

**Complexité** : ⭐⭐⭐⭐ (Élevée)

**Fichier recommandé** : `WORKFLOW_GESTION_DOCUMENTAIRE.md`

---

### 5. **Formulaires Chantier Dynamiques**
**Module** : `backend/modules/formulaires/`

**Workflow à documenter** :
1. **Création Templates** (Admin) :
   - Définition des champs (texte, date, photo, signature)
   - Validation (champs obligatoires)
   - Workflow d'approbation
   - Visibilité (tous/chantiers spécifiques)

2. **Remplissage** (Terrain) :
   - Sélection template
   - Saisie des données
   - Upload photos
   - Géolocalisation automatique
   - Signature électronique
   - Mode offline

3. **Validation** :
   - Soumission
   - Validation N+1
   - Génération PDF
   - Stockage GED

**Exemples** : PPSPS, Compte-rendu réunion, Rapport incident, PV réception

**Enjeux** :
- ⚠️ Conformité réglementaire (PPSPS obligatoire)
- ⚠️ Traçabilité complète
- ⚠️ Mode offline essentiel

**Complexité** : ⭐⭐⭐⭐ (Élevée)

**Fichier recommandé** : `WORKFLOW_FORMULAIRES_DYNAMIQUES.md`

---

### 6. **Signalements / Memos**
**Module** : `backend/modules/signalements/`

**Workflow à documenter** :
- Création signalement (urgence, problème, question)
- Niveaux de priorité (Bas, Moyen, Haut, Critique)
- Affectation automatique (chef chantier du chantier)
- Réaffectation manuelle
- Commentaires et historique
- Résolution et clôture
- Notifications push temps réel
- Pièces jointes (photos)

**Enjeux** :
- ⚠️ Communication terrain/bureau
- ⚠️ Traçabilité problèmes
- ⚠️ SLA résolution

**Complexité** : ⭐⭐⭐ (Moyenne)

**Fichier recommandé** : `WORKFLOW_SIGNALEMENTS.md`

---

### 7. **Logistique - Réservation Matériel**
**Module** : `backend/modules/logistique/`

**Workflow à documenter** :
1. **Création Ressource** (Admin) :
   - Type (engin, gros matériel)
   - Caractéristiques
   - Photo
   - Disponibilité
   - Besoin validation N+1

2. **Réservation** (Chef/Conducteur) :
   - Consultation calendrier disponibilité
   - Demande réservation (chantier, dates)
   - Validation N+1 (si requis)
   - Confirmation automatique
   - Annulation

3. **Gestion** :
   - Statuts (En attente, Validée, Refusée, Terminée)
   - Historique des réservations
   - Conflits de planning
   - Maintenance/indisponibilité

**Enjeux** :
- ⚠️ Optimisation ressources coûteuses
- ⚠️ Conflits de planning
- ⚠️ Traçabilité utilisation

**Complexité** : ⭐⭐⭐ (Moyenne)

**Fichier recommandé** : `WORKFLOW_LOGISTIQUE_MATERIEL.md`

---

### 8. **Planning de Charge**
**Module** : `backend/modules/planning_charge/`

**Workflow à documenter** :
- Vue capacitaire par métier
- Calcul besoins vs disponibilités
- Identification surcharges/sous-charges
- Projection sur plusieurs semaines
- Alertes déséquilibre
- Aide à la décision affectations

**Enjeux** :
- ⚠️ Optimisation RH
- ⚠️ Prévision besoins recrutement/intérim
- ⚠️ Calculs complexes

**Complexité** : ⭐⭐⭐⭐ (Élevée)

**Fichier recommandé** : `WORKFLOW_PLANNING_CHARGE.md`

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
| 1 | **Planning Opérationnel** | 🔴 URGENT | ⭐⭐⭐⭐⭐ | 🔥 CRITIQUE | 3j | ❌ À faire |
| 2 | **Cycle Vie Chantier** | 🔴 URGENT | ⭐⭐⭐⭐ | 🔥 CRITIQUE | 2j | ❌ À faire |
| 3 | **Validation Feuilles Heures** | 🔴 URGENT | ⭐⭐⭐⭐⭐ | 🔥 CRITIQUE | 3j | ⚠️ Partiel (WORKFLOW_FEUILLES_HEURES.md) |
| 4 | **GED** | 🟡 IMPORTANT | ⭐⭐⭐⭐ | ⚠️ IMPORTANT | 2j | ❌ À faire |
| 5 | **Formulaires Dynamiques** | 🟡 IMPORTANT | ⭐⭐⭐⭐ | ⚠️ IMPORTANT | 2j | ❌ À faire |
| 6 | **Signalements** | 🟡 IMPORTANT | ⭐⭐⭐ | ⚠️ IMPORTANT | 1j | ❌ À faire |
| 7 | **Logistique** | 🟡 IMPORTANT | ⭐⭐⭐ | ⚠️ IMPORTANT | 1j | ❌ À faire |
| 8 | **Planning Charge** | 🟡 IMPORTANT | ⭐⭐⭐⭐ | ⚠️ IMPORTANT | 2j | ❌ À faire |
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

**Statut actuel** : 4 workflows documentés sur 16 (25%)

**Recommandation** :
1. Prioriser les **3 workflows critiques** (Sprint 1 - 8j)
2. Compléter les **workflows importants** (Sprint 2 - 8j)
3. Finaliser les **workflows secondaires** (Sprint 3 - 4j)

**ROI** : 20 jours d'investissement → Gain estimé 50j/an (réduction bugs, onboarding, support)

---

**Prochaine action recommandée** : Commencer par **WORKFLOW_PLANNING_OPERATIONNEL.md** ?

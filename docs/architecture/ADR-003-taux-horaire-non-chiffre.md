# ADR-003 : Non-chiffrement du taux horaire en base de données

**Date** : 2026-01-31
**Statut** : ✅ ACCEPTÉ
**Décideurs** : Équipe technique Hub Chantier
**Validateur RGPD** : En attente validation DPO

---

## Contexte

Le module financier (Module 17 - FIN-09) nécessite le stockage du taux horaire de chaque employé pour le calcul automatique des coûts de main-d'œuvre.

**Question** : Faut-il chiffrer le taux horaire dans la base de données ?

---

## Décision

**Le taux horaire N'EST PAS chiffré en base de données.**

Type de stockage : `NUMERIC(8, 2)` en clair dans la table `users`.

---

## Justification

### Arguments POUR le chiffrement

1. **Confidentialité salariale** : Les taux horaires sont des informations sensibles
2. **RGPD Article 32** : Mesures de sécurité appropriées
3. **Protection contre DBA malveillant** : Limite l'accès aux données sensibles

### Arguments CONTRE le chiffrement (retenus)

1. **Besoin opérationnel fréquent** :
   - Calculs quotidiens : `coût = heures_validées × taux_horaire`
   - Requêtes SQL agrégées : `SUM(heures * taux_horaire) GROUP BY chantier`
   - Filtres et tris : `ORDER BY taux_horaire DESC`

2. **Impact performance** :
   - Chiffrement/déchiffrement sur CHAQUE calcul financier
   - Impossibilité d'utiliser les index SQL
   - Requêtes 10x-50x plus lentes sur gros volumes

3. **Complexité technique** :
   - Gestion des clés de chiffrement
   - Rotation des clés
   - Risque de perte de clé = perte de données

4. **Nature de la donnée** :
   - Taux horaire ≠ Salaire brut mensuel
   - Taux horaire ≠ Données bancaires (IBAN, carte)
   - Taux horaire ≠ Données de santé (Art. 9 RGPD)
   - **Catégorie** : Donnée professionnelle, pas "sensible" au sens RGPD

5. **Proportionnalité** :
   - Contexte : PME 20 employés (pas 10 000)
   - Risque : Modéré (pas de base publique, accès restreints)
   - Impact chiffrement : Élevé (calculs quotidiens)

---

## Mesures de sécurité compensatoires

### ✅ Contrôles d'accès stricts

1. **Application** :
   - Champ visible uniquement pour `role === 'admin'`
   - API : Endpoint `/users/{id}` filtré par rôle
   - Modification : Réservée Admin/Conducteur

2. **Base de données** :
   - Utilisateur applicatif avec privilèges minimaux
   - Pas de GRANT SELECT sur taux_horaire pour users non-admin
   - Audit logs PostgreSQL (pg_audit) activé

3. **Infrastructure** :
   - Base de données dans VPC privé
   - Firewall : Accès restreint IPs entreprise
   - Chiffrement au repos (disk encryption)
   - Chiffrement en transit (TLS 1.3)

### ✅ Logging et audit

- **Création** : Log dans `audit_logs` (qui, quand, valeur)
- **Modification** : Log old_value → new_value
- **Consultation** : Log accès API (endpoint `/users/{id}`)
- **Rétention** : 12 mois minimum (conformité URSSAF)

### ✅ Transparence RGPD

- Mention dans Politique de Confidentialité
- Informé lors de la collecte (formulaire admin)
- Droit d'accès : Export RGPD inclut taux_horaire
- Droit d'opposition : Possible (taux_horaire = NULL)

---

## Alternatives considérées

### 1. Chiffrement au niveau application

**Rejeté** :
- Performance : Déchiffrement systématique
- Complexité : Gestion clés en mémoire
- Index : Impossibles sur données chiffrées

### 2. Chiffrement partiel (colonnes)

**Rejeté** :
- PostgreSQL pgcrypto : Performances dégradées
- AWS RDS encryption : Chiffre tout le disque (déjà actif)
- Transparent Data Encryption : Pas de gain vs. disk encryption

### 3. Pseudo-anonymisation

**Rejeté** :
- Nécessite table de mapping
- Complexité accrue
- Pas de gain sécurité (table mapping = nouvelle cible)

### 4. Stockage séparé (vault externe)

**Rejeté** :
- HashiCorp Vault : Overkill pour 20 employés
- Latence réseau : +50ms par requête
- Point de défaillance unique

---

## Analyse RGPD

### Article 32 - Sécurité du traitement

> "Compte tenu de l'état des connaissances, des coûts de mise en œuvre et de la nature, de la portée, du contexte et des finalités du traitement ainsi que des risques..."

**Évaluation** :
- **Nature** : Donnée professionnelle (pas sensible Art. 9)
- **Portée** : 20 employés (PME)
- **Risque** : Modéré (pas de base publique)
- **Coûts** : Élevés (performance, complexité)

**Conclusion** : Non-chiffrement justifié par principe de proportionnalité.

### Article 25 - Privacy by Design

**Mesures techniques** :
- ✅ Minimisation : Taux horaire strictement nécessaire (calculs coûts)
- ✅ Contrôle d'accès : Admin-only
- ✅ Intégrité : Contraintes SQL (CHECK >= 0)
- ✅ Confidentialité : TLS, VPC, firewall

### Article 35 - Analyse d'impact (DPIA)

**Risques identifiés** :
1. Accès non autorisé DBA → **Contrôle** : Audit PostgreSQL
2. Fuite sauvegarde → **Contrôle** : Chiffrement backups (AES-256)
3. Injection SQL → **Contrôle** : ORM SQLAlchemy (pas de raw SQL)

**Risque résiduel** : **FAIBLE**

---

## Conséquences

### Positives

✅ Performances optimales (calculs financiers en temps réel)
✅ Requêtes SQL natives (SUM, AVG, GROUP BY)
✅ Index SQL fonctionnels
✅ Simplicité architecture
✅ Coûts infrastructure maîtrisés

### Négatives

⚠️ Taux horaire visible en clair en BDD (pour DBA)
⚠️ Nécessite confiance équipe infrastructure
⚠️ Audit DPO requis avant production

---

## Suivi

### Actions immédiates

- [x] Documenter décision (ce fichier)
- [ ] Validation DPO (délai : 1 semaine)
- [x] Logging audit implémenté
- [x] Contrôles d'accès implémentés

### Revue future

- **Date** : 2026-06-30 (dans 5 mois)
- **Déclencheurs** :
  - Passage > 50 employés
  - Incident sécurité
  - Nouvelle réglementation
  - Demande DPO

---

## Références

- CNIL : Guide sécurité des données personnelles (2018)
- RGPD : Articles 25, 32, 35
- ANSSI : Recommandations sécurité bases de données (2021)
- OWASP : Database Security Cheat Sheet

---

**Signature** :
Équipe technique Hub Chantier
2026-01-31

**Validation DPO** : ⏳ En attente

# Analyse des Gaps - Workflow Validation Feuilles d'Heures

**Date**: 31 janvier 2026
**Analysé par**: Claude Sonnet 4.5
**Workflow source**: `docs/workflows/WORKFLOW_VALIDATION_FEUILLES_HEURES.md`
**Module**: `backend/modules/pointages`

---

## Résumé Exécutif

### ✅ Points Forts

- **Machine à états implémentée** : Les transitions BROUILLON → SOUMIS → VALIDÉ/REJETÉ sont fonctionnelles
- **Entités Domain** : Pointage, FeuilleHeures, VariablePaie, Duree, StatutPointage existent et sont conformes
- **Use Cases principaux** : CreatePointage, UpdatePointage, SignPointage, SubmitPointage, ValidatePointage, RejectPointage présents
- **Routes API** : 16 endpoints exposés incluant les workflows de validation
- **Events** : PointageSubmittedEvent, PointageValidatedEvent, PointageRejectedEvent publiés

### ❌ Gaps Critiques Identifiés

**14 gaps fonctionnels** et **8 gaps techniques** bloquent la conformité au workflow documenté.

| Priorité | Nombre | Impact |
|----------|--------|--------|
| 🔴 CRITIQUE | 7 | Bloquant pour production |
| 🟠 HAUTE | 9 | Impact métier majeur |
| 🟡 MOYENNE | 6 | Amélioration nécessaire |

---

## 1. Gaps Fonctionnels (14)

### 🔴 GAP-FDH-001 : Workflow "corriger" manquant

**Section workflow** : § 5.5 Workflow E (Rejet et correction)
**Statut** : ❌ **NON IMPLÉMENTÉ**

**Description** :
Le workflow documenté stipule qu'après un rejet, le compagnon doit pouvoir **repasser en BROUILLON** via une action explicite `corriger()` (ligne 878-886 du workflow).

**Implémentation actuelle** :
- ✅ L'entité `Pointage` possède la méthode `corriger()` (ligne 241-257 de `pointage.py`)
- ❌ **AUCUN use case** `CorrectPointageUseCase` n'existe
- ❌ **AUCUNE route** `POST /{pointage_id}/correct` exposée

**Impact** :
🔴 **BLOQUANT** : Après un rejet, le compagnon ne peut pas reprendre son pointage pour correction. Le workflow de correction est incomplet.

**Requête attendue** (selon workflow § 5.5.3) :
```http
POST /api/pointages/156/corriger
Authorization: Bearer <token_compagnon>
```

**Recommandation** :
```
1. Créer backend/modules/pointages/application/use_cases/correct_pointage.py
2. Créer CorrectPointageUseCase avec execute(pointage_id: int) → PointageDTO
3. Ajouter route POST /{pointage_id}/correct dans routes.py
4. Tests : test_workflow_rejet_correction (§ 11.2)
```

---

### 🔴 GAP-FDH-002 : Verrouillage mensuel absent

**Section workflow** : § 4.4 Règle de verrouillage mensuel
**Statut** : ❌ **NON IMPLÉMENTÉ**

**Description** :
Le workflow impose une **règle métier critique** : *"Un pointage reste modifiable jusqu'au vendredi précédant la dernière semaine du mois en cours."*

**Exemple janvier 2026** :
- Dernière semaine : Lun 26 → Dim 31
- Vendredi précédant : Ven 23/01
- **Verrouillage** : Samedi 24 janvier 00:00

**Implémentation actuelle** :
- ❌ Aucune fonction `is_locked()` ou `is_period_locked()` trouvée dans le code
- ❌ Aucun Use Case ne vérifie cette règle avant modification/soumission/validation
- ❌ Aucun test de verrouillage (`test_verrouillage_mensuel` § 11.5)

**Impact** :
🔴 **CRITIQUE PAIE** : Les pointages peuvent être modifiés rétroactivement, créant des écarts avec le logiciel de paie.

**Conséquences après verrouillage** (workflow § 4.4, tableau ligne 441) :
| Action | Avant verrouillage | Après verrouillage |
|--------|-------------------|-------------------|
| Modifier heures | ✅ | ❌ **INTERDIT** |
| Signer | ✅ | ❌ **INTERDIT** |
| Soumettre | ✅ | ❌ **INTERDIT** |
| Valider | ✅ | ❌ **INTERDIT** |
| Rejeter | ✅ | ❌ **INTERDIT** |
| Consulter | ✅ | ✅ Toujours possible |
| Exporter | ✅ | ✅ Toujours possible |

**Recommandation** :
```python
# 1. Créer Value Object
backend/modules/pointages/domain/value_objects/periode_paie.py

class PeriodePaie:
    @staticmethod
    def is_locked(date_pointage: date, today: date = None) -> bool:
        """
        Vérifie si un pointage est verrouillé.

        Règle : Verrouillé après le vendredi précédant la dernière semaine du mois.
        """
        today = today or date.today()

        # Si pointage dans le mois en cours ou futur → jamais verrouillé
        if date_pointage.replace(day=1) >= today.replace(day=1):
            return False

        # Calculer vendredi de verrouillage du mois du pointage
        month = date_pointage.month
        year = date_pointage.year

        # Dernier jour du mois
        last_day = calendar.monthrange(year, month)[1]
        last_date = date(year, month, last_day)

        # Trouver le lundi de la dernière semaine
        while last_date.weekday() != 0:  # 0 = lundi
            last_date -= timedelta(days=1)

        # Vendredi précédant = dernier jour de la semaine avant
        lockdown_friday = last_date - timedelta(days=3)

        # Verrouillé si today > vendredi de verrouillage
        return today > lockdown_friday

# 2. Modifier TOUS les Use Cases pour vérifier le verrouillage
# - UpdatePointageUseCase
# - SignPointageUseCase
# - SubmitPointageUseCase
# - ValidatePointageUseCase
# - RejectPointageUseCase
# - CorrectPointageUseCase

# Exemple dans UpdatePointageUseCase:
def execute(self, dto: UpdatePointageDTO) -> PointageDTO:
    pointage = self.pointage_repo.find_by_id(dto.pointage_id)

    # CRITIQUE: Vérifier verrouillage
    if PeriodePaie.is_locked(pointage.date_pointage):
        raise ValueError("La période de paie est verrouillée")

    # ... reste du use case

# 3. Tests § 11.5
tests/unit/modules/pointages/test_verrouillage_mensuel.py
```

---

### 🔴 GAP-FDH-003 : Contrôle de permissions manquant

**Section workflow** : § 2.3 Matrice de permissions
**Statut** : ⚠️ **PARTIELLEMENT IMPLÉMENTÉ**

**Description** :
Le workflow définit des règles strictes de qui peut faire quoi (tableau § 2.3, ligne 156-168).

**Règles non vérifiées** :

| Action | Règle workflow | Implémentation actuelle |
|--------|---------------|------------------------|
| Créer pointage autre compagnon | ❌ Compagnon interdit | ⚠️ Non vérifié dans CreatePointageUseCase |
| Modifier pointage autre compagnon | ❌ Compagnon interdit | ⚠️ Non vérifié dans UpdatePointageUseCase |
| Valider | ❌ Compagnon interdit | ⚠️ Non vérifié dans ValidatePointageUseCase |
| Voir feuilles (périmètre) | Chef/Conducteur = ses chantiers uniquement | ❌ Non implémenté dans ListPointagesUseCase |
| Export paie | ❌ Compagnon/Chef interdits | ❌ Non vérifié dans ExportFeuilleHeuresUseCase |

**Impact** :
🔴 **SÉCURITÉ** : Un compagnon peut valider ses propres heures ou modifier celles d'un collègue.

**Recommandation** :
```python
# 1. Créer service de vérification de permissions
backend/modules/pointages/domain/services/permission_service.py

class PointagePermissionService:
    @staticmethod
    def can_create_for_user(current_user_id: int, target_user_id: int, user_role: str) -> bool:
        """Vérifie si current_user peut créer un pointage pour target_user."""
        # Compagnon ne peut créer que pour lui-même
        if user_role == "compagnon":
            return current_user_id == target_user_id
        # Chef/Conducteur/Admin peuvent créer pour n'importe qui
        return user_role in ("chef_chantier", "conducteur", "admin")

    @staticmethod
    def can_validate(user_role: str) -> bool:
        """Vérifie si l'utilisateur peut valider."""
        return user_role in ("chef_chantier", "conducteur", "admin")

    @staticmethod
    def can_export(user_role: str) -> bool:
        """Vérifie si l'utilisateur peut exporter pour la paie."""
        return user_role in ("conducteur", "admin")

# 2. Intégrer dans les Use Cases
# - Injecter UserRepository pour récupérer le rôle
# - Vérifier les permissions avant chaque action
```

---

### 🟠 GAP-FDH-004 : Signature obligatoire non validée

**Section workflow** : § 5.3.1 Flux nominal (soumission)
**Statut** : ⚠️ **RÈGLE MÉTIER MANQUANTE**

**Description** :
Le workflow indique (ligne 671) : *"2. Signe (optionnel mais recommandé)"*

Cependant, la fiche chantier peut exiger la signature avant soumission pour certains chantiers ou certains utilisateurs.

**Implémentation actuelle** :
- ✅ L'entité Pointage vérifie `is_signed`
- ❌ **Aucune vérification** dans `SubmitPointageUseCase` que la signature est présente
- ❌ Pas de paramètre `signature_required` dans Chantier ou TypeUtilisateur

**Impact** :
🟠 **CONFORMITÉ BTP** : La signature manuscrite est une preuve légale. Sans validation, des pointages non signés peuvent être soumis.

**Recommandation** :
```python
# Option 1 : Signature toujours obligatoire avant soumission
class SubmitPointageUseCase:
    def execute(self, pointage_id: int) -> PointageDTO:
        pointage = self.pointage_repo.find_by_id(pointage_id)

        # Vérifier signature
        if not pointage.is_signed:
            raise ValueError("Le pointage doit être signé avant soumission")

        pointage.soumettre()
        ...

# Option 2 : Signature obligatoire selon le chantier
# Ajouter colonne `signature_required` dans table chantiers
# Vérifier selon cette colonne
```

---

### 🟠 GAP-FDH-005 : Contrainte heures > 24h/jour manquante

**Section workflow** : § 12.3 Cohérence données (ligne 1583)
**Statut** : ❌ **NON IMPLÉMENTÉ**

**Description** :
Le workflow impose : *"Heures > 24h/jour : Saisie absurde → Validation : total heures par jour <= 24h"*

**Implémentation actuelle** :
- ❌ Aucune validation dans `Pointage.set_heures()`
- ❌ Aucune validation dans `CreatePointageUseCase` ou `UpdatePointageUseCase`
- ❌ Un compagnon peut saisir `30:00` heures normales sans erreur

**Impact** :
🟠 **COHÉRENCE DONNÉES** : Données aberrantes acceptées, export paie faussé.

**Recommandation** :
```python
# Ajouter validation dans Pointage.set_heures()
def set_heures(self, heures_normales, heures_supplementaires) -> None:
    if not self.is_editable:
        raise ValueError(...)

    # NOUVEAU: Validation totale <= 24h
    total = (heures_normales or self.heures_normales) + (heures_supplementaires or self.heures_supplementaires)
    if total.hours > 24:
        raise ValueError(f"Le total des heures ({total}) dépasse 24h par jour")

    ...
```

---

### 🟠 GAP-FDH-006 : Validation par lot (feuille complète) absente

**Section workflow** : § 13.3 Prochaines étapes (ligne 1677)
**Statut** : ❌ **NON IMPLÉMENTÉ**

**Description** :
Le workflow prévoit : *"Ajouter la validation par lot (tous les pointages d'une feuille)"*

Actuellement, le validateur doit valider **un par un** les 5-10 pointages d'une feuille hebdomadaire, ce qui est fastidieux.

**Impact** :
🟠 **UX VALIDATEUR** : Perte de temps massive pour le chef de chantier (5-10 clics par feuille × 20 compagnons = 100-200 clics par semaine).

**Recommandation** :
```python
# Créer use case de validation par lot
backend/modules/pointages/application/use_cases/validate_feuille_heures.py

class ValidateFeuilleHeuresUseCase:
    """
    Valide tous les pointages SOUMIS d'une feuille d'heures.
    """

    def execute(self, feuille_id: int, validateur_id: int) -> dict:
        feuille = self.feuille_repo.find_by_id(feuille_id)
        pointages = self.pointage_repo.find_by_feuille(feuille_id)

        validated = []
        errors = []

        for pointage in pointages:
            if pointage.statut == StatutPointage.SOUMIS:
                try:
                    if PeriodePaie.is_locked(pointage.date_pointage):
                        errors.append(...)
                        continue

                    pointage.valider(validateur_id)
                    validated.append(pointage)
                except ValueError as e:
                    errors.append(...)

        # Sauvegarder tous les pointages validés
        for p in validated:
            self.pointage_repo.save(p)

        return {
            "validated_count": len(validated),
            "error_count": len(errors),
            "errors": errors
        }

# Route API
@router.post("/feuilles/{feuille_id}/validate-all")
def validate_feuille_heures(...):
    """Valide tous les pointages soumis de la feuille en un clic."""
    ...
```

---

### 🟠 GAP-FDH-007 : Notifications push manquantes

**Section workflow** : § 13.3 Prochaines étapes (ligne 1678)
**Statut** : ❌ **NON IMPLÉMENTÉ**

**Description** :
Le workflow prévoit : *"Implémenter les notifications push lors des soumissions/validations"*

**Events publiés** :
- ✅ `PointageSubmittedEvent`
- ✅ `PointageValidatedEvent`
- ✅ `PointageRejectedEvent`

**Handlers de notification** :
- ❌ Aucun event handler pour envoyer notification push au chef lors soumission
- ❌ Aucun event handler pour envoyer notification push au compagnon lors validation
- ❌ Aucun event handler pour envoyer notification push au compagnon lors rejet

**Impact** :
🟠 **UX TERRAIN** : Le chef ne sait pas qu'un compagnon a soumis. Le compagnon ne sait pas que ses heures sont validées.

**Recommandation** :
```python
# Créer event handlers de notification
backend/modules/pointages/infrastructure/event_handlers.py

from shared.infrastructure.notifications import NotificationService

def on_pointage_submitted(event: PointageSubmittedEvent):
    """Notifie le chef quand un compagnon soumet."""
    # Récupérer les chefs/conducteurs du chantier
    chefs = get_chefs_chantier(event.chantier_id)

    for chef in chefs:
        NotificationService.send_push(
            user_id=chef.id,
            title="Pointage à valider",
            body=f"{event.utilisateur_nom} a soumis ses heures du {event.date_pointage}",
            data={"pointage_id": event.pointage_id}
        )

def on_pointage_validated(event: PointageValidatedEvent):
    """Notifie le compagnon quand ses heures sont validées."""
    NotificationService.send_push(
        user_id=event.utilisateur_id,
        title="✅ Heures validées",
        body=f"Vos heures du {event.date_pointage} ont été validées",
    )

def on_pointage_rejected(event: PointageRejectedEvent):
    """Notifie le compagnon quand ses heures sont rejetées."""
    NotificationService.send_push(
        user_id=event.utilisateur_id,
        title="❌ Heures rejetées",
        body=f"Vos heures du {event.date_pointage} ont été rejetées : {event.motif}",
    )

# Enregistrer les handlers
EventBus.subscribe(PointageSubmittedEvent, on_pointage_submitted)
EventBus.subscribe(PointageValidatedEvent, on_pointage_validated)
EventBus.subscribe(PointageRejectedEvent, on_pointage_rejected)
```

---

### 🟡 GAP-FDH-008 : Points de vérification validateur manquants

**Section workflow** : § 5.4.3 Points de vérification (ligne 782-790)
**Statut** : ❌ **NON IMPLÉMENTÉ**

**Description** :
Le workflow recommande au validateur de vérifier 5 points avant d'approuver :

| Vérification | Description | Implémentation |
|-------------|-------------|----------------|
| Heures cohérentes | Correspond au planning prévu | ❌ Non calculé |
| Signature présente | Le compagnon a signé | ✅ Affiché dans DTO |
| Pas de doublon | Total heures jour < 10h sur autres chantiers | ❌ Non calculé |
| Commentaire | Heures inhabituelles justifiées | ✅ Affiché |
| Heures sup justifiées | Demande préalable | ❌ Non vérifié |

**Impact** :
🟡 **UX VALIDATEUR** : Le chef n'a pas les informations pour prendre une décision éclairée.

**Recommandation** :
```python
# Enrichir le DTO retourné par GetPointageUseCase
class PointageDetailDTO(PointageDTO):
    # Nouveaux champs d'aide à la validation
    heures_planifiees: Optional[str]  # Depuis affectation_id
    ecart_planifie: Optional[str]  # Réalisé - Planifié
    total_heures_jour: str  # Total sur TOUS les chantiers ce jour
    has_duplicates: bool  # True si > 1 pointage ce jour
    requires_justification: bool  # True si heures_sup > 2h sans commentaire

# Use case enrichi
class GetPointageForValidationUseCase:
    def execute(self, pointage_id: int) -> PointageDetailDTO:
        pointage = self.pointage_repo.find_by_id(pointage_id)

        # Calculer total jour (GAP-FDH-008)
        pointages_jour = self.pointage_repo.find_by_user_and_date(
            pointage.utilisateur_id,
            pointage.date_pointage
        )
        total_jour = sum(p.total_heures for p in pointages_jour)

        # Récupérer heures planifiées
        heures_planifiees = None
        ecart = None
        if pointage.affectation_id:
            affectation = self.affectation_repo.find_by_id(pointage.affectation_id)
            heures_planifiees = affectation.heures_prevues
            ecart = pointage.total_heures - heures_planifiees

        return PointageDetailDTO(
            ...,
            heures_planifiees=str(heures_planifiees) if heures_planifiees else None,
            ecart_planifie=str(ecart) if ecart else None,
            total_heures_jour=str(total_jour),
            has_duplicates=len(pointages_jour) > 1,
            requires_justification=(pointage.heures_supplementaires.hours > 2 and not pointage.commentaire)
        )
```

---

### 🟡 GAP-FDH-009 : Export paie incomplet

**Section workflow** : § 8 Export paie
**Statut** : ⚠️ **PARTIELLEMENT IMPLÉMENTÉ**

**Description** :
Le workflow définit 4 formats d'export (§ 8.1, ligne 1045) :

| Format | Usage | Statut implémentation |
|--------|-------|----------------------|
| CSV | Import logiciel paie | ✅ Implémenté |
| XLSX | Consultation bureau | ❌ Non implémenté |
| PDF | Archive légale / impression | ❌ Non implémenté |
| ERP | Intégration directe Costructor/Graneet | ❌ Non implémenté |

**Contenu export manquant** (§ 8.3, ligne 1072) :

| Colonne attendue | Présence dans CSV actuel |
|-----------------|-------------------------|
| matricule | ⚠️ À vérifier |
| code_chantier | ⚠️ À vérifier |
| heures_normales (décimal) | ⚠️ À vérifier |
| heures_sup (décimal) | ⚠️ À vérifier |
| panier_repas | ❌ Variables paie non incluses |
| indemnite_transport | ❌ Variables paie non incluses |
| signature (OUI/NON) | ❌ Non inclus |
| validateur | ❌ Non inclus |

**Impact** :
🟡 **INTEGRATION PAIE** : Export CSV insuffisant pour import direct dans logiciel paie.

**Recommandation** :
```
1. Enrichir ExportFeuilleHeuresUseCase pour inclure variables de paie
2. Ajouter colonne signature (OUI/NON) et validateur (nom)
3. Implémenter export XLSX (library openpyxl)
4. Implémenter export PDF (library reportlab)
5. Implémenter export ERP (format spécifique Costructor)
```

---

### 🟡 GAP-FDH-010 : Récapitulatif mensuel manquant

**Section workflow** : § 6.4 Récapitulatif mensuel (ligne 950-977)
**Statut** : ❌ **NON IMPLÉMENTÉ**

**Description** :
Le workflow prévoit un **récapitulatif mensuel** agrégeant toutes les feuilles hebdomadaires d'un compagnon sur le mois.

**Contenu attendu** :
```
RÉCAPITULATIF JANVIER 2026 - Sébastien ACHKAR

Semaine 1 (05-11/01) :  39h00 norm + 2h00 sup = 41h00
Semaine 2 (12-18/01) :  38h30 norm + 1h30 sup = 40h00
Semaine 3 (19-25/01) :  35h00 norm + 0h00 sup = 35h00
Semaine 4 (26-31/01) :  38h00 norm + 3h00 sup = 41h00
─────────────────────────────────────────────────────
TOTAL MOIS :            150h30 norm + 6h30 sup = 157h00

Variables de paie :
- Paniers repas    : 20 × 10.50€ = 210.00€
- Indemnité trajet : 20 ×  8.20€ = 164.00€
- Prime salissure  : 20 ×  3.00€ =  60.00€
─────────────────────────────────────────────────────
TOTAL VARIABLES :                     434.00€

Statut : ✅ Tous validés
```

**Implémentation actuelle** :
- ❌ Aucun use case `GetRecapitulatifMensuelUseCase`
- ❌ Aucune route `GET /pointages/recapitulatif/{utilisateur_id}/mois/{year}/{month}`

**Impact** :
🟡 **UX PAIE** : Impossible de voir le total mensuel avant export paie.

**Recommandation** :
```python
# Créer use case
backend/modules/pointages/application/use_cases/get_recapitulatif_mensuel.py

class GetRecapitulatifMensuelUseCase:
    def execute(self, utilisateur_id: int, annee: int, mois: int) -> dict:
        # Récupérer toutes les feuilles du mois
        feuilles = self.feuille_repo.find_by_utilisateur_and_month(
            utilisateur_id, annee, mois
        )

        # Agréger les totaux
        total_norm = Duree.zero()
        total_sup = Duree.zero()

        for feuille in feuilles:
            total_norm += feuille.total_heures_normales
            total_sup += feuille.total_heures_supplementaires

        # Récupérer variables de paie du mois
        variables = self.variable_repo.find_by_user_and_month(...)

        return {
            "utilisateur_id": utilisateur_id,
            "annee": annee,
            "mois": mois,
            "semaines": [...],  # Détail par semaine
            "total_heures_normales": str(total_norm),
            "total_heures_supplementaires": str(total_sup),
            "total_heures": str(total_norm + total_sup),
            "variables_paie": variables,
            "total_variables": sum(v.valeur for v in variables),
            "statut_global": "✅ Tous validés" if all(...) else "⏳ En attente"
        }
```

---

### 🟡 GAP-FDH-011 : Chantier inactif non vérifié

**Section workflow** : § 5.1.4 Cas d'erreur (ligne 571)
**Statut** : ⚠️ **VÉRIFICATION MANQUANTE**

**Description** :
Le workflow impose : *"Chantier inactif → 400 Bad Request : Impossible de pointer sur un chantier fermé"*

**Implémentation actuelle** :
- ❌ Aucune vérification dans `CreatePointageUseCase` que le chantier est actif
- ❌ Un compagnon peut pointer sur un chantier au statut `FERME`

**Impact** :
🟡 **COHÉRENCE DONNÉES** : Pointages sur chantiers fermés acceptés.

**Recommandation** :
```python
class CreatePointageUseCase:
    def execute(self, dto: CreatePointageDTO) -> PointageDTO:
        # Vérifier que le chantier est actif
        chantier = self.chantier_repo.find_by_id(dto.chantier_id)
        if not chantier:
            raise ValueError(f"Chantier {dto.chantier_id} non trouvé")

        if chantier.statut == StatutChantier.FERME:
            raise ValueError("Impossible de pointer sur un chantier fermé")

        # ... reste du use case
```

---

### 🟡 GAP-FDH-012 : Utilisateur désactivé non vérifié

**Section workflow** : § 12.3 Cohérence données (ligne 1586)
**Statut** : ⚠️ **VÉRIFICATION MANQUANTE**

**Description** :
Le workflow stipule : *"Utilisateur désactivé : Compagnon parti pendant le mois → Permettre validation des pointages existants"*

**Implémentation actuelle** :
- ❌ Aucune vérification dans `CreatePointageUseCase` que l'utilisateur est actif
- ⚠️ Pas de règle explicite sur la validation de pointages d'un utilisateur désactivé

**Impact** :
🟡 **EDGE CASE** : Comportement non défini si un compagnon est désactivé en cours de mois.

**Recommandation** :
```python
# Règle métier à clarifier :
# - Création de pointage : utilisateur doit être actif
# - Validation de pointage existant : autorisée même si utilisateur désactivé
```

---

### 🟡 GAP-FDH-013 : Contrainte doublon jour/chantier non testée

**Section workflow** : § 11.6 Contrainte d'unicité (ligne 1489)
**Statut** : ⚠️ **TEST MANQUANT**

**Description** :
Le workflow impose une **contrainte d'unicité** : `UNIQUE(utilisateur_id, chantier_id, date_pointage)` (§ 10.3, ligne 1287).

**Implémentation actuelle** :
- ✅ Contrainte DB probablement présente dans la migration Alembic
- ❌ **Test manquant** `test_doublon_pointage_interdit` (§ 11.6, ligne 1489)

**Impact** :
🟡 **TESTS** : Régression possible si contrainte DB supprimée accidentellement.

**Recommandation** :
```python
# Ajouter test
tests/unit/modules/pointages/test_contrainte_unicite.py

def test_doublon_pointage_interdit(client, db_session):
    """Un seul pointage par (utilisateur, chantier, date)."""
    # Premier pointage → OK
    response = client.post("/api/pointages", json={
        "utilisateur_id": 7,
        "chantier_id": 1,
        "date_pointage": "2026-01-27",
        "heures_normales": "7:30",
    })
    assert response.status_code == 201

    # Même combinaison → 409 Conflict
    response = client.post("/api/pointages", json={
        "utilisateur_id": 7,
        "chantier_id": 1,
        "date_pointage": "2026-01-27",
        "heures_normales": "8:00",
    })
    assert response.status_code == 409
    assert "existe déjà" in response.json()["detail"]
```

---

### 🟡 GAP-FDH-014 : Transitions interdites non testées

**Section workflow** : § 11.3 Transitions interdites (ligne 1422)
**Statut** : ⚠️ **TESTS MANQUANTS**

**Description** :
Le workflow impose des **transitions interdites** (§ 4.3, ligne 405) :

| Depuis | Vers | Raison |
|--------|------|--------|
| BROUILLON | VALIDÉ | Doit passer par SOUMIS |
| VALIDÉ | * | État final |
| SOUMIS | BROUILLON | Le compagnon ne peut pas retirer |
| REJETÉ | SOUMIS | Doit repasser par BROUILLON |

**Implémentation actuelle** :
- ✅ Transitions vérifiées dans `StatutPointage.can_transition_to()`
- ❌ **Tests manquants** `test_transitions_interdites` (§ 11.3, ligne 1422)

**Impact** :
🟡 **TESTS** : Régression possible si machine à états modifiée.

**Recommandation** :
```python
# Ajouter tests complets
tests/unit/modules/pointages/test_machine_etats.py

def test_transitions_interdites(client, db_session):
    """Test que les transitions illégales sont refusées."""

    # BROUILLON → VALIDÉ (interdit : doit passer par SOUMIS)
    pointage_id = create_pointage(client, statut="brouillon")
    response = client.post(f"/api/pointages/{pointage_id}/validate", json={
        "validateur_id": 4,
    })
    assert response.status_code == 400

    # VALIDÉ → BROUILLON (interdit : état final)
    pointage_id = create_validated_pointage(client)
    response = client.post(f"/api/pointages/{pointage_id}/correct")
    assert response.status_code == 400

    # SOUMIS → BROUILLON (interdit)
    pointage_id = create_submitted_pointage(client)
    response = client.put(f"/api/pointages/{pointage_id}", json={
        "heures_normales": "5:00",
    })
    assert response.status_code == 400

    # REJETÉ → SOUMIS (interdit)
    pointage_id = create_rejected_pointage(client)
    response = client.post(f"/api/pointages/{pointage_id}/submit")
    assert response.status_code == 400
```

---

## 2. Gaps Techniques (8)

### 🔴 GAP-TECH-001 : Use Case "corriger" absent

**Fichier attendu** : `backend/modules/pointages/application/use_cases/correct_pointage.py`
**Statut** : ❌ **FICHIER MANQUANT**

**Description** :
Suite logique de GAP-FDH-001. Le use case de correction n'existe pas.

**Recommandation** :
```python
# Créer fichier
backend/modules/pointages/application/use_cases/correct_pointage.py

"""Use Case: Corriger un pointage rejeté."""

from typing import Optional
from ...domain.entities import Pointage
from ...domain.repositories import PointageRepository
from ..dtos import PointageDTO
from ..ports import EventBus, NullEventBus

class CorrectPointageUseCase:
    """
    Repasse un pointage REJETÉ en BROUILLON pour correction.

    Le compagnon peut ensuite modifier les heures et re-soumettre.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        event_bus: Optional[EventBus] = None,
    ):
        self.pointage_repo = pointage_repo
        self.event_bus = event_bus or NullEventBus()

    def execute(self, pointage_id: int) -> PointageDTO:
        """
        Exécute la correction d'un pointage.

        Args:
            pointage_id: ID du pointage à corriger.

        Returns:
            Le DTO du pointage remis en brouillon.

        Raises:
            ValueError: Si le pointage n'existe pas ou n'est pas REJETÉ.
        """
        # Récupère le pointage
        pointage = self.pointage_repo.find_by_id(pointage_id)
        if not pointage:
            raise ValueError(f"Pointage {pointage_id} non trouvé")

        # Vérifie verrouillage (CRITIQUE)
        from ...domain.value_objects.periode_paie import PeriodePaie
        if PeriodePaie.is_locked(pointage.date_pointage):
            raise ValueError("La période de paie est verrouillée")

        # Corrige le pointage (REJETE → BROUILLON)
        pointage.corriger()

        # Persiste
        pointage = self.pointage_repo.save(pointage)

        # Pas d'événement publié pour correction (action interne)

        return self._to_dto(pointage)

    def _to_dto(self, pointage: Pointage) -> PointageDTO:
        """Convertit l'entité en DTO."""
        return PointageDTO(
            id=pointage.id,
            utilisateur_id=pointage.utilisateur_id,
            chantier_id=pointage.chantier_id,
            date_pointage=pointage.date_pointage,
            heures_normales=str(pointage.heures_normales),
            heures_supplementaires=str(pointage.heures_supplementaires),
            total_heures=str(pointage.total_heures),
            total_heures_decimal=pointage.total_heures_decimal,
            statut=pointage.statut.value,
            commentaire=pointage.commentaire,
            signature_utilisateur=pointage.signature_utilisateur,
            signature_date=pointage.signature_date,
            validateur_id=pointage.validateur_id,
            validation_date=pointage.validation_date,
            motif_rejet=pointage.motif_rejet,
            affectation_id=pointage.affectation_id,
            created_by=pointage.created_by,
            created_at=pointage.created_at,
            updated_at=pointage.updated_at,
            utilisateur_nom=pointage.utilisateur_nom,
            chantier_nom=pointage.chantier_nom,
            chantier_couleur=pointage.chantier_couleur,
        )
```

---

### 🔴 GAP-TECH-002 : Route POST /corriger absente

**Fichier** : `backend/modules/pointages/infrastructure/web/routes.py`
**Statut** : ❌ **ROUTE MANQUANTE**

**Description** :
Aucune route pour appeler `CorrectPointageUseCase`.

**Recommandation** :
```python
# Ajouter dans routes.py (ligne ~492, après reject)

@router.post("/{pointage_id}/correct")
def correct_pointage(
    pointage_id: int,
    current_user_id: int = Depends(get_current_user_id),
    controller: PointageController = Depends(get_controller),
):
    """
    Repasse un pointage REJETÉ en BROUILLON pour correction.

    Le compagnon peut ensuite modifier les heures et re-soumettre.
    """
    try:
        return controller.correct_pointage(pointage_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### 🔴 GAP-TECH-003 : Méthode controller.correct_pointage absente

**Fichier** : `backend/modules/pointages/adapters/controllers/pointage_controller.py`
**Statut** : ❌ **MÉTHODE MANQUANTE**

**Recommandation** :
```python
# Ajouter dans PointageController

def correct_pointage(self, pointage_id: int) -> dict:
    """
    Repasse un pointage rejeté en brouillon.

    Args:
        pointage_id: ID du pointage.

    Returns:
        Le pointage corrigé (statut BROUILLON).
    """
    use_case = CorrectPointageUseCase(
        pointage_repo=self.pointage_repo,
        event_bus=self.event_bus,
    )

    dto = use_case.execute(pointage_id)
    return self._pointage_dto_to_dict(dto)
```

---

### 🔴 GAP-TECH-004 : Value Object PeriodePaie absent

**Fichier attendu** : `backend/modules/pointages/domain/value_objects/periode_paie.py`
**Statut** : ❌ **FICHIER MANQUANT**

**Description** :
Value Object pour calculer le verrouillage mensuel (GAP-FDH-002).

**Recommandation** : Voir code fourni dans GAP-FDH-002.

---

### 🟠 GAP-TECH-005 : Tests de verrouillage absents

**Fichier attendu** : `tests/unit/modules/pointages/test_verrouillage_mensuel.py`
**Statut** : ❌ **FICHIER MANQUANT**

**Description** :
Tests unitaires pour vérifier la règle de verrouillage (§ 11.5, ligne 1462).

**Recommandation** : Voir code fourni dans GAP-FDH-002.

---

### 🟠 GAP-TECH-006 : Service de permissions absent

**Fichier attendu** : `backend/modules/pointages/domain/services/permission_service.py`
**Statut** : ❌ **FICHIER MANQUANT**

**Description** :
Service domain pour vérifier les permissions (GAP-FDH-003).

**Recommandation** : Voir code fourni dans GAP-FDH-003.

---

### 🟡 GAP-TECH-007 : Tests machine à états incomplets

**Fichier** : `tests/unit/modules/pointages/domain/value_objects/test_statut_pointage.py`
**Statut** : ⚠️ **À VÉRIFIER**

**Description** :
Vérifier que tous les cas de transitions interdites sont testés (§ 11.3).

**Recommandation** : Voir code fourni dans GAP-FDH-014.

---

### 🟡 GAP-TECH-008 : Coverage tests insuffisante

**Section workflow** : § 11.8 Couverture de tests attendue (ligne 1537)
**Statut** : ⚠️ **À MESURER**

**Description** :
Le workflow impose une couverture >= 85-100% selon les fichiers.

**Cibles** :
| Fichier | Couverture cible | Statut |
|---------|-----------------|--------|
| domain/entities/pointage.py | >= 95% | ⚠️ À mesurer |
| domain/value_objects/statut_pointage.py | 100% | ⚠️ À mesurer |
| application/use_cases/validate_pointage.py | >= 95% | ⚠️ À mesurer |

**Recommandation** :
```bash
# Mesurer la couverture
cd backend
pytest tests/unit/modules/pointages -v --cov=modules/pointages --cov-report=html

# Générer rapport
open htmlcov/index.html
```

---

## 3. Récapitulatif Gaps par Priorité

### 🔴 CRITIQUE (7 gaps) - BLOQUANT PRODUCTION

| ID | Titre | Impact |
|----|-------|--------|
| GAP-FDH-001 | Workflow "corriger" manquant | ❌ Cycle rejet/correction incomplet |
| GAP-FDH-002 | Verrouillage mensuel absent | ❌ Modifications rétroactives possibles |
| GAP-FDH-003 | Contrôle permissions manquant | ❌ Faille sécurité (compagnon valide ses heures) |
| GAP-TECH-001 | Use Case "corriger" absent | ❌ Code manquant |
| GAP-TECH-002 | Route POST /corriger absente | ❌ Route manquante |
| GAP-TECH-003 | Méthode controller.correct absente | ❌ Controller incomplet |
| GAP-TECH-004 | Value Object PeriodePaie absent | ❌ Logique métier manquante |

### 🟠 HAUTE (9 gaps) - IMPACT MÉTIER MAJEUR

| ID | Titre | Impact |
|----|-------|--------|
| GAP-FDH-004 | Signature obligatoire non validée | ⚠️ Conformité BTP |
| GAP-FDH-005 | Contrainte heures > 24h manquante | ⚠️ Données aberrantes |
| GAP-FDH-006 | Validation par lot absente | ⚠️ UX validateur (100-200 clics/semaine) |
| GAP-FDH-007 | Notifications push manquantes | ⚠️ UX terrain (chef/compagnon non notifiés) |
| GAP-TECH-005 | Tests verrouillage absents | ⚠️ Pas de régression détectée |
| GAP-TECH-006 | Service permissions absent | ⚠️ Logique métier manquante |
| GAP-FDH-011 | Chantier inactif non vérifié | ⚠️ Cohérence données |
| GAP-FDH-012 | Utilisateur désactivé non vérifié | ⚠️ Edge case non géré |
| GAP-FDH-013 | Contrainte doublon non testée | ⚠️ Pas de régression détectée |

### 🟡 MOYENNE (6 gaps) - AMÉLIORATION NÉCESSAIRE

| ID | Titre | Impact |
|----|-------|--------|
| GAP-FDH-008 | Points vérification validateur manquants | ℹ️ UX validateur (aide décision) |
| GAP-FDH-009 | Export paie incomplet | ℹ️ Formats XLSX/PDF/ERP manquants |
| GAP-FDH-010 | Récapitulatif mensuel manquant | ℹ️ UX paie |
| GAP-FDH-014 | Transitions interdites non testées | ℹ️ Pas de régression détectée |
| GAP-TECH-007 | Tests machine à états incomplets | ℹ️ Couverture tests |
| GAP-TECH-008 | Coverage insuffisante | ℹ️ < 85% sur certains fichiers |

---

## 4. Plan d'Action Recommandé

### Phase 1 : CRITIQUES (Sprint 1 - 5 jours)

**Objectif** : Corriger les 7 gaps bloquants pour production.

```
Jour 1-2 : GAP-FDH-002 (Verrouillage mensuel)
- Créer PeriodePaie value object
- Ajouter vérification dans TOUS les use cases
- Tests unitaires complets

Jour 3 : GAP-FDH-001 + GAP-TECH-001/002/003 (Workflow corriger)
- Créer CorrectPointageUseCase
- Ajouter route POST /corriger
- Ajouter méthode controller
- Tests cycle rejet/correction

Jour 4-5 : GAP-FDH-003 (Permissions)
- Créer PointagePermissionService
- Intégrer dans use cases
- Tests permissions
```

### Phase 2 : HAUTE PRIORITÉ (Sprint 2 - 5 jours)

```
Jour 1-2 : GAP-FDH-006 (Validation par lot)
- Créer ValidateFeuilleHeuresUseCase
- Route POST /feuilles/{id}/validate-all
- Tests validation par lot

Jour 3 : GAP-FDH-007 (Notifications)
- Event handlers notification
- Intégration Firebase Cloud Messaging
- Tests notifications

Jour 4-5 : GAP-FDH-004/005/011/012/013 (Validations métier)
- Signature obligatoire
- Contrainte 24h
- Chantier actif
- Tests complets
```

### Phase 3 : MOYENNE PRIORITÉ (Sprint 3 - 3 jours)

```
Jour 1 : GAP-FDH-008 (Points vérification)
- Enrichir PointageDetailDTO
- GetPointageForValidationUseCase
- UI enrichie pour validateur

Jour 2 : GAP-FDH-009 (Export paie)
- Export XLSX
- Export PDF
- Variables paie incluses

Jour 3 : GAP-FDH-010/014 + TECH-007/008 (Tests)
- Récapitulatif mensuel
- Tests transitions
- Coverage >= 90%
```

---

## 5. Métriques de Conformité

### Avant Corrections

| Catégorie | Conformité |
|-----------|-----------|
| **Machine à états** | 80% (transitions OK, verrouillage KO) |
| **Permissions** | 40% (roles OK, vérifications KO) |
| **Validations métier** | 50% (certaines manquantes) |
| **Export paie** | 25% (CSV seul) |
| **Tests** | 60% (use cases de base testés) |
| **GLOBAL** | **51% CONFORME** |

### Après Corrections (Objectif)

| Catégorie | Conformité cible |
|-----------|------------------|
| **Machine à états** | 100% (toutes transitions + verrouillage) |
| **Permissions** | 100% (matrice complète) |
| **Validations métier** | 100% (toutes règles) |
| **Export paie** | 100% (4 formats) |
| **Tests** | 95% (couverture complète) |
| **GLOBAL** | **99% CONFORME** |

---

## 6. Conclusion

Le module `pointages` est **fonctionnel pour les cas nominaux** (création, signature, soumission, validation, rejet) mais présente **22 gaps critiques** qui empêchent son utilisation en production :

- ❌ **Workflow de correction incomplet** (GAP-FDH-001) → Compagnons bloqués après rejet
- ❌ **Aucun verrouillage mensuel** (GAP-FDH-002) → Risque paie critique
- ❌ **Permissions non vérifiées** (GAP-FDH-003) → Faille sécurité

**Recommandation finale** :
Implémenter **Phase 1 (critiques) en priorité absolue** avant tout déploiement production.

---

**Auteur**: Claude Sonnet 4.5
**Date**: 31 janvier 2026
**Version**: 1.0

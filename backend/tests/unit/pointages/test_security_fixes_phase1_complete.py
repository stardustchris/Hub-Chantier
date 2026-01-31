"""Tests unitaires complets pour les corrections de sécurité Phase 1 - Module pointages.

Ce module teste les corrections de sécurité suivantes:
- SEC-PTG-001: Validation stricte du format HH:MM
- SEC-PTG-002: Intégration de PermissionService dans les routes

Couverture cible: >= 90%
"""

import pytest
from datetime import date

from modules.pointages.infrastructure.web.routes import validate_time_format
from modules.pointages.domain.services.permission_service import PointagePermissionService


# =============================================================================
# Tests SEC-PTG-001: Validation stricte format HH:MM
# =============================================================================


class TestValidateTimeFormat:
    """Tests pour la fonction validate_time_format (SEC-PTG-001)."""

    def test_valid_formats(self):
        """Test des formats valides."""
        # Formats standards
        assert validate_time_format("08:30") == "08:30"
        assert validate_time_format("23:59") == "23:59"
        assert validate_time_format("00:00") == "00:00"
        assert validate_time_format("12:00") == "12:00"

        # Formats avec 1 chiffre pour les heures (normalisés à 2 chiffres)
        assert validate_time_format("0:00") == "00:00"
        assert validate_time_format("1:30") == "01:30"
        assert validate_time_format("9:45") == "09:45"

    def test_invalid_hours(self):
        """Test des heures invalides."""
        # Heures > 23
        with pytest.raises(ValueError, match="Heures invalides"):
            validate_time_format("24:00")

        with pytest.raises(ValueError, match="Heures invalides"):
            validate_time_format("99:30")

        with pytest.raises(ValueError, match="Heures invalides"):
            validate_time_format("25:00")

    def test_invalid_minutes(self):
        """Test des minutes invalides."""
        # Minutes > 59
        with pytest.raises(ValueError, match="Minutes invalides"):
            validate_time_format("12:60")

        with pytest.raises(ValueError, match="Minutes invalides"):
            validate_time_format("08:99")

        with pytest.raises(ValueError, match="Minutes invalides"):
            validate_time_format("00:61")

    def test_invalid_formats(self):
        """Test des formats complètement invalides."""
        # Format incorrect
        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("abc:def")

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("12:3")  # Minutes sur 1 chiffre

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("12-30")  # Mauvais séparateur

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("12.30")  # Mauvais séparateur

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("1230")  # Sans séparateur

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("")  # Vide

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("12:")  # Minutes manquantes

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format(":30")  # Heures manquantes

    def test_negative_values(self):
        """Test des valeurs négatives (rejetées par la regex)."""
        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("-1:30")

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format("12:-5")

    def test_non_string_input(self):
        """Test des entrées non-string."""
        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format(None)

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format(123)

        with pytest.raises(ValueError, match="Format d'heure invalide"):
            validate_time_format(12.30)

    def test_edge_cases(self):
        """Test des cas limites."""
        # Minuit
        assert validate_time_format("00:00") == "00:00"

        # Fin de journée
        assert validate_time_format("23:59") == "23:59"

        # Début de journée
        assert validate_time_format("00:01") == "00:01"


# =============================================================================
# Tests SEC-PTG-002: Intégration PermissionService (COMPLET)
# =============================================================================


class TestPermissionServiceIntegration:
    """Tests pour l'intégration de PermissionService dans les routes (SEC-PTG-002)."""

    # ----- Tests can_create_for_user -----

    def test_can_create_for_user_compagnon_self(self):
        """Un compagnon peut créer un pointage pour lui-même."""
        assert PointagePermissionService.can_create_for_user(
            current_user_id=7,
            target_user_id=7,
            user_role="compagnon",
        ) is True

    def test_can_create_for_user_compagnon_other(self):
        """Un compagnon ne peut PAS créer un pointage pour un autre."""
        assert PointagePermissionService.can_create_for_user(
            current_user_id=7,
            target_user_id=8,
            user_role="compagnon",
        ) is False

    def test_can_create_for_user_chef(self):
        """Un chef peut créer un pointage pour n'importe qui."""
        assert PointagePermissionService.can_create_for_user(
            current_user_id=4,
            target_user_id=7,
            user_role="chef_chantier",
        ) is True

        assert PointagePermissionService.can_create_for_user(
            current_user_id=4,
            target_user_id=8,
            user_role="chef_chantier",
        ) is True

    def test_can_create_for_user_conducteur(self):
        """Un conducteur peut créer un pointage pour n'importe qui."""
        assert PointagePermissionService.can_create_for_user(
            current_user_id=2,
            target_user_id=7,
            user_role="conducteur",
        ) is True

    def test_can_create_for_user_admin(self):
        """Un admin peut créer un pointage pour n'importe qui."""
        assert PointagePermissionService.can_create_for_user(
            current_user_id=1,
            target_user_id=7,
            user_role="admin",
        ) is True

    # ----- Tests can_modify -----

    def test_can_modify_compagnon_self(self):
        """Un compagnon peut modifier son propre pointage."""
        assert PointagePermissionService.can_modify(
            current_user_id=7,
            pointage_owner_id=7,
            user_role="compagnon",
        ) is True

    def test_can_modify_compagnon_other(self):
        """Un compagnon ne peut PAS modifier le pointage d'un autre."""
        assert PointagePermissionService.can_modify(
            current_user_id=7,
            pointage_owner_id=8,
            user_role="compagnon",
        ) is False

    def test_can_modify_chef(self):
        """Un chef peut modifier n'importe quel pointage."""
        assert PointagePermissionService.can_modify(
            current_user_id=4,
            pointage_owner_id=7,
            user_role="chef_chantier",
        ) is True

    def test_can_modify_conducteur(self):
        """Un conducteur peut modifier n'importe quel pointage."""
        assert PointagePermissionService.can_modify(
            current_user_id=2,
            pointage_owner_id=7,
            user_role="conducteur",
        ) is True

    def test_can_modify_admin(self):
        """Un admin peut modifier n'importe quel pointage."""
        assert PointagePermissionService.can_modify(
            current_user_id=1,
            pointage_owner_id=7,
            user_role="admin",
        ) is True

    # ----- Tests can_validate -----

    def test_can_validate_compagnon(self):
        """Un compagnon ne peut PAS valider."""
        assert PointagePermissionService.can_validate("compagnon") is False

    def test_can_validate_chef(self):
        """Un chef peut valider."""
        assert PointagePermissionService.can_validate("chef_chantier") is True

    def test_can_validate_conducteur(self):
        """Un conducteur peut valider."""
        assert PointagePermissionService.can_validate("conducteur") is True

    def test_can_validate_admin(self):
        """Un admin peut valider."""
        assert PointagePermissionService.can_validate("admin") is True

    def test_can_validate_unknown_role(self):
        """Un rôle inconnu ne peut PAS valider."""
        assert PointagePermissionService.can_validate("unknown_role") is False

    # ----- Tests can_reject -----

    def test_can_reject_compagnon(self):
        """Un compagnon ne peut PAS rejeter."""
        assert PointagePermissionService.can_reject("compagnon") is False

    def test_can_reject_chef(self):
        """Un chef peut rejeter."""
        assert PointagePermissionService.can_reject("chef_chantier") is True

    def test_can_reject_conducteur(self):
        """Un conducteur peut rejeter."""
        assert PointagePermissionService.can_reject("conducteur") is True

    def test_can_reject_admin(self):
        """Un admin peut rejeter."""
        assert PointagePermissionService.can_reject("admin") is True

    def test_can_reject_unknown_role(self):
        """Un rôle inconnu ne peut PAS rejeter."""
        assert PointagePermissionService.can_reject("unknown_role") is False

    # ----- Tests can_export -----

    def test_can_export_compagnon(self):
        """Un compagnon ne peut PAS exporter."""
        assert PointagePermissionService.can_export("compagnon") is False

    def test_can_export_chef(self):
        """Un chef ne peut PAS exporter (restriction métier)."""
        assert PointagePermissionService.can_export("chef_chantier") is False

    def test_can_export_conducteur(self):
        """Un conducteur peut exporter."""
        assert PointagePermissionService.can_export("conducteur") is True

    def test_can_export_admin(self):
        """Un admin peut exporter."""
        assert PointagePermissionService.can_export("admin") is True

    def test_can_export_unknown_role(self):
        """Un rôle inconnu ne peut PAS exporter."""
        assert PointagePermissionService.can_export("unknown_role") is False

    # ----- Tests rôles inconnus -----

    def test_unknown_role_denied(self):
        """Un rôle inconnu est refusé pour can_create_for_user."""
        assert PointagePermissionService.can_create_for_user(
            current_user_id=7,
            target_user_id=7,
            user_role="unknown_role",
        ) is False

        assert PointagePermissionService.can_modify(
            current_user_id=7,
            pointage_owner_id=7,
            user_role="unknown_role",
        ) is False


# =============================================================================
# Tests d'intégration pour Pydantic Validators
# =============================================================================


class TestPydanticValidators:
    """Tests pour les validateurs Pydantic utilisant validate_time_format."""

    def test_create_request_valid_times(self):
        """Test de CreatePointageRequest avec des heures valides."""
        from modules.pointages.infrastructure.web.routes import CreatePointageRequest

        request = CreatePointageRequest(
            utilisateur_id=1,
            chantier_id=1,
            date_pointage=date.today(),
            heures_normales="08:30",
            heures_supplementaires="01:30",
        )

        assert request.heures_normales == "08:30"
        assert request.heures_supplementaires == "01:30"

    def test_create_request_invalid_heures_normales(self):
        """Test de CreatePointageRequest avec heures_normales invalides."""
        from modules.pointages.infrastructure.web.routes import CreatePointageRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreatePointageRequest(
                utilisateur_id=1,
                chantier_id=1,
                date_pointage=date.today(),
                heures_normales="99:99",  # Invalid
                heures_supplementaires="00:00",
            )

    def test_create_request_invalid_heures_supplementaires(self):
        """Test de CreatePointageRequest avec heures_supplementaires invalides."""
        from modules.pointages.infrastructure.web.routes import CreatePointageRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreatePointageRequest(
                utilisateur_id=1,
                chantier_id=1,
                date_pointage=date.today(),
                heures_normales="08:30",
                heures_supplementaires="24:00",  # Invalid
            )

    def test_update_request_valid_times(self):
        """Test de UpdatePointageRequest avec des heures valides."""
        from modules.pointages.infrastructure.web.routes import UpdatePointageRequest

        request = UpdatePointageRequest(
            heures_normales="09:00",
            heures_supplementaires="02:00",
        )

        assert request.heures_normales == "09:00"
        assert request.heures_supplementaires == "02:00"

    def test_update_request_invalid_times(self):
        """Test de UpdatePointageRequest avec des heures invalides."""
        from modules.pointages.infrastructure.web.routes import UpdatePointageRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UpdatePointageRequest(
                heures_normales="25:00",  # Invalid
            )

    def test_update_request_none_times(self):
        """Test de UpdatePointageRequest avec None (optionnel)."""
        from modules.pointages.infrastructure.web.routes import UpdatePointageRequest

        request = UpdatePointageRequest(
            heures_normales=None,
            heures_supplementaires=None,
        )

        assert request.heures_normales is None
        assert request.heures_supplementaires is None

    def test_create_request_time_normalization(self):
        """Test que les heures avec 1 chiffre sont normalisées."""
        from modules.pointages.infrastructure.web.routes import CreatePointageRequest

        request = CreatePointageRequest(
            utilisateur_id=1,
            chantier_id=1,
            date_pointage=date.today(),
            heures_normales="8:30",  # 1 chiffre pour les heures
            heures_supplementaires="1:00",  # 1 chiffre pour les heures
        )

        # Doit être normalisé à 2 chiffres
        assert request.heures_normales == "08:30"
        assert request.heures_supplementaires == "01:00"

    def test_create_request_default_heures_sup(self):
        """Test que heures_supplementaires a une valeur par défaut."""
        from modules.pointages.infrastructure.web.routes import CreatePointageRequest

        request = CreatePointageRequest(
            utilisateur_id=1,
            chantier_id=1,
            date_pointage=date.today(),
            heures_normales="08:00",
            # heures_supplementaires omis
        )

        assert request.heures_supplementaires == "00:00"

    def test_update_request_partial_update(self):
        """Test de UpdatePointageRequest avec mise à jour partielle."""
        from modules.pointages.infrastructure.web.routes import UpdatePointageRequest

        request = UpdatePointageRequest(
            heures_normales="10:00",
            # heures_supplementaires omis
        )

        assert request.heures_normales == "10:00"
        assert request.heures_supplementaires is None


# =============================================================================
# Tests de couverture pour les autres validateurs Pydantic
# =============================================================================


class TestOtherPydanticSchemas:
    """Tests pour les autres schémas Pydantic du module."""

    def test_sign_pointage_request(self):
        """Test de SignPointageRequest."""
        from modules.pointages.infrastructure.web.routes import SignPointageRequest

        request = SignPointageRequest(signature="data:image/png;base64,iVBORw0KGgo...")
        assert request.signature == "data:image/png;base64,iVBORw0KGgo..."

    def test_reject_pointage_request(self):
        """Test de RejectPointageRequest."""
        from modules.pointages.infrastructure.web.routes import RejectPointageRequest

        request = RejectPointageRequest(motif="Heures incorrectes")
        assert request.motif == "Heures incorrectes"

    def test_create_variable_paie_request(self):
        """Test de CreateVariablePaieRequest."""
        from modules.pointages.infrastructure.web.routes import CreateVariablePaieRequest

        request = CreateVariablePaieRequest(
            pointage_id=1,
            type_variable="PRIME",
            valeur=50.0,
            date_application=date.today(),
            commentaire="Prime qualité",
        )

        assert request.pointage_id == 1
        assert request.type_variable == "PRIME"
        assert request.valeur == 50.0

    def test_bulk_create_request(self):
        """Test de BulkCreateRequest."""
        from modules.pointages.infrastructure.web.routes import BulkCreateRequest

        request = BulkCreateRequest(
            utilisateur_id=7,
            semaine_debut=date(2026, 2, 3),
            affectations=[
                {"chantier_id": 1, "heures": "08:00"},
                {"chantier_id": 2, "heures": "04:00"},
            ],
        )

        assert request.utilisateur_id == 7
        assert len(request.affectations) == 2

    def test_export_request_csv(self):
        """Test de ExportRequest avec format CSV."""
        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="csv",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 7),
            utilisateur_ids=[1, 2, 3],
            chantier_ids=[10, 20],
            inclure_variables_paie=True,
            inclure_signatures=False,
        )

        assert request.format_export == "csv"
        assert request.inclure_variables_paie is True
        assert request.inclure_signatures is False

    def test_export_request_xlsx(self):
        """Test de ExportRequest avec format XLSX."""
        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="xlsx",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 7),
        )

        assert request.format_export == "xlsx"

    def test_export_request_pdf(self):
        """Test de ExportRequest avec format PDF."""
        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="pdf",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 7),
        )

        assert request.format_export == "pdf"

    def test_export_request_erp(self):
        """Test de ExportRequest avec format ERP."""
        from modules.pointages.infrastructure.web.routes import ExportRequest

        request = ExportRequest(
            format_export="erp",
            date_debut=date(2026, 2, 1),
            date_fin=date(2026, 2, 7),
        )

        assert request.format_export == "erp"

    def test_export_request_invalid_format(self):
        """Test de ExportRequest avec format invalide."""
        from modules.pointages.infrastructure.web.routes import ExportRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ExportRequest(
                format_export="invalid_format",
                date_debut=date(2026, 2, 1),
                date_fin=date(2026, 2, 7),
            )

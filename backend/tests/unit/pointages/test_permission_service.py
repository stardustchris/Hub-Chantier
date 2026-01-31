"""Tests unitaires pour PointagePermissionService (Domain Service)."""

import pytest

from modules.pointages.domain.services.permission_service import PointagePermissionService


class TestPointagePermissionService:
    """Tests pour le service de permissions des pointages."""

    # ========================================================================
    # Tests pour can_create_for_user
    # ========================================================================

    def test_can_create_compagnon_pour_lui_meme(self):
        """Test: Compagnon peut créer un pointage pour lui-même.

        Selon la matrice de permissions § 2.3, un compagnon
        peut créer ses propres pointages.
        """
        # Arrange
        current_user_id = 7
        target_user_id = 7
        user_role = "compagnon"

        # Act
        result = PointagePermissionService.can_create_for_user(
            current_user_id, target_user_id, user_role
        )

        # Assert
        assert result is True, "Compagnon doit pouvoir créer pour lui-même"

    def test_can_create_compagnon_pour_autre(self):
        """Test: Compagnon ne peut PAS créer pour un autre utilisateur.

        Selon la matrice § 2.3, un compagnon ne peut créer
        que ses propres pointages.
        """
        # Arrange
        current_user_id = 7
        target_user_id = 8
        user_role = "compagnon"

        # Act
        result = PointagePermissionService.can_create_for_user(
            current_user_id, target_user_id, user_role
        )

        # Assert
        assert result is False, "Compagnon ne peut pas créer pour un autre"

    def test_can_create_chef_pour_autre(self):
        """Test: Chef de chantier peut créer pour n'importe qui.

        Les chefs peuvent créer des pointages pour leurs compagnons.
        """
        # Arrange
        current_user_id = 4
        target_user_id = 7
        user_role = "chef_chantier"

        # Act
        result = PointagePermissionService.can_create_for_user(
            current_user_id, target_user_id, user_role
        )

        # Assert
        assert result is True, "Chef doit pouvoir créer pour n'importe qui"

    def test_can_create_chef_pour_lui_meme(self):
        """Test: Chef peut créer pour lui-même."""
        # Arrange
        current_user_id = 4
        target_user_id = 4
        user_role = "chef_chantier"

        # Act
        result = PointagePermissionService.can_create_for_user(
            current_user_id, target_user_id, user_role
        )

        # Assert
        assert result is True, "Chef peut créer pour lui-même"

    def test_can_create_conducteur_pour_autre(self):
        """Test: Conducteur de travaux peut créer pour n'importe qui."""
        # Arrange
        current_user_id = 2
        target_user_id = 7
        user_role = "conducteur"

        # Act
        result = PointagePermissionService.can_create_for_user(
            current_user_id, target_user_id, user_role
        )

        # Assert
        assert result is True, "Conducteur peut créer pour n'importe qui"

    def test_can_create_admin_pour_autre(self):
        """Test: Admin peut créer pour n'importe qui."""
        # Arrange
        current_user_id = 1
        target_user_id = 7
        user_role = "admin"

        # Act
        result = PointagePermissionService.can_create_for_user(
            current_user_id, target_user_id, user_role
        )

        # Assert
        assert result is True, "Admin peut créer pour n'importe qui"

    def test_can_create_role_inconnu(self):
        """Test: Rôle inconnu refuse par défaut (sécurité)."""
        # Arrange
        current_user_id = 7
        target_user_id = 7
        user_role = "role_invalide"

        # Act
        result = PointagePermissionService.can_create_for_user(
            current_user_id, target_user_id, user_role
        )

        # Assert
        assert result is False, "Rôle inconnu doit être refusé par défaut"

    # ========================================================================
    # Tests pour can_modify
    # ========================================================================

    def test_can_modify_compagnon_ses_pointages(self):
        """Test: Compagnon peut modifier ses propres pointages."""
        # Arrange
        current_user_id = 7
        pointage_owner_id = 7
        user_role = "compagnon"

        # Act
        result = PointagePermissionService.can_modify(
            current_user_id, pointage_owner_id, user_role
        )

        # Assert
        assert result is True, "Compagnon peut modifier ses pointages"

    def test_can_modify_compagnon_pointages_autre(self):
        """Test: Compagnon ne peut PAS modifier les pointages d'un autre."""
        # Arrange
        current_user_id = 7
        pointage_owner_id = 8
        user_role = "compagnon"

        # Act
        result = PointagePermissionService.can_modify(
            current_user_id, pointage_owner_id, user_role
        )

        # Assert
        assert result is False, "Compagnon ne peut pas modifier un autre pointage"

    def test_can_modify_chef_pointages_autre(self):
        """Test: Chef peut modifier les pointages d'un compagnon."""
        # Arrange
        current_user_id = 4
        pointage_owner_id = 7
        user_role = "chef_chantier"

        # Act
        result = PointagePermissionService.can_modify(
            current_user_id, pointage_owner_id, user_role
        )

        # Assert
        assert result is True, "Chef peut modifier n'importe quel pointage"

    def test_can_modify_conducteur_pointages_autre(self):
        """Test: Conducteur peut modifier les pointages d'un compagnon."""
        # Arrange
        current_user_id = 2
        pointage_owner_id = 7
        user_role = "conducteur"

        # Act
        result = PointagePermissionService.can_modify(
            current_user_id, pointage_owner_id, user_role
        )

        # Assert
        assert result is True, "Conducteur peut modifier n'importe quel pointage"

    def test_can_modify_admin_pointages_autre(self):
        """Test: Admin peut modifier n'importe quel pointage."""
        # Arrange
        current_user_id = 1
        pointage_owner_id = 7
        user_role = "admin"

        # Act
        result = PointagePermissionService.can_modify(
            current_user_id, pointage_owner_id, user_role
        )

        # Assert
        assert result is True, "Admin peut modifier n'importe quel pointage"

    # ========================================================================
    # Tests pour can_validate
    # ========================================================================

    def test_can_validate_compagnon(self):
        """Test: Compagnon ne peut PAS valider de pointages.

        Selon § 2.3, seuls les managers peuvent valider.
        Un compagnon ne peut jamais valider ses propres heures.
        """
        # Arrange
        user_role = "compagnon"

        # Act
        result = PointagePermissionService.can_validate(user_role)

        # Assert
        assert result is False, "Compagnon ne peut pas valider"

    def test_can_validate_chef(self):
        """Test: Chef de chantier peut valider des pointages."""
        # Arrange
        user_role = "chef_chantier"

        # Act
        result = PointagePermissionService.can_validate(user_role)

        # Assert
        assert result is True, "Chef peut valider"

    def test_can_validate_conducteur(self):
        """Test: Conducteur de travaux peut valider des pointages."""
        # Arrange
        user_role = "conducteur"

        # Act
        result = PointagePermissionService.can_validate(user_role)

        # Assert
        assert result is True, "Conducteur peut valider"

    def test_can_validate_admin(self):
        """Test: Admin peut valider des pointages."""
        # Arrange
        user_role = "admin"

        # Act
        result = PointagePermissionService.can_validate(user_role)

        # Assert
        assert result is True, "Admin peut valider"

    def test_can_validate_role_inconnu(self):
        """Test: Rôle inconnu ne peut pas valider."""
        # Arrange
        user_role = "role_invalide"

        # Act
        result = PointagePermissionService.can_validate(user_role)

        # Assert
        assert result is False, "Rôle inconnu ne peut pas valider"

    # ========================================================================
    # Tests pour can_reject
    # ========================================================================

    def test_can_reject_compagnon(self):
        """Test: Compagnon ne peut PAS rejeter de pointages.

        Même règle que can_validate.
        """
        # Arrange
        user_role = "compagnon"

        # Act
        result = PointagePermissionService.can_reject(user_role)

        # Assert
        assert result is False, "Compagnon ne peut pas rejeter"

    def test_can_reject_chef(self):
        """Test: Chef peut rejeter des pointages."""
        # Arrange
        user_role = "chef_chantier"

        # Act
        result = PointagePermissionService.can_reject(user_role)

        # Assert
        assert result is True, "Chef peut rejeter"

    def test_can_reject_conducteur(self):
        """Test: Conducteur peut rejeter des pointages."""
        # Arrange
        user_role = "conducteur"

        # Act
        result = PointagePermissionService.can_reject(user_role)

        # Assert
        assert result is True, "Conducteur peut rejeter"

    def test_can_reject_admin(self):
        """Test: Admin peut rejeter des pointages."""
        # Arrange
        user_role = "admin"

        # Act
        result = PointagePermissionService.can_reject(user_role)

        # Assert
        assert result is True, "Admin peut rejeter"

    # ========================================================================
    # Tests pour can_export
    # ========================================================================

    def test_can_export_compagnon(self):
        """Test: Compagnon ne peut PAS exporter pour la paie.

        Selon § 2.3, seuls Conducteur et Admin peuvent exporter.
        """
        # Arrange
        user_role = "compagnon"

        # Act
        result = PointagePermissionService.can_export(user_role)

        # Assert
        assert result is False, "Compagnon ne peut pas exporter"

    def test_can_export_chef(self):
        """Test: Chef de chantier ne peut PAS exporter.

        Restriction métier: seuls Conducteur et Admin peuvent exporter.
        Le chef ne peut pas exporter même s'il peut valider.
        """
        # Arrange
        user_role = "chef_chantier"

        # Act
        result = PointagePermissionService.can_export(user_role)

        # Assert
        assert result is False, "Chef ne peut pas exporter (restriction métier)"

    def test_can_export_conducteur(self):
        """Test: Conducteur de travaux peut exporter pour la paie."""
        # Arrange
        user_role = "conducteur"

        # Act
        result = PointagePermissionService.can_export(user_role)

        # Assert
        assert result is True, "Conducteur peut exporter"

    def test_can_export_admin(self):
        """Test: Admin peut exporter pour la paie."""
        # Arrange
        user_role = "admin"

        # Act
        result = PointagePermissionService.can_export(user_role)

        # Assert
        assert result is True, "Admin peut exporter"

    def test_can_export_role_inconnu(self):
        """Test: Rôle inconnu ne peut pas exporter."""
        # Arrange
        user_role = "role_invalide"

        # Act
        result = PointagePermissionService.can_export(user_role)

        # Assert
        assert result is False, "Rôle inconnu ne peut pas exporter"

    # ========================================================================
    # Tests de cohérence métier
    # ========================================================================

    def test_coherence_can_reject_equals_can_validate(self):
        """Test: can_reject retourne toujours la même valeur que can_validate.

        Les deux méthodes doivent être cohérentes pour tous les rôles.
        """
        # Arrange
        roles = ["compagnon", "chef_chantier", "conducteur", "admin", "inconnu"]

        # Act & Assert
        for role in roles:
            validate = PointagePermissionService.can_validate(role)
            reject = PointagePermissionService.can_reject(role)
            assert validate == reject, (
                f"Rôle {role}: can_validate et can_reject doivent retourner la même valeur"
            )

    def test_coherence_export_plus_restrictif_que_validate(self):
        """Test: Tous ceux qui peuvent exporter peuvent aussi valider.

        L'export est plus restrictif que la validation.
        """
        # Arrange
        roles = ["compagnon", "chef_chantier", "conducteur", "admin"]

        # Act & Assert
        for role in roles:
            can_export = PointagePermissionService.can_export(role)
            can_validate = PointagePermissionService.can_validate(role)

            if can_export:
                assert can_validate, (
                    f"Rôle {role}: si export autorisé, validation doit l'être aussi"
                )

    def test_constantes_roles_definies(self):
        """Test: Vérification des constantes de rôles."""
        # Assert
        assert PointagePermissionService.ROLE_COMPAGNON == "compagnon"
        assert PointagePermissionService.ROLE_CHEF == "chef_chantier"
        assert PointagePermissionService.ROLE_CONDUCTEUR == "conducteur"
        assert PointagePermissionService.ROLE_ADMIN == "admin"

    def test_constantes_roles_managers(self):
        """Test: Set ROLES_MANAGERS contient les bons rôles."""
        # Assert
        expected = {"chef_chantier", "conducteur", "admin"}
        assert PointagePermissionService.ROLES_MANAGERS == expected

"""Service de gestion des permissions pour les pointages."""


class PointagePermissionService:
    """
    Service domaine pour vérifier les permissions sur les pointages.

    Selon la matrice de permissions du workflow § 2.3, les règles suivantes
    s'appliquent :

    - Compagnon : Peut créer/modifier ses propres pointages uniquement
    - Chef de chantier : Peut créer/modifier pour n'importe qui, valider, rejeter
    - Conducteur de travaux : Peut tout faire
    - Admin : Peut tout faire

    Ce service est un Pure Domain Service (pas de dépendances externes).
    """

    # Rôles autorisés
    ROLE_COMPAGNON = "compagnon"
    ROLE_CHEF = "chef_chantier"
    ROLE_CONDUCTEUR = "conducteur"
    ROLE_ADMIN = "admin"

    # Rôles avec permissions étendues
    ROLES_MANAGERS = {ROLE_CHEF, ROLE_CONDUCTEUR, ROLE_ADMIN}

    @staticmethod
    def can_create_for_user(
        current_user_id: int,
        target_user_id: int,
        user_role: str
    ) -> bool:
        """
        Vérifie si current_user peut créer un pointage pour target_user.

        Args:
            current_user_id: ID de l'utilisateur qui crée.
            target_user_id: ID de l'utilisateur pour qui on crée le pointage.
            user_role: Rôle de current_user (compagnon, chef_chantier, etc.).

        Returns:
            True si l'action est autorisée.

        Examples:
            >>> # Compagnon crée pour lui-même → OK
            >>> PointagePermissionService.can_create_for_user(7, 7, "compagnon")
            True

            >>> # Compagnon crée pour un autre → KO
            >>> PointagePermissionService.can_create_for_user(7, 8, "compagnon")
            False

            >>> # Chef crée pour n'importe qui → OK
            >>> PointagePermissionService.can_create_for_user(4, 7, "chef_chantier")
            True
        """
        # Un compagnon ne peut créer que pour lui-même
        if user_role == PointagePermissionService.ROLE_COMPAGNON:
            return current_user_id == target_user_id

        # Chef, Conducteur, Admin peuvent créer pour n'importe qui
        if user_role in PointagePermissionService.ROLES_MANAGERS:
            return True

        # Rôle inconnu → refus par défaut
        return False

    @staticmethod
    def can_modify(
        current_user_id: int,
        pointage_owner_id: int,
        user_role: str
    ) -> bool:
        """
        Vérifie si current_user peut modifier le pointage d'un utilisateur.

        Args:
            current_user_id: ID de l'utilisateur qui modifie.
            pointage_owner_id: ID du propriétaire du pointage.
            user_role: Rôle de current_user.

        Returns:
            True si l'action est autorisée.

        Examples:
            >>> # Compagnon modifie son pointage → OK
            >>> PointagePermissionService.can_modify(7, 7, "compagnon")
            True

            >>> # Compagnon modifie le pointage d'un autre → KO
            >>> PointagePermissionService.can_modify(7, 8, "compagnon")
            False

            >>> # Chef modifie n'importe quel pointage → OK
            >>> PointagePermissionService.can_modify(4, 7, "chef_chantier")
            True
        """
        # Même logique que can_create_for_user
        return PointagePermissionService.can_create_for_user(
            current_user_id, pointage_owner_id, user_role
        )

    @staticmethod
    def can_validate(user_role: str) -> bool:
        """
        Vérifie si l'utilisateur peut valider des pointages.

        Seuls les Chef, Conducteur et Admin peuvent valider.
        Un compagnon ne peut jamais valider ses propres heures.

        Args:
            user_role: Rôle de l'utilisateur.

        Returns:
            True si l'action est autorisée.

        Examples:
            >>> PointagePermissionService.can_validate("compagnon")
            False

            >>> PointagePermissionService.can_validate("chef_chantier")
            True
        """
        return user_role in PointagePermissionService.ROLES_MANAGERS

    @staticmethod
    def can_reject(user_role: str) -> bool:
        """
        Vérifie si l'utilisateur peut rejeter des pointages.

        Même règle que can_validate (seuls les managers).

        Args:
            user_role: Rôle de l'utilisateur.

        Returns:
            True si l'action est autorisée.
        """
        return PointagePermissionService.can_validate(user_role)

    @staticmethod
    def can_export(user_role: str) -> bool:
        """
        Vérifie si l'utilisateur peut exporter pour la paie.

        Seuls le Conducteur et l'Admin peuvent exporter.
        Le Chef de chantier ne peut pas exporter (restriction métier).

        Args:
            user_role: Rôle de l'utilisateur.

        Returns:
            True si l'action est autorisée.

        Examples:
            >>> PointagePermissionService.can_export("compagnon")
            False

            >>> PointagePermissionService.can_export("chef_chantier")
            False

            >>> PointagePermissionService.can_export("conducteur")
            True
        """
        return user_role in {
            PointagePermissionService.ROLE_CONDUCTEUR,
            PointagePermissionService.ROLE_ADMIN,
        }

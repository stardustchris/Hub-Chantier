"""Service de gestion des permissions pour les pointages.

Regle metier : un chef de chantier ne peut gerer que les pointages
des compagnons affectes a SES chantiers. Les conducteurs et admins
ont un acces total (N+2).
"""

from typing import Optional, Set


class PointagePermissionService:
    """
    Service domaine pour verifier les permissions sur les pointages.

    Selon la matrice de permissions du workflow § 2.3 :

    - Compagnon : Peut creer/modifier ses propres pointages uniquement
    - Chef de chantier : Peut creer/modifier pour les compagnons de SES chantiers
    - Conducteur de travaux : Peut tout faire (N+2)
    - Admin : Peut tout faire

    Ce service est un Pure Domain Service (pas de dependances externes).
    """

    # Roles autorises
    ROLE_COMPAGNON = "compagnon"
    ROLE_CHEF = "chef_chantier"
    ROLE_CONDUCTEUR = "conducteur"
    ROLE_ADMIN = "admin"

    # Roles avec acces total sans restriction de chantier (N+2)
    ROLES_FULL_ACCESS = {ROLE_CONDUCTEUR, ROLE_ADMIN}

    # Tous les roles managers
    ROLES_MANAGERS = {ROLE_CHEF, ROLE_CONDUCTEUR, ROLE_ADMIN}

    @staticmethod
    def can_create_for_user(
        current_user_id: int,
        target_user_id: int,
        user_role: str,
        pointage_chantier_id: Optional[int] = None,
        user_chantier_ids: Optional[Set[int]] = None,
    ) -> bool:
        """
        Verifie si current_user peut creer un pointage pour target_user.

        Args:
            current_user_id: ID de l'utilisateur qui cree.
            target_user_id: ID de l'utilisateur pour qui on cree le pointage.
            user_role: Role de current_user (compagnon, chef_chantier, etc.).
            pointage_chantier_id: ID du chantier du pointage (optionnel).
            user_chantier_ids: IDs des chantiers auxquels current_user est affecte
                en tant que chef (requis pour chef_chantier).

        Returns:
            True si l'action est autorisee.
        """
        # Un compagnon ne peut creer que pour lui-meme
        if user_role == PointagePermissionService.ROLE_COMPAGNON:
            return current_user_id == target_user_id

        # Conducteur et Admin : acces total
        if user_role in PointagePermissionService.ROLES_FULL_ACCESS:
            return True

        # Chef de chantier : peut toujours creer pour lui-meme
        if user_role == PointagePermissionService.ROLE_CHEF:
            if current_user_id == target_user_id:
                return True
            # Pour un autre utilisateur : verifier l'appartenance au chantier
            return PointagePermissionService._chef_has_access_to_chantier(
                pointage_chantier_id, user_chantier_ids
            )

        # Role inconnu -> refus par defaut
        return False

    @staticmethod
    def can_modify(
        current_user_id: int,
        pointage_owner_id: int,
        user_role: str,
        pointage_chantier_id: Optional[int] = None,
        user_chantier_ids: Optional[Set[int]] = None,
    ) -> bool:
        """
        Verifie si current_user peut modifier le pointage d'un utilisateur.

        Args:
            current_user_id: ID de l'utilisateur qui modifie.
            pointage_owner_id: ID du proprietaire du pointage.
            user_role: Role de current_user.
            pointage_chantier_id: ID du chantier du pointage (optionnel).
            user_chantier_ids: IDs des chantiers du chef (optionnel).

        Returns:
            True si l'action est autorisee.
        """
        return PointagePermissionService.can_create_for_user(
            current_user_id, pointage_owner_id, user_role,
            pointage_chantier_id, user_chantier_ids,
        )

    @staticmethod
    def can_validate(
        user_role: str,
        pointage_chantier_id: Optional[int] = None,
        user_chantier_ids: Optional[Set[int]] = None,
    ) -> bool:
        """
        Verifie si l'utilisateur peut valider des pointages.

        Seuls les Chef, Conducteur et Admin peuvent valider.
        Un chef ne peut valider que les pointages de SES chantiers.

        Args:
            user_role: Role de l'utilisateur.
            pointage_chantier_id: ID du chantier du pointage (optionnel).
            user_chantier_ids: IDs des chantiers du chef (optionnel).

        Returns:
            True si l'action est autorisee.
        """
        if user_role not in PointagePermissionService.ROLES_MANAGERS:
            return False

        if user_role in PointagePermissionService.ROLES_FULL_ACCESS:
            return True

        # Chef : verifier l'appartenance au chantier
        if user_role == PointagePermissionService.ROLE_CHEF:
            return PointagePermissionService._chef_has_access_to_chantier(
                pointage_chantier_id, user_chantier_ids
            )

        return False

    @staticmethod
    def can_reject(
        user_role: str,
        pointage_chantier_id: Optional[int] = None,
        user_chantier_ids: Optional[Set[int]] = None,
    ) -> bool:
        """
        Verifie si l'utilisateur peut rejeter des pointages.

        Meme regle que can_validate (seuls les managers de leurs chantiers).

        Args:
            user_role: Role de l'utilisateur.
            pointage_chantier_id: ID du chantier du pointage (optionnel).
            user_chantier_ids: IDs des chantiers du chef (optionnel).

        Returns:
            True si l'action est autorisee.
        """
        return PointagePermissionService.can_validate(
            user_role, pointage_chantier_id, user_chantier_ids
        )

    @staticmethod
    def can_export(user_role: str) -> bool:
        """
        Verifie si l'utilisateur peut exporter pour la paie.

        Seuls le Conducteur et l'Admin peuvent exporter.
        Le Chef de chantier ne peut pas exporter (restriction metier).

        Args:
            user_role: Role de l'utilisateur.

        Returns:
            True si l'action est autorisee.
        """
        return user_role in {
            PointagePermissionService.ROLE_CONDUCTEUR,
            PointagePermissionService.ROLE_ADMIN,
        }

    @staticmethod
    def _chef_has_access_to_chantier(
        pointage_chantier_id: Optional[int],
        user_chantier_ids: Optional[Set[int]],
    ) -> bool:
        """
        Verifie si un chef de chantier a acces au chantier du pointage.

        Si les informations de chantier ne sont pas fournies (backward compat),
        l'acces est autorise par defaut.

        Args:
            pointage_chantier_id: ID du chantier du pointage.
            user_chantier_ids: IDs des chantiers du chef.

        Returns:
            True si le chef a acces, ou si les infos ne sont pas fournies.
        """
        if pointage_chantier_id is None:
            return True  # backward compat
        if user_chantier_ids is None:
            return True  # backward compat
        return pointage_chantier_id in user_chantier_ids

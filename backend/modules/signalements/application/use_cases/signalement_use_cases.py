"""Use Cases pour la gestion des signalements."""

from datetime import datetime
from typing import Optional, Callable

from ..dtos import (
    SignalementDTO,
    SignalementCreateDTO,
    SignalementUpdateDTO,
    SignalementListDTO,
    SignalementSearchDTO,
    SignalementStatsDTO,
)
from ...domain.entities import Signalement
from ...domain.repositories import SignalementRepository, ReponseRepository
from ...domain.value_objects import Priorite, StatutSignalement


class SignalementNotFoundError(Exception):
    """Erreur levée quand un signalement n'est pas trouvé."""

    pass


class InvalidStatusTransitionError(Exception):
    """Erreur levée quand une transition de statut est invalide."""

    pass


class AccessDeniedError(Exception):
    """Erreur levée quand l'accès est refusé."""

    pass


# Type pour la fonction de récupération des noms d'utilisateurs
UserNameResolver = Callable[[int], Optional[str]]


class CreateSignalementUseCase:
    """Use case pour créer un signalement (SIG-01)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._get_user_name = get_user_name

    def execute(self, dto: SignalementCreateDTO) -> SignalementDTO:
        """
        Crée un nouveau signalement.

        Args:
            dto: Données de création.

        Returns:
            Le signalement créé.
        """
        priorite = Priorite.from_string(dto.priorite)

        signalement = Signalement(
            chantier_id=dto.chantier_id,
            titre=dto.titre,
            description=dto.description,
            cree_par=dto.cree_par,
            priorite=priorite,
            assigne_a=dto.assigne_a,
            date_resolution_souhaitee=dto.date_resolution_souhaitee,
            photo_url=dto.photo_url,
            localisation=dto.localisation,
        )

        signalement = self._signalement_repo.save(signalement)

        return SignalementDTO.from_entity(signalement, get_user_name=self._get_user_name)


class GetSignalementUseCase:
    """Use case pour récupérer un signalement (SIG-02)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(self, signalement_id: int) -> SignalementDTO:
        """
        Récupère un signalement par son ID.

        Args:
            signalement_id: ID du signalement.

        Returns:
            Le signalement trouvé.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
        """
        signalement = self._signalement_repo.find_by_id(signalement_id)
        if not signalement:
            raise SignalementNotFoundError(f"Signalement {signalement_id} non trouvé")

        nb_reponses = self._reponse_repo.count_by_signalement(signalement_id)

        return SignalementDTO.from_entity(signalement, nb_reponses, self._get_user_name)


class ListSignalementsUseCase:
    """Use case pour lister les signalements d'un chantier (SIG-03)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100,
        statut: Optional[str] = None,
        priorite: Optional[str] = None,
    ) -> SignalementListDTO:
        """
        Liste les signalements d'un chantier.

        Args:
            chantier_id: ID du chantier.
            skip: Nombre à sauter.
            limit: Limite.
            statut: Filtrer par statut (optionnel).
            priorite: Filtrer par priorité (optionnel).

        Returns:
            Liste des signalements avec pagination.
        """
        statut_vo = StatutSignalement.from_string(statut) if statut else None
        priorite_vo = Priorite.from_string(priorite) if priorite else None

        signalements = self._signalement_repo.find_by_chantier(
            chantier_id, skip, limit, statut_vo, priorite_vo
        )
        total = self._signalement_repo.count_by_chantier(chantier_id, statut_vo, priorite_vo)

        dtos = []
        for sig in signalements:
            nb_reponses = self._reponse_repo.count_by_signalement(sig.id)  # type: ignore
            dtos.append(SignalementDTO.from_entity(sig, nb_reponses, self._get_user_name))

        return SignalementListDTO(
            signalements=dtos,
            total=total,
            skip=skip,
            limit=limit,
        )


class SearchSignalementsUseCase:
    """Use case pour rechercher des signalements (SIG-10, SIG-19, SIG-20)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(self, search_dto: SignalementSearchDTO) -> SignalementListDTO:
        """
        Recherche des signalements avec filtres.

        Args:
            search_dto: Critères de recherche.

        Returns:
            Liste des signalements trouvés.
        """
        statut_vo = None
        if search_dto.statut:
            try:
                statut_vo = StatutSignalement.from_string(search_dto.statut)
            except ValueError:
                pass

        priorite_vo = None
        if search_dto.priorite:
            try:
                priorite_vo = Priorite.from_string(search_dto.priorite)
            except ValueError:
                pass

        # Recherche via le repository
        if search_dto.query:
            signalements, total = self._signalement_repo.search(
                query=search_dto.query,
                chantier_id=search_dto.chantier_id,
                skip=search_dto.skip,
                limit=search_dto.limit,
            )
        else:
            signalements, total = self._signalement_repo.find_all(
                skip=search_dto.skip,
                limit=search_dto.limit,
                chantier_ids=search_dto.chantier_ids,
                statut=statut_vo,
                priorite=priorite_vo,
                date_debut=search_dto.date_debut,
                date_fin=search_dto.date_fin,
            )

        # Filtrer par en_retard si demandé
        if search_dto.en_retard_only:
            signalements = [s for s in signalements if s.est_en_retard]
            total = len(signalements)

        dtos = []
        for sig in signalements:
            nb_reponses = self._reponse_repo.count_by_signalement(sig.id)  # type: ignore
            dtos.append(SignalementDTO.from_entity(sig, nb_reponses, self._get_user_name))

        return SignalementListDTO(
            signalements=dtos,
            total=total,
            skip=search_dto.skip,
            limit=search_dto.limit,
        )


class UpdateSignalementUseCase:
    """Use case pour mettre à jour un signalement (SIG-04)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        signalement_id: int,
        dto: SignalementUpdateDTO,
        user_id: int,
        user_role: str,
    ) -> SignalementDTO:
        """
        Met à jour un signalement.

        Args:
            signalement_id: ID du signalement.
            dto: Données de mise à jour.
            user_id: ID de l'utilisateur effectuant la modification.
            user_role: Rôle de l'utilisateur.

        Returns:
            Le signalement mis à jour.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
        """
        signalement = self._signalement_repo.find_by_id(signalement_id)
        if not signalement:
            raise SignalementNotFoundError(f"Signalement {signalement_id} non trouvé")

        if not signalement.peut_modifier(user_id, user_role):
            raise AccessDeniedError("Vous n'avez pas les droits pour modifier ce signalement")

        if dto.titre is not None:
            signalement.titre = dto.titre.strip()

        if dto.description is not None:
            signalement.description = dto.description.strip()

        if dto.priorite is not None:
            signalement.changer_priorite(Priorite.from_string(dto.priorite))

        if dto.assigne_a is not None:
            signalement.assigner(dto.assigne_a)

        if dto.date_resolution_souhaitee is not None:
            signalement.definir_date_resolution(dto.date_resolution_souhaitee)

        if dto.photo_url is not None:
            signalement.photo_url = dto.photo_url

        if dto.localisation is not None:
            signalement.localisation = dto.localisation.strip() if dto.localisation else None

        signalement = self._signalement_repo.save(signalement)
        nb_reponses = self._reponse_repo.count_by_signalement(signalement_id)

        return SignalementDTO.from_entity(signalement, nb_reponses, self._get_user_name)


class DeleteSignalementUseCase:
    """Use case pour supprimer un signalement (SIG-05)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository

    def execute(
        self,
        signalement_id: int,
        user_id: int,
        user_role: str,
    ) -> bool:
        """
        Supprime un signalement.

        Args:
            signalement_id: ID du signalement.
            user_id: ID de l'utilisateur effectuant la suppression.
            user_role: Rôle de l'utilisateur.

        Returns:
            True si supprimé.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
        """
        signalement = self._signalement_repo.find_by_id(signalement_id)
        if not signalement:
            raise SignalementNotFoundError(f"Signalement {signalement_id} non trouvé")

        # Seuls admin et conducteur peuvent supprimer
        if user_role not in ("admin", "conducteur"):
            raise AccessDeniedError("Seuls les administrateurs et conducteurs peuvent supprimer des signalements")

        # Supprimer les réponses associées
        self._reponse_repo.delete_by_signalement(signalement_id)

        return self._signalement_repo.delete(signalement_id)


class AssignerSignalementUseCase:
    """Use case pour assigner un signalement (SIG-04)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        signalement_id: int,
        assigne_a: int,
        user_role: str,
    ) -> SignalementDTO:
        """
        Assigne un signalement à un utilisateur.

        Args:
            signalement_id: ID du signalement.
            assigne_a: ID de l'utilisateur assigné.
            user_role: Rôle de l'utilisateur effectuant l'assignation.

        Returns:
            Le signalement mis à jour.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
        """
        signalement = self._signalement_repo.find_by_id(signalement_id)
        if not signalement:
            raise SignalementNotFoundError(f"Signalement {signalement_id} non trouvé")

        # Seuls admin, conducteur et chef de chantier peuvent assigner
        if user_role not in ("admin", "conducteur", "chef_chantier"):
            raise AccessDeniedError("Vous n'avez pas les droits pour assigner ce signalement")

        signalement.assigner(assigne_a)
        signalement = self._signalement_repo.save(signalement)
        nb_reponses = self._reponse_repo.count_by_signalement(signalement_id)

        return SignalementDTO.from_entity(signalement, nb_reponses, self._get_user_name)


class MarquerTraiteUseCase:
    """Use case pour marquer un signalement comme traité (SIG-08)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        signalement_id: int,
        commentaire: str,
        user_role: str,
    ) -> SignalementDTO:
        """
        Marque un signalement comme traité.

        Args:
            signalement_id: ID du signalement.
            commentaire: Commentaire de traitement obligatoire.
            user_role: Rôle de l'utilisateur.

        Returns:
            Le signalement mis à jour.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
            InvalidStatusTransitionError: Si la transition n'est pas valide.
        """
        signalement = self._signalement_repo.find_by_id(signalement_id)
        if not signalement:
            raise SignalementNotFoundError(f"Signalement {signalement_id} non trouvé")

        try:
            signalement.marquer_traite(commentaire)
        except ValueError as e:
            raise InvalidStatusTransitionError(str(e))

        signalement = self._signalement_repo.save(signalement)
        nb_reponses = self._reponse_repo.count_by_signalement(signalement_id)

        return SignalementDTO.from_entity(signalement, nb_reponses, self._get_user_name)


class CloturerSignalementUseCase:
    """Use case pour clôturer un signalement (SIG-09)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        signalement_id: int,
        user_role: str,
    ) -> SignalementDTO:
        """
        Clôture un signalement.

        Args:
            signalement_id: ID du signalement.
            user_role: Rôle de l'utilisateur.

        Returns:
            Le signalement mis à jour.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
            InvalidStatusTransitionError: Si la transition n'est pas valide.
        """
        signalement = self._signalement_repo.find_by_id(signalement_id)
        if not signalement:
            raise SignalementNotFoundError(f"Signalement {signalement_id} non trouvé")

        if not signalement.peut_cloturer(user_role):
            raise AccessDeniedError("Vous n'avez pas les droits pour clôturer ce signalement")

        try:
            signalement.cloturer()
        except ValueError as e:
            raise InvalidStatusTransitionError(str(e))

        signalement = self._signalement_repo.save(signalement)
        nb_reponses = self._reponse_repo.count_by_signalement(signalement_id)

        return SignalementDTO.from_entity(signalement, nb_reponses, self._get_user_name)


class ReouvrirsignalementUseCase:
    """Use case pour réouvrir un signalement."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        signalement_id: int,
        user_role: str,
    ) -> SignalementDTO:
        """
        Réouvre un signalement clôturé.

        Args:
            signalement_id: ID du signalement.
            user_role: Rôle de l'utilisateur.

        Returns:
            Le signalement mis à jour.

        Raises:
            SignalementNotFoundError: Si le signalement n'existe pas.
            AccessDeniedError: Si l'utilisateur n'a pas les droits.
            InvalidStatusTransitionError: Si la transition n'est pas valide.
        """
        signalement = self._signalement_repo.find_by_id(signalement_id)
        if not signalement:
            raise SignalementNotFoundError(f"Signalement {signalement_id} non trouvé")

        # Seuls admin et conducteur peuvent réouvrir
        if user_role not in ("admin", "conducteur"):
            raise AccessDeniedError("Seuls les administrateurs et conducteurs peuvent réouvrir des signalements")

        try:
            signalement.reouvrir()
        except ValueError as e:
            raise InvalidStatusTransitionError(str(e))

        signalement = self._signalement_repo.save(signalement)
        nb_reponses = self._reponse_repo.count_by_signalement(signalement_id)

        return SignalementDTO.from_entity(signalement, nb_reponses, self._get_user_name)


class GetStatistiquesUseCase:
    """Use case pour obtenir les statistiques des signalements (SIG-18)."""

    def __init__(self, signalement_repository: SignalementRepository):
        self._signalement_repo = signalement_repository

    def execute(
        self,
        chantier_id: Optional[int] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
    ) -> SignalementStatsDTO:
        """
        Récupère les statistiques des signalements.

        Args:
            chantier_id: ID du chantier (optionnel, tous si None).
            date_debut: Date de début (optionnel).
            date_fin: Date de fin (optionnel).

        Returns:
            Les statistiques.
        """
        stats = self._signalement_repo.get_statistiques(
            chantier_id, date_debut, date_fin
        )

        return SignalementStatsDTO(
            total=stats.get("total", 0),
            par_statut=stats.get("par_statut", {}),
            par_priorite=stats.get("par_priorite", {}),
            en_retard=stats.get("en_retard", 0),
            traites_cette_semaine=stats.get("traites_cette_semaine", 0),
            temps_moyen_resolution=stats.get("temps_moyen_resolution"),
            taux_resolution=stats.get("taux_resolution", 0.0),
        )


class GetSignalementsEnRetardUseCase:
    """Use case pour obtenir les signalements en retard (SIG-16)."""

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[UserNameResolver] = None,
    ):
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    def execute(
        self,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> SignalementListDTO:
        """
        Récupère les signalements en retard.

        Args:
            chantier_id: ID du chantier (optionnel).
            skip: Nombre à sauter.
            limit: Limite.

        Returns:
            Liste des signalements en retard.
        """
        signalements = self._signalement_repo.find_en_retard(
            chantier_id, skip, limit
        )

        dtos = []
        for sig in signalements:
            nb_reponses = self._reponse_repo.count_by_signalement(sig.id)  # type: ignore
            dtos.append(SignalementDTO.from_entity(sig, nb_reponses, self._get_user_name))

        return SignalementListDTO(
            signalements=dtos,
            total=len(dtos),
            skip=skip,
            limit=limit,
        )

"""Controller pour les signalements - Orchestration des use cases."""

from datetime import datetime
from typing import Optional, Callable

from ...domain.repositories import SignalementRepository, ReponseRepository
from ...application.dtos import (
    SignalementDTO,
    SignalementCreateDTO,
    SignalementUpdateDTO,
    SignalementListDTO,
    SignalementSearchDTO,
    SignalementStatsDTO,
    ReponseDTO,
    ReponseCreateDTO,
    ReponseUpdateDTO,
    ReponseListDTO,
)
from ...application.use_cases import (
    CreateSignalementUseCase,
    GetSignalementUseCase,
    ListSignalementsUseCase,
    SearchSignalementsUseCase,
    UpdateSignalementUseCase,
    DeleteSignalementUseCase,
    AssignerSignalementUseCase,
    MarquerTraiteUseCase,
    CloturerSignalementUseCase,
    ReouvrirsignalementUseCase,
    GetStatistiquesUseCase,
    GetSignalementsEnRetardUseCase,
    CreateReponseUseCase,
    ListReponsesUseCase,
    UpdateReponseUseCase,
    DeleteReponseUseCase,
)


class SignalementController:
    """
    Controller pour les signalements.

    Orchestre les use cases et gère les transactions.
    """

    def __init__(
        self,
        signalement_repository: SignalementRepository,
        reponse_repository: ReponseRepository,
        get_user_name: Optional[Callable[[int], Optional[str]]] = None,
    ):
        """
        Initialise le controller.

        Args:
            signalement_repository: Repository des signalements.
            reponse_repository: Repository des réponses.
            get_user_name: Fonction pour résoudre les noms d'utilisateurs.
        """
        self._signalement_repo = signalement_repository
        self._reponse_repo = reponse_repository
        self._get_user_name = get_user_name

    # ============ SIGNALEMENTS ============

    def create_signalement(self, dto: SignalementCreateDTO) -> SignalementDTO:
        """Crée un nouveau signalement."""
        use_case = CreateSignalementUseCase(
            self._signalement_repo,
            self._get_user_name,
        )
        return use_case.execute(dto)

    def get_signalement(self, signalement_id: int) -> SignalementDTO:
        """Récupère un signalement par son ID."""
        use_case = GetSignalementUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(signalement_id)

    def list_signalements(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100,
        statut: Optional[str] = None,
        priorite: Optional[str] = None,
    ) -> SignalementListDTO:
        """Liste les signalements d'un chantier."""
        use_case = ListSignalementsUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(chantier_id, skip, limit, statut, priorite)

    def search_signalements(
        self,
        search_dto: SignalementSearchDTO,
    ) -> SignalementListDTO:
        """Recherche des signalements avec filtres."""
        use_case = SearchSignalementsUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(search_dto)

    def update_signalement(
        self,
        signalement_id: int,
        dto: SignalementUpdateDTO,
        user_id: int,
        user_role: str,
    ) -> SignalementDTO:
        """Met à jour un signalement."""
        use_case = UpdateSignalementUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(signalement_id, dto, user_id, user_role)

    def delete_signalement(
        self,
        signalement_id: int,
        user_id: int,
        user_role: str,
    ) -> bool:
        """Supprime un signalement."""
        use_case = DeleteSignalementUseCase(
            self._signalement_repo,
            self._reponse_repo,
        )
        return use_case.execute(signalement_id, user_id, user_role)

    def assigner_signalement(
        self,
        signalement_id: int,
        assigne_a: int,
        user_role: str,
    ) -> SignalementDTO:
        """Assigne un signalement à un utilisateur."""
        use_case = AssignerSignalementUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(signalement_id, assigne_a, user_role)

    def marquer_traite(
        self,
        signalement_id: int,
        commentaire: str,
        user_role: str,
    ) -> SignalementDTO:
        """Marque un signalement comme traité."""
        use_case = MarquerTraiteUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(signalement_id, commentaire, user_role)

    def cloturer_signalement(
        self,
        signalement_id: int,
        user_role: str,
    ) -> SignalementDTO:
        """Clôture un signalement."""
        use_case = CloturerSignalementUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(signalement_id, user_role)

    def reouvrir_signalement(
        self,
        signalement_id: int,
        user_role: str,
    ) -> SignalementDTO:
        """Réouvre un signalement clôturé."""
        use_case = ReouvrirsignalementUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(signalement_id, user_role)

    def get_statistiques(
        self,
        chantier_id: Optional[int] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
    ) -> SignalementStatsDTO:
        """Récupère les statistiques des signalements."""
        use_case = GetStatistiquesUseCase(self._signalement_repo)
        return use_case.execute(chantier_id, date_debut, date_fin)

    def get_signalements_en_retard(
        self,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> SignalementListDTO:
        """Récupère les signalements en retard."""
        use_case = GetSignalementsEnRetardUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(chantier_id, skip, limit)

    # ============ REPONSES ============

    def create_reponse(self, dto: ReponseCreateDTO) -> ReponseDTO:
        """Crée une nouvelle réponse."""
        use_case = CreateReponseUseCase(
            self._signalement_repo,
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(dto)

    def list_reponses(
        self,
        signalement_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> ReponseListDTO:
        """Liste les réponses d'un signalement."""
        use_case = ListReponsesUseCase(
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(signalement_id, skip, limit)

    def update_reponse(
        self,
        reponse_id: int,
        dto: ReponseUpdateDTO,
        user_id: int,
        user_role: str,
    ) -> ReponseDTO:
        """Met à jour une réponse."""
        use_case = UpdateReponseUseCase(
            self._reponse_repo,
            self._get_user_name,
        )
        return use_case.execute(reponse_id, dto, user_id, user_role)

    def delete_reponse(
        self,
        reponse_id: int,
        user_id: int,
        user_role: str,
    ) -> bool:
        """Supprime une réponse."""
        use_case = DeleteReponseUseCase(self._reponse_repo)
        return use_case.execute(reponse_id, user_id, user_role)

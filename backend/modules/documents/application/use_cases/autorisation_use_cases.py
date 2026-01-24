"""Use Cases pour la gestion des autorisations (GED-05, GED-10)."""


from ..dtos import AutorisationDTO, AutorisationCreateDTO, AutorisationListDTO
from ...domain.entities import AutorisationDocument, TypeAutorisation
from ...domain.repositories import AutorisationRepository, DossierRepository, DocumentRepository


class AutorisationAlreadyExistsError(Exception):
    """Erreur levée quand une autorisation existe déjà."""

    pass


class AutorisationNotFoundError(Exception):
    """Erreur levée quand une autorisation n'est pas trouvée."""

    pass


class InvalidTargetError(Exception):
    """Erreur levée quand la cible (dossier/document) est invalide."""

    pass


class CreateAutorisationUseCase:
    """Use case pour créer une autorisation nominative (GED-05)."""

    def __init__(
        self,
        autorisation_repository: AutorisationRepository,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ):
        """
        Initialise le use case.

        Args:
            autorisation_repository: Repository des autorisations.
            dossier_repository: Repository des dossiers.
            document_repository: Repository des documents.
        """
        self._autorisation_repo = autorisation_repository
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository

    def execute(self, dto: AutorisationCreateDTO) -> AutorisationDTO:
        """
        Crée une nouvelle autorisation.

        Args:
            dto: Données de l'autorisation.

        Returns:
            L'autorisation créée.

        Raises:
            AutorisationAlreadyExistsError: Si l'autorisation existe déjà.
            InvalidTargetError: Si la cible n'existe pas.
        """
        # Vérifier que la cible existe
        if dto.dossier_id:
            dossier = self._dossier_repo.find_by_id(dto.dossier_id)
            if not dossier:
                raise InvalidTargetError(f"Dossier {dto.dossier_id} non trouvé")
        elif dto.document_id:
            document = self._document_repo.find_by_id(dto.document_id)
            if not document:
                raise InvalidTargetError(f"Document {dto.document_id} non trouvé")
        else:
            raise InvalidTargetError("Dossier ou document requis")

        # Vérifier unicité
        if self._autorisation_repo.exists(
            dto.user_id, dto.dossier_id, dto.document_id
        ):
            raise AutorisationAlreadyExistsError(
                "Une autorisation existe déjà pour cet utilisateur sur cette cible"
            )

        # Créer l'entité
        type_autorisation = TypeAutorisation(dto.type_autorisation)

        if dto.dossier_id:
            autorisation = AutorisationDocument.creer_pour_dossier(
                dossier_id=dto.dossier_id,
                user_id=dto.user_id,
                type_autorisation=type_autorisation,
                accorde_par=dto.accorde_par,
                expire_at=dto.expire_at,
            )
        else:
            autorisation = AutorisationDocument.creer_pour_document(
                document_id=dto.document_id,  # type: ignore
                user_id=dto.user_id,
                type_autorisation=type_autorisation,
                accorde_par=dto.accorde_par,
                expire_at=dto.expire_at,
            )

        # Persister
        autorisation = self._autorisation_repo.save(autorisation)

        return self._to_dto(autorisation)

    def _to_dto(self, autorisation: AutorisationDocument) -> AutorisationDTO:
        """Convertit une entité en DTO."""
        return AutorisationDTO(
            id=autorisation.id,  # type: ignore
            user_id=autorisation.user_id,
            user_nom=None,
            type_autorisation=autorisation.type_autorisation.value,
            dossier_id=autorisation.dossier_id,
            document_id=autorisation.document_id,
            cible_nom=None,
            accorde_par=autorisation.accorde_par,
            accorde_par_nom=None,
            created_at=autorisation.created_at,
            expire_at=autorisation.expire_at,
            est_valide=autorisation.est_valide,
        )


class ListAutorisationsUseCase:
    """Use case pour lister les autorisations."""

    def __init__(self, autorisation_repository: AutorisationRepository):
        """Initialise le use case."""
        self._autorisation_repo = autorisation_repository

    def execute_by_dossier(self, dossier_id: int) -> AutorisationListDTO:
        """
        Liste les autorisations d'un dossier.

        Args:
            dossier_id: ID du dossier.

        Returns:
            Liste des autorisations.
        """
        autorisations = self._autorisation_repo.find_by_dossier(dossier_id)

        return AutorisationListDTO(
            autorisations=[
                AutorisationDTO(
                    id=a.id,  # type: ignore
                    user_id=a.user_id,
                    user_nom=None,
                    type_autorisation=a.type_autorisation.value,
                    dossier_id=a.dossier_id,
                    document_id=a.document_id,
                    cible_nom=None,
                    accorde_par=a.accorde_par,
                    accorde_par_nom=None,
                    created_at=a.created_at,
                    expire_at=a.expire_at,
                    est_valide=a.est_valide,
                )
                for a in autorisations
            ],
            total=len(autorisations),
        )

    def execute_by_document(self, document_id: int) -> AutorisationListDTO:
        """
        Liste les autorisations d'un document.

        Args:
            document_id: ID du document.

        Returns:
            Liste des autorisations.
        """
        autorisations = self._autorisation_repo.find_by_document(document_id)

        return AutorisationListDTO(
            autorisations=[
                AutorisationDTO(
                    id=a.id,  # type: ignore
                    user_id=a.user_id,
                    user_nom=None,
                    type_autorisation=a.type_autorisation.value,
                    dossier_id=a.dossier_id,
                    document_id=a.document_id,
                    cible_nom=None,
                    accorde_par=a.accorde_par,
                    accorde_par_nom=None,
                    created_at=a.created_at,
                    expire_at=a.expire_at,
                    est_valide=a.est_valide,
                )
                for a in autorisations
            ],
            total=len(autorisations),
        )

    def execute_by_user(self, user_id: int) -> AutorisationListDTO:
        """
        Liste les autorisations d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur.

        Returns:
            Liste des autorisations.
        """
        autorisations = self._autorisation_repo.find_by_user(user_id)

        return AutorisationListDTO(
            autorisations=[
                AutorisationDTO(
                    id=a.id,  # type: ignore
                    user_id=a.user_id,
                    user_nom=None,
                    type_autorisation=a.type_autorisation.value,
                    dossier_id=a.dossier_id,
                    document_id=a.document_id,
                    cible_nom=None,
                    accorde_par=a.accorde_par,
                    accorde_par_nom=None,
                    created_at=a.created_at,
                    expire_at=a.expire_at,
                    est_valide=a.est_valide,
                )
                for a in autorisations
            ],
            total=len(autorisations),
        )


class RevokeAutorisationUseCase:
    """Use case pour révoquer une autorisation."""

    def __init__(self, autorisation_repository: AutorisationRepository):
        """Initialise le use case."""
        self._autorisation_repo = autorisation_repository

    def execute(self, autorisation_id: int) -> bool:
        """
        Révoque une autorisation.

        Args:
            autorisation_id: ID de l'autorisation.

        Returns:
            True si révoquée.

        Raises:
            AutorisationNotFoundError: Si l'autorisation n'existe pas.
        """
        autorisation = self._autorisation_repo.find_by_id(autorisation_id)
        if not autorisation:
            raise AutorisationNotFoundError(
                f"Autorisation {autorisation_id} non trouvée"
            )

        return self._autorisation_repo.delete(autorisation_id)


class CheckAccessUseCase:
    """Use case pour vérifier l'accès d'un utilisateur."""

    def __init__(
        self,
        autorisation_repository: AutorisationRepository,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ):
        """Initialise le use case."""
        self._autorisation_repo = autorisation_repository
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository

    def can_access_dossier(
        self, user_id: int, user_role: str, dossier_id: int
    ) -> bool:
        """
        Vérifie si un utilisateur peut accéder à un dossier.

        Args:
            user_id: ID de l'utilisateur.
            user_role: Rôle de l'utilisateur.
            dossier_id: ID du dossier.

        Returns:
            True si l'utilisateur a accès.
        """
        dossier = self._dossier_repo.find_by_id(dossier_id)
        if not dossier:
            return False

        # Récupérer les autorisations nominatives
        user_ids = self._autorisation_repo.find_user_ids_for_dossier(dossier_id)

        return dossier.peut_acceder(user_role, user_id, user_ids)

    def can_access_document(
        self, user_id: int, user_role: str, document_id: int
    ) -> bool:
        """
        Vérifie si un utilisateur peut accéder à un document.

        Args:
            user_id: ID de l'utilisateur.
            user_role: Rôle de l'utilisateur.
            document_id: ID du document.

        Returns:
            True si l'utilisateur a accès.
        """
        document = self._document_repo.find_by_id(document_id)
        if not document:
            return False

        # Récupérer le niveau du dossier parent
        dossier = self._dossier_repo.find_by_id(document.dossier_id)
        niveau_dossier = dossier.niveau_acces if dossier else None

        # Récupérer les autorisations nominatives
        user_ids = self._autorisation_repo.find_user_ids_for_document(document_id)

        return document.peut_acceder(user_role, user_id, user_ids, niveau_dossier)

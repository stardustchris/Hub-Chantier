"""Use Case GetChantier - Récupération d'un chantier."""


from ...domain.repositories import ChantierRepository
from ...domain.value_objects import CodeChantier
from ..dtos import ChantierDTO


class ChantierNotFoundError(Exception):
    """Exception levée quand le chantier n'est pas trouvé."""

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.message = f"Chantier non trouvé: {identifier}"
        super().__init__(self.message)


class GetChantierUseCase:
    """
    Cas d'utilisation : Récupération d'un chantier par ID ou code.

    Attributes:
        chantier_repo: Repository pour accéder aux chantiers.
    """

    def __init__(self, chantier_repo: ChantierRepository):
        """
        Initialise le use case.

        Args:
            chantier_repo: Repository chantiers (interface).
        """
        self.chantier_repo = chantier_repo

    def execute_by_id(self, chantier_id: int) -> ChantierDTO:
        """
        Récupère un chantier par son ID.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            ChantierDTO du chantier trouvé.

        Raises:
            ChantierNotFoundError: Si le chantier n'existe pas.
        """
        chantier = self.chantier_repo.find_by_id(chantier_id)
        if not chantier:
            raise ChantierNotFoundError(str(chantier_id))
        return ChantierDTO.from_entity(chantier)

    def execute_by_code(self, code: str) -> ChantierDTO:
        """
        Récupère un chantier par son code.

        Args:
            code: Le code du chantier (ex: A001).

        Returns:
            ChantierDTO du chantier trouvé.

        Raises:
            ChantierNotFoundError: Si le chantier n'existe pas.
        """
        code_obj = CodeChantier(code)
        chantier = self.chantier_repo.find_by_code(code_obj)
        if not chantier:
            raise ChantierNotFoundError(code)
        return ChantierDTO.from_entity(chantier)

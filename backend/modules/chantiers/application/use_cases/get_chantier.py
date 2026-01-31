"""Use Case GetChantier - Récupération d'un chantier."""

import logging

from ...domain.repositories import ChantierRepository

logger = logging.getLogger(__name__)
from ...domain.value_objects import CodeChantier
from ..dtos import ChantierDTO


class ChantierNotFoundError(Exception):
    """Exception levée quand le chantier n'est pas trouvé."""

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.message = f"Chantier non trouvé: {identifier}"
        super().__init__(self.message)


class GetChantierUseCase:
    """
    Cas d'utilisation : Récupération d'un chantier par ID ou code.

    Attributes:
        chantier_repo: Repository pour accéder aux chantiers.
    """

    def __init__(self, chantier_repo: ChantierRepository) -> None:
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
        # Logging structured (GAP-CHT-006)
        logger.info(
            "Use case execution started",
            extra={
                "event": "chantier.use_case.started",
                "use_case": "GetChantierUseCase",
                "chantier_id": chantier_id,
                "operation": "get_by_id",
            }
        )

        try:
            chantier = self.chantier_repo.find_by_id(chantier_id)
            if not chantier:
                raise ChantierNotFoundError(str(chantier_id))

            logger.info(
                "Use case execution succeeded",
                extra={
                    "event": "chantier.use_case.succeeded",
                    "use_case": "GetChantierUseCase",
                    "chantier_id": chantier.id,
                }
            )

            return ChantierDTO.from_entity(chantier)

        except Exception as e:
            logger.error(
                "Use case execution failed",
                extra={
                    "event": "chantier.use_case.failed",
                    "use_case": "GetChantierUseCase",
                    "chantier_id": chantier_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            raise

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

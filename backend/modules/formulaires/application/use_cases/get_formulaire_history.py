"""Use Case GetFormulaireHistory - Historique d'un formulaire (FOR-08)."""

from typing import List

from ...domain.repositories import FormulaireRempliRepository
from ..dtos import FormulaireRempliDTO


class FormulaireNotFoundError(Exception):
    """Erreur levee si le formulaire n'est pas trouve."""

    pass


class GetFormulaireHistoryUseCase:
    """
    Use Case pour recuperer l'historique d'un formulaire.

    Implemente FOR-08 - Historique complet.
    """

    def __init__(self, formulaire_repo: FormulaireRempliRepository):
        """
        Initialise le use case.

        Args:
            formulaire_repo: Repository des formulaires.
        """
        self._formulaire_repo = formulaire_repo

    def execute(self, formulaire_id: int) -> List[FormulaireRempliDTO]:
        """
        Execute la recuperation de l'historique.

        Args:
            formulaire_id: ID du formulaire.

        Returns:
            Liste des versions du formulaire (du plus recent au plus ancien).

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
        """
        # Verifier que le formulaire existe
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        # Recuperer l'historique
        history = self._formulaire_repo.find_history(formulaire_id)

        return [FormulaireRempliDTO.from_entity(f) for f in history]

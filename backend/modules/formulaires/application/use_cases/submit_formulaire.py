"""Use Case SubmitFormulaire - Soumission d'un formulaire (FOR-07)."""

from typing import Optional, Callable

from ...domain.repositories import FormulaireRempliRepository
from ...domain.events import FormulaireSubmittedEvent, FormulaireSignedEvent
from ..dtos import SubmitFormulaireDTO, FormulaireRempliDTO


class FormulaireNotFoundError(Exception):
    """Erreur levee si le formulaire n'est pas trouve."""

    pass


class FormulaireNotSubmittableError(Exception):
    """Erreur levee si le formulaire ne peut pas etre soumis."""

    pass


class SubmitFormulaireUseCase:
    """
    Use Case pour soumettre un formulaire.

    Implemente FOR-07 - Horodatage automatique.
    """

    def __init__(
        self,
        formulaire_repo: FormulaireRempliRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            formulaire_repo: Repository des formulaires.
            event_publisher: Fonction pour publier les evenements.
        """
        self._formulaire_repo = formulaire_repo
        self._event_publisher = event_publisher

    def execute(self, dto: SubmitFormulaireDTO) -> FormulaireRempliDTO:
        """
        Execute la soumission d'un formulaire.

        Args:
            dto: Les donnees de soumission.

        Returns:
            Le formulaire soumis.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
            FormulaireNotSubmittableError: Si le formulaire ne peut pas etre soumis.
        """
        # Recuperer le formulaire
        formulaire = self._formulaire_repo.find_by_id(dto.formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {dto.formulaire_id} non trouve"
            )

        if not formulaire.est_brouillon:
            raise FormulaireNotSubmittableError(
                f"Le formulaire a deja ete soumis"
            )

        # Ajouter la signature si fournie (FOR-05)
        if dto.signature_url and dto.signature_nom:
            formulaire.signer(dto.signature_url, dto.signature_nom)

            # Publier l'evenement de signature
            if self._event_publisher:
                sign_event = FormulaireSignedEvent(
                    formulaire_id=formulaire.id,
                    signature_nom=dto.signature_nom,
                    signature_timestamp=formulaire.signature_timestamp,
                )
                self._event_publisher(sign_event)

        # Soumettre avec horodatage (FOR-07)
        formulaire.soumettre()

        # Sauvegarder
        saved = self._formulaire_repo.save(formulaire)

        # Publier l'evenement de soumission
        if self._event_publisher:
            event = FormulaireSubmittedEvent(
                formulaire_id=saved.id,
                template_id=saved.template_id,
                chantier_id=saved.chantier_id,
                user_id=saved.user_id,
                soumis_at=saved.soumis_at,
            )
            self._event_publisher(event)

        return FormulaireRempliDTO.from_entity(saved)

    def validate(
        self,
        formulaire_id: int,
        valideur_id: int,
    ) -> FormulaireRempliDTO:
        """
        Valide un formulaire soumis.

        Args:
            formulaire_id: ID du formulaire.
            valideur_id: ID de l'utilisateur qui valide.

        Returns:
            Le formulaire valide.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
            ValueError: Si le formulaire n'est pas soumis.
        """
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        formulaire.valider(valideur_id)
        saved = self._formulaire_repo.save(formulaire)

        return FormulaireRempliDTO.from_entity(saved)

    def reject(
        self,
        formulaire_id: int,
    ) -> FormulaireRempliDTO:
        """
        Refuse un formulaire soumis et le renvoie en brouillon.

        Args:
            formulaire_id: ID du formulaire.

        Returns:
            Le formulaire refuse (revenu en brouillon).

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
            ValueError: Si le formulaire n'est pas soumis.
        """
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        formulaire.refuser()
        saved = self._formulaire_repo.save(formulaire)

        return FormulaireRempliDTO.from_entity(saved)

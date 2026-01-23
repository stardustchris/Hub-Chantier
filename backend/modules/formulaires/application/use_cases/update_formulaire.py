"""Use Case UpdateFormulaire - Mise a jour d'un formulaire."""

from typing import Optional, Callable

from ...domain.entities import PhotoFormulaire
from ...domain.value_objects import TypeChamp
from ...domain.repositories import FormulaireRempliRepository
from ..dtos import UpdateFormulaireDTO, FormulaireRempliDTO


class FormulaireNotFoundError(Exception):
    """Erreur levee si le formulaire n'est pas trouve."""

    pass


class FormulaireNotModifiableError(Exception):
    """Erreur levee si le formulaire n'est pas modifiable."""

    pass


class UpdateFormulaireUseCase:
    """Use Case pour mettre a jour un formulaire."""

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

    def execute(
        self,
        formulaire_id: int,
        dto: UpdateFormulaireDTO,
    ) -> FormulaireRempliDTO:
        """
        Execute la mise a jour d'un formulaire.

        Args:
            formulaire_id: ID du formulaire a mettre a jour.
            dto: Les donnees de mise a jour.

        Returns:
            Le formulaire mis a jour.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
            FormulaireNotModifiableError: Si le formulaire n'est pas modifiable.
        """
        # Recuperer le formulaire
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        if not formulaire.statut.est_modifiable:
            raise FormulaireNotModifiableError(
                f"Le formulaire n'est plus modifiable (statut: {formulaire.statut.value})"
            )

        # Mettre a jour les champs
        if dto.champs:
            for champ_data in dto.champs:
                formulaire.set_champ(
                    nom=champ_data["nom"],
                    valeur=champ_data.get("valeur"),
                    type_champ=TypeChamp.from_string(champ_data["type_champ"]),
                )

        # Mettre a jour la localisation (FOR-03)
        if dto.latitude is not None and dto.longitude is not None:
            formulaire.set_localisation(dto.latitude, dto.longitude)

        # Sauvegarder
        saved = self._formulaire_repo.save(formulaire)

        return FormulaireRempliDTO.from_entity(saved)

    def add_photo(
        self,
        formulaire_id: int,
        url: str,
        nom_fichier: str,
        champ_nom: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> FormulaireRempliDTO:
        """
        Ajoute une photo au formulaire (FOR-04).

        Args:
            formulaire_id: ID du formulaire.
            url: URL de la photo.
            nom_fichier: Nom du fichier.
            champ_nom: Nom du champ associe.
            latitude: Latitude GPS (optionnel).
            longitude: Longitude GPS (optionnel).

        Returns:
            Le formulaire mis a jour.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
            FormulaireNotModifiableError: Si le formulaire n'est pas modifiable.
        """
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        if not formulaire.statut.est_modifiable:
            raise FormulaireNotModifiableError(
                f"Le formulaire n'est plus modifiable"
            )

        photo = PhotoFormulaire(
            url=url,
            nom_fichier=nom_fichier,
            champ_nom=champ_nom,
            latitude=latitude,
            longitude=longitude,
        )
        formulaire.ajouter_photo(photo)

        saved = self._formulaire_repo.save(formulaire)
        return FormulaireRempliDTO.from_entity(saved)

    def add_signature(
        self,
        formulaire_id: int,
        signature_url: str,
        signature_nom: str,
    ) -> FormulaireRempliDTO:
        """
        Ajoute une signature au formulaire (FOR-05).

        Args:
            formulaire_id: ID du formulaire.
            signature_url: URL de la signature.
            signature_nom: Nom du signataire.

        Returns:
            Le formulaire mis a jour.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
            FormulaireNotModifiableError: Si le formulaire n'est pas modifiable.
        """
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        if not formulaire.statut.est_modifiable:
            raise FormulaireNotModifiableError(
                f"Le formulaire n'est plus modifiable"
            )

        formulaire.signer(signature_url, signature_nom)

        saved = self._formulaire_repo.save(formulaire)
        return FormulaireRempliDTO.from_entity(saved)

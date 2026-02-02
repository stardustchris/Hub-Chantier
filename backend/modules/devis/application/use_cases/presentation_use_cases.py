"""Use Cases pour les options de presentation de devis.

DEV-11: Personnalisation presentation - Modeles de mise en page configurables.
"""

from typing import List

from ...domain.entities.journal_devis import JournalDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ...domain.value_objects.options_presentation import (
    OptionsPresentation,
    OptionsPresentationInvalideError,
    TEMPLATES_PRESENTATION,
)
from ..dtos.options_presentation_dtos import (
    OptionsPresentationDTO,
    UpdateOptionsPresentationDTO,
    TemplatePresentationDTO,
    ListeTemplatesPresentationDTO,
)
from .devis_use_cases import DevisNotFoundError


class UpdateOptionsPresentationUseCase:
    """Cas d'utilisation : Mettre a jour les options de presentation d'un devis.

    Permet de configurer quels elements sont visibles dans le rendu
    du devis (quantites, prix unitaires, TVA detaillee, etc.).

    Attributes:
        devis_repo: Repository pour acceder aux devis.
        journal_repo: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        devis_repo: DevisRepository,
        journal_repo: JournalDevisRepository,
    ):
        """Initialise le use case.

        Args:
            devis_repo: Repository devis (interface).
            journal_repo: Repository journal (interface).
        """
        self.devis_repo = devis_repo
        self.journal_repo = journal_repo

    def execute(
        self,
        devis_id: int,
        dto: UpdateOptionsPresentationDTO,
        user_id: int,
    ) -> OptionsPresentationDTO:
        """Met a jour les options de presentation d'un devis.

        Si un template_nom est fourni, les options du template sont appliquees
        en premier, puis les options individuelles surchargent le template.

        Args:
            devis_id: L'ID du devis.
            dto: Les options a mettre a jour.
            user_id: L'ID de l'utilisateur effectuant la modification.

        Returns:
            OptionsPresentationDTO avec les options mises a jour.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            OptionsPresentationInvalideError: Si le template est invalide.
        """
        # 1. Charger le devis
        devis = self.devis_repo.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # 2. Recuperer les options actuelles
        options_actuelles = devis.options_presentation.to_dict()

        # 3. Si un template est specifie, partir de ses options
        if dto.template_nom is not None:
            options = OptionsPresentation.from_template(dto.template_nom)
            options_actuelles = options.to_dict()

        # 4. Appliquer les surcharges individuelles
        champs_modifiables = [
            "afficher_debourses",
            "afficher_composants",
            "afficher_quantites",
            "afficher_prix_unitaires",
            "afficher_tva_detaillee",
            "afficher_conditions_generales",
            "afficher_logo",
            "afficher_coordonnees_entreprise",
            "afficher_retenue_garantie",
            "afficher_frais_chantier_detail",
        ]

        for champ in champs_modifiables:
            valeur = getattr(dto, champ, None)
            if valeur is not None:
                options_actuelles[champ] = valeur

        if dto.template_nom is not None:
            options_actuelles["template_nom"] = dto.template_nom

        # 5. Valider en creant le value object
        nouvelles_options = OptionsPresentation.from_dict(options_actuelles)

        # 6. Persister
        devis.set_options_presentation(nouvelles_options)
        self.devis_repo.save(devis)

        # 7. Journal
        self.journal_repo.save(
            JournalDevis(
                devis_id=devis_id,
                action="modification_options_presentation",
                details_json={
                    "message": f"Options de presentation mises a jour (template: {nouvelles_options.template_nom})",
                    "template_nom": nouvelles_options.template_nom,
                },
                auteur_id=user_id,
            )
        )

        # 8. Retour
        return OptionsPresentationDTO.from_value_object(nouvelles_options)


class GetOptionsPresentationUseCase:
    """Cas d'utilisation : Recuperer les options de presentation d'un devis.

    Retourne les options configurees ou les options par defaut si aucune
    configuration n'a ete sauvegardee.

    Attributes:
        devis_repo: Repository pour acceder aux devis.
    """

    def __init__(self, devis_repo: DevisRepository):
        """Initialise le use case.

        Args:
            devis_repo: Repository devis (interface).
        """
        self.devis_repo = devis_repo

    def execute(self, devis_id: int) -> OptionsPresentationDTO:
        """Recupere les options de presentation d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            OptionsPresentationDTO avec les options (defaut si non configurees).

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        devis = self.devis_repo.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        return OptionsPresentationDTO.from_value_object(devis.options_presentation)


class ListTemplatesPresentationUseCase:
    """Cas d'utilisation : Lister les templates de presentation disponibles.

    Retourne tous les templates predefinis avec leur description et options.
    """

    def execute(self) -> ListeTemplatesPresentationDTO:
        """Liste les templates de presentation disponibles.

        Returns:
            ListeTemplatesPresentationDTO avec tous les templates.
        """
        templates: List[TemplatePresentationDTO] = []
        for nom, config in TEMPLATES_PRESENTATION.items():
            templates.append(
                TemplatePresentationDTO(
                    nom=config["nom"],
                    description=config["description"],
                    options=config["options"],
                )
            )

        return ListeTemplatesPresentationDTO(templates=templates)

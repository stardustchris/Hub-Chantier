"""Use Cases pour la gestion des dossiers."""

from typing import Optional, List

from ..dtos import DossierDTO, DossierCreateDTO, DossierUpdateDTO, DossierTreeDTO, ArborescenceDTO
from ...domain.entities import Dossier
from ...domain.repositories import DossierRepository, DocumentRepository
from ...domain.value_objects import NiveauAcces, DossierType


class DossierNotFoundError(Exception):
    """Erreur levée quand un dossier n'est pas trouvé."""

    pass


class DossierNotEmptyError(Exception):
    """Erreur levée quand on essaie de supprimer un dossier non vide."""

    pass


class DuplicateDossierNameError(Exception):
    """Erreur levée quand un dossier avec ce nom existe déjà."""

    pass


class CreateDossierUseCase:
    """Use case pour créer un dossier."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ):
        """
        Initialise le use case.

        Args:
            dossier_repository: Repository des dossiers.
            document_repository: Repository des documents.
        """
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository

    def execute(self, dto: DossierCreateDTO) -> DossierDTO:
        """
        Crée un nouveau dossier.

        Args:
            dto: Données du dossier à créer.

        Returns:
            Le dossier créé.

        Raises:
            DuplicateDossierNameError: Si un dossier avec ce nom existe.
        """
        # Vérifier unicité du nom
        if self._dossier_repo.exists_by_nom_in_parent(
            dto.nom, dto.chantier_id, dto.parent_id
        ):
            raise DuplicateDossierNameError(
                f"Un dossier '{dto.nom}' existe déjà à cet emplacement"
            )

        # Créer l'entité
        dossier = Dossier(
            chantier_id=dto.chantier_id,
            nom=dto.nom,
            type_dossier=DossierType.from_string(dto.type_dossier),
            niveau_acces=NiveauAcces.from_string(dto.niveau_acces),
            parent_id=dto.parent_id,
        )

        # Persister
        dossier = self._dossier_repo.save(dossier)

        return self._to_dto(dossier)

    def _to_dto(self, dossier: Dossier) -> DossierDTO:
        """Convertit une entité en DTO."""
        return DossierDTO(
            id=dossier.id,  # type: ignore
            chantier_id=dossier.chantier_id,
            nom=dossier.nom,
            type_dossier=dossier.type_dossier.value,
            niveau_acces=dossier.niveau_acces.value,
            parent_id=dossier.parent_id,
            ordre=dossier.ordre,
            chemin_complet=dossier.chemin_complet,
            nombre_documents=self._document_repo.count_by_dossier(dossier.id),  # type: ignore
            nombre_sous_dossiers=len(self._dossier_repo.find_children(dossier.id)),  # type: ignore
            created_at=dossier.created_at,
        )


class GetDossierUseCase:
    """Use case pour récupérer un dossier."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ):
        """Initialise le use case."""
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository

    def execute(self, dossier_id: int) -> DossierDTO:
        """
        Récupère un dossier par son ID.

        Args:
            dossier_id: ID du dossier.

        Returns:
            Le dossier trouvé.

        Raises:
            DossierNotFoundError: Si le dossier n'existe pas.
        """
        dossier = self._dossier_repo.find_by_id(dossier_id)
        if not dossier:
            raise DossierNotFoundError(f"Dossier {dossier_id} non trouvé")

        return DossierDTO(
            id=dossier.id,  # type: ignore
            chantier_id=dossier.chantier_id,
            nom=dossier.nom,
            type_dossier=dossier.type_dossier.value,
            niveau_acces=dossier.niveau_acces.value,
            parent_id=dossier.parent_id,
            ordre=dossier.ordre,
            chemin_complet=dossier.chemin_complet,
            nombre_documents=self._document_repo.count_by_dossier(dossier.id),  # type: ignore
            nombre_sous_dossiers=len(self._dossier_repo.find_children(dossier.id)),  # type: ignore
            created_at=dossier.created_at,
        )


class ListDossiersUseCase:
    """Use case pour lister les dossiers d'un chantier."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ):
        """Initialise le use case."""
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository

    def execute(
        self, chantier_id: int, parent_id: Optional[int] = None
    ) -> List[DossierDTO]:
        """
        Liste les dossiers d'un chantier.

        Args:
            chantier_id: ID du chantier.
            parent_id: ID du parent (None pour racine).

        Returns:
            Liste des dossiers.
        """
        dossiers = self._dossier_repo.find_by_chantier(chantier_id, parent_id)

        return [
            DossierDTO(
                id=d.id,  # type: ignore
                chantier_id=d.chantier_id,
                nom=d.nom,
                type_dossier=d.type_dossier.value,
                niveau_acces=d.niveau_acces.value,
                parent_id=d.parent_id,
                ordre=d.ordre,
                chemin_complet=d.chemin_complet,
                nombre_documents=self._document_repo.count_by_dossier(d.id),  # type: ignore
                nombre_sous_dossiers=len(self._dossier_repo.find_children(d.id)),  # type: ignore
                created_at=d.created_at,
            )
            for d in dossiers
        ]


class GetArborescenceUseCase:
    """Use case pour récupérer l'arborescence complète (GED-02)."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ):
        """Initialise le use case."""
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository

    def execute(self, chantier_id: int) -> ArborescenceDTO:
        """
        Récupère l'arborescence complète d'un chantier.

        Args:
            chantier_id: ID du chantier.

        Returns:
            L'arborescence avec statistiques.
        """
        all_dossiers = self._dossier_repo.get_arborescence(chantier_id)

        # Construire l'arbre
        dossiers_by_id = {d.id: d for d in all_dossiers}
        root_dossiers = []

        def build_tree(dossier: Dossier) -> DossierTreeDTO:
            children = [
                build_tree(d) for d in all_dossiers if d.parent_id == dossier.id
            ]
            return DossierTreeDTO(
                id=dossier.id,  # type: ignore
                chantier_id=dossier.chantier_id,
                nom=dossier.nom,
                type_dossier=dossier.type_dossier.value,
                niveau_acces=dossier.niveau_acces.value,
                parent_id=dossier.parent_id,
                ordre=dossier.ordre,
                chemin_complet=dossier.chemin_complet,
                nombre_documents=self._document_repo.count_by_dossier(dossier.id),  # type: ignore
                children=sorted(children, key=lambda x: x.ordre),
            )

        for dossier in all_dossiers:
            if dossier.parent_id is None:
                root_dossiers.append(build_tree(dossier))

        # Trier par ordre/numéro
        root_dossiers.sort(key=lambda x: x.ordre)

        return ArborescenceDTO(
            chantier_id=chantier_id,
            dossiers=root_dossiers,
            total_documents=self._document_repo.count_by_chantier(chantier_id),
            total_taille=self._document_repo.get_total_size_by_chantier(chantier_id),
        )


class UpdateDossierUseCase:
    """Use case pour mettre à jour un dossier."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ):
        """Initialise le use case."""
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository

    def execute(self, dossier_id: int, dto: DossierUpdateDTO) -> DossierDTO:
        """
        Met à jour un dossier.

        Args:
            dossier_id: ID du dossier.
            dto: Données de mise à jour.

        Returns:
            Le dossier mis à jour.
        """
        dossier = self._dossier_repo.find_by_id(dossier_id)
        if not dossier:
            raise DossierNotFoundError(f"Dossier {dossier_id} non trouvé")

        if dto.nom is not None:
            # Vérifier unicité
            if self._dossier_repo.exists_by_nom_in_parent(
                dto.nom, dossier.chantier_id, dossier.parent_id
            ):
                existing = self._dossier_repo.find_by_chantier(
                    dossier.chantier_id, dossier.parent_id
                )
                for d in existing:
                    if d.nom == dto.nom and d.id != dossier_id:
                        raise DuplicateDossierNameError(
                            f"Un dossier '{dto.nom}' existe déjà"
                        )
            dossier.renommer(dto.nom)

        if dto.niveau_acces is not None:
            dossier.changer_niveau_acces(NiveauAcces.from_string(dto.niveau_acces))

        if dto.parent_id is not None:
            dossier.deplacer(dto.parent_id)

        dossier = self._dossier_repo.save(dossier)

        return DossierDTO(
            id=dossier.id,  # type: ignore
            chantier_id=dossier.chantier_id,
            nom=dossier.nom,
            type_dossier=dossier.type_dossier.value,
            niveau_acces=dossier.niveau_acces.value,
            parent_id=dossier.parent_id,
            ordre=dossier.ordre,
            chemin_complet=dossier.chemin_complet,
            nombre_documents=self._document_repo.count_by_dossier(dossier.id),  # type: ignore
            nombre_sous_dossiers=len(self._dossier_repo.find_children(dossier.id)),  # type: ignore
            created_at=dossier.created_at,
        )


class DeleteDossierUseCase:
    """Use case pour supprimer un dossier."""

    def __init__(self, dossier_repository: DossierRepository):
        """Initialise le use case."""
        self._dossier_repo = dossier_repository

    def execute(self, dossier_id: int, force: bool = False) -> bool:
        """
        Supprime un dossier.

        Args:
            dossier_id: ID du dossier.
            force: Si True, supprime même si non vide.

        Returns:
            True si supprimé.

        Raises:
            DossierNotFoundError: Si le dossier n'existe pas.
            DossierNotEmptyError: Si le dossier n'est pas vide et force=False.
        """
        dossier = self._dossier_repo.find_by_id(dossier_id)
        if not dossier:
            raise DossierNotFoundError(f"Dossier {dossier_id} non trouvé")

        if not force:
            if self._dossier_repo.has_documents(dossier_id):
                raise DossierNotEmptyError("Le dossier contient des documents")
            if self._dossier_repo.has_children(dossier_id):
                raise DossierNotEmptyError("Le dossier contient des sous-dossiers")

        return self._dossier_repo.delete(dossier_id)


class InitArborescenceUseCase:
    """Use case pour initialiser l'arborescence type d'un chantier."""

    def __init__(self, dossier_repository: DossierRepository):
        """Initialise le use case."""
        self._dossier_repo = dossier_repository

    def execute(self, chantier_id: int) -> List[DossierDTO]:
        """
        Crée l'arborescence type pour un nouveau chantier.

        Selon CDC Section 9.4 - Arborescence type.

        Args:
            chantier_id: ID du chantier.

        Returns:
            Liste des dossiers créés.
        """
        dossiers_crees = []

        for i, type_dossier in enumerate(DossierType):
            if type_dossier == DossierType.CUSTOM:
                continue

            # Vérifier si le dossier existe déjà
            existing = self._dossier_repo.find_by_type(chantier_id, type_dossier)
            if existing:
                continue

            dossier = Dossier(
                chantier_id=chantier_id,
                nom=type_dossier.nom_affichage,
                type_dossier=type_dossier,
                niveau_acces=NiveauAcces.from_string(type_dossier.niveau_acces_defaut),
                ordre=i,
            )

            saved = self._dossier_repo.save(dossier)
            dossiers_crees.append(
                DossierDTO(
                    id=saved.id,  # type: ignore
                    chantier_id=saved.chantier_id,
                    nom=saved.nom,
                    type_dossier=saved.type_dossier.value,
                    niveau_acces=saved.niveau_acces.value,
                    parent_id=saved.parent_id,
                    ordre=saved.ordre,
                    chemin_complet=saved.chemin_complet,
                    nombre_documents=0,
                    nombre_sous_dossiers=0,
                    created_at=saved.created_at,
                )
            )

        return dossiers_crees

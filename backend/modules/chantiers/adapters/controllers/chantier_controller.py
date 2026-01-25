"""ChantierController - Gestion des requêtes liées aux chantiers."""

from typing import Dict, Any, Optional, List

from ...application.use_cases import (
    CreateChantierUseCase,
    GetChantierUseCase,
    ListChantiersUseCase,
    UpdateChantierUseCase,
    DeleteChantierUseCase,
    ChangeStatutUseCase,
    AssignResponsableUseCase,
)
from ...application.dtos import (
    CreateChantierDTO,
    UpdateChantierDTO,
    ChangeStatutDTO,
)


class ChantierController:
    """
    Controller pour les opérations sur les chantiers.

    Fait le pont entre les requêtes HTTP et les Use Cases.
    Convertit les données brutes en DTOs et formate les réponses.
    Selon CDC Section 4 - Gestion des Chantiers (CHT-01 à CHT-20).
    """

    def __init__(
        self,
        create_use_case: CreateChantierUseCase,
        get_use_case: GetChantierUseCase,
        list_use_case: ListChantiersUseCase,
        update_use_case: UpdateChantierUseCase,
        delete_use_case: DeleteChantierUseCase,
        change_statut_use_case: ChangeStatutUseCase,
        assign_responsable_use_case: AssignResponsableUseCase,
    ):
        """
        Initialise le controller.

        Args:
            create_use_case: Use case de création.
            get_use_case: Use case de récupération.
            list_use_case: Use case de liste.
            update_use_case: Use case de mise à jour.
            delete_use_case: Use case de suppression.
            change_statut_use_case: Use case de changement de statut.
            assign_responsable_use_case: Use case d'assignation.
        """
        self.create_use_case = create_use_case
        self.get_use_case = get_use_case
        self.list_use_case = list_use_case
        self.update_use_case = update_use_case
        self.delete_use_case = delete_use_case
        self.change_statut_use_case = change_statut_use_case
        self.assign_responsable_use_case = assign_responsable_use_case

    def _chantier_dto_to_dict(self, dto) -> Dict[str, Any]:
        """Convertit un ChantierDTO en dictionnaire."""
        # Convertir les contacts en liste de dicts
        contacts = []
        if hasattr(dto, 'contacts') and dto.contacts:
            contacts = [
                {"nom": c.nom, "profession": c.profession, "telephone": c.telephone}
                for c in dto.contacts
            ]

        return {
            "id": dto.id,
            "code": dto.code,
            "nom": dto.nom,
            "adresse": dto.adresse,
            "statut": dto.statut,
            "statut_icon": dto.statut_icon,
            "couleur": dto.couleur,
            "coordonnees_gps": dto.coordonnees_gps,
            "photo_couverture": dto.photo_couverture,
            "contact": dto.contact,
            "contacts": contacts,
            "heures_estimees": dto.heures_estimees,
            "date_debut": dto.date_debut,
            "date_fin": dto.date_fin,
            "description": dto.description,
            "conducteur_ids": dto.conducteur_ids,
            "chef_chantier_ids": dto.chef_chantier_ids,
            "is_active": dto.is_active,
            "created_at": dto.created_at.isoformat() if dto.created_at else None,
            "updated_at": dto.updated_at.isoformat() if dto.updated_at else None,
        }

    def create(
        self,
        nom: str,
        adresse: str,
        code: Optional[str] = None,
        couleur: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        photo_couverture: Optional[str] = None,
        contact_nom: Optional[str] = None,
        contact_telephone: Optional[str] = None,
        contacts: Optional[List[Dict[str, Any]]] = None,
        heures_estimees: Optional[float] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        description: Optional[str] = None,
        conducteur_ids: Optional[List[int]] = None,
        chef_chantier_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Crée un nouveau chantier.

        Args:
            nom: Nom du chantier.
            adresse: Adresse complète.
            code: Code unique (auto-généré si non fourni).
            couleur: Couleur d'identification (CHT-02).
            latitude: Latitude GPS (CHT-04).
            longitude: Longitude GPS (CHT-04).
            photo_couverture: URL photo (CHT-01).
            contact_nom: Nom du contact legacy (CHT-07).
            contact_telephone: Téléphone du contact legacy (CHT-07).
            contacts: Liste des contacts (CHT-07).
            heures_estimees: Budget temps (CHT-18).
            date_debut: Date début ISO (CHT-20).
            date_fin: Date fin ISO (CHT-20).
            description: Description.
            conducteur_ids: IDs des conducteurs (CHT-05).
            chef_chantier_ids: IDs des chefs (CHT-06).

        Returns:
            Dictionnaire avec le chantier créé.

        Raises:
            CodeChantierAlreadyExistsError: Si code déjà utilisé.
            InvalidDatesError: Si dates invalides.
        """
        # Convertir contacts dicts en ContactDTO
        from ...application.dtos import ContactDTO
        contacts_dto = None
        if contacts:
            contacts_dto = [
                ContactDTO(
                    nom=c.get("nom", ""),
                    profession=c.get("profession"),
                    telephone=c.get("telephone"),
                )
                for c in contacts
            ]

        dto = CreateChantierDTO(
            nom=nom,
            adresse=adresse,
            code=code,
            couleur=couleur,
            latitude=latitude,
            longitude=longitude,
            photo_couverture=photo_couverture,
            contact_nom=contact_nom,
            contact_telephone=contact_telephone,
            contacts=contacts_dto,
            heures_estimees=heures_estimees,
            date_debut=date_debut,
            date_fin=date_fin,
            description=description,
            conducteur_ids=conducteur_ids,
            chef_chantier_ids=chef_chantier_ids,
        )
        result = self.create_use_case.execute(dto)
        return self._chantier_dto_to_dict(result)

    def get_by_id(self, chantier_id: int) -> Dict[str, Any]:
        """
        Récupère un chantier par son ID.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Dictionnaire avec le chantier.

        Raises:
            ChantierNotFoundError: Si non trouvé.
        """
        result = self.get_use_case.execute_by_id(chantier_id)
        return self._chantier_dto_to_dict(result)

    def get_by_code(self, code: str) -> Dict[str, Any]:
        """
        Récupère un chantier par son code.

        Args:
            code: Le code du chantier (ex: A001).

        Returns:
            Dictionnaire avec le chantier.

        Raises:
            ChantierNotFoundError: Si non trouvé.
        """
        result = self.get_use_case.execute_by_code(code)
        return self._chantier_dto_to_dict(result)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        statut: Optional[str] = None,
        conducteur_id: Optional[int] = None,
        chef_chantier_id: Optional[int] = None,
        responsable_id: Optional[int] = None,
        actifs_uniquement: bool = False,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Liste les chantiers avec pagination et filtres.

        Args:
            skip: Nombre à sauter.
            limit: Limite de résultats.
            statut: Filtrer par statut.
            conducteur_id: Filtrer par conducteur.
            chef_chantier_id: Filtrer par chef.
            responsable_id: Filtrer par responsable.
            actifs_uniquement: Uniquement les actifs.
            search: Recherche textuelle.

        Returns:
            Dictionnaire avec liste paginée.
        """
        result = self.list_use_case.execute(
            skip=skip,
            limit=limit,
            statut=statut,
            conducteur_id=conducteur_id,
            chef_chantier_id=chef_chantier_id,
            responsable_id=responsable_id,
            actifs_uniquement=actifs_uniquement,
            search=search,
        )
        return {
            "chantiers": [self._chantier_dto_to_dict(c) for c in result.chantiers],
            "total": result.total,
            "skip": result.skip,
            "limit": result.limit,
            "has_next": result.has_next,
            "has_previous": result.has_previous,
        }

    def update(
        self,
        chantier_id: int,
        nom: Optional[str] = None,
        adresse: Optional[str] = None,
        couleur: Optional[str] = None,
        statut: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        photo_couverture: Optional[str] = None,
        contact_nom: Optional[str] = None,
        contact_telephone: Optional[str] = None,
        contacts: Optional[List[Dict[str, Any]]] = None,
        heures_estimees: Optional[float] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Met à jour un chantier.

        Args:
            chantier_id: ID du chantier.
            nom: Nouveau nom.
            adresse: Nouvelle adresse.
            couleur: Nouvelle couleur.
            statut: Nouveau statut.
            latitude: Nouvelle latitude.
            longitude: Nouvelle longitude.
            photo_couverture: Nouvelle photo.
            contact_nom: Nouveau contact nom (legacy).
            contact_telephone: Nouveau contact tel (legacy).
            contacts: Liste des contacts.
            heures_estimees: Nouvelles heures.
            date_debut: Nouvelle date début.
            date_fin: Nouvelle date fin.
            description: Nouvelle description.

        Returns:
            Dictionnaire avec le chantier mis à jour.

        Raises:
            ChantierNotFoundError: Si non trouvé.
            ChantierFermeError: Si fermé.
        """
        # Convertir contacts dicts en ContactDTO
        from ...application.dtos import ContactDTO
        contacts_dto = None
        if contacts:
            contacts_dto = [
                ContactDTO(
                    nom=c.get("nom", ""),
                    profession=c.get("profession"),
                    telephone=c.get("telephone"),
                )
                for c in contacts
            ]

        dto = UpdateChantierDTO(
            nom=nom,
            adresse=adresse,
            couleur=couleur,
            latitude=latitude,
            longitude=longitude,
            photo_couverture=photo_couverture,
            contact_nom=contact_nom,
            contact_telephone=contact_telephone,
            contacts=contacts_dto,
            heures_estimees=heures_estimees,
            date_debut=date_debut,
            date_fin=date_fin,
            description=description,
        )
        result = self.update_use_case.execute(chantier_id, dto)

        # Si statut fourni ET different du statut actuel, changer le statut
        if statut and result.statut != statut:
            result = self.change_statut_use_case.execute(
                chantier_id,
                ChangeStatutDTO(nouveau_statut=statut)
            )

        return self._chantier_dto_to_dict(result)

    def delete(self, chantier_id: int, force: bool = False) -> Dict[str, Any]:
        """
        Supprime un chantier.

        Args:
            chantier_id: ID du chantier.
            force: Forcer la suppression même si actif.

        Returns:
            Dictionnaire avec confirmation.

        Raises:
            ChantierNotFoundError: Si non trouvé.
            ChantierActifError: Si actif et force=False.
        """
        result = self.delete_use_case.execute(chantier_id, force=force)
        return {"deleted": result, "id": chantier_id}

    def change_statut(self, chantier_id: int, nouveau_statut: str) -> Dict[str, Any]:
        """
        Change le statut d'un chantier (CHT-03).

        Args:
            chantier_id: ID du chantier.
            nouveau_statut: Nouveau statut.

        Returns:
            Dictionnaire avec le chantier mis à jour.

        Raises:
            ChantierNotFoundError: Si non trouvé.
            TransitionNonAutoriseeError: Si transition invalide.
        """
        dto = ChangeStatutDTO(nouveau_statut=nouveau_statut)
        result = self.change_statut_use_case.execute(chantier_id, dto)
        return self._chantier_dto_to_dict(result)

    def demarrer(self, chantier_id: int) -> Dict[str, Any]:
        """Raccourci pour passer en 'En cours'."""
        result = self.change_statut_use_case.demarrer(chantier_id)
        return self._chantier_dto_to_dict(result)

    def receptionner(self, chantier_id: int) -> Dict[str, Any]:
        """Raccourci pour passer en 'Réceptionné'."""
        result = self.change_statut_use_case.receptionner(chantier_id)
        return self._chantier_dto_to_dict(result)

    def fermer(self, chantier_id: int) -> Dict[str, Any]:
        """Raccourci pour passer en 'Fermé'."""
        result = self.change_statut_use_case.fermer(chantier_id)
        return self._chantier_dto_to_dict(result)

    def assigner_conducteur(self, chantier_id: int, user_id: int) -> Dict[str, Any]:
        """
        Assigne un conducteur au chantier (CHT-05).

        Args:
            chantier_id: ID du chantier.
            user_id: ID du conducteur.

        Returns:
            Dictionnaire avec le chantier mis à jour.
        """
        result = self.assign_responsable_use_case.assigner_conducteur(
            chantier_id, user_id
        )
        return self._chantier_dto_to_dict(result)

    def assigner_chef_chantier(self, chantier_id: int, user_id: int) -> Dict[str, Any]:
        """
        Assigne un chef de chantier (CHT-06).

        Args:
            chantier_id: ID du chantier.
            user_id: ID du chef.

        Returns:
            Dictionnaire avec le chantier mis à jour.
        """
        result = self.assign_responsable_use_case.assigner_chef_chantier(
            chantier_id, user_id
        )
        return self._chantier_dto_to_dict(result)

    def retirer_conducteur(self, chantier_id: int, user_id: int) -> Dict[str, Any]:
        """
        Retire un conducteur du chantier.

        Args:
            chantier_id: ID du chantier.
            user_id: ID du conducteur.

        Returns:
            Dictionnaire avec le chantier mis à jour.
        """
        result = self.assign_responsable_use_case.retirer_conducteur(
            chantier_id, user_id
        )
        return self._chantier_dto_to_dict(result)

    def retirer_chef_chantier(self, chantier_id: int, user_id: int) -> Dict[str, Any]:
        """
        Retire un chef de chantier.

        Args:
            chantier_id: ID du chantier.
            user_id: ID du chef.

        Returns:
            Dictionnaire avec le chantier mis à jour.
        """
        result = self.assign_responsable_use_case.retirer_chef_chantier(
            chantier_id, user_id
        )
        return self._chantier_dto_to_dict(result)

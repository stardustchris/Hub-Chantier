"""Use Cases pour les signatures d'intervention."""

from typing import List, Optional

from ...domain.entities import SignatureIntervention, TypeSignataire
from ...domain.repositories import SignatureInterventionRepository
from ..dtos import CreateSignatureDTO


class AddSignatureUseCase:
    """Use case pour ajouter une signature.

    INT-13: Signature client
    """

    def __init__(self, repository: SignatureInterventionRepository):
        """
        Initialise le use case.

        Args:
            repository: Repository pour acceder aux signatures d'intervention.
        """
        self._repository = repository

    def execute(
        self,
        intervention_id: int,
        dto: CreateSignatureDTO,
        utilisateur_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> SignatureIntervention:
        """
        Ajoute une signature a l'intervention.

        Args:
            intervention_id: ID de l'intervention a signer.
            dto: Donnees de la signature.
            utilisateur_id: ID de l'utilisateur (pour signature technicien).
            ip_address: Adresse IP du signataire (optionnel).

        Returns:
            La signature creee.

        Raises:
            ValueError: Si signature deja existante ou utilisateur_id manquant.
        """
        type_signataire = TypeSignataire(dto.type_signataire)

        if type_signataire == TypeSignataire.CLIENT:
            # Verifier qu'il n'y a pas deja une signature client
            existing = self._repository.get_signature_client(intervention_id)
            if existing:
                raise ValueError("Une signature client existe deja pour cette intervention")

            signature = SignatureIntervention.creer_signature_client(
                intervention_id=intervention_id,
                nom_client=dto.nom_signataire,
                signature_data=dto.signature_data,
                ip_address=ip_address,
                latitude=dto.latitude,
                longitude=dto.longitude,
            )
        else:
            if not utilisateur_id:
                raise ValueError(
                    "L'ID utilisateur est obligatoire pour une signature technicien"
                )

            # Verifier qu'il n'a pas deja signe
            existing = self._repository.get_signature_technicien(
                intervention_id, utilisateur_id
            )
            if existing:
                raise ValueError("Ce technicien a deja signe cette intervention")

            signature = SignatureIntervention.creer_signature_technicien(
                intervention_id=intervention_id,
                utilisateur_id=utilisateur_id,
                nom_technicien=dto.nom_signataire,
                signature_data=dto.signature_data,
                ip_address=ip_address,
                latitude=dto.latitude,
                longitude=dto.longitude,
            )

        return self._repository.save(signature)


class ListSignaturesUseCase:
    """Use case pour lister les signatures."""

    def __init__(self, repository: SignatureInterventionRepository):
        """
        Initialise le use case.

        Args:
            repository: Repository pour acceder aux signatures d'intervention.
        """
        self._repository = repository

    def execute(
        self, intervention_id: int
    ) -> List[SignatureIntervention]:
        """
        Liste les signatures d'une intervention.

        Args:
            intervention_id: ID de l'intervention.

        Returns:
            Liste des signatures de l'intervention.
        """
        return self._repository.list_by_intervention(intervention_id)

    def has_all_signatures(self, intervention_id: int) -> dict:
        """
        Verifie si toutes les signatures sont presentes.

        Args:
            intervention_id: ID de l'intervention.

        Returns:
            Dictionnaire avec les flags has_signature_client,
            has_all_signatures_techniciens et complete.
        """
        has_client = self._repository.has_signature_client(intervention_id)
        has_all_tech = self._repository.has_all_signatures_techniciens(
            intervention_id
        )

        return {
            "has_signature_client": has_client,
            "has_all_signatures_techniciens": has_all_tech,
            "complete": has_client and has_all_tech,
        }

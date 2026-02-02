"""Implementation SQLAlchemy du repository SignatureDevis.

DEV-14: Signature electronique client.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ...domain.entities.signature_devis import SignatureDevis
from ...domain.value_objects.type_signature import TypeSignature
from ...domain.repositories.signature_devis_repository import SignatureDevisRepository
from .models import SignatureDevisModel


class SQLAlchemySignatureDevisRepository(SignatureDevisRepository):
    """Implementation SQLAlchemy du repository SignatureDevis."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: SignatureDevisModel) -> SignatureDevis:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite SignatureDevis correspondante.
        """
        return SignatureDevis(
            id=model.id,
            devis_id=model.devis_id,
            type_signature=TypeSignature(model.type_signature),
            signataire_nom=model.signataire_nom,
            signataire_email=model.signataire_email,
            signataire_telephone=model.signataire_telephone,
            signature_data=model.signature_data,
            ip_adresse=model.ip_adresse,
            user_agent=model.user_agent,
            horodatage=model.horodatage,
            hash_document=model.hash_document,
            valide=model.valide,
            revoquee_at=model.revoquee_at,
            revoquee_par=model.revoquee_par,
            motif_revocation=model.motif_revocation,
            created_at=model.created_at or datetime.utcnow(),
        )

    def _update_model(
        self, model: SignatureDevisModel, signature: SignatureDevis
    ) -> None:
        """Met a jour les champs du modele depuis l'entite.

        Seuls les champs modifiables sont mis a jour (revocation).
        Les donnees de signature originales sont immuables.

        Args:
            model: Le modele SQLAlchemy a mettre a jour.
            signature: L'entite SignatureDevis source.
        """
        model.valide = signature.valide
        model.revoquee_at = signature.revoquee_at
        model.revoquee_par = signature.revoquee_par
        model.motif_revocation = signature.motif_revocation

    def find_by_id(self, signature_id: int) -> Optional[SignatureDevis]:
        """Trouve une signature electronique par son ID.

        Args:
            signature_id: L'ID de la signature.

        Returns:
            La signature ou None si non trouvee.
        """
        model = (
            self._session.query(SignatureDevisModel)
            .filter(SignatureDevisModel.id == signature_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_devis_id(self, devis_id: int) -> Optional[SignatureDevis]:
        """Trouve la signature electronique associee a un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            La signature ou None si non trouvee.
        """
        model = (
            self._session.query(SignatureDevisModel)
            .filter(SignatureDevisModel.devis_id == devis_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, signature: SignatureDevis) -> SignatureDevis:
        """Persiste une signature electronique (creation ou mise a jour).

        Args:
            signature: La signature a persister.

        Returns:
            La signature avec son ID attribue.
        """
        if signature.id:
            model = (
                self._session.query(SignatureDevisModel)
                .filter(SignatureDevisModel.id == signature.id)
                .first()
            )
            if model:
                self._update_model(model, signature)
        else:
            model = SignatureDevisModel(
                devis_id=signature.devis_id,
                type_signature=signature.type_signature.value,
                signataire_nom=signature.signataire_nom,
                signataire_email=signature.signataire_email,
                signataire_telephone=signature.signataire_telephone,
                signature_data=signature.signature_data,
                ip_adresse=signature.ip_adresse,
                user_agent=signature.user_agent,
                horodatage=signature.horodatage,
                hash_document=signature.hash_document,
                valide=signature.valide,
                revoquee_at=signature.revoquee_at,
                revoquee_par=signature.revoquee_par,
                motif_revocation=signature.motif_revocation,
                created_at=signature.created_at or datetime.utcnow(),
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def delete(self, signature_id: int) -> bool:
        """Supprime une signature electronique.

        Args:
            signature_id: L'ID de la signature a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        model = (
            self._session.query(SignatureDevisModel)
            .filter(SignatureDevisModel.id == signature_id)
            .first()
        )
        if not model:
            return False

        self._session.delete(model)
        self._session.flush()
        return True

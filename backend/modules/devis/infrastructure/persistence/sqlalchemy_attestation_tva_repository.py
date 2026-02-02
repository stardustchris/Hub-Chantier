"""Implementation SQLAlchemy du repository AttestationTVA.

DEV-23: Generation attestation TVA reglementaire.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from ...domain.entities.attestation_tva import AttestationTVA
from ...domain.repositories.attestation_tva_repository import AttestationTVARepository
from .models import AttestationTVAModel


class SQLAlchemyAttestationTVARepository(AttestationTVARepository):
    """Implementation SQLAlchemy du repository AttestationTVA."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: AttestationTVAModel) -> AttestationTVA:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite AttestationTVA correspondante.
        """
        return AttestationTVA(
            id=model.id,
            devis_id=model.devis_id,
            type_cerfa=model.type_cerfa,
            taux_tva=float(model.taux_tva),
            nom_client=model.nom_client,
            adresse_client=model.adresse_client,
            telephone_client=model.telephone_client,
            adresse_immeuble=model.adresse_immeuble,
            nature_immeuble=model.nature_immeuble,
            date_construction_plus_2ans=model.date_construction_plus_2ans,
            description_travaux=model.description_travaux,
            nature_travaux=model.nature_travaux,
            atteste_par=model.atteste_par or "",
            date_attestation=model.date_attestation,
            generee_at=model.generee_at,
            created_at=model.created_at or datetime.utcnow(),
            updated_at=model.updated_at or datetime.utcnow(),
        )

    def _update_model(
        self, model: AttestationTVAModel, attestation: AttestationTVA
    ) -> None:
        """Met a jour les champs du modele depuis l'entite.

        Args:
            model: Le modele SQLAlchemy a mettre a jour.
            attestation: L'entite AttestationTVA source.
        """
        model.type_cerfa = attestation.type_cerfa
        model.taux_tva = attestation.taux_tva
        model.nom_client = attestation.nom_client
        model.adresse_client = attestation.adresse_client
        model.telephone_client = attestation.telephone_client
        model.adresse_immeuble = attestation.adresse_immeuble
        model.nature_immeuble = attestation.nature_immeuble
        model.date_construction_plus_2ans = attestation.date_construction_plus_2ans
        model.description_travaux = attestation.description_travaux
        model.nature_travaux = attestation.nature_travaux
        model.atteste_par = attestation.atteste_par
        model.date_attestation = attestation.date_attestation
        model.generee_at = attestation.generee_at
        model.updated_at = datetime.utcnow()

    def find_by_id(self, attestation_id: int) -> Optional[AttestationTVA]:
        """Trouve une attestation TVA par son ID.

        Args:
            attestation_id: L'ID de l'attestation.

        Returns:
            L'attestation TVA ou None si non trouvee.
        """
        model = (
            self._session.query(AttestationTVAModel)
            .filter(AttestationTVAModel.id == attestation_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_devis_id(self, devis_id: int) -> Optional[AttestationTVA]:
        """Trouve l'attestation TVA associee a un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            L'attestation TVA ou None si non trouvee.
        """
        model = (
            self._session.query(AttestationTVAModel)
            .filter(AttestationTVAModel.devis_id == devis_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def save(self, attestation: AttestationTVA) -> AttestationTVA:
        """Persiste une attestation TVA (creation ou mise a jour).

        Args:
            attestation: L'attestation TVA a persister.

        Returns:
            L'attestation avec son ID attribue.
        """
        if attestation.id:
            model = (
                self._session.query(AttestationTVAModel)
                .filter(AttestationTVAModel.id == attestation.id)
                .first()
            )
            if model:
                self._update_model(model, attestation)
        else:
            model = AttestationTVAModel(
                devis_id=attestation.devis_id,
                type_cerfa=attestation.type_cerfa,
                taux_tva=attestation.taux_tva,
                nom_client=attestation.nom_client,
                adresse_client=attestation.adresse_client,
                telephone_client=attestation.telephone_client,
                adresse_immeuble=attestation.adresse_immeuble,
                nature_immeuble=attestation.nature_immeuble,
                date_construction_plus_2ans=attestation.date_construction_plus_2ans,
                description_travaux=attestation.description_travaux,
                nature_travaux=attestation.nature_travaux,
                atteste_par=attestation.atteste_par,
                date_attestation=attestation.date_attestation,
                generee_at=attestation.generee_at,
                created_at=attestation.created_at or datetime.utcnow(),
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def delete(self, attestation_id: int) -> bool:
        """Supprime une attestation TVA.

        Args:
            attestation_id: L'ID de l'attestation a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        model = (
            self._session.query(AttestationTVAModel)
            .filter(AttestationTVAModel.id == attestation_id)
            .first()
        )
        if not model:
            return False

        self._session.delete(model)
        self._session.flush()
        return True

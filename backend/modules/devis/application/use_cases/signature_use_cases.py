"""Use Cases pour la signature electronique de devis.

DEV-14: Signature electronique client.
Signature simple conforme eIDAS avec tracabilite complete.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional

from ...domain.entities.signature_devis import (
    SignatureDevis,
    SignatureDevisValidationError,
)
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects import StatutDevis
from ...domain.value_objects.type_signature import TypeSignature
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.signature_devis_repository import SignatureDevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.signature_dtos import SignatureCreateDTO, SignatureDTO, VerificationSignatureDTO


# Statuts autorisant la signature
STATUTS_SIGNABLES = {
    StatutDevis.ENVOYE,
    StatutDevis.VU,
    StatutDevis.EN_NEGOCIATION,
}


class SignatureNotFoundError(Exception):
    """Erreur levee quand une signature n'est pas trouvee."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        self.message = f"Aucune signature trouvee pour le devis {devis_id}"
        super().__init__(self.message)


class DevisNonSignableError(Exception):
    """Erreur levee quand un devis ne peut pas etre signe."""

    def __init__(self, devis_id: int, statut: str):
        self.devis_id = devis_id
        self.statut = statut
        self.message = (
            f"Le devis {devis_id} ne peut pas etre signe en statut '{statut}'. "
            f"Statuts autorises: envoye, vu, en_negociation."
        )
        super().__init__(self.message)


class DevisDejaSigneError(Exception):
    """Erreur levee quand un devis est deja signe."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        self.message = f"Le devis {devis_id} possede deja une signature"
        super().__init__(self.message)


def _calculer_hash_devis(devis: "Devis") -> str:
    """Calcule le hash SHA-512 des donnees du devis pour preuve d'integrite.

    Le hash est calcule sur un ensemble determine de champs du devis
    pour garantir que le document n'a pas ete modifie apres signature.

    Args:
        devis: L'entite Devis.

    Returns:
        Hash SHA-512 en hexadecimal (128 caracteres).
    """
    donnees = {
        "numero": devis.numero,
        "client_nom": devis.client_nom,
        "client_adresse": devis.client_adresse,
        "client_email": devis.client_email,
        "objet": devis.objet,
        "montant_total_ht": str(devis.montant_total_ht),
        "montant_total_ttc": str(devis.montant_total_ttc),
        "taux_marge_global": str(devis.taux_marge_global),
        "taux_tva_defaut": str(devis.taux_tva_defaut),
        "date_validite": (
            devis.date_validite.isoformat() if devis.date_validite else None
        ),
    }
    contenu = json.dumps(donnees, sort_keys=True, ensure_ascii=False)
    return hashlib.sha512(contenu.encode("utf-8")).hexdigest()


class SignerDevisUseCase:
    """Signe un devis electroniquement.

    DEV-14: Verifie le statut signable, cree la signature,
    passe le devis en 'accepte', journalise.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        signature_repository: SignatureDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._signature_repository = signature_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, dto: SignatureCreateDTO
    ) -> SignatureDTO:
        """Signe un devis electroniquement.

        Args:
            devis_id: L'ID du devis a signer.
            dto: Les donnees de signature.

        Returns:
            Le DTO de la signature creee.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisNonSignableError: Si le devis n'est pas dans un statut signable.
            DevisDejaSigneError: Si le devis est deja signe.
            SignatureDevisValidationError: Si les donnees de signature sont invalides.
        """
        from .devis_use_cases import DevisNotFoundError

        # 1. Recuperer le devis
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # 2. Verifier le statut signable
        if devis.statut not in STATUTS_SIGNABLES:
            raise DevisNonSignableError(devis_id, devis.statut.value)

        # 3. Verifier qu'il n'y a pas deja une signature
        signature_existante = self._signature_repository.find_by_devis_id(devis_id)
        if signature_existante:
            raise DevisDejaSigneError(devis_id)

        # 4. Valider le type de signature
        try:
            type_sig = TypeSignature(dto.type_signature)
        except ValueError:
            raise SignatureDevisValidationError(
                f"Type de signature invalide: {dto.type_signature}. "
                f"Valeurs autorisees: dessin_tactile, upload_scan, nom_prenom."
            )

        # 5. Calculer le hash du document
        hash_document = _calculer_hash_devis(devis)

        # 6. Creer l'entite signature
        horodatage = datetime.utcnow()
        signature = SignatureDevis(
            devis_id=devis_id,
            type_signature=type_sig,
            signataire_nom=dto.signataire_nom,
            signataire_email=dto.signataire_email,
            signataire_telephone=dto.signataire_telephone,
            signature_data=dto.signature_data,
            ip_adresse=dto.ip_adresse,
            user_agent=dto.user_agent,
            horodatage=horodatage,
            hash_document=hash_document,
            valide=True,
            created_at=horodatage,
        )

        # 7. Persister la signature
        signature = self._signature_repository.save(signature)

        # 8. Passer le devis en statut 'accepte'
        devis.accepter()
        self._devis_repository.save(devis)

        # 9. Journaliser
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="signature_client",
                details_json={
                    "message": (
                        f"Devis signe electroniquement par {dto.signataire_nom} "
                        f"({dto.signataire_email})"
                    ),
                    "type_signature": dto.type_signature,
                    "signataire_nom": dto.signataire_nom,
                    "signataire_email": dto.signataire_email,
                    "ip_adresse": dto.ip_adresse,
                    "horodatage": horodatage.isoformat(),
                    "hash_document": hash_document,
                },
                auteur_id=None,
                created_at=horodatage,
            )
        )

        return SignatureDTO.from_entity(signature)


class GetSignatureUseCase:
    """Recupere la signature d'un devis.

    DEV-14: Consultation de la signature electronique.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        signature_repository: SignatureDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._signature_repository = signature_repository

    def execute(self, devis_id: int) -> SignatureDTO:
        """Recupere la signature d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le DTO de la signature.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            SignatureNotFoundError: Si aucune signature n'existe.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        signature = self._signature_repository.find_by_devis_id(devis_id)
        if not signature:
            raise SignatureNotFoundError(devis_id)

        return SignatureDTO.from_entity(signature)


class RevoquerSignatureUseCase:
    """Revoque la signature d'un devis (admin only).

    DEV-14: Revocation de signature - remet le devis en statut 'en_negociation'.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        signature_repository: SignatureDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._signature_repository = signature_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, motif: str, revoque_par: int
    ) -> SignatureDTO:
        """Revoque la signature d'un devis.

        Args:
            devis_id: L'ID du devis.
            motif: Le motif de la revocation (obligatoire).
            revoque_par: L'ID de l'utilisateur admin qui revoque.

        Returns:
            Le DTO de la signature revoquee.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            SignatureNotFoundError: Si aucune signature n'existe.
            SignatureDevisValidationError: Si la signature est deja revoquee.
        """
        from .devis_use_cases import DevisNotFoundError

        # 1. Recuperer le devis
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # 2. Recuperer la signature
        signature = self._signature_repository.find_by_devis_id(devis_id)
        if not signature:
            raise SignatureNotFoundError(devis_id)

        # 3. Revoquer la signature (leve une erreur si deja revoquee)
        signature.revoquer(par=revoque_par, motif=motif)

        # 4. Persister la signature revoquee
        signature = self._signature_repository.save(signature)

        # 5. Remettre le devis en statut 'en_negociation'
        #    Utilise la methode dediee du domaine pour la revocation d'acceptation.
        devis.revoquer_acceptation()
        self._devis_repository.save(devis)

        # 6. Journaliser
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="revocation_signature",
                details_json={
                    "message": f"Signature revoquee - Motif: {motif.strip()}",
                    "revoque_par": revoque_par,
                    "motif": motif.strip(),
                    "signature_id": signature.id,
                },
                auteur_id=revoque_par,
                created_at=datetime.utcnow(),
            )
        )

        return SignatureDTO.from_entity(signature)


class VerifierSignatureUseCase:
    """Verifie la validite d'une signature electronique.

    DEV-14: Verification de l'integrite du document signe
    (hash SHA-512 compare entre signature et document actuel).
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        signature_repository: SignatureDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._signature_repository = signature_repository

    def execute(self, devis_id: int) -> VerificationSignatureDTO:
        """Verifie la validite de la signature d'un devis.

        Compare le hash du document actuel avec le hash enregistre
        lors de la signature pour detecter toute modification.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le DTO de verification avec le resultat.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        # 1. Recuperer le devis
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # 2. Recuperer la signature
        signature = self._signature_repository.find_by_devis_id(devis_id)
        if not signature:
            return VerificationSignatureDTO(
                devis_id=devis_id,
                signature_id=None,
                est_signee=False,
                est_valide=False,
                hash_document_actuel=None,
                hash_document_signature=None,
                integrite_document=False,
                message="Ce devis n'a pas ete signe electroniquement.",
            )

        # 3. Calculer le hash actuel du document
        hash_actuel = _calculer_hash_devis(devis)

        # 4. Comparer les hash
        integrite_ok = hash_actuel == signature.hash_document

        # 5. Determiner le message
        if not signature.est_valide:
            message = "La signature a ete revoquee."
        elif not integrite_ok:
            message = (
                "ATTENTION: Le document a ete modifie depuis la signature. "
                "L'integrite du document n'est plus garantie."
            )
        else:
            message = (
                "La signature est valide et le document est intact "
                "(hash SHA-512 verifie)."
            )

        return VerificationSignatureDTO(
            devis_id=devis_id,
            signature_id=signature.id,
            est_signee=True,
            est_valide=signature.est_valide,
            hash_document_actuel=hash_actuel,
            hash_document_signature=signature.hash_document,
            integrite_document=integrite_ok,
            message=message,
        )

"""Use Cases pour la gestion des devis.

DEV-03: Creation devis structure.
DEV-18: Historique modifications (avant/apres).
DEV-TVA: Ventilation TVA multi-taux et mention TVA reduite.
"""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable, Optional, Protocol, Tuple

from ...domain.entities.devis import Devis
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects import StatutDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.devis_dtos import (
    DevisCreateDTO,
    DevisUpdateDTO,
    DevisDTO,
    DevisDetailDTO,
    DevisListDTO,
    VentilationTVADTO,
    MENTION_TVA_REDUITE,
)
from ..dtos.lot_dtos import LotDevisDTO
from ..dtos.ligne_dtos import LigneDevisDTO
from ..dtos.debourse_dtos import DebourseDetailDTO
from ...domain.value_objects.taux_tva import TauxTVA

# DEV-TVA: Type pour le resolveur de contexte TVA chantier (evite couplage inter-modules)
# Signature: (chantier_ref) -> (type_travaux, batiment_plus_2ans, usage_habitation) ou None
ChantierTVAResolver = Callable[[str], Optional[Tuple[Optional[str], Optional[bool], Optional[bool]]]]


def _serialize_for_journal(value: Any) -> Optional[str]:
    """Serialise une valeur pour stockage dans le journal (DEV-18).

    Convertit les types Python en strings comparables et stockables en JSON.

    Args:
        value: La valeur a serialiser.

    Returns:
        La representation string de la valeur, ou None.
    """
    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return str(value)
    return str(value)


class DevisNotFoundError(Exception):
    """Erreur levee quand un devis n'est pas trouve."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        super().__init__(f"Devis {devis_id} non trouve")


class DevisNotModifiableError(Exception):
    """Erreur levee quand on essaie de modifier un devis non modifiable."""

    def __init__(self, devis_id: int, statut: StatutDevis):
        self.devis_id = devis_id
        self.statut = statut
        super().__init__(
            f"Le devis {devis_id} est en statut '{statut.label}' et ne peut pas etre modifie"
        )


class CreateDevisUseCase:
    """Use case pour creer un devis.

    DEV-03: Creation en statut Brouillon avec numero auto-genere.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
        chantier_tva_resolver: Optional[ChantierTVAResolver] = None,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository
        self._chantier_tva_resolver = chantier_tva_resolver

    def execute(self, dto: DevisCreateDTO, created_by: int) -> DevisDTO:
        """Cree un nouveau devis en statut Brouillon.

        Args:
            dto: Les donnees du devis a creer.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO du devis cree.
        """
        numero = self._devis_repository.generate_numero()

        # DEV-TVA: Pre-remplissage du taux TVA par defaut selon le contexte chantier
        taux_tva_defaut = dto.taux_tva_defaut
        if dto.chantier_ref and self._chantier_tva_resolver:
            # Utiliser le taux du DTO seulement si l'utilisateur l'a explicitement change
            # (i.e. different du defaut 20%)
            if taux_tva_defaut == Decimal("20"):
                contexte = self._chantier_tva_resolver(dto.chantier_ref)
                if contexte:
                    type_travaux, bat_2ans, usage_hab = contexte
                    taux_tva_defaut = TauxTVA.taux_defaut_pour_chantier(
                        type_travaux, bat_2ans, usage_hab,
                    )

        devis = Devis(
            numero=numero,
            client_nom=dto.client_nom,
            objet=dto.objet,
            statut=StatutDevis.BROUILLON,
            chantier_ref=dto.chantier_ref,
            client_adresse=dto.client_adresse,
            client_email=dto.client_email,
            client_telephone=dto.client_telephone,
            date_creation=date.today(),
            date_validite=dto.date_validite,
            taux_tva_defaut=taux_tva_defaut,
            taux_marge_global=dto.taux_marge_global,
            taux_marge_moe=dto.taux_marge_moe,
            taux_marge_materiaux=dto.taux_marge_materiaux,
            taux_marge_sous_traitance=dto.taux_marge_sous_traitance,
            taux_marge_materiel=dto.taux_marge_materiel,
            taux_marge_deplacement=dto.taux_marge_deplacement,
            coefficient_frais_generaux=dto.coefficient_frais_generaux,
            retenue_garantie_pct=dto.retenue_garantie_pct,
            notes=dto.notes,
            # Generateur de devis - champs complementaires
            acompte_pct=dto.acompte_pct,
            echeance=dto.echeance,
            moyens_paiement=dto.moyens_paiement,
            date_visite=dto.date_visite,
            date_debut_travaux=dto.date_debut_travaux,
            duree_estimee_jours=dto.duree_estimee_jours,
            notes_bas_page=dto.notes_bas_page,
            nom_interne=dto.nom_interne,
            commercial_id=dto.commercial_id,
            conducteur_id=dto.conducteur_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by,
        )

        devis = self._devis_repository.save(devis)

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis.id,
                action="creation",
                details_json={"message": f"Creation du devis {numero} - {dto.objet}"},
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return DevisDTO.from_entity(devis)


class UpdateDevisUseCase:
    """Use case pour mettre a jour un devis (modifiable uniquement)."""

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, dto: DevisUpdateDTO, updated_by: int
    ) -> DevisDTO:
        """Met a jour un devis.

        Args:
            devis_id: L'ID du devis a mettre a jour.
            dto: Les donnees a mettre a jour.
            updated_by: L'ID de l'utilisateur.

        Returns:
            Le DTO du devis mis a jour.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisNotModifiableError: Si le devis n'est pas modifiable.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        if not devis.est_modifiable:
            raise DevisNotModifiableError(devis_id, devis.statut)

        # DEV-18: Capturer les valeurs avant/apres pour chaque champ modifie
        changements = {}  # champ -> {"avant": old, "apres": new}

        champs_a_verifier = [
            "client_nom", "objet", "chantier_ref", "client_adresse",
            "client_email", "client_telephone", "date_validite",
            "taux_tva_defaut", "taux_marge_global", "taux_marge_moe",
            "taux_marge_materiaux", "taux_marge_sous_traitance",
            "taux_marge_materiel", "taux_marge_deplacement",
            "coefficient_frais_generaux", "retenue_garantie_pct",
            "notes", "acompte_pct", "echeance", "moyens_paiement",
            "date_visite", "date_debut_travaux", "duree_estimee_jours",
            "notes_bas_page", "nom_interne", "commercial_id", "conducteur_id",
        ]

        for champ in champs_a_verifier:
            nouvelle_valeur = getattr(dto, champ, None)
            if nouvelle_valeur is not None:
                ancienne_valeur = getattr(devis, champ, None)
                # Serialiser pour comparaison et stockage JSON
                ancien_str = _serialize_for_journal(ancienne_valeur)
                nouveau_str = _serialize_for_journal(nouvelle_valeur)
                if ancien_str != nouveau_str:
                    changements[champ] = {
                        "avant": ancien_str,
                        "apres": nouveau_str,
                    }
                setattr(devis, champ, nouvelle_valeur)

        devis.updated_at = datetime.utcnow()
        devis = self._devis_repository.save(devis)

        # DEV-18: Journal avec detail avant/apres pour chaque champ
        if changements:
            self._journal_repository.save(
                JournalDevis(
                    devis_id=devis.id,
                    action="modification",
                    details_json={
                        "message": f"Modification des champs: {', '.join(changements.keys())}",
                        "type_modification": "update_devis",
                        "changements": changements,
                    },
                    auteur_id=updated_by,
                    created_at=datetime.utcnow(),
                )
            )

        return DevisDTO.from_entity(devis)


class GetDevisUseCase:
    """Use case pour recuperer un devis avec ses details complets."""

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository

    def execute(self, devis_id: int) -> DevisDetailDTO:
        """Recupere un devis avec ses lots, lignes et debourses.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        lots = self._lot_repository.find_by_devis(devis_id)
        lot_dtos = []
        ventilation: dict[str, Decimal] = {}  # taux -> base_ht

        for lot in lots:
            lignes = self._ligne_repository.find_by_lot(lot.id)
            ligne_dtos = []
            for ligne in lignes:
                debourses = self._debourse_repository.find_by_ligne(ligne.id)
                debourse_dtos = [DebourseDetailDTO.from_entity(d) for d in debourses]
                ligne_dtos.append(LigneDevisDTO.from_entity(ligne, debourse_dtos))
                # DEV-TVA: Accumuler base HT par taux
                taux_key = str(ligne.taux_tva)
                ventilation[taux_key] = ventilation.get(taux_key, Decimal("0")) + ligne.total_ht
            lot_dtos.append(LotDevisDTO.from_entity(lot, ligne_dtos))

        dto = DevisDetailDTO.from_entity(devis, lot_dtos)

        # DEV-TVA: Construire ventilation TVA triee par taux
        dto.ventilation_tva = sorted(
            [
                VentilationTVADTO(
                    taux=taux,
                    base_ht=str(base_ht.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                    montant_tva=str(
                        (base_ht * Decimal(taux) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    ),
                )
                for taux, base_ht in ventilation.items()
            ],
            key=lambda v: Decimal(v.taux),
        )

        # DEV-TVA: Mention legale si taux reduit detecte (reforme 01/2025)
        has_taux_reduit = any(Decimal(t) < Decimal("20") for t in ventilation.keys())
        if has_taux_reduit:
            dto.mention_tva_reduite = MENTION_TVA_REDUITE

        return dto


class ListDevisUseCase:
    """Use case pour lister les devis avec pagination."""

    def __init__(self, devis_repository: DevisRepository):
        self._devis_repository = devis_repository

    def execute(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> DevisListDTO:
        """Liste les devis avec pagination."""
        devis_list = self._devis_repository.find_all(limit=limit, offset=offset)
        total = self._devis_repository.count()
        return DevisListDTO(
            items=[DevisDTO.from_entity(d) for d in devis_list],
            total=total,
            limit=limit,
            offset=offset,
        )


class DeleteDevisUseCase:
    """Use case pour supprimer un devis (brouillon uniquement, soft delete)."""

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, deleted_by: int) -> None:
        """Supprime un devis en statut brouillon uniquement.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisNotModifiableError: Si le devis n'est pas en brouillon.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # DEV-08: Les versions figees ne peuvent pas etre supprimees
        if devis.version_figee:
            from ...domain.entities.devis import DevisValidationError
            raise DevisValidationError(
                f"Le devis {devis.numero} est fige et ne peut pas etre supprime"
            )

        if devis.statut != StatutDevis.BROUILLON:
            raise DevisNotModifiableError(devis_id, devis.statut)

        self._devis_repository.delete(devis_id, deleted_by=deleted_by)

        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="suppression",
                details_json={"message": f"Suppression du devis {devis.numero}"},
                auteur_id=deleted_by,
                created_at=datetime.utcnow(),
            )
        )

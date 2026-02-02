"""Use Cases pour la gestion des versions de devis.

DEV-08: Variantes et revisions - Creation de revisions, variantes,
comparaisons et gel de versions.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from ...domain.entities.devis import Devis, DevisValidationError
from ...domain.entities.lot_devis import LotDevis
from ...domain.entities.ligne_devis import LigneDevis
from ...domain.entities.debourse_detail import DebourseDetail
from ...domain.entities.comparatif_devis import ComparatifDevis
from ...domain.entities.comparatif_ligne import ComparatifLigne
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects import StatutDevis
from ...domain.value_objects.type_version import TypeVersion
from ...domain.value_objects.type_ecart import TypeEcart
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.lot_devis_repository import LotDevisRepository
from ...domain.repositories.ligne_devis_repository import LigneDevisRepository
from ...domain.repositories.debourse_detail_repository import DebourseDetailRepository
from ...domain.repositories.comparatif_repository import ComparatifRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.version_dtos import (
    CreerRevisionDTO,
    CreerVarianteDTO,
    FigerVersionDTO,
    VersionDTO,
    ComparatifDTO,
)
from .devis_use_cases import DevisNotFoundError


# ─────────────────────────────────────────────────────────────────────────────
# Labels de variantes valides
# ─────────────────────────────────────────────────────────────────────────────

LABELS_VARIANTES_VALIDES = {
    "ECO": "Economique",
    "STD": "Standard",
    "PREM": "Premium",
    "ALT": "Alternative",
}


class VersionFigeeError(Exception):
    """Erreur levee quand on essaie de modifier une version figee."""

    def __init__(self, devis_id: int):
        self.devis_id = devis_id
        super().__init__(
            f"Le devis {devis_id} est fige et ne peut pas etre modifie"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers internes
# ─────────────────────────────────────────────────────────────────────────────

def _copie_profonde_devis(
    devis_source: Devis,
    lot_repository: LotDevisRepository,
    ligne_repository: LigneDevisRepository,
    debourse_repository: DebourseDetailRepository,
    devis_repository: DevisRepository,
    nouveau_numero: str,
    type_version: TypeVersion,
    devis_parent_id: int,
    numero_version: int,
    label_variante: Optional[str],
    commentaire: Optional[str],
    created_by: int,
) -> Devis:
    """Effectue une copie profonde atomique d'un devis avec lots, lignes et debourses.

    Args:
        devis_source: Le devis a copier.
        lot_repository: Repository des lots.
        ligne_repository: Repository des lignes.
        debourse_repository: Repository des debourses.
        devis_repository: Repository des devis.
        nouveau_numero: Le numero du nouveau devis.
        type_version: Le type de version (revision/variante).
        devis_parent_id: L'ID du devis parent (original).
        numero_version: Le numero de version.
        label_variante: Le label de la variante (None si revision).
        commentaire: Le commentaire de version.
        created_by: L'ID de l'utilisateur createur.

    Returns:
        Le nouveau devis cree avec toute sa structure.
    """
    now = datetime.utcnow()

    # 1. Creer le nouveau devis (copie des champs)
    nouveau_devis = Devis(
        numero=nouveau_numero,
        client_nom=devis_source.client_nom,
        client_adresse=devis_source.client_adresse,
        client_telephone=devis_source.client_telephone,
        client_email=devis_source.client_email,
        chantier_ref=devis_source.chantier_ref,
        objet=devis_source.objet,
        date_creation=date.today(),
        date_validite=devis_source.date_validite,
        statut=StatutDevis.BROUILLON,
        montant_total_ht=devis_source.montant_total_ht,
        montant_total_ttc=devis_source.montant_total_ttc,
        taux_marge_global=devis_source.taux_marge_global,
        coefficient_frais_generaux=devis_source.coefficient_frais_generaux,
        taux_tva_defaut=devis_source.taux_tva_defaut,
        retenue_garantie_pct=devis_source.retenue_garantie_pct,
        taux_marge_moe=devis_source.taux_marge_moe,
        taux_marge_materiaux=devis_source.taux_marge_materiaux,
        taux_marge_sous_traitance=devis_source.taux_marge_sous_traitance,
        taux_marge_materiel=devis_source.taux_marge_materiel,
        taux_marge_deplacement=devis_source.taux_marge_deplacement,
        notes=devis_source.notes,
        conditions_generales=devis_source.conditions_generales,
        commercial_id=devis_source.commercial_id,
        conducteur_id=devis_source.conducteur_id,
        created_by=created_by,
        created_at=now,
        updated_at=now,
        # Versioning
        devis_parent_id=devis_parent_id,
        numero_version=numero_version,
        type_version=type_version,
        label_variante=label_variante,
        version_commentaire=commentaire,
        version_figee=False,
    )

    nouveau_devis = devis_repository.save(nouveau_devis)

    # 2. Copier les lots (avec mapping ancien_id -> nouveau_id pour les parents)
    lots_source = lot_repository.find_by_devis(devis_source.id)
    lot_id_mapping: Dict[int, int] = {}

    # Trier pour traiter les parents avant les enfants
    lots_racine = [l for l in lots_source if l.parent_id is None]
    lots_enfants = [l for l in lots_source if l.parent_id is not None]

    for lot_source in lots_racine:
        nouveau_lot = LotDevis(
            devis_id=nouveau_devis.id,
            code_lot=lot_source.code_lot,
            libelle=lot_source.libelle,
            ordre=lot_source.ordre,
            taux_marge_lot=lot_source.taux_marge_lot,
            parent_id=None,
            montant_debourse_ht=lot_source.montant_debourse_ht,
            montant_vente_ht=lot_source.montant_vente_ht,
            montant_vente_ttc=lot_source.montant_vente_ttc,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )
        nouveau_lot = lot_repository.save(nouveau_lot)
        lot_id_mapping[lot_source.id] = nouveau_lot.id

        # Copier les lignes de ce lot
        _copier_lignes_lot(
            lot_source.id,
            nouveau_lot.id,
            ligne_repository,
            debourse_repository,
            created_by,
            now,
        )

    for lot_source in lots_enfants:
        nouveau_parent_id = lot_id_mapping.get(lot_source.parent_id)
        nouveau_lot = LotDevis(
            devis_id=nouveau_devis.id,
            code_lot=lot_source.code_lot,
            libelle=lot_source.libelle,
            ordre=lot_source.ordre,
            taux_marge_lot=lot_source.taux_marge_lot,
            parent_id=nouveau_parent_id,
            montant_debourse_ht=lot_source.montant_debourse_ht,
            montant_vente_ht=lot_source.montant_vente_ht,
            montant_vente_ttc=lot_source.montant_vente_ttc,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )
        nouveau_lot = lot_repository.save(nouveau_lot)
        lot_id_mapping[lot_source.id] = nouveau_lot.id

        _copier_lignes_lot(
            lot_source.id,
            nouveau_lot.id,
            ligne_repository,
            debourse_repository,
            created_by,
            now,
        )

    return nouveau_devis


def _copier_lignes_lot(
    lot_source_id: int,
    lot_cible_id: int,
    ligne_repository: LigneDevisRepository,
    debourse_repository: DebourseDetailRepository,
    created_by: int,
    now: datetime,
) -> None:
    """Copie toutes les lignes et debourses d'un lot source vers un lot cible.

    Args:
        lot_source_id: L'ID du lot source.
        lot_cible_id: L'ID du lot cible.
        ligne_repository: Repository des lignes.
        debourse_repository: Repository des debourses.
        created_by: L'ID de l'utilisateur createur.
        now: Timestamp actuel.
    """
    lignes_source = ligne_repository.find_by_lot(lot_source_id)
    for ligne_source in lignes_source:
        nouvelle_ligne = LigneDevis(
            lot_devis_id=lot_cible_id,
            article_id=ligne_source.article_id,
            libelle=ligne_source.libelle,
            unite=ligne_source.unite,
            quantite=ligne_source.quantite,
            prix_unitaire_ht=ligne_source.prix_unitaire_ht,
            taux_marge_ligne=ligne_source.taux_marge_ligne,
            taux_tva=ligne_source.taux_tva,
            ordre=ligne_source.ordre,
            verrouille=False,  # Deverrouiller dans la copie
            total_ht=ligne_source.total_ht,
            montant_ttc=ligne_source.montant_ttc,
            debourse_sec=ligne_source.debourse_sec,
            prix_revient=ligne_source.prix_revient,
            created_at=now,
            updated_at=now,
            created_by=created_by,
        )
        nouvelle_ligne = ligne_repository.save(nouvelle_ligne)

        # Copier les debourses
        debourses_source = debourse_repository.find_by_ligne(ligne_source.id)
        for deb_source in debourses_source:
            nouveau_debourse = DebourseDetail(
                ligne_devis_id=nouvelle_ligne.id,
                type_debourse=deb_source.type_debourse,
                libelle=deb_source.libelle,
                quantite=deb_source.quantite,
                prix_unitaire=deb_source.prix_unitaire,
                metier=deb_source.metier,
                taux_horaire=deb_source.taux_horaire,
                total=deb_source.total,
                created_at=now,
                updated_at=now,
            )
            debourse_repository.save(nouveau_debourse)


def _get_parent_id(devis: Devis) -> int:
    """Retourne l'ID du devis parent (original) de la famille.

    Si le devis est l'original, retourne son propre ID.
    Sinon, retourne le devis_parent_id.

    Args:
        devis: Le devis source.

    Returns:
        L'ID du devis parent (original).
    """
    if devis.devis_parent_id is not None:
        return devis.devis_parent_id
    return devis.id


def _generer_numero_revision(numero_base: str, version: int) -> str:
    """Genere le numero d'une revision.

    Convention: DEV-2026-042-R2

    Args:
        numero_base: Le numero de base (ex: DEV-2026-042).
        version: Le numero de version.

    Returns:
        Le numero de revision.
    """
    # Extraire le numero de base (sans suffixe de version)
    base = numero_base.split("-R")[0].split("-ECO")[0].split("-STD")[0]
    base = base.split("-PREM")[0].split("-ALT")[0]
    return f"{base}-R{version}"


def _generer_numero_variante(numero_base: str, label: str) -> str:
    """Genere le numero d'une variante.

    Convention: DEV-2026-042-ECO

    Args:
        numero_base: Le numero de base (ex: DEV-2026-042).
        label: Le label de la variante (ECO, STD, PREM, ALT).

    Returns:
        Le numero de variante.
    """
    # Extraire le numero de base (sans suffixe de version)
    base = numero_base.split("-R")[0].split("-ECO")[0].split("-STD")[0]
    base = base.split("-PREM")[0].split("-ALT")[0]
    return f"{base}-{label.upper()}"


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases
# ─────────────────────────────────────────────────────────────────────────────

class CreerRevisionUseCase:
    """Use case pour creer une revision d'un devis.

    DEV-08: Copie profonde du devis + lots + lignes + debourses.
    Fige automatiquement la version precedente.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, dto: CreerRevisionDTO, created_by: int
    ) -> VersionDTO:
        """Cree une revision d'un devis existant.

        La version precedente est automatiquement figee.
        La copie est profonde : devis + lots + lignes + debourses.

        Args:
            devis_id: L'ID du devis source.
            dto: Les donnees de la revision.
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de la nouvelle version creee.

        Raises:
            DevisNotFoundError: Si le devis source n'existe pas.
            VersionFigeeError: Si le devis source est deja fige.
        """
        devis_source = self._devis_repository.find_by_id(devis_id)
        if not devis_source:
            raise DevisNotFoundError(devis_id)

        # Determiner le parent (original) de la famille
        parent_id = _get_parent_id(devis_source)

        # Prochain numero de version
        next_version = self._devis_repository.get_next_version_number(parent_id)

        # Generer le numero
        # Utiliser le numero du parent ou du devis source pour la base
        if devis_source.devis_parent_id is not None:
            parent = self._devis_repository.find_by_id(parent_id)
            numero_base = parent.numero if parent else devis_source.numero
        else:
            numero_base = devis_source.numero

        nouveau_numero = _generer_numero_revision(numero_base, next_version)

        # Figer automatiquement la version precedente si pas encore figee
        if not devis_source.version_figee:
            devis_source.figer(created_by)
            self._devis_repository.save(devis_source)

            self._journal_repository.save(
                JournalDevis(
                    devis_id=devis_source.id,
                    action="gel_version",
                    details_json={
                        "message": f"Version figee automatiquement avant creation de la revision {nouveau_numero}"
                    },
                    auteur_id=created_by,
                    created_at=datetime.utcnow(),
                )
            )

        # Copie profonde
        nouveau_devis = _copie_profonde_devis(
            devis_source=devis_source,
            lot_repository=self._lot_repository,
            ligne_repository=self._ligne_repository,
            debourse_repository=self._debourse_repository,
            devis_repository=self._devis_repository,
            nouveau_numero=nouveau_numero,
            type_version=TypeVersion.REVISION,
            devis_parent_id=parent_id,
            numero_version=next_version,
            label_variante=None,
            commentaire=dto.commentaire,
            created_by=created_by,
        )

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=nouveau_devis.id,
                action="creation_revision",
                details_json={
                    "message": f"Revision {nouveau_numero} creee a partir du devis {devis_source.numero}",
                    "devis_source_id": devis_source.id,
                    "numero_version": next_version,
                },
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return VersionDTO.from_entity(nouveau_devis)


class CreerVarianteUseCase:
    """Use case pour creer une variante d'un devis.

    DEV-08: Clone avec label variante (economique/standard/premium).
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        debourse_repository: DebourseDetailRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._debourse_repository = debourse_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, dto: CreerVarianteDTO, created_by: int
    ) -> VersionDTO:
        """Cree une variante d'un devis existant.

        Args:
            devis_id: L'ID du devis source.
            dto: Les donnees de la variante (label obligatoire).
            created_by: L'ID de l'utilisateur createur.

        Returns:
            Le DTO de la nouvelle variante creee.

        Raises:
            DevisNotFoundError: Si le devis source n'existe pas.
            ValueError: Si le label de la variante est invalide.
        """
        if not dto.label_variante or not dto.label_variante.strip():
            raise ValueError("Le label de la variante est obligatoire")

        label = dto.label_variante.strip().upper()
        if label not in LABELS_VARIANTES_VALIDES:
            labels_str = ", ".join(
                f"{k} ({v})" for k, v in LABELS_VARIANTES_VALIDES.items()
            )
            raise ValueError(
                f"Label de variante invalide: '{label}'. "
                f"Labels autorises: {labels_str}"
            )

        devis_source = self._devis_repository.find_by_id(devis_id)
        if not devis_source:
            raise DevisNotFoundError(devis_id)

        parent_id = _get_parent_id(devis_source)
        next_version = self._devis_repository.get_next_version_number(parent_id)

        # Numero base depuis le parent
        if devis_source.devis_parent_id is not None:
            parent = self._devis_repository.find_by_id(parent_id)
            numero_base = parent.numero if parent else devis_source.numero
        else:
            numero_base = devis_source.numero

        nouveau_numero = _generer_numero_variante(numero_base, label)

        # Copie profonde
        nouveau_devis = _copie_profonde_devis(
            devis_source=devis_source,
            lot_repository=self._lot_repository,
            ligne_repository=self._ligne_repository,
            debourse_repository=self._debourse_repository,
            devis_repository=self._devis_repository,
            nouveau_numero=nouveau_numero,
            type_version=TypeVersion.VARIANTE,
            devis_parent_id=parent_id,
            numero_version=next_version,
            label_variante=label,
            commentaire=dto.commentaire,
            created_by=created_by,
        )

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=nouveau_devis.id,
                action="creation_variante",
                details_json={
                    "message": (
                        f"Variante {LABELS_VARIANTES_VALIDES[label]} ({nouveau_numero}) "
                        f"creee a partir du devis {devis_source.numero}"
                    ),
                    "devis_source_id": devis_source.id,
                    "label_variante": label,
                    "numero_version": next_version,
                },
                auteur_id=created_by,
                created_at=datetime.utcnow(),
            )
        )

        return VersionDTO.from_entity(nouveau_devis)


class ListerVersionsUseCase:
    """Use case pour lister toutes les versions/variantes d'un devis.

    DEV-08: Liste la famille complete (original + revisions + variantes).
    """

    def __init__(self, devis_repository: DevisRepository):
        self._devis_repository = devis_repository

    def execute(self, devis_id: int) -> List[VersionDTO]:
        """Liste toutes les versions d'un devis.

        Args:
            devis_id: L'ID du devis (original ou enfant).

        Returns:
            Liste des versions triee par numero_version.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        versions = self._devis_repository.find_versions(devis_id)
        return [VersionDTO.from_entity(v) for v in versions]


class GenererComparatifUseCase:
    """Use case pour generer un comparatif entre deux versions de devis.

    DEV-08: Compare 2 versions, calcule tous les ecarts, persiste le resultat.
    Le matching se fait par (lot_titre, designation) avec article_id prioritaire.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        lot_repository: LotDevisRepository,
        ligne_repository: LigneDevisRepository,
        comparatif_repository: ComparatifRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._lot_repository = lot_repository
        self._ligne_repository = ligne_repository
        self._comparatif_repository = comparatif_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_source_id: int, devis_cible_id: int, genere_par: int
    ) -> ComparatifDTO:
        """Genere un comparatif detaille entre deux versions.

        Args:
            devis_source_id: L'ID du devis source (ancienne version).
            devis_cible_id: L'ID du devis cible (nouvelle version).
            genere_par: L'ID de l'utilisateur qui genere le comparatif.

        Returns:
            Le DTO du comparatif genere.

        Raises:
            DevisNotFoundError: Si l'un des devis n'existe pas.
            ValueError: Si les deux IDs sont identiques.
        """
        if devis_source_id == devis_cible_id:
            raise ValueError(
                "Le devis source et le devis cible doivent etre differents"
            )

        devis_source = self._devis_repository.find_by_id(devis_source_id)
        if not devis_source:
            raise DevisNotFoundError(devis_source_id)

        devis_cible = self._devis_repository.find_by_id(devis_cible_id)
        if not devis_cible:
            raise DevisNotFoundError(devis_cible_id)

        # Collecter les lignes avec leur lot_titre pour le matching
        lignes_source = self._collecter_lignes_avec_lot(devis_source_id)
        lignes_cible = self._collecter_lignes_avec_lot(devis_cible_id)

        # Matching et calcul des ecarts
        comparatif_lignes: List[ComparatifLigne] = []
        nb_ajoutees = 0
        nb_supprimees = 0
        nb_modifiees = 0
        nb_identiques = 0

        # Index des lignes cible pour le matching
        cible_index = self._indexer_lignes(lignes_cible)
        cible_matched: set = set()

        # Parcourir les lignes source
        for lot_titre, designation, article_id, ligne_src in lignes_source:
            cle = self._cle_matching(lot_titre, designation, article_id)
            match = cible_index.get(cle)

            if match is None:
                # Ligne supprimee (presente dans source, absente dans cible)
                cl = ComparatifLigne(
                    comparatif_id=1,  # Sera mis a jour apres save
                    type_ecart=TypeEcart.SUPPRESSION,
                    lot_titre=lot_titre,
                    designation=designation,
                    article_id=article_id,
                    source_quantite=ligne_src.quantite,
                    source_prix_unitaire=ligne_src.prix_unitaire_ht,
                    source_montant_ht=ligne_src.total_ht,
                    source_debourse_sec=ligne_src.debourse_sec,
                    cible_quantite=None,
                    cible_prix_unitaire=None,
                    cible_montant_ht=None,
                    cible_debourse_sec=None,
                    ecart_quantite=Decimal("0") - ligne_src.quantite,
                    ecart_prix_unitaire=Decimal("0") - ligne_src.prix_unitaire_ht,
                    ecart_montant_ht=Decimal("0") - ligne_src.total_ht,
                    ecart_debourse_sec=Decimal("0") - ligne_src.debourse_sec,
                )
                comparatif_lignes.append(cl)
                nb_supprimees += 1
            else:
                cible_matched.add(cle)
                _, _, _, ligne_cbl = match

                # Calculer les ecarts
                ecart_qte = ligne_cbl.quantite - ligne_src.quantite
                ecart_pu = ligne_cbl.prix_unitaire_ht - ligne_src.prix_unitaire_ht
                ecart_ht = ligne_cbl.total_ht - ligne_src.total_ht
                ecart_ds = ligne_cbl.debourse_sec - ligne_src.debourse_sec

                # Determiner si modifie ou identique
                est_identique = (
                    ecart_qte == Decimal("0")
                    and ecart_pu == Decimal("0")
                    and ecart_ht == Decimal("0")
                    and ecart_ds == Decimal("0")
                )

                type_ecart = TypeEcart.IDENTIQUE if est_identique else TypeEcart.MODIFICATION

                cl = ComparatifLigne(
                    comparatif_id=1,
                    type_ecart=type_ecart,
                    lot_titre=lot_titre,
                    designation=designation,
                    article_id=article_id,
                    source_quantite=ligne_src.quantite,
                    source_prix_unitaire=ligne_src.prix_unitaire_ht,
                    source_montant_ht=ligne_src.total_ht,
                    source_debourse_sec=ligne_src.debourse_sec,
                    cible_quantite=ligne_cbl.quantite,
                    cible_prix_unitaire=ligne_cbl.prix_unitaire_ht,
                    cible_montant_ht=ligne_cbl.total_ht,
                    cible_debourse_sec=ligne_cbl.debourse_sec,
                    ecart_quantite=ecart_qte,
                    ecart_prix_unitaire=ecart_pu,
                    ecart_montant_ht=ecart_ht,
                    ecart_debourse_sec=ecart_ds,
                )
                comparatif_lignes.append(cl)

                if est_identique:
                    nb_identiques += 1
                else:
                    nb_modifiees += 1

        # Lignes ajoutees (presentes dans cible, absentes dans source)
        for cle, (lot_titre, designation, article_id, ligne_cbl) in cible_index.items():
            if cle not in cible_matched:
                cl = ComparatifLigne(
                    comparatif_id=1,
                    type_ecart=TypeEcart.AJOUT,
                    lot_titre=lot_titre,
                    designation=designation,
                    article_id=article_id,
                    source_quantite=None,
                    source_prix_unitaire=None,
                    source_montant_ht=None,
                    source_debourse_sec=None,
                    cible_quantite=ligne_cbl.quantite,
                    cible_prix_unitaire=ligne_cbl.prix_unitaire_ht,
                    cible_montant_ht=ligne_cbl.total_ht,
                    cible_debourse_sec=ligne_cbl.debourse_sec,
                    ecart_quantite=ligne_cbl.quantite,
                    ecart_prix_unitaire=ligne_cbl.prix_unitaire_ht,
                    ecart_montant_ht=ligne_cbl.total_ht,
                    ecart_debourse_sec=ligne_cbl.debourse_sec,
                )
                comparatif_lignes.append(cl)
                nb_ajoutees += 1

        # Ecarts globaux
        ecart_montant_ht = devis_cible.montant_total_ht - devis_source.montant_total_ht
        ecart_montant_ttc = devis_cible.montant_total_ttc - devis_source.montant_total_ttc
        ecart_marge_pct = devis_cible.taux_marge_global - devis_source.taux_marge_global

        # Calculer ecart debourse total a partir des lignes
        ecart_debourse = sum(
            (cl.ecart_debourse_sec or Decimal("0")) for cl in comparatif_lignes
        )

        # Creer et persister le comparatif
        comparatif = ComparatifDevis(
            devis_source_id=devis_source_id,
            devis_cible_id=devis_cible_id,
            ecart_montant_ht=ecart_montant_ht,
            ecart_montant_ttc=ecart_montant_ttc,
            ecart_marge_pct=ecart_marge_pct,
            ecart_debourse_total=ecart_debourse,
            nb_lignes_ajoutees=nb_ajoutees,
            nb_lignes_supprimees=nb_supprimees,
            nb_lignes_modifiees=nb_modifiees,
            nb_lignes_identiques=nb_identiques,
            lignes=comparatif_lignes,
            genere_par=genere_par,
            created_at=datetime.utcnow(),
        )

        comparatif = self._comparatif_repository.save(comparatif)

        # Journal sur les deux devis
        for did in [devis_source_id, devis_cible_id]:
            self._journal_repository.save(
                JournalDevis(
                    devis_id=did,
                    action="comparatif_genere",
                    details_json={
                        "message": (
                            f"Comparatif genere entre {devis_source.numero} "
                            f"et {devis_cible.numero}"
                        ),
                        "comparatif_id": comparatif.id,
                        "devis_source_id": devis_source_id,
                        "devis_cible_id": devis_cible_id,
                    },
                    auteur_id=genere_par,
                    created_at=datetime.utcnow(),
                )
            )

        return ComparatifDTO.from_entity(comparatif)

    def _collecter_lignes_avec_lot(
        self, devis_id: int
    ) -> List[Tuple[str, str, Optional[int], LigneDevis]]:
        """Collecte les lignes d'un devis avec le titre du lot parent.

        Returns:
            Liste de tuples (lot_titre, designation, article_id, ligne).
        """
        lots = self._lot_repository.find_by_devis(devis_id)
        result = []
        for lot in lots:
            lignes = self._ligne_repository.find_by_lot(lot.id)
            for ligne in lignes:
                result.append((lot.libelle, ligne.libelle, ligne.article_id, ligne))
        return result

    def _indexer_lignes(
        self,
        lignes_avec_lot: List[Tuple[str, str, Optional[int], LigneDevis]],
    ) -> Dict[str, Tuple[str, str, Optional[int], LigneDevis]]:
        """Indexe les lignes par cle de matching.

        Args:
            lignes_avec_lot: Liste de tuples (lot_titre, designation, article_id, ligne).

        Returns:
            Dictionnaire {cle_matching: (lot_titre, designation, article_id, ligne)}.
        """
        index: Dict[str, Tuple[str, str, Optional[int], LigneDevis]] = {}
        for lot_titre, designation, article_id, ligne in lignes_avec_lot:
            cle = self._cle_matching(lot_titre, designation, article_id)
            index[cle] = (lot_titre, designation, article_id, ligne)
        return index

    def _cle_matching(
        self,
        lot_titre: str,
        designation: str,
        article_id: Optional[int],
    ) -> str:
        """Genere la cle de matching pour une ligne.

        Priorite: article_id si disponible, sinon (lot_titre, designation).

        Args:
            lot_titre: Le titre du lot.
            designation: La designation de la ligne.
            article_id: L'ID de l'article (optionnel).

        Returns:
            La cle de matching sous forme de string.
        """
        if article_id is not None:
            return f"article:{article_id}"
        return f"lot:{lot_titre}|desig:{designation}"


class GetComparatifUseCase:
    """Use case pour recuperer un comparatif existant.

    DEV-08: Lecture d'un comparatif deja genere.
    """

    def __init__(self, comparatif_repository: ComparatifRepository):
        self._comparatif_repository = comparatif_repository

    def execute(self, comparatif_id: int) -> ComparatifDTO:
        """Recupere un comparatif par son ID.

        Args:
            comparatif_id: L'ID du comparatif.

        Returns:
            Le DTO du comparatif.

        Raises:
            ValueError: Si le comparatif n'existe pas.
        """
        comparatif = self._comparatif_repository.find_by_id(comparatif_id)
        if not comparatif:
            raise ValueError(f"Comparatif {comparatif_id} non trouve")

        return ComparatifDTO.from_entity(comparatif)


class FigerVersionUseCase:
    """Use case pour figer manuellement une version de devis.

    DEV-08: Gele une version pour la rendre non modifiable et non supprimable.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self, devis_id: int, dto: FigerVersionDTO, fige_par: int
    ) -> VersionDTO:
        """Fige une version de devis.

        Args:
            devis_id: L'ID du devis a figer.
            dto: Les donnees optionnelles (commentaire).
            fige_par: L'ID de l'utilisateur qui fige.

        Returns:
            Le DTO de la version figee.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            DevisValidationError: Si la version est deja figee.
        """
        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # Appel la methode du domaine (leve DevisValidationError si deja fige)
        devis.figer(fige_par)

        if dto.commentaire:
            devis.version_commentaire = dto.commentaire

        devis = self._devis_repository.save(devis)

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="gel_version",
                details_json={
                    "message": f"Version {devis.numero} figee manuellement",
                    "commentaire": dto.commentaire,
                },
                auteur_id=fige_par,
                created_at=datetime.utcnow(),
            )
        )

        return VersionDTO.from_entity(devis)

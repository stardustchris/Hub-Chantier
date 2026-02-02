"""Use Cases pour les relances automatiques de devis.

DEV-24: Relances automatiques - Notifications push/email si delai
de reponse depasse (configurable : 7j, 15j, 30j) avec historique.
"""

from datetime import datetime
from typing import List, Optional

from ...domain.entities.relance_devis import RelanceDevis, RelanceDevisValidationError
from ...domain.entities.journal_devis import JournalDevis
from ...domain.value_objects.config_relances import ConfigRelances, ConfigRelancesInvalideError
from ...domain.value_objects import StatutDevis
from ...domain.repositories.devis_repository import DevisRepository
from ...domain.repositories.relance_devis_repository import RelanceDevisRepository
from ...domain.repositories.journal_devis_repository import JournalDevisRepository
from ..dtos.relance_dtos import (
    RelanceDTO,
    ConfigRelancesDTO,
    RelancesHistoriqueDTO,
    ExecutionRelancesResultDTO,
    PlanifierRelancesDTO,
    UpdateConfigRelancesDTO,
)


class RelanceDevisError(Exception):
    """Exception de base pour les erreurs de relances."""

    def __init__(self, message: str = "Erreur de relance devis"):
        self.message = message
        super().__init__(self.message)


class RelanceDevisPlanificationError(RelanceDevisError):
    """Erreur lors de la planification des relances."""

    pass


class RelanceDevisExecutionError(RelanceDevisError):
    """Erreur lors de l'execution des relances."""

    pass


# ─────────────────────────────────────────────────────────────────────────────
# PlanifierRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class PlanifierRelancesUseCase:
    """Planifie les relances automatiques pour un devis envoye.

    DEV-24: A la mise en statut 'envoye', les relances sont planifiees
    selon la configuration du devis (delais 7j, 15j, 30j par defaut).

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
        _relance_repository: Repository pour persister les relances.
        _journal_repository: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        relance_repository: RelanceDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._relance_repository = relance_repository
        self._journal_repository = journal_repository

    def execute(
        self,
        devis_id: int,
        dto: PlanifierRelancesDTO,
        planifie_par: int,
    ) -> List[RelanceDTO]:
        """Planifie les relances pour un devis envoye.

        Args:
            devis_id: L'ID du devis.
            dto: Donnees de planification (message personnalise optionnel).
            planifie_par: L'ID de l'utilisateur qui planifie.

        Returns:
            Liste des relances planifiees.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            RelanceDevisPlanificationError: Si le devis n'est pas en statut 'envoye'.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # Verifier que le devis est en statut envoye (ou vu/en_negociation)
        statuts_autorise = (
            StatutDevis.ENVOYE,
            StatutDevis.VU,
            StatutDevis.EN_NEGOCIATION,
        )
        if devis.statut not in statuts_autorise:
            raise RelanceDevisPlanificationError(
                f"Le devis {devis.numero} doit etre en statut "
                f"'envoye', 'vu' ou 'en_negociation' pour planifier des relances "
                f"(statut actuel: {devis.statut.label})"
            )

        # Verifier qu'il n'y a pas deja des relances planifiees
        relances_existantes = self._relance_repository.find_planifiees_by_devis_id(devis_id)
        if relances_existantes:
            raise RelanceDevisPlanificationError(
                f"Le devis {devis.numero} a deja {len(relances_existantes)} "
                f"relance(s) planifiee(s)"
            )

        # Recuperer la config de relances du devis
        config = devis.config_relances
        if not config.actif:
            raise RelanceDevisPlanificationError(
                f"Les relances sont desactivees pour le devis {devis.numero}"
            )

        # Calculer les relances deja envoyees
        toutes_relances = self._relance_repository.find_by_devis_id(devis_id)
        nb_envoyees = sum(1 for r in toutes_relances if r.est_envoyee)

        # Date de reference = maintenant (ou date d'envoi du devis si disponible)
        date_reference = devis.updated_at or datetime.utcnow()

        # Planifier les relances restantes
        relances_a_creer: List[RelanceDevis] = []
        for i in range(nb_envoyees, config.nombre_relances):
            date_prevue = config.prochaine_relance(date_reference, i)
            if date_prevue is None:
                break
            relance = RelanceDevis(
                devis_id=devis_id,
                numero_relance=i + 1,
                type_relance=config.type_relance_defaut,
                date_prevue=date_prevue,
                statut="planifiee",
                message_personnalise=dto.message_personnalise,
                created_at=datetime.utcnow(),
            )
            relances_a_creer.append(relance)

        if not relances_a_creer:
            raise RelanceDevisPlanificationError(
                f"Aucune relance a planifier pour le devis {devis.numero} "
                f"(toutes les relances sont deja effectuees)"
            )

        # Persister les relances
        relances_creees = self._relance_repository.save_batch(relances_a_creer)

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="planification_relances",
                details_json={
                    "message": f"{len(relances_creees)} relance(s) planifiee(s)",
                    "dates_prevues": [
                        r.date_prevue.isoformat() for r in relances_creees
                    ],
                },
                auteur_id=planifie_par,
                created_at=datetime.utcnow(),
            )
        )

        return [RelanceDTO.from_entity(r) for r in relances_creees]


# ─────────────────────────────────────────────────────────────────────────────
# ExecuterRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class ExecuterRelancesUseCase:
    """Execute les relances planifiees dont la date est arrivee (batch job).

    DEV-24: Job periodique qui parcourt les relances planifiees et
    les marque comme envoyees. L'envoi effectif (email/push) est
    delegue a un service de notification externe.

    Attributes:
        _relance_repository: Repository pour acceder aux relances.
        _journal_repository: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        relance_repository: RelanceDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._relance_repository = relance_repository
        self._journal_repository = journal_repository

    def execute(self) -> ExecutionRelancesResultDTO:
        """Execute toutes les relances planifiees dont la date est arrivee.

        Returns:
            Resultat de l'execution avec nombre de relances envoyees et erreurs.
        """
        maintenant = datetime.utcnow()
        relances_a_envoyer = self._relance_repository.find_planifiees_avant(maintenant)

        nb_envoyees = 0
        nb_erreurs = 0
        details = []

        for relance in relances_a_envoyer:
            try:
                relance.envoyer()
                self._relance_repository.save(relance)

                self._journal_repository.save(
                    JournalDevis(
                        devis_id=relance.devis_id,
                        action="envoi_relance",
                        details_json={
                            "message": (
                                f"Relance #{relance.numero_relance} envoyee "
                                f"({relance.type_relance})"
                            ),
                            "relance_id": relance.id,
                            "numero_relance": relance.numero_relance,
                            "type_relance": relance.type_relance,
                        },
                        auteur_id=None,
                        created_at=datetime.utcnow(),
                    )
                )

                nb_envoyees += 1
                details.append({
                    "relance_id": relance.id,
                    "devis_id": relance.devis_id,
                    "numero_relance": relance.numero_relance,
                    "statut": "envoyee",
                })
            except RelanceDevisValidationError as e:
                nb_erreurs += 1
                details.append({
                    "relance_id": relance.id,
                    "devis_id": relance.devis_id,
                    "numero_relance": relance.numero_relance,
                    "statut": "erreur",
                    "erreur": str(e),
                })

        return ExecutionRelancesResultDTO(
            nb_relances_envoyees=nb_envoyees,
            nb_erreurs=nb_erreurs,
            details=details,
        )


# ─────────────────────────────────────────────────────────────────────────────
# AnnulerRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class AnnulerRelancesUseCase:
    """Annule les relances planifiees d'un devis.

    DEV-24: Si le devis change de statut (accepte/refuse/perdu),
    les relances en attente sont automatiquement annulees.

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
        _relance_repository: Repository pour persister les relances.
        _journal_repository: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        relance_repository: RelanceDevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._relance_repository = relance_repository
        self._journal_repository = journal_repository

    def execute(self, devis_id: int, annule_par: int) -> List[RelanceDTO]:
        """Annule toutes les relances planifiees d'un devis.

        Args:
            devis_id: L'ID du devis.
            annule_par: L'ID de l'utilisateur qui annule.

        Returns:
            Liste des relances annulees.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        relances_planifiees = self._relance_repository.find_planifiees_by_devis_id(
            devis_id
        )

        relances_annulees = []
        for relance in relances_planifiees:
            try:
                relance.annuler()
                self._relance_repository.save(relance)
                relances_annulees.append(relance)
            except RelanceDevisValidationError:
                continue

        if relances_annulees:
            self._journal_repository.save(
                JournalDevis(
                    devis_id=devis_id,
                    action="annulation_relances",
                    details_json={
                        "message": (
                            f"{len(relances_annulees)} relance(s) annulee(s)"
                        ),
                        "relances_annulees": [r.id for r in relances_annulees],
                    },
                    auteur_id=annule_par,
                    created_at=datetime.utcnow(),
                )
            )

        return [RelanceDTO.from_entity(r) for r in relances_annulees]


# ─────────────────────────────────────────────────────────────────────────────
# GetRelancesDevisUseCase
# ─────────────────────────────────────────────────────────────────────────────

class GetRelancesDevisUseCase:
    """Recupere l'historique complet des relances d'un devis.

    DEV-24: Consultation de l'historique avec config + compteurs.

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
        _relance_repository: Repository pour acceder aux relances.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        relance_repository: RelanceDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._relance_repository = relance_repository

    def execute(self, devis_id: int) -> RelancesHistoriqueDTO:
        """Recupere l'historique des relances d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Historique complet avec config, relances et compteurs.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        relances = self._relance_repository.find_by_devis_id(devis_id)
        config = devis.config_relances

        relances_dto = [RelanceDTO.from_entity(r) for r in relances]
        config_dto = ConfigRelancesDTO(
            delais=list(config.delais),
            actif=config.actif,
            type_relance_defaut=config.type_relance_defaut,
        )

        return RelancesHistoriqueDTO(
            devis_id=devis_id,
            config=config_dto,
            relances=relances_dto,
            nb_planifiees=sum(1 for r in relances if r.est_planifiee),
            nb_envoyees=sum(1 for r in relances if r.est_envoyee),
            nb_annulees=sum(1 for r in relances if r.est_annulee),
        )


# ─────────────────────────────────────────────────────────────────────────────
# UpdateConfigRelancesUseCase
# ─────────────────────────────────────────────────────────────────────────────

class UpdateConfigRelancesUseCase:
    """Modifie la configuration des relances d'un devis.

    DEV-24: Permet de personnaliser les delais et le type de relance
    par devis.

    Attributes:
        _devis_repository: Repository pour acceder aux devis.
        _journal_repository: Repository pour le journal d'audit.
    """

    def __init__(
        self,
        devis_repository: DevisRepository,
        journal_repository: JournalDevisRepository,
    ):
        self._devis_repository = devis_repository
        self._journal_repository = journal_repository

    def execute(
        self,
        devis_id: int,
        dto: UpdateConfigRelancesDTO,
        modifie_par: int,
    ) -> ConfigRelancesDTO:
        """Modifie la configuration des relances d'un devis.

        Args:
            devis_id: L'ID du devis.
            dto: Donnees de mise a jour.
            modifie_par: L'ID de l'utilisateur qui modifie.

        Returns:
            La configuration mise a jour.

        Raises:
            DevisNotFoundError: Si le devis n'existe pas.
            ConfigRelancesInvalideError: Si la configuration est invalide.
        """
        from .devis_use_cases import DevisNotFoundError

        devis = self._devis_repository.find_by_id(devis_id)
        if not devis:
            raise DevisNotFoundError(devis_id)

        # Construire la nouvelle config en fusionnant avec l'existante
        config_actuelle = devis.config_relances
        new_delais = (
            tuple(dto.delais) if dto.delais is not None
            else config_actuelle.delais
        )
        new_actif = (
            dto.actif if dto.actif is not None
            else config_actuelle.actif
        )
        new_type = (
            dto.type_relance_defaut if dto.type_relance_defaut is not None
            else config_actuelle.type_relance_defaut
        )

        # Valider la nouvelle config (leve ConfigRelancesInvalideError si invalide)
        nouvelle_config = ConfigRelances(
            delais=new_delais,
            actif=new_actif,
            type_relance_defaut=new_type,
        )

        # Persister la config sur le devis
        devis.config_relances_json = nouvelle_config.to_dict()
        self._devis_repository.save(devis)

        # Journal
        self._journal_repository.save(
            JournalDevis(
                devis_id=devis_id,
                action="modification_config_relances",
                details_json={
                    "message": "Configuration des relances modifiee",
                    "config": nouvelle_config.to_dict(),
                },
                auteur_id=modifie_par,
                created_at=datetime.utcnow(),
            )
        )

        return ConfigRelancesDTO(
            delais=list(nouvelle_config.delais),
            actif=nouvelle_config.actif,
            type_relance_defaut=nouvelle_config.type_relance_defaut,
        )

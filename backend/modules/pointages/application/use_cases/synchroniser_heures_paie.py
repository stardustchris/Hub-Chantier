"""Use Case : envoyer les heures validees vers un systeme de paie externe."""

import logging
from dataclasses import dataclass, field

from ...domain.entities import Pointage, StatutSynchronisation, SynchronisationPaie
from ...domain.repositories import (
    CorrespondanceExterneRepository,
    PointageRepository,
    SynchronisationPaieRepository,
)
from ...domain.services import HorairesReference, decouper_en_creneaux
from ...domain.value_objects import StatutPointage
from ..ports import ClientPaieExternePort, ErreurPaieExterne

logger = logging.getLogger(__name__)


@dataclass
class RapportSynchronisation:
    """Bilan d'un lot d'envois, par pointage."""

    envoyes: list[int] = field(default_factory=list)
    deja_envoyes: list[int] = field(default_factory=list)
    ignores: list[int] = field(default_factory=list)
    erreurs: list[int] = field(default_factory=list)
    non_valides: list[int] = field(default_factory=list)


def _minutes(duree) -> int:
    return duree.heures * 60 + duree.minutes


class SynchroniserHeuresPaieUseCase:
    """Envoie les pointages valides vers la paie externe, sans jamais les doubler.

    Le systeme externe exige des horaires et ne deduit pas la pause : chaque
    journee est envoyee en creneaux encadrant le repas, dont le total egale les
    heures validees (normales + supplementaires).

    Aucune heure n'est qualifiee de supplementaire a la journee : dans
    l'entreprise, les heures sup se declenchent au-dela de 35h par semaine,
    calcul qui revient a la paie a partir des totaux journaliers.

    Garanties :
    - un pointage deja envoye n'est jamais renvoye ;
    - un envoi partiel est supprime avant d'etre relance ;
    - l'echec d'un pointage n'interrompt pas les autres.
    """

    def __init__(
        self,
        pointage_repo: PointageRepository,
        synchronisation_repo: SynchronisationPaieRepository,
        correspondance_repo: CorrespondanceExterneRepository,
        client: ClientPaieExternePort,
        horaires: HorairesReference,
    ):
        """
        Initialise le use case.

        Args:
            pointage_repo: Depot des pointages.
            synchronisation_repo: Suivi des envois.
            correspondance_repo: Identifiants externes des compagnons et chantiers.
            client: Acces au systeme de paie externe.
            horaires: Horaires de reference pour reconstituer les creneaux.
        """
        self.pointage_repo = pointage_repo
        self.synchronisation_repo = synchronisation_repo
        self.correspondance_repo = correspondance_repo
        self.client = client
        self.horaires = horaires

    def execute(self, pointage_ids: list[int]) -> RapportSynchronisation:
        """Envoie les pointages donnes.

        Args:
            pointage_ids: Pointages a envoyer (les non valides sont ignores).

        Returns:
            Le bilan de l'envoi.
        """
        rapport = RapportSynchronisation()
        for pointage_id in pointage_ids:
            try:
                self._synchroniser(pointage_id, rapport)
            except Exception as exc:  # un pointage defaillant ne bloque pas le lot
                logger.exception("Synchronisation paie du pointage %s en echec", pointage_id)
                self._enregistrer(pointage_id, StatutSynchronisation.ERREUR, [], str(exc))
                rapport.erreurs.append(pointage_id)
        return rapport

    def relancer(self) -> RapportSynchronisation:
        """Renvoie les pointages en erreur ou ignores (correspondance ajoutee depuis...).

        Returns:
            Le bilan de l'envoi.
        """
        suivis = self.synchronisation_repo.find_by_statuts(
            [StatutSynchronisation.ERREUR, StatutSynchronisation.IGNORE]
        )
        return self.execute([suivi.pointage_id for suivi in suivis])

    def _synchroniser(self, pointage_id: int, rapport: RapportSynchronisation) -> None:
        suivi = self.synchronisation_repo.find_by_pointage_id(pointage_id)
        if suivi and suivi.est_envoye:
            rapport.deja_envoyes.append(pointage_id)
            return

        pointage = self.pointage_repo.find_by_id(pointage_id)
        if not pointage or pointage.statut != StatutPointage.VALIDE:
            rapport.non_valides.append(pointage_id)
            return

        # Nettoie un envoi partiel precedent, sinon la relance creerait des doublons
        restantes = list(suivi.saisies_externes) if suivi else []
        try:
            for saisie_id in list(restantes):
                self.client.supprimer_saisie(saisie_id)
                restantes.remove(saisie_id)
        except ErreurPaieExterne as exc:
            self._enregistrer(pointage_id, StatutSynchronisation.ERREUR, restantes,
                              f"Nettoyage de l'envoi precedent impossible : {exc}")
            rapport.erreurs.append(pointage_id)
            return

        manquant = self._correspondance_manquante(pointage)
        if manquant:
            self._enregistrer(pointage_id, StatutSynchronisation.IGNORE, [], manquant)
            rapport.ignores.append(pointage_id)
            return

        total = _minutes(pointage.heures_normales) + _minutes(pointage.heures_supplementaires)
        try:
            creneaux = decouper_en_creneaux(total, self.horaires)
        except ValueError as exc:
            self._enregistrer(pointage_id, StatutSynchronisation.IGNORE, [], str(exc))
            rapport.ignores.append(pointage_id)
            return
        if not creneaux:
            self._enregistrer(pointage_id, StatutSynchronisation.IGNORE, [],
                              "Aucune heure a envoyer.")
            rapport.ignores.append(pointage_id)
            return

        notes = f"Hub Chantier - pointage #{pointage_id}"

        utilisateur_ext = self.correspondance_repo.get_identifiant_externe(
            CorrespondanceExterneRepository.TYPE_UTILISATEUR, pointage.utilisateur_id)
        chantier_ext = self.correspondance_repo.get_identifiant_externe(
            CorrespondanceExterneRepository.TYPE_CHANTIER, pointage.chantier_id)

        creees: list[str] = []
        try:
            for creneau in creneaux:
                creees.append(self.client.creer_saisie_travail(
                    utilisateur_ext, chantier_ext, pointage.date_pointage,
                    creneau.debut, creneau.fin, notes,
                ))
        except ErreurPaieExterne as exc:
            # Les saisies deja creees sont memorisees pour etre nettoyees a la relance
            self._enregistrer(pointage_id, StatutSynchronisation.ERREUR, creees, str(exc))
            rapport.erreurs.append(pointage_id)
            return

        self._enregistrer(pointage_id, StatutSynchronisation.ENVOYE, creees)
        rapport.envoyes.append(pointage_id)

    def _correspondance_manquante(self, pointage: Pointage) -> str | None:
        manquants = []
        if not self.correspondance_repo.get_identifiant_externe(
            CorrespondanceExterneRepository.TYPE_UTILISATEUR, pointage.utilisateur_id
        ):
            manquants.append(f"compagnon #{pointage.utilisateur_id}")
        if not self.correspondance_repo.get_identifiant_externe(
            CorrespondanceExterneRepository.TYPE_CHANTIER, pointage.chantier_id
        ):
            manquants.append(f"chantier #{pointage.chantier_id}")
        if not manquants:
            return None
        return "Identifiant externe manquant pour : " + ", ".join(manquants)

    def _enregistrer(
        self,
        pointage_id: int,
        statut: StatutSynchronisation,
        saisies: list[str],
        message: str | None = None,
    ) -> None:
        suivi = self.synchronisation_repo.find_by_pointage_id(pointage_id) or SynchronisationPaie(
            pointage_id=pointage_id, statut=statut
        )
        suivi.enregistrer_tentative(statut, saisies, message)
        self.synchronisation_repo.save(suivi)

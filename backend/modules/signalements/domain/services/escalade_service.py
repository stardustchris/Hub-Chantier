"""Service d'escalade des signalements (SIG-16, SIG-17)."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from ..entities import Signalement


@dataclass
class EscaladeInfo:
    """Information sur une escalade à effectuer."""

    signalement: Signalement
    niveau: str  # "chef_chantier", "conducteur", "admin"
    pourcentage_temps: float
    destinataires_roles: List[str]


class EscaladeService:
    """
    Service de domaine gérant la logique d'escalade des signalements.

    Selon CDC SIG-16 et SIG-17:
    - À 50% du temps: alerte Chef de Chantier
    - À 100% du temps: escalade Conducteur de Travaux
    - À 200% du temps: escalade Admin
    """

    # Seuils d'escalade et destinataires
    SEUILS_ESCALADE: List[Tuple[float, str, List[str]]] = [
        (50.0, "chef_chantier", ["chef_chantier"]),
        (100.0, "conducteur", ["conducteur"]),
        (200.0, "admin", ["admin"]),
    ]

    def determiner_escalades(
        self,
        signalements: List[Signalement],
    ) -> List[EscaladeInfo]:
        """
        Détermine les escalades à effectuer pour une liste de signalements.

        Args:
            signalements: Liste des signalements à vérifier.

        Returns:
            Liste des escalades à effectuer.
        """
        escalades = []

        for sig in signalements:
            escalade = self._evaluer_escalade(sig)
            if escalade:
                escalades.append(escalade)

        return escalades

    def _evaluer_escalade(
        self,
        signalement: Signalement,
    ) -> Optional[EscaladeInfo]:
        """
        Évalue si un signalement nécessite une escalade.

        Args:
            signalement: Le signalement à évaluer.

        Returns:
            EscaladeInfo si escalade nécessaire, None sinon.
        """
        # Ne pas escalader les signalements résolus
        if signalement.statut.est_resolu:
            return None

        pct = signalement.pourcentage_temps_ecoule

        # Trouver le niveau d'escalade approprié
        niveau_atteint = None
        roles_destinataires = []

        for seuil, niveau, roles in self.SEUILS_ESCALADE:
            if pct >= seuil:
                niveau_atteint = niveau
                roles_destinataires = roles

        if not niveau_atteint:
            return None

        # Vérifier si cette escalade a déjà été faite
        # (basé sur le nombre d'escalades déjà effectuées)
        index_niveau = self._get_index_niveau(niveau_atteint)
        if signalement.nb_escalades > index_niveau:
            return None

        return EscaladeInfo(
            signalement=signalement,
            niveau=niveau_atteint,
            pourcentage_temps=pct,
            destinataires_roles=roles_destinataires,
        )

    def _get_index_niveau(self, niveau: str) -> int:
        """Retourne l'index du niveau d'escalade."""
        for i, (_, n, _) in enumerate(self.SEUILS_ESCALADE):
            if n == niveau:
                return i
        return -1

    def calculer_prochaine_escalade(
        self,
        signalement: Signalement,
    ) -> Optional[Tuple[str, datetime]]:
        """
        Calcule quand aura lieu la prochaine escalade.

        Args:
            signalement: Le signalement à analyser.

        Returns:
            Tuple (niveau, date) de la prochaine escalade, ou None.
        """
        if signalement.statut.est_resolu:
            return None

        pct = signalement.pourcentage_temps_ecoule
        date_limite = signalement.date_limite_traitement
        duree_totale = (date_limite - signalement.created_at).total_seconds()

        for seuil, niveau, _ in self.SEUILS_ESCALADE:
            if pct < seuil:
                # Calculer quand ce seuil sera atteint
                temps_seuil = (seuil / 100) * duree_totale
                date_escalade = signalement.created_at
                from datetime import timedelta
                date_escalade = signalement.created_at + timedelta(seconds=temps_seuil)
                return (niveau, date_escalade)

        return None

    def generer_message_escalade(
        self,
        escalade: EscaladeInfo,
        chantier_nom: str,
    ) -> str:
        """
        Génère le message de notification pour une escalade.

        Args:
            escalade: Les informations d'escalade.
            chantier_nom: Le nom du chantier.

        Returns:
            Le message formaté.
        """
        sig = escalade.signalement
        niveau_label = self._get_niveau_label(escalade.niveau)

        message = (
            f"[ESCALADE {niveau_label.upper()}] "
            f"Signalement #{sig.id} - {sig.titre}\n"
            f"Chantier: {chantier_nom}\n"
            f"Priorité: {sig.priorite.label}\n"
            f"Temps écoulé: {escalade.pourcentage_temps:.0f}%\n"
            f"Temps restant: {sig.temps_restant_formatte}\n"
        )

        if sig.localisation:
            message += f"Localisation: {sig.localisation}\n"

        return message

    def _get_niveau_label(self, niveau: str) -> str:
        """Retourne le label du niveau d'escalade."""
        labels = {
            "chef_chantier": "Chef de Chantier",
            "conducteur": "Conducteur de Travaux",
            "admin": "Administrateur",
        }
        return labels.get(niveau, niveau)

    def get_statistiques_escalade(
        self,
        signalements: List[Signalement],
    ) -> dict:
        """
        Calcule les statistiques d'escalade.

        Args:
            signalements: Liste des signalements.

        Returns:
            Dict avec les statistiques.
        """
        stats = {
            "total": len(signalements),
            "en_retard": 0,
            "a_50_pct": 0,
            "a_100_pct": 0,
            "a_200_pct": 0,
            "deja_escalades": 0,
        }

        for sig in signalements:
            if sig.statut.est_resolu:
                continue

            pct = sig.pourcentage_temps_ecoule

            if pct >= 200:
                stats["a_200_pct"] += 1
                stats["en_retard"] += 1
            elif pct >= 100:
                stats["a_100_pct"] += 1
                stats["en_retard"] += 1
            elif pct >= 50:
                stats["a_50_pct"] += 1

            if sig.nb_escalades > 0:
                stats["deja_escalades"] += 1

        return stats

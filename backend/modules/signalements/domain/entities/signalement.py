"""Entité Signalement - Représente un signalement/incident sur chantier."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from ..value_objects import Priorite, StatutSignalement


@dataclass
class Signalement:
    """
    Entité représentant un signalement sur un chantier.

    Selon CDC Section 10 - Signalements (SIG-01 à SIG-20).

    Attributes:
        id: Identifiant unique.
        chantier_id: Identifiant du chantier associé.
        titre: Titre du signalement.
        description: Description détaillée du problème.
        priorite: Niveau de priorité (SIG-14).
        statut: Statut actuel du signalement.
        cree_par: ID de l'utilisateur créateur.
        assigne_a: ID de l'utilisateur assigné (optionnel).
        date_resolution_souhaitee: Date limite souhaitée (SIG-15).
        date_traitement: Date de traitement effectif.
        date_cloture: Date de clôture.
        commentaire_traitement: Commentaire lors du traitement (SIG-08).
        photo_url: URL de la photo associée (SIG-06).
        localisation: Localisation sur le chantier.
        created_at: Date de création.
        updated_at: Date de dernière modification.
        nb_escalades: Nombre d'escalades effectuées (SIG-16, SIG-17).
        derniere_escalade_at: Date de la dernière escalade.
    """

    chantier_id: int
    titre: str
    description: str
    cree_par: int
    priorite: Priorite = Priorite.MOYENNE
    statut: StatutSignalement = StatutSignalement.OUVERT
    id: Optional[int] = None
    assigne_a: Optional[int] = None
    date_resolution_souhaitee: Optional[datetime] = None
    date_traitement: Optional[datetime] = None
    date_cloture: Optional[datetime] = None
    commentaire_traitement: Optional[str] = None
    photo_url: Optional[str] = None
    localisation: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    nb_escalades: int = 0
    derniere_escalade_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Valide les données à la création."""
        if not self.titre or not self.titre.strip():
            raise ValueError("Le titre du signalement ne peut pas être vide")

        if not self.description or not self.description.strip():
            raise ValueError("La description du signalement ne peut pas être vide")

        self.titre = self.titre.strip()
        self.description = self.description.strip()

        if self.localisation:
            self.localisation = self.localisation.strip()

    @property
    def est_en_retard(self) -> bool:
        """
        Vérifie si le signalement est en retard.

        Basé sur la date de résolution souhaitée ou le délai par défaut
        selon la priorité.
        """
        if self.statut.est_resolu:
            return False

        now = datetime.now()

        # Si date souhaitée définie
        if self.date_resolution_souhaitee:
            return now > self.date_resolution_souhaitee

        # Sinon, basé sur le délai de la priorité
        date_limite = self.created_at + self.priorite.delai_traitement
        return now > date_limite

    @property
    def date_limite_traitement(self) -> datetime:
        """
        Retourne la date limite de traitement.

        Utilise la date souhaitée si définie, sinon calcule
        selon la priorité.
        """
        if self.date_resolution_souhaitee:
            return self.date_resolution_souhaitee
        return self.created_at + self.priorite.delai_traitement

    @property
    def pourcentage_temps_ecoule(self) -> float:
        """
        Calcule le pourcentage de temps écoulé avant la date limite.

        Utilisé pour le système d'escalade (SIG-16, SIG-17):
        - 50% -> alerte Chef de Chantier
        - 100% -> escalade Conducteur de Travaux
        - 200% -> escalade Admin
        """
        if self.statut.est_resolu:
            return 0.0

        now = datetime.now()
        date_limite = self.date_limite_traitement
        duree_totale = (date_limite - self.created_at).total_seconds()

        if duree_totale <= 0:
            return 100.0

        temps_ecoule = (now - self.created_at).total_seconds()
        return (temps_ecoule / duree_totale) * 100

    @property
    def niveau_escalade_requis(self) -> Optional[str]:
        """
        Détermine le niveau d'escalade requis selon le temps écoulé.

        Returns:
            - "chef_chantier": si >= 50%
            - "conducteur": si >= 100%
            - "admin": si >= 200%
            - None: si pas d'escalade requise
        """
        if self.statut.est_resolu:
            return None

        pct = self.pourcentage_temps_ecoule

        if pct >= 200:
            return "admin"
        elif pct >= 100:
            return "conducteur"
        elif pct >= 50:
            return "chef_chantier"
        return None

    @property
    def temps_restant(self) -> Optional[timedelta]:
        """
        Retourne le temps restant avant la date limite.

        Returns:
            timedelta positif si temps restant, négatif si en retard.
            None si résolu.
        """
        if self.statut.est_resolu:
            return None

        return self.date_limite_traitement - datetime.now()

    @property
    def temps_restant_formatte(self) -> str:
        """Retourne le temps restant formaté."""
        temps = self.temps_restant
        if temps is None:
            return "Résolu"

        total_seconds = int(temps.total_seconds())
        if total_seconds < 0:
            return f"En retard de {abs(total_seconds) // 3600}h"

        heures = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if heures > 24:
            jours = heures // 24
            return f"{jours}j {heures % 24}h"
        return f"{heures}h {minutes}min"

    def assigner(self, user_id: int) -> None:
        """
        Assigne le signalement à un utilisateur.

        Args:
            user_id: ID de l'utilisateur assigné.
        """
        self.assigne_a = user_id
        if self.statut == StatutSignalement.OUVERT:
            self.statut = StatutSignalement.EN_COURS
        self.updated_at = datetime.now()

    def marquer_traite(self, commentaire: str) -> None:
        """
        Marque le signalement comme traité (SIG-08).

        Args:
            commentaire: Commentaire obligatoire.

        Raises:
            ValueError: Si le commentaire est vide.
        """
        if not commentaire or not commentaire.strip():
            raise ValueError("Le commentaire de traitement est obligatoire")

        if not self.statut.peut_transitionner_vers(StatutSignalement.TRAITE):
            raise ValueError(
                f"Impossible de passer de {self.statut.label} à Traité"
            )

        self.statut = StatutSignalement.TRAITE
        self.commentaire_traitement = commentaire.strip()
        self.date_traitement = datetime.now()
        self.updated_at = datetime.now()

    def cloturer(self) -> None:
        """
        Clôture le signalement (SIG-09).

        Raises:
            ValueError: Si la transition n'est pas valide.
        """
        if not self.statut.peut_transitionner_vers(StatutSignalement.CLOTURE):
            raise ValueError(
                f"Impossible de clôturer depuis l'état {self.statut.label}"
            )

        self.statut = StatutSignalement.CLOTURE
        self.date_cloture = datetime.now()
        self.updated_at = datetime.now()

    def reouvrir(self) -> None:
        """
        Réouvre un signalement clôturé.

        Raises:
            ValueError: Si la transition n'est pas valide.
        """
        if not self.statut.peut_transitionner_vers(StatutSignalement.OUVERT):
            raise ValueError(
                f"Impossible de réouvrir depuis l'état {self.statut.label}"
            )

        self.statut = StatutSignalement.OUVERT
        self.date_traitement = None
        self.date_cloture = None
        self.commentaire_traitement = None
        self.updated_at = datetime.now()

    def changer_priorite(self, nouvelle_priorite: Priorite) -> None:
        """
        Change la priorité du signalement.

        Args:
            nouvelle_priorite: La nouvelle priorité.
        """
        self.priorite = nouvelle_priorite
        self.updated_at = datetime.now()

    def definir_date_resolution(self, date: Optional[datetime]) -> None:
        """
        Définit ou modifie la date de résolution souhaitée (SIG-15).

        Args:
            date: La date souhaitée (ou None pour supprimer).
        """
        self.date_resolution_souhaitee = date
        self.updated_at = datetime.now()

    def enregistrer_escalade(self) -> None:
        """Enregistre une nouvelle escalade."""
        self.nb_escalades += 1
        self.derniere_escalade_at = datetime.now()
        self.updated_at = datetime.now()

    def peut_modifier(self, user_id: int, user_role: str) -> bool:
        """
        Vérifie si un utilisateur peut modifier ce signalement.

        Args:
            user_id: ID de l'utilisateur.
            user_role: Rôle de l'utilisateur.

        Returns:
            True si l'utilisateur peut modifier.
        """
        # Admin et Conducteur peuvent tout modifier
        if user_role in ("admin", "conducteur"):
            return True

        # Chef de chantier peut modifier ses signalements et ceux de son chantier
        if user_role == "chef_chantier":
            return True

        # Compagnon peut modifier uniquement ses propres signalements non clôturés
        if user_role == "compagnon":
            return self.cree_par == user_id and self.statut.peut_etre_modifie

        return False

    def peut_cloturer(self, user_role: str) -> bool:
        """
        Vérifie si un utilisateur peut clôturer ce signalement.

        Args:
            user_role: Rôle de l'utilisateur.

        Returns:
            True si l'utilisateur peut clôturer.
        """
        # Seuls admin, conducteur et chef de chantier peuvent clôturer
        return user_role in ("admin", "conducteur", "chef_chantier")

    def __eq__(self, other: object) -> bool:
        """Égalité basée sur l'ID."""
        if not isinstance(other, Signalement):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash basé sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

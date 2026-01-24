"""Exceptions pour les use cases du module Planning.

Ce module centralise toutes les exceptions metier utilisees par les use cases.
"""

from datetime import date


class AffectationConflictError(Exception):
    """Exception levee quand une affectation existe deja pour cette date.

    Attributes:
        utilisateur_id: ID de l'utilisateur concerne.
        date: Date de l'affectation en conflit.
        message: Message d'erreur descriptif.
    """

    def __init__(self, utilisateur_id: int, date_affectation: date):
        """
        Initialise l'exception de conflit.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_affectation: Date de l'affectation en conflit.
        """
        self.utilisateur_id = utilisateur_id
        self.date = date_affectation
        self.message = (
            f"L'utilisateur {utilisateur_id} a deja une affectation "
            f"pour le {date_affectation}"
        )
        super().__init__(self.message)


class AffectationNotFoundError(Exception):
    """Exception levee quand une affectation n'est pas trouvee.

    Attributes:
        affectation_id: ID de l'affectation non trouvee.
        message: Message d'erreur descriptif.
    """

    def __init__(self, affectation_id: int):
        """
        Initialise l'exception.

        Args:
            affectation_id: ID de l'affectation non trouvee.
        """
        self.affectation_id = affectation_id
        self.message = f"Affectation {affectation_id} non trouvee"
        super().__init__(self.message)


class InvalidDateRangeError(Exception):
    """Exception levee quand la plage de dates est invalide.

    Attributes:
        message: Message d'erreur descriptif.
    """

    def __init__(self, message: str):
        """
        Initialise l'exception.

        Args:
            message: Description de l'erreur.
        """
        self.message = message
        super().__init__(self.message)


class NoAffectationsToDuplicateError(Exception):
    """Exception levee quand il n'y a pas d'affectations a dupliquer.

    Attributes:
        utilisateur_id: ID de l'utilisateur concerne.
        date_debut: Date de debut de la periode source.
        date_fin: Date de fin de la periode source.
        message: Message d'erreur descriptif.
    """

    def __init__(
        self,
        utilisateur_id: int,
        date_debut: date,
        date_fin: date,
    ):
        """
        Initialise l'exception.

        Args:
            utilisateur_id: ID de l'utilisateur.
            date_debut: Date de debut de la periode source.
            date_fin: Date de fin de la periode source.
        """
        self.utilisateur_id = utilisateur_id
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.message = (
            f"Aucune affectation a dupliquer pour l'utilisateur {utilisateur_id} "
            f"entre le {date_debut} et le {date_fin}"
        )
        super().__init__(self.message)

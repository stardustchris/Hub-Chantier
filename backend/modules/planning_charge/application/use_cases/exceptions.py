"""Exceptions metier du module planning_charge."""


class BesoinNotFoundError(Exception):
    """Exception levee quand un besoin n'est pas trouve."""

    def __init__(self, besoin_id: int):
        self.besoin_id = besoin_id
        super().__init__(f"Besoin non trouve: ID {besoin_id}")


class BesoinAlreadyExistsError(Exception):
    """Exception levee quand un besoin existe deja."""

    def __init__(self, chantier_id: int, semaine_code: str, type_metier: str):
        self.chantier_id = chantier_id
        self.semaine_code = semaine_code
        self.type_metier = type_metier
        super().__init__(
            f"Un besoin existe deja pour le chantier {chantier_id}, "
            f"semaine {semaine_code}, type {type_metier}"
        )


class InvalidSemaineRangeError(Exception):
    """Exception levee quand la plage de semaines est invalide."""

    def __init__(self, message: str):
        super().__init__(message)


class ChantierNotFoundError(Exception):
    """Exception levee quand un chantier n'est pas trouve."""

    def __init__(self, chantier_id: int):
        self.chantier_id = chantier_id
        super().__init__(f"Chantier non trouve: ID {chantier_id}")

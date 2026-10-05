"""Enrichissement des pointages avec les libelles des entites liees.

Les pointages stockes en base ne portent que les identifiants de
l'utilisateur et du chantier. Les libelles vivent dans d'autres modules :
ils sont recuperes via le port partage EntityInfoService, sans import direct
entre modules.
"""

from shared.application.ports.entity_info_service import EntityInfoService


def enrichir_pointages(
    pointages: list,
    entity_info_service: EntityInfoService | None,
) -> None:
    """Renseigne le nom de l'utilisateur et du chantier sur chaque pointage.

    Les pointages sont modifies sur place. Les identifiants sont dedoublonnes
    avant interrogation, pour ne faire qu'un appel par utilisateur et par
    chantier distinct, quel que soit le nombre de lignes.

    Args:
        pointages: Les pointages a enrichir.
        entity_info_service: Service d'acces aux libelles. Si absent, les
            pointages sont laisses tels quels.
    """
    if not entity_info_service or not pointages:
        return

    infos_utilisateurs = {}
    for utilisateur_id in {p.utilisateur_id for p in pointages}:
        info = entity_info_service.get_user_info(utilisateur_id)
        if info:
            infos_utilisateurs[utilisateur_id] = info

    infos_chantiers = {}
    for chantier_id in {p.chantier_id for p in pointages}:
        info = entity_info_service.get_chantier_info(chantier_id)
        if info:
            infos_chantiers[chantier_id] = info

    for pointage in pointages:
        info_utilisateur = infos_utilisateurs.get(pointage.utilisateur_id)
        if info_utilisateur:
            pointage.utilisateur_nom = info_utilisateur.nom

        info_chantier = infos_chantiers.get(pointage.chantier_id)
        if info_chantier:
            pointage.chantier_nom = info_chantier.nom

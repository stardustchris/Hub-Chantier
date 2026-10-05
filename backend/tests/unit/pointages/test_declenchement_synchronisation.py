"""Tests du declenchement de l'envoi vers la paie externe apres validation."""

from fastapi import BackgroundTasks

from modules.pointages.infrastructure.paie_externe import synchronisation
from shared.infrastructure.config import settings


def _activer(monkeypatch, actif=True, cle="sk_test_cle"):
    monkeypatch.setattr(settings, "COSTRUCTOR_SYNC_ENABLED", actif)
    monkeypatch.setattr(settings, "COSTRUCTOR_API_KEY", cle)


def test_rien_n_est_programme_si_la_synchronisation_est_desactivee(monkeypatch):
    _activer(monkeypatch, actif=False)
    taches = BackgroundTasks()

    synchronisation.planifier_synchronisation(taches, [1, 2])

    assert taches.tasks == []


def test_rien_n_est_programme_sans_cle_d_api(monkeypatch):
    _activer(monkeypatch, cle="   ")
    taches = BackgroundTasks()

    synchronisation.planifier_synchronisation(taches, [1])

    assert taches.tasks == []


def test_envoi_programme_avec_les_pointages_valides(monkeypatch):
    _activer(monkeypatch)
    taches = BackgroundTasks()

    synchronisation.planifier_synchronisation(taches, [3, None, 7])

    assert len(taches.tasks) == 1
    assert taches.tasks[0].args == ([3, 7],)


def test_aucun_pointage_valide_aucune_tache(monkeypatch):
    _activer(monkeypatch)
    taches = BackgroundTasks()

    synchronisation.planifier_synchronisation(taches, [])

    assert taches.tasks == []


def test_la_tache_de_fond_ne_leve_jamais(monkeypatch):
    """Une panne inattendue est journalisee, pas propagee (sinon bruit serveur)."""
    def en_panne(_ids):
        raise RuntimeError("base indisponible")

    monkeypatch.setattr(synchronisation, "synchroniser", en_panne)

    synchronisation._synchroniser_sans_lever([1])  # ne doit pas lever


def test_horaires_lus_depuis_la_configuration(monkeypatch):
    monkeypatch.setattr(settings, "PAIE_HEURE_DEBUT", "07:30")
    monkeypatch.setattr(settings, "PAIE_PAUSE_DEBUT", "12:00")
    monkeypatch.setattr(settings, "PAIE_PAUSE_FIN", "12:45")

    horaires = synchronisation.horaires_reference()

    assert horaires.debut.strftime("%H:%M") == "07:30"
    assert horaires.pause_fin.strftime("%H:%M") == "12:45"


class _SessionFactice:
    def __init__(self):
        self.fermee = False

    def close(self):
        self.fermee = True


class _ClientFactice:
    def __init__(self):
        self.ferme = False

    def fermer(self):
        self.ferme = True


def _remplacer_infrastructure(monkeypatch, use_case):
    session, client = _SessionFactice(), _ClientFactice()
    monkeypatch.setattr(synchronisation, "SessionLocal", lambda: session)
    monkeypatch.setattr(synchronisation, "construire_client", lambda: client)
    monkeypatch.setattr(synchronisation, "construire_use_case", lambda s, c: use_case)
    return session, client


def test_synchroniser_envoie_les_pointages_donnes_et_libere_les_ressources(monkeypatch):
    from unittest.mock import Mock

    from modules.pointages.application.use_cases import RapportSynchronisation

    use_case = Mock()
    use_case.execute.return_value = RapportSynchronisation(envoyes=[4])
    session, client = _remplacer_infrastructure(monkeypatch, use_case)

    rapport = synchronisation.synchroniser([4])

    assert rapport.envoyes == [4]
    use_case.execute.assert_called_once_with([4])
    assert session.fermee and client.ferme


def test_synchroniser_sans_pointage_relance_les_echecs(monkeypatch):
    from unittest.mock import Mock

    from modules.pointages.application.use_cases import RapportSynchronisation

    use_case = Mock()
    use_case.relancer.return_value = RapportSynchronisation()
    _remplacer_infrastructure(monkeypatch, use_case)

    synchronisation.synchroniser(None)

    use_case.relancer.assert_called_once()
    use_case.execute.assert_not_called()


def test_ressources_liberees_meme_en_cas_d_echec(monkeypatch):
    from unittest.mock import Mock

    import pytest

    use_case = Mock()
    use_case.execute.side_effect = RuntimeError("panne")
    session, client = _remplacer_infrastructure(monkeypatch, use_case)

    with pytest.raises(RuntimeError):
        synchronisation.synchroniser([1])
    assert session.fermee and client.ferme


def test_assemblage_du_use_case_sur_une_session(monkeypatch):
    from unittest.mock import Mock

    from modules.pointages.application.use_cases import SynchroniserHeuresPaieUseCase

    use_case = synchronisation.construire_use_case(Mock(), Mock())

    assert isinstance(use_case, SynchroniserHeuresPaieUseCase)
    assert use_case.horaires.debut.strftime("%H:%M") == settings.PAIE_HEURE_DEBUT


def test_construction_du_client_depuis_la_configuration(monkeypatch):
    _activer(monkeypatch, cle="sk_test_cle")

    client = synchronisation.construire_client()
    try:
        assert client._http.headers["Authorization"] == "Bearer sk_test_cle"
    finally:
        client.fermer()

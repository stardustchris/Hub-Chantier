"""Tests de l'adaptateur HTTP Costructor (sans reseau : transport simule)."""

import json
from datetime import date, time

import httpx
import pytest

from modules.pointages.application.ports import ErreurPaieExterne
from modules.pointages.infrastructure.paie_externe.costructor_client import CostructorClient


def _client(handler):
    return CostructorClient("sk_test_cle", transport=httpx.MockTransport(handler))


def _creer(client):
    return client.creer_saisie_travail(
        "usr_1", "pj_1", date(2026, 10, 5), time(8, 0), time(12, 0), "Hub Chantier #10"
    )


class TestCreation:
    def test_envoie_le_format_attendu_par_costructor(self):
        recues = []

        def handler(request: httpx.Request):
            recues.append(request)
            return httpx.Response(200, json={"data": {"id": "tse_abc"}})

        assert _creer(_client(handler)) == "tse_abc"

        requete = recues[0]
        assert requete.method == "POST"
        assert requete.url.path == "/external/v1/timesheet_entries"
        assert requete.headers["Authorization"] == "Bearer sk_test_cle"
        assert json.loads(requete.content) == {
            "user": "usr_1", "type": "work", "day": "2026-10-05", "project": "pj_1",
            "startTime": "08:00", "endTime": "12:00", "notes": "Hub Chantier #10",
        }

    def test_refus_traduit_en_erreur_lisible(self):
        def handler(request):
            return httpx.Response(400, json={"message": "Les entrées de type travail..."})

        with pytest.raises(ErreurPaieExterne, match="400.*Les entrées de type travail"):
            _creer(_client(handler))

    def test_page_html_d_erreur_non_reprise_dans_le_message(self):
        def handler(request):
            return httpx.Response(500, text="<!DOCTYPE html><html>...</html>")

        with pytest.raises(ErreurPaieExterne) as exc:
            _creer(_client(handler))
        assert "<html" not in str(exc.value)

    def test_reseau_indisponible(self):
        def handler(request):
            raise httpx.ConnectError("refus de connexion")

        with pytest.raises(ErreurPaieExterne, match="injoignable"):
            _creer(_client(handler))

    def test_reponse_sans_identifiant(self):
        def handler(request):
            return httpx.Response(200, json={"data": {}})

        with pytest.raises(ErreurPaieExterne, match="identifiant"):
            _creer(_client(handler))


class TestSuppression:
    def test_supprime_la_saisie(self):
        recues = []

        def handler(request):
            recues.append(request)
            return httpx.Response(200, json={"data": {"deleted": True}})

        _client(handler).supprimer_saisie("tse_abc")
        assert recues[0].method == "DELETE"
        assert recues[0].url.path == "/external/v1/timesheet_entries/tse_abc"

    def test_saisie_deja_absente_n_est_pas_une_erreur(self):
        _client(lambda request: httpx.Response(404, json={"message": "Not found"})) \
            .supprimer_saisie("tse_disparue")


def test_cle_absente_refusee():
    with pytest.raises(ValueError, match="COSTRUCTOR_API_KEY"):
        CostructorClient("  ")


class TestLimitationDeDebit:
    """Costructor repond 429 apres une dizaine d'appels rapproches."""

    def _client_scenario(self, reponses):
        attentes = []
        file = list(reponses)

        def handler(request):
            return file.pop(0)

        client = CostructorClient(
            "sk_test_cle", transport=httpx.MockTransport(handler), attendre=attentes.append
        )
        return client, attentes

    def test_patiente_puis_reussit(self):
        client, attentes = self._client_scenario([
            httpx.Response(429), httpx.Response(429),
            httpx.Response(200, json={"data": {"id": "tse_ok"}}),
        ])

        assert _creer(client) == "tse_ok"
        assert attentes == [2, 4]  # attentes croissantes

    def test_respecte_le_delai_demande_par_costructor(self):
        client, attentes = self._client_scenario([
            httpx.Response(429, headers={"Retry-After": "7"}),
            httpx.Response(200, json={"data": {"id": "tse_ok"}}),
        ])

        _creer(client)
        assert attentes == [7.0]

    def test_abandonne_apres_les_essais_autorises(self):
        client, attentes = self._client_scenario([httpx.Response(429)] * 5)

        with pytest.raises(ErreurPaieExterne, match="429"):
            _creer(client)
        assert attentes == [2, 4, 8, 16]

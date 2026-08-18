"""Outils de gel du temps pour les tests.

Plusieurs use cases calculent leurs resultats par rapport a `date.today()`
(evolution financiere, burn rate, verrouillage de la periode de paie). Sans
gel de cette date, les tests qui verifient des valeurs precises ne passent
que pendant la periode ou ils ont ete ecrits, puis echouent avec le temps.

`freeze_today` fige `date.today()` dans un module donne, pour rendre ces
tests deterministes quelle que soit la date d'execution.
"""

from datetime import date

import pytest


def freeze_today(monkeypatch: pytest.MonkeyPatch, module, jour: date) -> None:
    """Fige `date.today()` dans le module indique.

    La classe de remplacement herite de `date` pour que les constructions
    `date(...)` et les `isinstance(..., date)` du code teste continuent de
    fonctionner normalement.

    Args:
        monkeypatch: Fixture pytest de patch.
        module: Module dans lequel figer la date.
        jour: Date retournee par `date.today()`.
    """

    class _DateFigee(date):
        @classmethod
        def today(cls) -> date:
            return jour

    monkeypatch.setattr(module, "date", _DateFigee)

"""Shared fixtures for the test suite."""

from pathlib import Path
import sys

import pytest


def find_project_root():
    """Trouve la racine du projet contenant custom_components,
    que l'on soit :
    - dans Home Assistant local
    - dans GitHub Actions
    - en local hors HA
    """

    current = Path(__file__).resolve()

    # On remonte jusqu'à 10 niveaux (large mais safe)
    for parent in current.parents:
        if (parent / "custom_components").exists():
            return parent

    raise RuntimeError("custom_components introuvable dans les parents")


ROOT = find_project_root()

# Ajoute la racine au PYTHONPATH
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def fake_hass():
    class FakeHass:
        class config_entries:
            @staticmethod
            def async_update_entry(entry, data):
                entry.data = data

            @staticmethod
            async def async_reload(entry_id):
                return True

    return FakeHass()


@pytest.fixture
def flow_factory(fake_hass):
    """Return a factory that builds a testable Flow class combining a Step and FakeFlowBase."""

    class FakeFlowBase:
        """Minimal fake of Home Assistant ConfigFlow."""

        def __init__(self):
            self.hass = fake_hass
            self.entry = None
            self.api_key = None

        def async_show_form(self, **kwargs):
            return kwargs

        def async_create_entry(self, title, data):
            return {"type": "create_entry", "title": title, "data": data}

        def _async_current_entries(self):
            return []

        async def async_step_main_menu(self):
            return {"step_id": "main_menu"}

    def factory(step_cls):
        """Return a new class combining the step and FakeFlowBase."""

        class Testable(step_cls, FakeFlowBase):
            pass

        return Testable()

    return factory

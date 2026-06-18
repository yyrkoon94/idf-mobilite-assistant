"""Shared fixtures for the test suite."""

from pathlib import Path
import sys

import pytest

# Ajoute la racine du projet au PYTHONPATH
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def fake_hass():
    """Provide a minimal fake hass object for flow tests."""

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

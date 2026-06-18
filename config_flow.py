from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .steps.delete import StepDelete
from .steps.main_menu import StepMainMenu
from .steps.search_line import SearchLineStep
from .steps.search_stop_area import SearchStopAreaStep
from .steps.select_line import SelectLineStep
from .steps.select_stop_area import StepSelectStopArea
from .steps.update_api import StepUpdateApi

# Mixins de steps
from .steps.user import StepUser

# ---------------------------------------------------------
# ⭐ Générateur automatique de méthodes async_step_*
# ---------------------------------------------------------


def inject_step_methods(target_cls, *mixins):
    """Copie les méthodes async_step_* des mixins dans la classe cible."""
    for mixin in mixins:
        for name, method in mixin.__dict__.items():
            if name.startswith("async_step_") and callable(method):
                # On crée une closure qui appelle la méthode du mixin
                async def wrapper(self, user_input=None, _method=method):
                    return await _method(self, user_input)

                setattr(target_cls, name, wrapper)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.entry = None
        self.api_key = None
        self._search_results = {}
        self._selected_stop_area = None
        self._first_line_name = None
        self._first_line = False


# ---------------------------------------------------------
# ⭐ Injection des steps dans ConfigFlow
# ---------------------------------------------------------

inject_step_methods(
    ConfigFlow,
    StepUser,
    SearchStopAreaStep,
    StepSelectStopArea,
    StepMainMenu,
    SearchLineStep,
    SelectLineStep,
    StepDelete,
    StepUpdateApi,
)

"""Flux de configuration pour l’intégration IDF Mobilité Assistant.

Ce module gère la génération dynamique des méthodes `async_step_*`
à partir des mixins de steps, ainsi que la classe principale `ConfigFlow`.
"""

from homeassistant import config_entries

from .const import DOMAIN
from .steps.delete import StepDelete
from .steps.main_menu import StepMainMenu
from .steps.search_line import SearchLineStep
from .steps.search_stop_area import SearchStopAreaStep
from .steps.select_line import SelectLineStep
from .steps.select_stop_area import StepSelectStopArea
from .steps.update_api import StepUpdateApi
from .steps.user import StepUser


def inject_step_methods(target_cls, *mixins) -> None:
    """Injecter automatiquement les méthodes async_step_* dans la classe cible.

    Cette fonction parcourt les mixins fournis et copie toutes les méthodes
    commençant par `async_step_` dans la classe `target_cls`. Cela permet
    de composer dynamiquement le flux de configuration sans héritage multiple.
    """
    for mixin in mixins:
        for name, method in mixin.__dict__.items():
            if name.startswith("async_step_") and callable(method):

                async def wrapper(self, user_input=None, _method=method):
                    """Appeler la méthode du mixin correspondant."""
                    return await _method(self, user_input)

                setattr(target_cls, name, wrapper)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flux de configuration principal pour l’intégration IDF Mobilité Assistant."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialiser le flux de configuration.

        Initialise les variables internes utilisées par les différents steps.
        """
        self.entry = None
        self.api_key = None
        self._search_results = {}
        self._selected_stop_area = None
        self._first_line_name = None
        self._first_line = False


# ---------------------------------------------------------
# Injection des steps dans ConfigFlow
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

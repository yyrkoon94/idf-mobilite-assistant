"""Première étape du flux de configuration IDF Mobilité Assistant.

Cette étape demande la clé API si aucune configuration n’existe encore.
Si une config_entry est déjà présente, l’utilisateur est redirigé
directement vers le menu principal.
"""

import voluptuous as vol

from ..const import CONF_API_KEY  # noqa: TID252


class StepUser:
    """Étape initiale du flux : saisie de la clé API."""

    api_key: str | None = None
    entry: object | None = None

    async def async_step_user(self, user_input=None):
        """Afficher le formulaire de saisie de la clé API ou accéder au menu.

        - Si une config_entry existe déjà : redirection immédiate vers le menu.
        - Si `user_input` est fourni : validation et passage à l’étape suivante.
        - Sinon : affichage du formulaire de saisie.
        """
        # Si une entrée existe déjà → on saute directement au menu principal
        existing = self._async_current_entries()
        if existing:
            self.entry = existing[0]
            return await self.async_step_main_menu()

        # Si l'utilisateur a soumis le formulaire
        if user_input is not None:
            self.api_key = user_input[CONF_API_KEY]
            return await self.async_step_search_stop_area()

        # Formulaire vierge
        schema = vol.Schema({vol.Required(CONF_API_KEY): str})

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors={},  # propre, même si vide
            description_placeholders={},  # requis si strings.json contient {placeholders}
        )

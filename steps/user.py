import voluptuous as vol
from ..const import CONF_API_KEY


class StepUser:
    async def async_step_user(self, user_input=None):
        """Première étape : saisie de l'API key ou accès au menu si déjà configuré."""

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

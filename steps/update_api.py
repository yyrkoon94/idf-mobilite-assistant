import voluptuous as vol


class StepUpdateApi:
    async def async_step_update_api_key(self, user_input=None):
        """Mise à jour de l'API Key."""
        errors = {}

        # API Key actuelle (si existante)
        current_key = self.entry.data.get("api_key", "")

        # Si l'utilisateur a soumis quelque chose
        if user_input is not None:
            key = user_input["api_key"].strip()

            # Toujours mémoriser la dernière saisie
            self._last_api_key = key

            # Gestion du bouton retour
            if key == "__back__":
                return await self.async_step_main_menu()

            # Vérification basique
            if not key:
                errors["base"] = "api_key_empty"

            else:
                # Mise à jour de la config_entry
                new_data = {
                    **self.entry.data,
                    "api_key": key,
                }

                self.hass.config_entries.async_update_entry(self.entry, data=new_data)

                # Reload propre
                await self.hass.config_entries.async_reload(self.entry.entry_id)

                # Retour au menu
                return await self.async_step_main_menu()

        # Valeur par défaut du champ (dernière saisie ou clé actuelle)
        default_key = getattr(self, "_last_api_key", current_key)

        # Schéma avec option retour
        schema = vol.Schema({vol.Required("api_key", default=default_key): str})

        return self.async_show_form(
            step_id="update_api_key",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "current_key": current_key or "Aucune clé enregistrée"
            },
        )

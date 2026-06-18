import voluptuous as vol
from ..utils.navitia_line_search import search_navitia_lines
from ..const import MODE_LABELS, PLACEHOLDERS


class SearchLineStep:
    async def async_step_search_line(self, user_input=None):
        errors = {}

        if user_input is not None:
            mode = user_input["mode"]
            code = user_input["code"]

            # Toujours sauvegarder les valeurs saisies
            self._mode = mode
            self._code = code

            # Validation
            if mode == "all" and not code.strip():
                errors["base"] = "empty_code"

            else:
                api_key = self.entry.data.get("api_key")
                clean_code = code.strip().upper()

                results = await search_navitia_lines(api_key, mode, clean_code)

                if not results:
                    errors["base"] = "no_results"
                else:
                    self._line_results = results
                    return await self.async_step_select_line()

        # Relire les valeurs après validation
        default_mode = getattr(self, "_mode", "all")
        default_code = getattr(self, "_code", "")

        placeholder = PLACEHOLDERS.get(default_mode, PLACEHOLDERS["all"])

        schema = vol.Schema(
            {
                vol.Required("mode", default=default_mode): vol.In(MODE_LABELS),
                vol.Optional("code", default=default_code): str,
            }
        )

        return self.async_show_form(
            step_id="search_line",
            data_schema=schema,
            description_placeholders={"placeholder": placeholder},
            errors=errors,
        )

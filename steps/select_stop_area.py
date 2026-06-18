import voluptuous as vol
import uuid
from ..const import CONF_NAME
from ..const import ICON_MAP


class StepSelectStopArea:
    async def async_step_select_stop_area(self, user_input=None):
        """Page 3 : sélection de l'arrêt + nom de la ligne."""

        results = self._search_results  # dict {ref: {label, arr_type, name, town}}
        errors = {}

        selected = None
        default_name = ""

        # -------------------------
        # Soumission du formulaire
        # -------------------------
        if user_input:
            selected = user_input.get("selected_stop_area")

            if selected == "__back__":
                return await self.async_step_search_stop_area()

            raw_name = user_input.get(CONF_NAME)

            if selected:
                stop_info = results[selected]

                # CAS 1 : première entrée
                if self.entry is None:
                    lignes = [
                        {
                            "uuid": str(uuid.uuid4()),
                            "name": raw_name,
                            "stop_name": stop_info["name"],
                            "town": stop_info["town"],
                            "monitoring_ref": selected,
                            "arr_type": stop_info["arr_type"],
                        }
                    ]

                    return self.async_create_entry(
                        title="IDF Mobilité Assistant",
                        data={
                            "api_key": self.api_key,
                            "lignes": lignes,
                        },
                    )

                # CAS 2 : entrée existante
                lignes = list(self.entry.data.get("lignes", []))

                lignes.append(
                    {
                        "uuid": str(uuid.uuid4()),
                        "name": raw_name,
                        "stop_name": stop_info["name"],
                        "town": stop_info["town"],
                        "monitoring_ref": selected,
                        "arr_type": stop_info["arr_type"],
                    }
                )

                new_data = {**self.entry.data, "lignes": lignes}
                self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                await self.hass.config_entries.async_reload(self.entry.entry_id)

                return await self.async_step_main_menu()

            if selected:
                default_name = f"{results[selected]['name']}"

        # -------------------------
        # Construction du menu déroulant
        # -------------------------
        options = {"__back__": "⬅️ Retour à la recherche"}

        for ref, info in results.items():
            icon = ICON_MAP.get(info["arr_type"], "❓")

            indent = " " * info.get("indent", 0)  # espace insécable large

            options[ref] = f"{indent}{icon} {info['label']}"

        schema = vol.Schema(
            {
                vol.Required("selected_stop_area", default=selected): vol.In(options),
                vol.Optional(CONF_NAME, default=default_name): str,
            }
        )

        return self.async_show_form(
            step_id="select_stop_area",
            data_schema=schema,
            errors=errors,
            description_placeholders={},  # requis si strings.json contient {placeholders}
        )

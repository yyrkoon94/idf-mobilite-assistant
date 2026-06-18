"""Étape de sélection d’une ligne Navitia dans le flux de configuration.

Cette étape affiche les lignes trouvées lors de la recherche précédente
et permet à l’utilisateur d’en sélectionner une pour créer ou mettre à jour
un capteur de messages.
"""

import uuid

import voluptuous as vol

from ..const import ICON_MAP, MODE_LABELS  # noqa: TID252


class SelectLineStep:
    """Étape du flux permettant de sélectionner une ligne Navitia."""

    _line_results: list | None = None

    async def async_step_select_line(self, user_input=None):
        """Afficher la liste des lignes trouvées et traiter la sélection.

        - Si `user_input` est fourni : validation du choix, création ou mise à jour
          du capteur correspondant.
        - Sinon : affichage du menu listant les lignes disponibles.
        """
        errors = {}

        results = getattr(self, "_line_results", None)
        if not results:
            return await self.async_step_search_line()

        # Soumission
        if user_input is not None:
            selected = user_input.get("selected_line")

            if selected == "__back__":
                return await self.async_step_search_line()

            # results contient déjà des lignes Navitia
            line = next((r for r in results if r["id"] == selected), None)

            if line:
                # Extraction des infos utiles
                line_id = line["id"]
                code = line.get("code", "")
                cm = line.get("commercial_mode", {}).get("name", "")

                # CAS 1 : première entrée
                if self.entry is None:
                    sensor_name = f"Messages {cm} {code}"

                    messages = {
                        "uuid": str(uuid.uuid4()),
                        "name": sensor_name,
                        "line_id": line_id,
                        "line_type": cm,
                        "code": code,
                    }

                    return self.async_create_entry(
                        title="IDF Mobilité Assistant",
                        data={
                            "api_key": self.api_key,
                            "messages": messages,  # ⭐ PAS de lignes ici
                        },
                    )

                # CAS 2 : entrée existante
                entry_data = self.entry.data

                # On récupère les messages existants ou une liste vide
                messages = list(entry_data.get("messages", []))

                sensor_name = f"Messages {cm} {code}"

                messages.append(
                    {
                        "uuid": str(uuid.uuid4()),
                        "name": sensor_name,
                        "line_id": line_id,
                        "line_type": cm,
                        "code": code,
                    }
                )

                # On met à jour uniquement messages
                new_data = {**entry_data, "messages": messages}

                self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                await self.hass.config_entries.async_reload(self.entry.entry_id)

                return await self.async_step_main_menu()

            errors["base"] = "invalid_selection"

        # Construction du menu
        options = {"__back__": "⬅️ Retour à la recherche"}

        # Mapping inverse MODE_LABELS → clé
        mode_by_label = {
            value.split(" ", 1)[1].lower(): key
            for key, value in MODE_LABELS.items()
            if key != "all"
        }

        def detect_mode(line):
            """Détermine le mode (clé ICON_MAP) à partir du commercial_mode + code."""
            cm = (line.get("commercial_mode", {}).get("name") or "").lower()
            code = (line.get("code") or "").upper()

            rules = [
                ("night_bus", lambda: code.startswith("N")),
                ("cableway", lambda: "cable" in cm or "téléph" in cm),
                ("ter", lambda: "ter" in cm or "interc" in cm),
                ("transilien", lambda: "transilien" in cm),
            ]

            for mode_key, condition in rules:
                if condition():
                    return mode_key

            # fallback MODE_LABELS
            for label, key in mode_by_label.items():
                if label in cm:
                    return key

            return "other"

        for line in results:
            mode_key = detect_mode(line)
            icon = ICON_MAP.get(mode_key, "❓")

            cm_name = line.get("commercial_mode", {}).get("name", "")
            name = line.get("name", "")

            # TER → pas de cm_name dans le label
            display_cm = "" if cm_name == "TER" else cm_name

            label = f"{icon} {display_cm} {name}".strip()

            options[line["id"]] = label

        # Tri
        options = dict(sorted(options.items(), key=lambda x: x[1]))

        schema = vol.Schema({vol.Required("selected_line"): vol.In(options)})

        return self.async_show_form(
            step_id="select_line",
            data_schema=schema,
            errors=errors,
        )

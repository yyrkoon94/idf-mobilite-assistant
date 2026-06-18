"""Étape de suppression d'une ligne ou d'un message dans le flux de configuration.

Cette étape permet :
- d'afficher toutes les lignes et messages existants,
- de proposer un tri alphabétique,
- de supprimer proprement l'entité Home Assistant,
- de mettre à jour la config_entry,
- de revenir au menu principal.
"""

import voluptuous as vol

from homeassistant.helpers import entity_registry as er

from idf_mobilite_assistant.const import DOMAIN, ICON_MAP


class StepDelete:
    """Étape du flux de configuration permettant de supprimer une ligne ou un message."""

    async def async_step_delete(self, user_input=None):
        """Afficher la liste des éléments supprimables et traiter la suppression."""

        # Récupération des données actuelles de la config_entry
        lignes = list(self.entry.data.get("lignes", []))
        messages = list(self.entry.data.get("messages", []))

        # ---------------------------------------------------------
        # CONSTRUCTION DE LA LISTE DES CHOIX (lignes + messages)
        # ---------------------------------------------------------
        entries: list[tuple[str, str]] = []

        # --- LIGNES ---
        for i, l in enumerate(lignes):
            arr_type = l.get("arr_type")
            icon = ICON_MAP.get(arr_type, "❓")

            name = l.get("name")
            stop_name = l.get("stop_name")
            town = l.get("town", "")
            if name:
                full_name = f"{name}"
            else:
                full_name = f"{stop_name} ({town})"
            # Multimodal → suffixe explicite
            if arr_type == "multimodal":
                label = f"{icon} {full_name} – Multimodal"
            else:
                label = f"{icon} {full_name}"

            # clé interne (ligne_i), label affiché
            entries.append((f"ligne_{i}", label))

        # --- MESSAGES ---
        for i, m in enumerate(messages):
            arr_type = m.get("arr_type")
            icon = "💬"

            name = m.get("name", "Inconnu")
            town = m.get("town", "")
            town_str = f" ({town})" if town else ""

            if arr_type == "multimodal":
                label = f"{icon} {name}{town_str} – Multimodal"
            else:
                label = f"{icon} {name}{town_str}"

            entries.append((f"msg_{i}", label))

        # Si aucune entrée, on arrête proprement
        if not entries:
            return self.async_abort(reason="no_entries")

        # ---------------------------------------------------------
        # TRI ALPHABÉTIQUE GLOBAL (en ignorant l'icône)
        # ---------------------------------------------------------
        def sort_key(entry: tuple[str, str]) -> str:
            key, label = entry
            # On enlève l'icône + l'espace initial, s'il y en a un
            parts = label.split(" ", 1)
            return parts[1] if len(parts) == 2 else label

        entries.sort(key=sort_key)

        # ---------------------------------------------------------
        # AJOUT DE L'OPTION RETOUR
        # ---------------------------------------------------------
        choices = {"__back__": "⬅️ Retour"}

        # Dictionnaire final pour vol.In
        choices.update({key: label for key, label in entries})

        # ---------------------------------------------------------
        # TRAITEMENT DE LA SUPPRESSION (après choix utilisateur)
        # ---------------------------------------------------------
        if user_input is not None:
            key = user_input["entry"]

            if key == "__back__":
                return await self.async_step_main_menu()

            entity_registry = er.async_get(self.hass)

            # Suppression d'une ligne
            if key.startswith("ligne_"):
                idx = int(key.split("_")[1])
                uuid = lignes[idx]["uuid"]

                unique_id = f"{DOMAIN}_ligne_{uuid}"

                # On supprime l'entité du registry si elle existe
                entity_id = entity_registry.async_get_entity_id(
                    "sensor", DOMAIN, unique_id
                )
                if entity_id:
                    entity_registry.async_remove(entity_id)

                # On retire la ligne de la config_entry
                lignes.pop(idx)

            # Suppression d'un message
            if key.startswith("msg_"):
                idx = int(key.split("_")[1])
                uuid = messages[idx]["uuid"]

                unique_id = f"{DOMAIN}_messages_{uuid}"

                entity_id = entity_registry.async_get_entity_id(
                    "sensor", DOMAIN, unique_id
                )
                if entity_id:
                    entity_registry.async_remove(entity_id)

                messages.pop(idx)

            # Mise à jour de la config_entry avec les listes modifiées
            new_data = {
                **self.entry.data,
                "lignes": lignes,
                "messages": messages,
            }
            self.hass.config_entries.async_update_entry(self.entry, data=new_data)

            # Reload propre de l'intégration
            await self.hass.config_entries.async_reload(self.entry.entry_id)

            # On boucle si on veut en supprimer d'autre
            return await self.async_step_delete()

        # ---------------------------------------------------------
        # FORMULAIRE DE SÉLECTION DES SENSOR
        # ---------------------------------------------------------
        schema = vol.Schema({vol.Required("entry"): vol.In(choices)})

        return self.async_show_form(
            step_id="delete",
            data_schema=schema,
            errors={},
            description_placeholders={},  # requis si strings.json contient {placeholders}
        )

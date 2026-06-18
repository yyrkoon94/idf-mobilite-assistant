"""Étape principale du flux de configuration IDF Mobilité Assistant.

Ce module contient le menu principal permettant à l’utilisateur de :
- ajouter une ligne,
- ajouter un message,
- supprimer un élément existant,
- mettre à jour la clé API.
"""

import voluptuous as vol

from ..const import (  # noqa: TID252
    MENU_ADD_LIGNE,
    MENU_ADD_MESSAGE,
    MENU_DELETE,
    MENU_UPDATE_API,
)


class StepMainMenu:
    """Menu principal du flux de configuration.

    Cette étape sert de hub central : elle redirige l’utilisateur vers les
    différentes sous‑étapes (ajout de ligne, ajout de message, suppression,
    mise à jour de la clé API).
    """

    async def async_step_main_menu(self, user_input=None):
        """Afficher le menu principal et traiter la sélection utilisateur.

        Si `user_input` est fourni, l’étape correspondante est exécutée.
        Sinon, un formulaire listant les actions disponibles est affiché.
        """
        if user_input is not None:
            choice = user_input["menu"]

            if choice == MENU_ADD_LIGNE:
                return await self.async_step_search_stop_area()

            if choice == MENU_ADD_MESSAGE:
                return await self.async_step_search_line()

            if choice == MENU_DELETE:
                return await self.async_step_delete()

            if choice == MENU_UPDATE_API:
                return await self.async_step_update_api_key()

        schema = vol.Schema(
            {
                vol.Required("menu"): vol.In(
                    {
                        MENU_ADD_LIGNE: "➕ Ajouter une ligne",
                        MENU_ADD_MESSAGE: "📝 Ajouter un message",
                        MENU_DELETE: "🗑️ Supprimer un élément",
                        MENU_UPDATE_API: "🔑 Mettre à jour la clé API",
                    }
                )
            }
        )

        return self.async_show_form(
            step_id="main_menu",
            data_schema=schema,
            errors={},
            description_placeholders={},  # requis si strings.json contient {placeholders}
        )

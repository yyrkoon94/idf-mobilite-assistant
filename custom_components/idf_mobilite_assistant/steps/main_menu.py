import voluptuous as vol

from ..const import (
    MENU_ADD_LIGNE,
    MENU_ADD_MESSAGE,
    MENU_DELETE,
    MENU_UPDATE_API,
)


class StepMainMenu:
    async def async_step_main_menu(self, user_input=None):
        """Menu principal pour gérer lignes et messages."""

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

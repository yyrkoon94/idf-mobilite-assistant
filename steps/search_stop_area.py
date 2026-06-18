"""Étape de recherche d’un arrêt IDFM dans le flux de configuration.

Cette étape permet à l’utilisateur de saisir un nom d’arrêt, puis interroge
l’API open data IDFM pour récupérer les zones d’arrêt correspondantes.
"""

import voluptuous as vol

from ..utils.prim_stop_area_search import search_local_stop_areas  # noqa: TID252


class SearchStopAreaStep:
    """Étape du flux permettant de rechercher un arrêt IDFM."""

    _query: str | None = None
    _search_results: dict | None = None

    async def async_step_search_stop_area(self, user_input=None):
        """Afficher le formulaire de recherche et traiter la validation.

        - Si `user_input` est fourni : validation de la requête, appel API,
          puis passage à l’étape suivante si des résultats existent.
        - Sinon : affichage du formulaire avec la dernière valeur saisie.
        """
        errors = {}

        if user_input is not None:
            query = user_input["search"].strip()

            # Toujours mémoriser la dernière saisie
            self._query = query

            # Vérification longueur minimale
            if len(query) < 3:
                errors["base"] = "query_too_short"

            else:
                # Recherche asynchrone
                results = await search_local_stop_areas(query)

                if not results:
                    errors["base"] = "no_results"
                else:
                    # Succès → on stocke les résultats et on passe à l'étape suivante
                    self._search_results = results
                    return await self.async_step_select_stop_area()

        # Valeur par défaut du champ (dernière saisie)
        default_query = getattr(self, "_query", "")

        schema = vol.Schema({vol.Required("search", default=default_query): str})

        return self.async_show_form(
            step_id="search_stop_area",
            data_schema=schema,
            errors=errors,
            description_placeholders={},  # requis si strings.json contient {placeholders}
        )

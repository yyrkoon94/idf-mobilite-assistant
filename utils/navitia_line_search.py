"""Fonctions utilitaires pour interroger l’API Navitia via PRIM.

Ce module fournit la fonction `search_navitia_lines` permettant de rechercher
des lignes de transport en fonction d’un mode (bus, métro, tram…) et d’un code.
"""

import asyncio

import aiohttp

NAVITIA_BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia"

# Mapping mode → physical_modes Navitia
MODE_TO_NAVITIA = {
    "bus": ["Bus"],
    "metro": ["Métro"],
    "tram": ["Tramway"],
    "rer": ["RER"],
    "ter": ["TER"],
    "transilien": ["Train Transilien"],
    "cableway": ["CableWay"],
    "noctilien": ["Bus"],  # filtré ensuite par code N*
    "all": [],
}


async def search_navitia_lines(api_key: str, mode: str, code: str):
    """Recherche de lignes Navitia filtrée par mode + code.

    Version optimisée :
    - mode "all" → /places + depth=2 → récupère toutes les lignes directement
    - autres modes → /pt_objects.
    """

    # -------------------------------
    # 1) MODE "ALL" → recherche globale
    # -------------------------------
    if mode == "all":
        params = {
            "q": code,
            "type[]": "stop_area",
            "depth": "2",
            "count": "200",
            "display_geojson": "false",
        }

        async with (
            aiohttp.ClientSession() as session,
            asyncio.timeout(5),
            session.get(
                f"{NAVITIA_BASE_URL}/places",
                headers={"apiKey": api_key},
                params=params,
                ssl=False,
            ) as resp,
        ):
            if resp.status != 200:
                return []

            data = await resp.json()
            places = data.get("places", [])

            lines = []

            for obj in places:
                if obj.get("embedded_type") == "stop_area":
                    sa = obj["stop_area"]
                    for line in sa.get("lines", []):
                        lines.append(line)

                elif obj.get("embedded_type") == "line":
                    lines.append(obj["line"])

                elif obj.get("embedded_type") == "route":
                    lines.append(obj["route"]["line"])

            # Déduplication
            unique = {line["id"]: line for line in lines}
            return list(unique.values())

    # -------------------------------
    # 2) AUTRES MODES → /pt_objects
    # -------------------------------

    true_mode = mode
    true_code = code

    # Préfixes intelligents
    if mode == "noctilien":
        true_mode = "bus"
        if not code.upper().startswith("N"):
            true_code = "N" + code

    if mode == "tram":
        if not code.upper().startswith("T"):
            true_code = "T" + code

    if mode == "all":
        true_mode = ""

    params = {
        "q": f"{true_mode} {true_code}".strip(),
        "type[]": "line",
        "display_geojson": "false",
        "count": "500",
    }

    async with (
        aiohttp.ClientSession() as session,
        session.get(
            f"{NAVITIA_BASE_URL}/pt_objects",
            headers={"apiKey": api_key},
            params=params,
            ssl=False,
        ) as resp,
    ):
        if resp.status != 200:
            return []

        data = await resp.json()
        results = data.get("pt_objects", [])

        # Filtrage par mode
        if mode == "noctilien":
            return [
                r["line"] for r in results if r["line"]["code"].upper().startswith("N")
            ]

        allowed = MODE_TO_NAVITIA[mode]

        return [
            r["line"]
            for r in results
            if any(a in r["line"]["commercial_mode"]["name"] for a in allowed)
        ]

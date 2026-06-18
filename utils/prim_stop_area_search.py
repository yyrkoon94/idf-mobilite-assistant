import aiohttp
import async_timeout
from collections import OrderedDict

IDFM_URL = "https://data.iledefrance-mobilites.fr/api/records/1.0/search/"

TYPE_MAP = {
    "onstreetBus": "bus",
    "onstreetTram": "tram",
    "railStation": "rail",
    "metroStation": "metro",
    "liftStation": "lift",
}


async def search_local_stop_areas(query: str):
    query = query.strip()
    if not query:
        return {}

    params = {
        "dataset": "zones-d-arrets",
        "q": query,
        "rows": 100,
    }

    try:
        async with aiohttp.ClientSession() as session:
            with async_timeout.timeout(5):
                async with session.get(IDFM_URL, params=params) as resp:
                    data = await resp.json()
    except Exception:
        return {}

    records = data.get("records", [])
    if not records:
        return {}

    raw_results = {}
    groups = {}

    # ---------------------------------------------------------
    # 1) Arrêts individuels
    # ---------------------------------------------------------
    for rec in records:
        fields = rec.get("fields", {})
        zdaid = fields.get("zdaid")
        zdacid = fields.get("zdcid")
        name = fields.get("zdaname", "").strip()
        town = fields.get("zdatown", "").strip()
        zdatype = fields.get("zdatype", "").strip()

        if not zdaid or not name:
            continue

        zdaid = str(zdaid)
        zdacid = str(zdacid) if zdacid else None
        arr_type = TYPE_MAP.get(zdatype, "other")

        ref = f"STIF:StopArea:SP:{zdaid}:"
        label = f"{name} ({town})" if town else name

        raw_results[ref] = {
            "label": label,
            "name": name,
            "town": town,
            "zdaid": zdaid,
            "zdacid": zdacid,
            "zdatype": zdatype,
            "arr_type": arr_type,
            "is_group": False,
        }

        # Regroupement multimodal
        if zdacid:
            if zdacid not in groups:
                groups[zdacid] = {
                    "name": name,
                    "town": town,
                    "types": set(),
                    "zdaids": set(),
                }
            groups[zdacid]["types"].add(zdatype)
            groups[zdacid]["zdaids"].add(zdaid)

    # ---------------------------------------------------------
    # 2) Ajout des multimodaux
    # ---------------------------------------------------------
    for zdacid, info in groups.items():
        if len(info["zdaids"]) < 2:
            continue

        ref = f"STIF:StopArea:SP:{zdacid}:"
        label = (
            f"{info['name']} ({info['town']}) – Multimodal"
            if info["town"]
            else f"{info['name']} – Multimodal"
        )

        raw_results[ref] = {
            "label": label,
            "name": info["name"],
            "town": info["town"],
            "zdaid": None,
            "zdacid": zdacid,
            "zdatype": None,
            "arr_type": "multimodal",
            "is_group": True,
            "group_types": list(info["types"]),
        }

    # ---------------------------------------------------------
    # 3) Construction triée : isolés → multimodaux → enfants
    # ---------------------------------------------------------
    # --- 3) Construction triée : multimodaux → enfants → isolés ---
    ordered = OrderedDict()

    # 3A) Multimodaux triés
    multimodals = [
        (zdacid, info) for zdacid, info in groups.items() if len(info["zdaids"]) >= 2
    ]

    multimodals_sorted = sorted(
        multimodals, key=lambda x: raw_results[f"STIF:StopArea:SP:{x[0]}:"]["label"]
    )

    for zdacid, info in multimodals_sorted:
        multimodal_ref = f"STIF:StopArea:SP:{zdacid}:"
        entry = raw_results[multimodal_ref]
        entry["indent"] = 0
        ordered[multimodal_ref] = entry

        # enfants triés
        children_sorted = sorted(
            info["zdaids"],
            key=lambda zdaid: raw_results[f"STIF:StopArea:SP:{zdaid}:"]["label"],
        )

        for zdaid in children_sorted:
            ref = f"STIF:StopArea:SP:{zdaid}:"
            if ref in raw_results:
                child = raw_results[ref]
                child["indent"] = 1
                ordered[ref] = child

    # 3B) Arrêts isolés triés
    # zdaid appartenant à un vrai multimodal
    multimodal_zdaids = set()
    for zdacid, info in groups.items():
        if len(info["zdaids"]) >= 2:
            multimodal_zdaids.update(info["zdaids"])

    isolated = [
        (ref, data)
        for ref, data in raw_results.items()
        if not data.get("is_group") and data.get("zdaid") not in multimodal_zdaids
    ]

    isolated_sorted = sorted(isolated, key=lambda x: x[1]["label"])

    for ref, data in isolated_sorted:
        data["indent"] = 0
        ordered[ref] = data

    return ordered

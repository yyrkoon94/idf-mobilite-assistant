from __future__ import annotations

import logging
import aiohttp
import async_timeout
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)

SESSION_KEY = "idf_mobilite_session"


# ============================================================
#  SETUP ENTRY
# ============================================================


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Créer toutes les entités (Lignes + Messages) pour une seule entry."""

    if SESSION_KEY not in hass.data:
        hass.data[SESSION_KEY] = aiohttp.ClientSession()

    session = hass.data[SESSION_KEY]

    lignes = entry.data.get("lignes", [])
    messages = entry.data.get("messages", [])

    entities: list[SensorEntity] = []

    for ligne in lignes:
        entities.append(
            PRIMLigneSensor(
                uuid=ligne["uuid"],
                name=ligne["name"],
                stop_name=ligne["stop_name"],
                town=ligne["town"],
                monitoring_ref=ligne["monitoring_ref"],
                arr_type=ligne["arr_type"],
                entry=entry,
                session=session,
            )
        )

    for msg in messages:
        entities.append(
            PRIMMessageSensor(
                uuid=msg["uuid"],
                name=msg["name"],
                line_id=msg["line_id"],
                line_type=msg["line_type"],
                entry=entry,
                session=session,
            )
        )

    async_add_entities(entities, update_before_add=True)

    scan_interval = 60
    for entity in entities:
        entry.async_on_unload(
            async_track_time_interval(
                hass, entity.async_update, timedelta(seconds=scan_interval)
            )
        )


# ============================================================
#  BASE SENSOR FACTORISÉ
# ============================================================


class PRIMBaseSensor(SensorEntity):
    """Base commune pour les capteurs PRIM."""

    _timeout = 30
    _verify_ssl = False

    def __init__(self, entry: ConfigEntry, session: aiohttp.ClientSession):
        self._entry_id = entry.entry_id
        self._session = session
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    # -------------------------
    # API KEY dynamique
    # -------------------------
    @property
    def api_key(self):
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        return entry.data.get(CONF_API_KEY)

    # -------------------------
    # Méthode générique d'appel API
    # -------------------------
    async def _fetch_json(self, url: str, params: dict):
        try:
            with async_timeout.timeout(self._timeout):
                async with self._session.get(
                    url,
                    headers={"apiKey": self.api_key},
                    params=params,
                    ssl=self._verify_ssl,
                ) as resp:
                    status = resp.status

                    # Succès
                    if status == 200:
                        return "OK", await resp.json()

                    # API KEY invalide
                    if status in (401, 403):
                        return "API_KEY_ERROR", {"http_status": status}

                    # Rate limit
                    if status == 429:
                        return "RATE_LIMIT", {"http_status": status}

                    # Erreur serveur
                    if status >= 500:
                        return "SERVER_ERROR", {"http_status": status}

                    # Autres erreurs HTTP
                    return "HTTP_ERROR", {"http_status": status}

        except Exception as err:
            return "ERROR", {"error": str(err)}

    # -------------------------
    # Méthode commune de mise à jour
    # -------------------------
    async def _update_state(self, status: str, raw: dict):
        """À surcharger dans les classes enfants."""
        raise NotImplementedError

    async def async_update(self, *_):
        status, raw = await self._fetch_json(self._resource, self._params)
        await self._update_state(status, raw)


# ============================================================
#  SENSOR : LIGNES
# ============================================================


class PRIMLigneSensor(PRIMBaseSensor):
    """Sensor PRIM StopMonitoring (Lignes)."""

    def __init__(
        self, uuid, name, stop_name, town, monitoring_ref, arr_type, entry, session
    ):
        super().__init__(entry, session)

        self._uuid = uuid
        self._attr_stop_name = stop_name
        self._attr_town = town
        self._arr_type = arr_type
        self._monitoring_ref = monitoring_ref

        self._resource = (
            "https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring"
        )
        self._params = {"MonitoringRef": monitoring_ref}

        if name:
            self._attr_name = name
        else:
            suffix = " – Multimodal" if arr_type == "multimodal" else ""
            self._attr_name = f"{stop_name} ({town}){suffix}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, "lignes")},
            "name": "Lignes",
            "manufacturer": "PRIM",
        }

    @property
    def unique_id(self):
        return f"{DOMAIN}_ligne_{self._uuid}"

    @property
    def icon(self):
        return {
            "bus": "mdi:bus",
            "metro": "mdi:subway",
            "tram": "mdi:tram",
            "rail": "mdi:train",
            "cableway": "mdi:cable-car",
        }.get(self._arr_type, "mdi:train-bus")

    async def _update_state(self, status: str, raw: dict):
        self._attr_native_value = status

        if status == "OK":
            self._attr_extra_state_attributes = {
                "name": self._attr_stop_name,
                "town": self._attr_town,
                "monitoring_ref": self._monitoring_ref,
                "type": self._arr_type,
                "Siri": raw.get("Siri", {}),
                "http_status": 200,
            }
        else:
            self._attr_extra_state_attributes = {
                "name": self._attr_stop_name,
                "town": self._attr_town,
                "monitoring_ref": self._monitoring_ref,
                "type": self._arr_type,
                **raw,
            }


# ============================================================
#  SENSOR : MESSAGES
# ============================================================


class PRIMMessageSensor(PRIMBaseSensor):
    """Sensor PRIM Messages (Navitia line_reports)."""

    def __init__(self, uuid, name, line_id, line_type, entry, session):
        super().__init__(entry, session)

        self._uuid = uuid
        self._attr_name = name
        self._line_id = line_id
        self._line_type = line_type  # Bus, RER, Tramway…

        self._resource = (
            f"https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/"
            f"line_reports/lines/{line_id}/line_reports"
        )

        self._params = {
            "filter_status[]": "active",
            "disable_geojson": "true",
        }

        self._attr_icon = "mdi:message-bulleted"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "messages")},  # ⭐ un seul groupe
            "name": "Messages",
            "manufacturer": "PRIM",
        }

    @property
    def unique_id(self):
        return f"{DOMAIN}_messages_{self._uuid}"

    async def _update_state(self, status: str, raw: dict):
        self._attr_native_value = status

        if status == "OK":
            self._attr_extra_state_attributes = {
                "line_id": self._line_id,
                "line_type": self._line_type,
                "disruptions": raw.get("disruptions", []),
                "line_reports": raw.get("line_reports", []),
                "http_status": 200,
            }
        else:
            self._attr_extra_state_attributes = raw

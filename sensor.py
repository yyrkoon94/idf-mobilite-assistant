"""Plateformes de capteurs PRIM pour l’intégration IDF Mobilité Assistant.

Ce module gère :
- la création des entités (lignes + messages),
- la base factorisée des capteurs PRIM,
- les capteurs spécialisés StopMonitoring et Messages.
"""

import asyncio
from datetime import timedelta
import logging

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_API_KEY, DOMAIN

_LOGGER = logging.getLogger(__name__)

SESSION_KEY = "idf_mobilite_session"


# ============================================================
#  SETUP ENTRY
# ============================================================


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Créer toutes les entités (Lignes + Messages) pour une entrée de configuration.

    Cette fonction instancie les capteurs PRIMLigneSensor et PRIMMessageSensor
    en fonction des données stockées dans l’entrée.
    """
    if SESSION_KEY not in hass.data:
        hass.data[SESSION_KEY] = aiohttp.ClientSession()

    session = hass.data[SESSION_KEY]

    lignes = entry.data.get("lignes", [])
    messages = entry.data.get("messages", [])

    entities: list[SensorEntity] = []

    # Capteurs de lignes
    entities = [
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
        for ligne in lignes
    ]

    # Capteurs de messages
    entities += [
        PRIMMessageSensor(
            uuid=msg["uuid"],
            name=msg["name"],
            line_id=msg["line_id"],
            line_type=msg["line_type"],
            entry=entry,
            session=session,
        )
        for msg in messages
    ]

    async_add_entities(entities, update_before_add=True)

    # Mise à jour automatique
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
    """Classe de base commune pour les capteurs PRIM.

    Fournit :
    - stockage de l’entrée et de la session HTTP,
    - récupération dynamique de l’API key,
    - méthode générique d’appel API,
    - méthode de mise à jour commune.
    """

    _timeout = 30
    _verify_ssl = False

    def __init__(self, entry: ConfigEntry, session: aiohttp.ClientSession) -> None:
        """Initialiser le capteur de base."""
        self._entry_id = entry.entry_id
        self._session = session
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

    @property
    def api_key(self) -> str | None:
        """Retourner la clé API stockée dans l’entrée."""
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        return entry.data.get(CONF_API_KEY)

    async def _fetch_json(self, url: str, params: dict) -> tuple[str, dict]:
        """Effectuer un appel HTTP générique vers l’API PRIM.

        Retourne un tuple (status, payload) où `status` indique le type de réponse.
        """
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.get(
                    url,
                    headers={"apiKey": self.api_key},
                    params=params,
                    ssl=self._verify_ssl,
                ) as resp:
                    status = resp.status

                    if status == 200:
                        return "OK", await resp.json()

                    if status in (401, 403):
                        return "API_KEY_ERROR", {"http_status": status}

                    if status == 429:
                        return "RATE_LIMIT", {"http_status": status}

                    if status >= 500:
                        return "SERVER_ERROR", {"http_status": status}

                    return "HTTP_ERROR", {"http_status": status}

        except aiohttp.ClientError as err:
            return "CLIENT_ERROR", {"error": str(err)}

        except ValueError as err:
            return "INVALID_JSON", {"error": str(err)}

        except Exception as err:
            _LOGGER.exception("Erreur inattendue lors de l'appel API PRIM: %s", err)
            return "ERROR", {"error": str(err)}

    async def _update_state(self, status: str, raw: dict) -> None:
        """Mettre à jour l’état du capteur (à surcharger dans les classes enfants)."""
        raise NotImplementedError

    async def async_update(self, *_: object) -> None:
        """Mettre à jour le capteur en appelant l’API PRIM."""
        status, raw = await self._fetch_json(self._resource, self._params)
        await self._update_state(status, raw)


# ============================================================
#  SENSOR : LIGNES
# ============================================================


class PRIMLigneSensor(PRIMBaseSensor):
    """Capteur PRIM StopMonitoring (Lignes)."""

    def __init__(
        self,
        uuid: str,
        name: str,
        stop_name: str,
        town: str,
        monitoring_ref: str,
        arr_type: str,
        entry: ConfigEntry,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialiser un capteur de ligne PRIM."""
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
    def unique_id(self) -> str:
        """Retourner l’identifiant unique du capteur."""
        return f"{DOMAIN}_ligne_{self._uuid}"

    @property
    def icon(self) -> str:
        """Retourner l’icône correspondant au type de ligne."""
        return {
            "bus": "mdi:bus",
            "metro": "mdi:subway",
            "tram": "mdi:tram",
            "rail": "mdi:train",
            "cableway": "mdi:cable-car",
        }.get(self._arr_type, "mdi:train-bus")

    async def _update_state(self, status: str, raw: dict) -> None:
        """Mettre à jour l’état du capteur de ligne."""
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
    """Capteur PRIM Messages (Navitia line_reports)."""

    def __init__(
        self,
        uuid: str,
        name: str,
        line_id: str,
        line_type: str,
        entry: ConfigEntry,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialiser un capteur de messages PRIM."""
        super().__init__(entry, session)

        self._uuid = uuid
        self._attr_name = name
        self._line_id = line_id
        self._line_type = line_type

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
            "identifiers": {(DOMAIN, "messages")},
            "name": "Messages",
            "manufacturer": "PRIM",
        }

    @property
    def unique_id(self) -> str:
        """Retourner l’identifiant unique du capteur."""
        return f"{DOMAIN}_messages_{self._uuid}"

    async def _update_state(self, status: str, raw: dict) -> None:
        """Mettre à jour l’état du capteur de messages."""
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

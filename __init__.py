"""Logique d’initialisation de l’intégration IDF Mobilité Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configurer l’intégration via YAML.

    Cette intégration ne supporte pas la configuration YAML, mais cette
    fonction est requise par Home Assistant. Elle initialise simplement
    l’espace de stockage du domaine.
    """
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurer l’intégration lors de l’ajout d’une entrée de configuration.

    Cette fonction initialise les données du domaine et délègue la création
    des entités à la plateforme `sensor`.
    """
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharger l’intégration lors de la suppression d’une entrée de configuration.

    Cette fonction décharge toutes les plateformes associées à l’entrée.
    """
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

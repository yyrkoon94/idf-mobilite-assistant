"""Constantes globales pour l’intégration IDF Mobilité Assistant.

Ce module regroupe les clés de configuration, les actions de menu,
ainsi que les mappings d’icônes et de libellés utilisés dans l’interface
et les flux de configuration.
"""

DOMAIN = "idf_mobilite_assistant"

# Clés de configuration
CONF_API_KEY = "api_key"
CONF_MONITORING_REF = "monitoring_ref"
CONF_NAME = "name"
CONF_STOP_ID = "stop_id"

# Actions du menu principal
MENU_ADD_LIGNE = "add_ligne"
MENU_ADD_MESSAGE = "add_message"
MENU_DELETE = "delete"
MENU_UPDATE_API = "update_api"
MENU_EXIT = "exit"

# Icônes associées aux modes de transport
ICON_MAP = {
    "bus": "🚍",
    "metro": "🚇",
    "subway": "🚇",
    "tramway": "🚊",
    "tram": "🚊",
    "rail": "🚆",
    "transilien": "🚆",
    "ter": "🚆",
    "rer": "🚆",
    "cableway": "🚡",
    "rapidtransit": "🚆",
    "train": "🚈",
    "night_bus": "🌙",
    "multimodal": "🚆🚇🚍",
    "other": "❓",
}

# Libellés affichés dans les menus de sélection
MODE_LABELS = {
    "all": "🔍 Localisation (ex: Gare du Nord, Créteil)",
    "bus": "🚍 Bus",
    "metro": "🚇 Métro",
    "rer": "🚆 RER",
    "tram": "🚊 Tramway",
    "cableway": "🚡 Téléphérique",
    "transilien": "🚈 Transilien",
    "ter": "🚈 TER / Intercités",
    "noctilien": "🌙 Noctilien",
}

# Placeholders affichés dans les champs de recherche
PLACEHOLDERS = {
    "all": "Ex: Gare du Nord, Créteil",
    "bus": "Ex: 206, 210, 317",
    "metro": "Ex: 1, 7, 14",
    "rer": "Ex: A, B, C",
    "tram": "Ex: T1, T2, T3b",
    "transilien": "Ex: J, L, P",
    "noctilien": "Ex: N34, N130",
}

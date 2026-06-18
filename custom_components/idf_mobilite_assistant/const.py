DOMAIN = "idf_mobilite_assistant"

CONF_API_KEY = "api_key"
CONF_MONITORING_REF = "monitoring_ref"
CONF_NAME = "name"
CONF_STOP_ID = "stop_id"

# Menu actions
MENU_ADD_LIGNE = "add_ligne"
MENU_ADD_MESSAGE = "add_message"
MENU_DELETE = "delete"
MENU_UPDATE_API = "update_api"
MENU_EXIT = "exit"

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
    "rapidtransit": "🚆",  # RER
    "train": "🚈",  # Transilien
    "night_bus": "🌙",
    "multimodal": "🚆🚇🚍",
    "other": "❓",
}

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

PLACEHOLDERS = {
    "all": "Ex: Gare du Nord, Créteil",
    "bus": "Ex: 206, 210, 317",
    "metro": "Ex: 1, 7, 14",
    "rer": "Ex: A, B, C",
    "tram": "Ex: T1, T2, T3b",
    "transilien": "Ex: J, L, P",
    "noctilien": "Ex: N34, N130",
}

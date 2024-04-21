"""Constants for the SprinklerControl integration."""
from homeassistant.backports.enum import StrEnum

DOMAIN = "sprinklercontrol"

CONF_IP = "IP"

SC_VERSION = "1.0.0"
WATERING_TIME_KEY = "watering_time"
WATERING_MAX_TIME = 3600
WATERING_STATE = "watering_state"

SPRINKLER_DEFAULT_WATERING_TIME = 300

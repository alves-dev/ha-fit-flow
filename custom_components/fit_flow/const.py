"""Constants for FitFlow."""

from homeassistant.const import Platform

DOMAIN = "fit_flow"
INTEGRATION_NAME = "FitFlow"
INTEGRATION_VERSION = "2026.9.0"
PLATFORMS = (Platform.SENSOR,)
STORAGE_VERSION = 1
SIGNAL_UPDATE = f"{DOMAIN}_update"
EVENT_UPDATED = f"{DOMAIN}_updated"

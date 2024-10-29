"""
Support for Jarolift cover
"""
import logging
import voluptuous as vol
from homeassistant.components.cover import (
    CoverEntityFeature,
    PLATFORM_SCHEMA,
    CoverDeviceClass,
    CoverEntity,
)
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

CONF_COVERS = "covers"
CONF_GROUP = "group"
CONF_SERIAL = "serial"

_COVERS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Schema(
            {
                CONF_NAME: cv.string,
                CONF_GROUP: cv.string,
                CONF_SERIAL: cv.string,
            }
        )
    ],
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_COVERS): _COVERS_SCHEMA,
    }
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Jarolift covers."""
    covers = [JaroliftCover(cover[CONF_NAME], cover[CONF_GROUP], cover[CONF_SERIAL], hass) for cover in config[CONF_COVERS]]
    async_add_entities(covers)

class JaroliftCover(CoverEntity):
    """Representation of a Jarolift Cover."""

    def __init__(self, name, group, serial, hass):
        """Initialize the Jarolift device."""
        self._name = name
        self._group = group
        self._serial = serial
        self._hass = hass
        supported_features = (
            CoverEntityFeature.SET_TILT_POSITION | 
            CoverEntityFeature.OPEN |
            CoverEntityFeature.CLOSE |
            CoverEntityFeature.STOP
        )
        self._attr_supported_features = supported_features
        self._attr_device_class = CoverDeviceClass.BLIND

    @property
    def serial(self):
        """Return the serial of this cover."""
        return self._serial

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def group(self):
        """Return the group of the cover."""
        return self._group

    @property
    def should_poll(self):
        """No polling needed for Jarolift cover."""
        return False

    @property
    def is_closed(self):
        """Return true if cover is closed."""
        return None

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        await self._hass.services.async_call(
            "jarolift",
            "send_command",
            {"group": self._group, "serial": self._serial, "button": "0x8"},
        )

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self._hass.services.async_call(
            "jarolift",
            "send_command",
            {"group": self._group, "serial": self._serial, "button": "0x2"},
        )

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        await self._hass.services.async_call(
            "jarolift",
            "send_command",
            {"group": self._group, "serial": self._serial, "button": "0x4"},
        )

    async def async_set_cover_tilt_position(self, **kwargs):
        """Set the cover tilt position."""
        await self._hass.services.async_call(
            "jarolift",
            "send_command",
            {
                "group": self._group,
                "serial": self._serial,
                "button": "0x4",
                "hold": True,
            },
        )

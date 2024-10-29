"""
Support a 'Jarolift' remote as a separate remote.
"""

import base64
import binascii
import os
import logging
import aiofiles  # Für asynchronen Dateizugriff
from time import sleep
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

COUNTER_FILENAME = "mycounter.txt"
DOMAIN = "jarolift"
_LOGGER = logging.getLogger(__name__)

def bitRead(value, bit):
    return ((value) >> (bit)) & 0x01

def bitSet(value, bit):
    return (value) | (1 << (bit))

# KeeLoq Encryption bleibt gleich

async def async_read_counter(counter_file):
    """Lese Zähler asynchron."""
    if os.path.isfile(counter_file):
        async with aiofiles.open(counter_file, "r") as f:
            return int(await f.readline())
    return 0

async def async_write_counter(counter_file, counter):
    """Schreibe Zähler asynchron."""
    async with aiofiles.open(counter_file, "w") as f:
        await f.write(str(counter))

async def async_setup(hass, config):
    """Setup für die Jarolift-Remote."""
    remote_entity_id = config[DOMAIN]["remote_entity_id"]
    MSB = int(config[DOMAIN]["MSB"], 16)
    LSB = int(config[DOMAIN]["LSB"], 16)
    counter_file = hass.config.path(COUNTER_FILENAME)

    async def async_handle_send_command(call):
        Grouping = int(call.data.get("group", "0x0001"), 16)
        Serial = int(call.data.get("serial", "0x106aa01"), 16)
        Button = int(call.data.get("button", "0x2"), 16)
        Hold = call.data.get("hold", False)
        RCounter = await async_read_counter(counter_file)
        packet = BuildPacket(Grouping, Serial, Button, RCounter, MSB, LSB, Hold)
        await async_write_counter(counter_file, RCounter + 1)
        await hass.services.async_call(
            "remote",
            "send_command",
            {"entity_id": remote_entity_id, "command": [packet]},
        )

    hass.services.async_register(DOMAIN, "send_command", async_handle_send_command)
    return True

"""Support for RYD sensors."""
from typing import Set
import logging
import voluptuous as vol
from datetime import timedelta
from homeassistant import core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_URL, CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_interval


_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_URL): cv.url,
        vol.Required(CONF_EMAIL): cv.matches_regex(r".+@.+\..+"),
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


def setup_platform(hass: core.HomeAssistant, config: dict, add_devices, discovery_info=None) -> bool:
    """Set up the RYD Custom Component."""
    # @TODO: Add setup code.
    from pyryd import Ryd
    url = config.get(CONF_URL)
    email = config.get(CONF_EMAIL)
    password = config.get(CONF_PASSWORD)
    scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    ryd = Ryd(url,email,password)
    ryd_adapter = RydAdapter(ryd, add_devices)
    fetch = lambda: ryd_adapter.update()
    track_time_interval(hass, fetch, scan_interval)
    
    return True


class RydAdapter(Entity):
    """Representation of a ryd sensor."""
        
    def __init__(self, ryd, add_devices):
        self.ryd = ryd
        self._add_devices = add_devices
        self.values = {}
        self._sensors = set()
        self._registered_sensors : Set[RydTemplateSensor] = set()
    
    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            self.ryd.fetch()
        except ConnectionError:
            _LOGGER.error(
                "Failed to update: No Connection."
            )
            return

        self.values = self.ryd._ref_data
        # Add discovered value fields as sensors
        # because some fields are only sent temporarily
        new_sensors = []
        for key in self.values:
            if key not in self._sensors:
                self._sensors.add(key)
                _LOGGER.info("Discovered %s, adding as sensor", key)
                new_sensors.append(RydTemplateSensor(self, key))
        self._add_devices(new_sensors, True)

        # Schedule an update for all included sensors
        for sensor in self._registered_sensors:
            sensor.async_schedule_update_ha_state(True)

    async def register(self, sensor):
        """Register child sensor for update subscriptions."""
        self._registered_sensors.add(sensor)


class RydTemplateSensor(Entity):
    """Sensor for the single values (e.g. Fuel, Location...)."""

    def __init__(self, parent: RydAdapter, name):
        """Initialize a singular value sensor."""
        self._name = name
        self.parent = parent
        self._state = None
        self._unit = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name.replace('_', ' ').capitalize()} {self.parent.name}"

    @property
    def state(self):
        """Return the current state."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def should_poll(self):
        """Device should not be polled, returns False."""
        return False

    @property
    def available(self):
        """Whether the ryd device is active."""
        return self.parent.available

    async def async_update(self):
        """Update the internal state."""
        state = self.parent.values.get(self._name)
        self._state = state.get("value")
        self._unit = state.get("unit")

    async def async_added_to_hass(self):
        """Register at parent component for updates."""
        await self.parent.register(self)

    def __hash__(self):
        """Hash sensor by hashing its name."""
        return hash(self.name)

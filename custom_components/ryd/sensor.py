"""Support for RYD sensors."""
from typing import Optional, Dict, Any
import logging
import requests
import json
import uuid
import voluptuous as vol
from homeassistant import core
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_URL, CONF_EMAIL, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

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
    url = config.get(CONF_URL)
    email = config.get(CONF_EMAIL)
    password = config.get(CONF_PASSWORD)
    add_devices([RydSensor(url, email, password)])
    return True


class RydSensor(Entity):
    """Representation of a ryd sensor."""

    def __init__(self, url: str, email: str, password: str, hass, sensor_id, name):
        # copied from https://github.com/NemoN/ioBroker.ryd/blob/master/io-package.json
        self._ryd_api_server = url
        self._ryd_app_version = "2.52.4(201008000)"
        self._client_device_version = "9.0.0"
        self._client_device_resolution = "2960x1440"
        self._client_device_id = "SM-G960F"
        self._client_device_type = "Android"
        self._think_properties = "curLocation,parkingLocation,carOdometer,estimates,reportedFuelTotal,fuel"
        self._think_properties_ignore = "recurrences,openDtcs,score"
        self._ryd_app_locale = "de-de"
        self._ryd_app_internal_name = "TankTaler"
        self._ryd_app_platform = "{} [{},{},{}]".format(
            self._client_device_type, self._client_device_id, self._client_device_version, self._client_device_resolution
        )
        self._ryd_app_user_agent = "{}/{}({};{} {})".format(
            self._ryd_app_internal_name, self._ryd_app_version, self._client_device_id, self._client_device_type, self._client_device_version
        )
        self._data = json.dumps({"email": email, "password": password})
        self._headers = {
            'x-txn-platform': self._ryd_app_platform,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': str(0),
            'x-txn-app-version': self._ryd_app_version,
            'User-agent': self._ryd_app_user_agent,
            'X-Txn-Request-Id': str(uuid.uuid4()),
            'X-Txn-Locale': self._ryd_app_locale,
            'Content-Type': 'application/json; charset=utf-8',
        }
        self._attributes = {}
        self._identifier = name
        self._name = name
        self._friendly_name = name
        self._state = None
        self._unit_of_measurement = None
        self._icon = None

    @property
    def state(self):
        """Return the state."""
        return self._state

    @property
    def device_state_attributes(self) -> Optional[Dict[str, Any]]:
        """Return the unit of measurement."""
        return self._attributes
    @property
    def unit_of_measurement(self) -> Optional[str]:
        return "l"  # litre

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        response = requests.post(
            self._ryd_api_server +
            "/auth%2Flogin%2Flocal",
            data=self._data,
            headers=self._headers,
            timeout=2000
        )
        json_object = json.loads(response.text)

        ryd_auth_token=json_object["auth_token"]
        rydid = json_object["things"][0]["id"]

        response = requests.get(
            self._ryd_api_server +
            "/things/" +
            rydid +
            "/status?auth_token=" +
            ryd_auth_token,
            headers=self._headers,
            timeout=2000
        )
        json_data = response.json()

        self._attributes = json_data["data"]
        """
        data=json_data["data"]
        fueltype=data["fuelType"]
        license_plate=data["licensePlate"]
        battery_mvoltage=data["batteryLevelMV"]
        battery_percentage=data["batteryLevelPercent"]
        batteryv=battery_mvoltage/1000
        fuel=data["fuel"]
        level=fuel["level"]
        obdlevel=level["OBD_FUELLEVEL"]
        fuel_percentage=obdlevel["percent"]
        """
        self._state = self._attributes["percent"]

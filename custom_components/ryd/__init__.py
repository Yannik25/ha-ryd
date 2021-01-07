"""Support for RYD sensors."""
import logging
from homeassistant import core
from homeassistant.const import CONF_URL
from homeassistant.const import CONF_EMAIL
from homeassistant.const import CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the RYD Custom Component."""
    # @TODO: Add setup code.
    import requests
	import json
	import uuid
	
	url = config_entry.data.get(CONF_URL)
	email = config_entry.data.get(CONF_EMAIL)
	password = config_entry.data.get(CONF_PASSWORD)
	
	data = json.dumps({"email":email,"password":password})
	# copied from https://github.com/NemoN/ioBroker.ryd/blob/master/io-package.json
	ryd_api_server = url
	ryd_app_version = "2.52.4(201008000)"
	client_device_version = "9.0.0"
	client_device_resolution = "2960x1440"
	client_device_id = "SM-G960F"
	client_device_type = "Android"
	think_properties = "curLocation,parkingLocation,carOdometer,estimates,reportedFuelTotal,fuel"
	think_properties_ignore = "recurrences,openDtcs,score"
	ryd_app_locale = "de-de"
	ryd_app_internal_name = "TankTaler"
	ryd_app_platform = "{} [{},{},{}]".format(
	    client_device_type, client_device_id, client_device_version, client_device_resolution
	)
	ryd_app_user_agent = "{}/{}({};{} {})".format(
	    ryd_app_internal_name, ryd_app_version, client_device_id, client_device_type, client_device_version
	)
	headers = {
	    'x-txn-platform': ryd_app_platform,
	    'Cache-Control': 'no-cache, no-store, must-revalidate',
	    'Pragma': 'no-cache',
	    'Expires': str(0),
	    'x-txn-app-version': ryd_app_version,
	    'User-agent': ryd_app_user_agent,
	    'X-Txn-Request-Id': str(uuid.uuid4()),
	    'X-Txn-Locale': ryd_app_locale,
	    'Content-Type': 'application/json; charset=utf-8',
	}
	
	#print(fueltype)
	#print(str(fuel_percentage) + "%")
	#print(license_plate)
	#print(str(batteryv) + "," + str(battery_mvoltage-(batteryv*1000)) + "V")
	#print(str(battery_percentage) + "%")
    return True


class rydSensor(Entity):
    """Representation of a ryd sensor."""

    @property
    def state(self):
        """Return the state."""
        return self.state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return battery
        
    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        
        response = requests.post(ryd_api_server+"/auth%2Flogin%2Flocal", data=data,
	                         headers=headers, timeout=2000)
		json_object = json.loads(response.text)
		
		ryd_auth_token=json_object["auth_token"]
		rydid = json_object["things"][0]["id"]
		
		response = requests.get(ryd_api_server + "/things/" + rydid + "/status?auth_token=" + ryd_auth_token,
		                         headers=headers, timeout=2000) 
		json_data = json.loads(response.text)
		
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
        self._state =  fuel_percentage
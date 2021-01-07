[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# RYD Custom Component for Home Assistant

Still work in progress

lots of information from https://github.com/NemoN/ioBroker.ryd

Also thank you @nielstron for always correcting my mess :)

planned:
  - [ ] put information in seperate sensors or make one general sensor
  - [ ] add 
  - [x] make repo be able to be added to HACS for home-assistant 
  
## Installation

Add this repository to [hacs](https://hacs.xyz/) or copy the `custom_component/ryd` file structure into your custom_component directory .

## Example configuration

```yaml
# Configuration for the BLNET component
sensor:
  - platform: ryd
    url: "https://tt4.thinxcloud.de"
    email: "your email with quotes"
    password: "your password with quotes"
```

The result for now (not pretty but you can read all information for now):
the sensors name is for me now sensor.unnamed_device (will be fixed)

![First version of sensor](sensor.png)

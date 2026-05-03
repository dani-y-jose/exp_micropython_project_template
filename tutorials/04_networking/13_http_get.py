# Fetch the current weather from open-meteo (no API key required).
#
#     uvx mpremote mip install urequests   # built-in on ESP32, install on RP2

import network
import time
import urequests

from lib.secrets import WIFI_SSID, WIFI_PASSWORD

# Berlin — change lat/lon to your city.
URL = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    deadline = time.time() + 15
    while not wlan.isconnected() and time.time() < deadline:
        time.sleep(0.5)

if not wlan.isconnected():
    raise RuntimeError("WiFi failed")

print("fetching", URL)
r = urequests.get(URL)
data = r.json()
r.close()

current = data["current"]
print("temperature:", current["temperature_2m"], "C")
print("wind:       ", current["wind_speed_10m"], "km/h")

import network
import time

from lib.secrets import WIFI_SSID, WIFI_PASSWORD

TIMEOUT_S = 15

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    print("connecting to", WIFI_SSID)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    deadline = time.time() + TIMEOUT_S
    while not wlan.isconnected() and time.time() < deadline:
        time.sleep(0.5)

if wlan.isconnected():
    print("connected:", wlan.ifconfig())
else:
    print("failed to connect within", TIMEOUT_S, "s — status:", wlan.status())

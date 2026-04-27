import network
import time

SSID = "JoseNET"
PASSWORD = "pass"
TIMEOUT_S = 15

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    print("connecting to", SSID)
    wlan.connect(SSID, PASSWORD)
    deadline = time.time() + TIMEOUT_S
    while not wlan.isconnected() and time.time() < deadline:
        time.sleep(0.5)

if wlan.isconnected():
    print("connected:", wlan.ifconfig())
else:
    print("failed to connect within", TIMEOUT_S, "s — status:", wlan.status())

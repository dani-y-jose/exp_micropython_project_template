import espnow
import json
import network

# Channel MUST match the sender nodes.
CHANNEL = 1

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=CHANNEL)

e = espnow.ESPNow()
e.active(True)

print("gateway listening on channel", CHANNEL)

while True:
    host, msg = e.recv()
    if not msg:
        continue
    try:
        data = json.loads(msg)
        print("rx:", data)
    except Exception as err:
        print("packet error:", err, "raw:", msg)

import espnow
import json
import network
import time

# Change this per board before flashing.
NODE_ID = "C3_Alpha"
CHANNEL = 1

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=CHANNEL)

e = espnow.ESPNow()
e.active(True)

BROADCAST = b"\xff" * 6
e.add_peer(BROADCAST)

print("node", NODE_ID, "broadcasting on channel", CHANNEL)

counter = 0
while True:
    status = "alert" if counter % 5 == 0 else "ok"
    payload = json.dumps({"id": NODE_ID, "status": status, "count": counter})
    print("tx:", payload)
    e.send(BROADCAST, payload)
    counter += 1
    time.sleep(2)

import time

from lib.mesh import MeshNode

# Change this per board before flashing.
NODE_ID = "C3_Alpha"
INTERVAL_MS = 2000

mesh = MeshNode(NODE_ID, channel=1, ttl=3)

print("mesh node", NODE_ID, "active")

counter = 0
next_tx = time.ticks_add(time.ticks_ms(), INTERVAL_MS)
while True:
    remaining = time.ticks_diff(next_tx, time.ticks_ms())
    if remaining <= 0:
        counter += 1
        status = "alert" if counter % 5 == 0 else "ok"
        mesh.broadcast({"count": counter, "status": status})
        next_tx = time.ticks_add(time.ticks_ms(), INTERVAL_MS)
        continue
    pkt = mesh.recv(timeout_ms=remaining)
    if pkt and pkt.get("id") != NODE_ID:
        print("rx:", pkt)

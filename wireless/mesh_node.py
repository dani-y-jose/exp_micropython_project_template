from lib.mesh import MeshNode

# Change this per board before flashing.
NODE_ID = "C3_Alpha"

mesh = MeshNode(NODE_ID, channel=1, ttl=3)

print("mesh node", NODE_ID, "active")

counter = 0
while True:
    pkt = mesh.recv(timeout_ms=2000)
    if pkt and pkt.get("id") != NODE_ID:
        print("rx:", pkt)
    counter += 1
    status = "alert" if counter % 5 == 0 else "ok"
    mesh.broadcast({"count": counter, "status": status})

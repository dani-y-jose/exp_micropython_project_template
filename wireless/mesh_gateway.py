from lib.mesh import MeshNode

mesh = MeshNode("gateway", channel=1)

print("mesh gateway listening on channel 1")

while True:
    pkt = mesh.recv()
    if pkt:
        print("rx:", pkt)

# ESP-NOW examples

Peer-to-peer messaging between ESP boards using ESP-NOW. No router or
internet — boards talk to each other directly as long as they're on the same
WiFi channel.

## What's here

- [espnow_gateway.py](espnow_gateway.py) — listens, prints any JSON it receives
- [espnow_node.py](espnow_node.py) — broadcasts a JSON status message every 2s

## What you need

- At least **two** ESP boards already flashed with MicroPython
- Both boards must use the same `CHANNEL` (default `1`)

## Run it

### 1. Gateway board

Plug in the board you want to act as the listener. Open
[espnow_gateway.py](espnow_gateway.py) in VS Code and run **Tasks: Run Build
Task** (`Cmd+Shift+B`) — this executes the script in RAM via `mpremote run`
and streams `print()` output to your terminal. Leave it running.

You should see:

```
gateway listening on channel 1
```

### 2. Node board(s)

On a *second* board, first edit [espnow_node.py](espnow_node.py) and set a
unique `NODE_ID`:

```python
NODE_ID = "C3_Alpha"   # or "C3_Beta", etc. — unique per board
```

Plug it in (different USB port, or swap cables; whichever is easier). With
the file open, run **Tasks: Run Build Task** again. The node prints lines
like:

```
node C3_Alpha broadcasting on channel 1
tx: {"id": "C3_Alpha", "status": "alert", "count": 0}
tx: {"id": "C3_Alpha", "status": "ok", "count": 1}
...
```

Back on the gateway terminal you should see:

```
rx: {'id': 'C3_Alpha', 'status': 'alert', 'count': 0}
rx: {'id': 'C3_Alpha', 'status': 'ok', 'count': 1}
```

Repeat with more boards using different `NODE_ID` values to see multiple
nodes broadcasting at once.

## Making it persistent

`mpremote run` only keeps the script alive while USB is connected. To run a
script automatically when the board powers on, open the file you want and
trigger **MicroPython: Upload to Flash** — it copies the file to the board
as `main.py` and resets. After that the gateway runs on boot — useful for the node boards in
particular, so you can power them off USB.

## Mesh examples

[mesh_gateway.py](mesh_gateway.py) and [mesh_node.py](mesh_node.py) extend
the basic gateway/node above with **multi-hop relaying**, so a node out of
direct radio range can reach the gateway via intermediate nodes.

The mesh logic lives in [lib/mesh](../lib/mesh/) — it's a flood-and-suppress
layer over ESP-NOW broadcast. Each packet carries `(id, seq, ttl)`. Every
node deduplicates on `(id, seq)`, decrements `ttl`, and rebroadcasts while
`ttl > 0`. A small dedup history (last 64 keys) keeps duplicates from
ping-ponging.

### Run it

Same flow as the basic example — edit `NODE_ID` in `mesh_node.py`, **Upload
to Flash** to each node board (the upload task copies `lib/` to the device
automatically), and **Live Run** `mesh_gateway.py` on the gateway. Output on
the gateway looks like:

```
rx: {'id': 'C3_Alpha', 'seq': 1, 'ttl': 3, 'data': {'count': 1, 'status': 'ok'}}
```

To actually exercise the *mesh* part you need at least 3 boards, with one of
the nodes positioned far enough from the gateway that it can only reach it
via the second node. With 2 boards in the same room you'll just see direct
delivery — same as the basic example, but with the extra TTL/seq fields.

### With visualization

Two extra entry scripts add board-specific visualization on top of the same
mesh:

- [mesh_node_oled.py](mesh_node_oled.py) — runs on an ESP32-C3 with the
  0.42" 72×40 OLED. Shows `NODE_ID` on the top half (auto-scaled to fit
  width and height) and the local counter on the bottom half. Requires
  `mpremote mip install ssd1306` once on the board.
- [mesh_gateway_matrix.py](mesh_gateway_matrix.py) — runs on the ESP32-S3
  Matrix. Each received packet triggers a quick ripple from the center of
  the 8×8 NeoPixel: **green** if the payload's `status == "ok"`, **red** if
  `"alert"`.

## Troubleshooting

- **Gateway sees nothing.** Confirm both boards use the same `CHANNEL`. Some
  builds default WiFi to a different channel; setting it explicitly (as both
  scripts do) is what makes ESP-NOW pair up.
- **`packet error: ...`** Gateway received a non-JSON frame (e.g. another
  ESP-NOW device on the same channel). The raw bytes are printed alongside
  the error so you can identify it.
- **`OSError: ESP_ERR_ESPNOW_NOT_INIT`** Make sure `sta.active(True)` runs
  *before* `espnow.ESPNow().active(True)`.

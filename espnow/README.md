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
script automatically when the board powers on, use **MicroPython: Upload to
Flash** with the file renamed to `main.py` on the board:

```bash
uvx mpremote cp espnow_gateway.py :main.py + reset
```

After that the gateway runs on boot — useful for the node boards in
particular, so you can power them off USB.

## Troubleshooting

- **Gateway sees nothing.** Confirm both boards use the same `CHANNEL`. Some
  builds default WiFi to a different channel; setting it explicitly (as both
  scripts do) is what makes ESP-NOW pair up.
- **`packet error: ...`** Gateway received a non-JSON frame (e.g. another
  ESP-NOW device on the same channel). The raw bytes are printed alongside
  the error so you can identify it.
- **`OSError: ESP_ERR_ESPNOW_NOT_INIT`** Make sure `sta.active(True)` runs
  *before* `espnow.ESPNow().active(True)`.

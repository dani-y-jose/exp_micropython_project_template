# MicroPython ESP32 Project Template

A starting point for MicroPython development on ESP32 boards (tested on the
Waveshare ESP32-S3-Matrix) with VS Code autocomplete and one-keystroke
run/upload via `mpremote`.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) on your `PATH`
- VS Code
- An ESP32 board already flashed with MicroPython, connected over USB

## Setup

Clone the repo, then from the project root:

```bash
./setup.sh
```

This will:

1. Install `micropython-esp32-stubs` into `.vscode/stubs/` so VS Code
   autocompletes `machine`, `neopixel`, `network`, etc.
2. Write `.vscode/settings.json` (points Pylance at the stubs).
3. Write `.vscode/tasks.json` (the run/upload tasks below).

Open the folder in VS Code afterwards.

## Running code on the board

Open any `.py` file and trigger one of the two tasks:

| Task | What it does | Command |
|---|---|---|
| **MicroPython: Live Run (RAM)** | Mounts the project dir on the board (so local `lib/` modules are importable) and runs the open file in RAM. Nothing is persisted. Best for iterating. | `uvx mpremote mount . run ${file}` |
| **MicroPython: Upload to Flash** | Copies `lib/` to the board, then writes the open file as `main.py` and resets — so it auto-runs on boot with all modules available. Overwrites whatever `main.py` was there before. | `uvx mpremote cp -r lib : + cp ${file} :main.py + reset` |

### Keyboard shortcuts

- **Live Run** is the default build task — `Cmd+Shift+B` (macOS) /
  `Ctrl+Shift+B` (Win/Linux) runs it on the open file.
- **Upload to Flash** has no default binding. Either:
  - Pick it from the command palette: `Tasks: Run Task` →
    *MicroPython: Upload to Flash*, or
  - Bind it: open Keyboard Shortcuts, search `Tasks: Run Task`, assign
    something like `Cmd+U`, and either pick the task each time or use
    `workbench.action.tasks.runTask` with `args: "MicroPython: Upload to Flash"`.

## Sharing code via [lib/](lib/)

Put any module you want to import from multiple entry scripts into `lib/`.
The folder is a Python package (it has [`__init__.py`](lib/__init__.py)), so
imports always look like:

```python
from lib.mesh import broadcast
from lib.sensors import read_temp
```

Use `from lib.<module> import ...` (not bare `import <module>`) — that form
works identically in both run modes:

- **Live Run** mounts the project dir on the board and adds it to `sys.path`,
  so `lib/` resolves to `./lib/` on your laptop. No copy step needed.
- **Upload to Flash** copies `lib/` to the board's filesystem (`:lib/`) before
  writing the entry script as `main.py`, so the same imports work after boot.

Entry scripts in any subfolder (`display/`, `wireless/`, etc.) can use these
imports — the script's location on disk doesn't affect import resolution.

## Example files

### Root

| File | What it does |
|---|---|
| [blink.py](blink.py) | Plain on/off blink on a single GPIO. Adjust `LED_PIN` for your board. |

### [display/](display/)

| File | What it does |
|---|---|
| [neopixel_blink.py](display/neopixel_blink.py) | Blinks a single NeoPixel on `DATA_PIN = 14`. |
| [matrix_scan.py](display/matrix_scan.py) | Walks one lit pixel across an 8×8 NeoPixel matrix in R/G/B. |
| [matrix_heartbeat.py](display/matrix_heartbeat.py) | Heartbeat ripple from the center of an 8×8 matrix with gaussian shading. |
| [oled_c3_hello.py](display/oled_c3_hello.py) | Text + counter on the 0.42" 72×40 OLED found on cheap ESP32-C3 dev boards. Requires `mpremote mip install ssd1306`. |
| [rp2040_matrix_pio.py](display/rp2040_matrix_pio.py) | PIO-driven WS2812 scan on the Waveshare **RP2040-Matrix** (5×5 on GPIO 16). Smoke test for `rp2.asm_pio` + RP2 stubs. |

> The matrix examples assume serpentine wiring (row 0 left-to-right, row 1
> right-to-left, …). If a scan looks scrambled, change the body of `xy()` to
> `return y * WIDTH + x` for plain row-major.

### [wifi/](wifi/)

| File | What it does |
|---|---|
| [wifi_connect.py](wifi/wifi_connect.py) | STA-mode WiFi connect with timeout. Edit `SSID` / `PASSWORD` before running. |

### [wireless/](wireless/)

Peer-to-peer messaging between ESP boards over ESP-NOW (no router required).
Both ends must use the same channel. The folder is named `wireless/` rather
than `espnow/` to avoid shadowing the built-in `espnow` MicroPython module
when the project is mounted on the device.

| File | What it does |
|---|---|
| [espnow_gateway.py](wireless/espnow_gateway.py) | Listens for ESP-NOW packets on channel 1 and prints any JSON payload received. |
| [espnow_node.py](wireless/espnow_node.py) | Broadcasts a JSON status message every 2s. Edit `NODE_ID` per board before flashing. |
| [mesh_gateway.py](wireless/mesh_gateway.py) | Mesh sink built on [lib/mesh](lib/mesh/). Receives + relays — same as the basic gateway but with multi-hop. |
| [mesh_node.py](wireless/mesh_node.py) | Mesh originator. Sends a counter every 2s and relays others. Uses [lib/mesh](lib/mesh/). |
| [mesh_node_oled.py](wireless/mesh_node_oled.py) | Same as `mesh_node.py` but for the ESP32-C3 + 0.42" OLED — shows `NODE_ID` (auto-scaled) on top and the counter below. |
| [mesh_gateway_matrix.py](wireless/mesh_gateway_matrix.py) | Same as `mesh_gateway.py` but for the ESP32-S3 Matrix — flashes a green/red ripple on the 8×8 NeoPixel for each rx. |

## Useful `mpremote` commands

```bash
uvx mpremote ls                     # list files on the board
uvx mpremote cat main.py            # print a file from the board
uvx mpremote rm :somefile.py        # delete a file from the board
uvx mpremote reset                  # soft-reset the board
uvx mpremote repl                   # interactive REPL (Ctrl-X to exit)
```

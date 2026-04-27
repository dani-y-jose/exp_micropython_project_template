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
| **MicroPython: Live Run (RAM)** | Runs the open file in RAM via `mpremote run`. Nothing is persisted to the board. Best for iterating. | `uvx mpremote run ${file}` |
| **MicroPython: Upload to Flash** | Copies the open file to the board's filesystem (as `${fileBasename}`) and resets. Use this for `main.py` or modules you want to keep. | `uvx mpremote cp ${file} :${fileBasename} + reset` |

### Keyboard shortcuts

- **Live Run** is the default build task — `Cmd+Shift+B` (macOS) /
  `Ctrl+Shift+B` (Win/Linux) runs it on the open file.
- **Upload to Flash** has no default binding. Either:
  - Pick it from the command palette: `Tasks: Run Task` →
    *MicroPython: Upload to Flash*, or
  - Bind it: open Keyboard Shortcuts, search `Tasks: Run Task`, assign
    something like `Cmd+U`, and either pick the task each time or use
    `workbench.action.tasks.runTask` with `args: "MicroPython: Upload to Flash"`.

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

> The matrix examples assume serpentine wiring (row 0 left-to-right, row 1
> right-to-left, …). If a scan looks scrambled, change the body of `xy()` to
> `return y * WIDTH + x` for plain row-major.

### [wifi/](wifi/)

| File | What it does |
|---|---|
| [wifi_connect.py](wifi/wifi_connect.py) | STA-mode WiFi connect with timeout. Edit `SSID` / `PASSWORD` before running. |

### [espnow/](espnow/)

Peer-to-peer messaging between ESP boards over ESP-NOW (no router required).
Both ends must use the same channel.

| File | What it does |
|---|---|
| [espnow_gateway.py](espnow/espnow_gateway.py) | Listens for ESP-NOW packets on channel 1 and prints any JSON payload received. |
| [espnow_node.py](espnow/espnow_node.py) | Broadcasts a JSON status message every 2s. Edit `NODE_ID` per board before flashing. |

## Useful `mpremote` commands

```bash
uvx mpremote ls                     # list files on the board
uvx mpremote cat main.py            # print a file from the board
uvx mpremote rm :somefile.py        # delete a file from the board
uvx mpremote reset                  # soft-reset the board
uvx mpremote repl                   # interactive REPL (Ctrl-X to exit)
```

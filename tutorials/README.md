# MicroPython Peripheral Tutorial

A reference library that walks from "blink an LED" to "publish sensor data over MQTT", with side tracks for motor control and the Pico Explorer Base LCD. Each script is small and self-contained — copy, adapt, and combine them as you build real projects.

The teaching prose lives in the per-section READMEs; the scripts themselves stay minimal. Each section's README lists the scripts in that section.

## Layout

| Section | What you learn |
|---|---|
| [01_core_gpio/](01_core_gpio/) | Digital I/O, IRQs, hardware timers |
| [02_analog_pwm/](02_analog_pwm/) | PWM, servos, ADC, DC-motor + encoder |
| [03_buses/](03_buses/) | I2C, sensors, OLED, SPI/SD |
| [04_display/](04_display/) | Pico Explorer Base ST7789 LCD: primitives, animation, buttons |
| [05_networking/](05_networking/) | WiFi, HTTP, web server, MQTT |
| [06_neopixels/](06_neopixels/) | Addressable RGB LEDs and matrix animation |
| [07_async/](07_async/) | Cooperative multitasking with `asyncio` |

## Board support

Tutorials target **ESP32** and **RP2040 (Pico / Pico W)**. Pin assignments are centralized in [lib/pins.py](../lib/pins.py) — auto-detected via `sys.platform`. If your wiring differs from the defaults, edit that one file.

| Section | ESP32 | RP2040 (Pico W) | RP2040 (Pico, no WiFi) | Notes |
|---|---|---|---|---|
| 01_core_gpio | yes | yes | yes | |
| 02_analog_pwm | yes | yes | yes | Motor/encoder scripts (08-13) are RP2-specific |
| 03_buses | yes | yes | yes | |
| 04_display | — | yes | yes | Pimoroni Pico Explorer Base only |
| 05_networking | yes | yes | no | |
| 06_neopixels | yes | yes | yes | |
| 07_async (web server) | yes | yes | no | other async scripts work everywhere |

## Setup

### One-time

Run [setup.sh](../setup.sh) once to install MicroPython stubs and VS Code tasks. It also vendors `ssd1306.py` for the OLED tutorial.

### Required `mip install` (run from your host once per board)

```sh
# always
uvx mpremote mip install ssd1306        # script 10

# SD card tutorial
uvx mpremote mip install sdcard         # script 11

# networking
uvx mpremote mip install urequests      # script 13 — built-in on ESP32, needed on RP2
uvx mpremote mip install umqtt.simple   # script 15
```

DHT22 (script 09) uses the built-in `dht` module — no install needed.

### Credentials

Scripts 12-15 read from `lib/secrets.py`. Create it once:

```sh
cp lib/secrets_example.py lib/secrets.py
# then edit lib/secrets.py with your WiFi/MQTT details
```

The real `lib/secrets.py` is gitignored.

## Running a tutorial

Two ways, both already wired up by [setup.sh](../setup.sh):

```sh
# Live run (mounts project, no flashing — fastest iteration)
uvx mpremote mount . run tutorials/01_core_gpio/01_blink.py

# Persist as main.py on the device (runs at boot)
uvx mpremote cp -r lib : + cp tutorials/01_core_gpio/01_blink.py :main.py + reset
```

In VS Code these are exposed as **Live Run (RAM)** and **Upload to Flash** tasks (`Cmd+Shift+B`).

## Reading order

The scripts are numbered for a reason — concepts build on each other. If you're new to MicroPython, work through them in order. If you already know the basics, the section table above lets you jump to a specific peripheral.

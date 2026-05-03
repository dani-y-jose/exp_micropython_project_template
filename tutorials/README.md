# MicroPython Peripheral Tutorial

A 15-script reference library that walks from "blink an LED" to "publish sensor data over MQTT". Each script is small and self-contained — copy, adapt, and combine them as you build real projects.

The teaching prose lives in the per-section READMEs; the scripts themselves stay minimal.

## Layout

| Section | What you learn | Scripts |
|---|---|---|
| [01_core_gpio/](01_core_gpio/) | Digital I/O, IRQs, hardware timers | 01-04 |
| [02_analog_pwm/](02_analog_pwm/) | PWM, servos, ADC | 05-07 |
| [03_buses/](03_buses/) | I2C, sensors, OLED, SPI/SD | 08-11 |
| [04_networking/](04_networking/) | WiFi, HTTP, web server, MQTT | 12-15 |
| [05_neopixels/](05_neopixels/) | Addressable RGB LEDs and matrix animation | 16-20 |
| [06_async/](06_async/) | Cooperative multitasking with `asyncio` | 21-25 |

## Script index

| # | Script | One-liner |
|---|---|---|
| 01 | [01_core_gpio/01_blink.py](01_core_gpio/01_blink.py) | Toggle the onboard LED with `time.sleep`. |
| 02 | [01_core_gpio/02_button_polling.py](01_core_gpio/02_button_polling.py) | Read a button by polling, with debounce. |
| 03 | [01_core_gpio/03_button_interrupts.py](01_core_gpio/03_button_interrupts.py) | Handle a button press via `pin.irq()`. |
| 04 | [01_core_gpio/04_hardware_timers.py](01_core_gpio/04_hardware_timers.py) | Blink with `machine.Timer` while the main loop is free. |
| 05 | [02_analog_pwm/05_pwm_led_fade.py](02_analog_pwm/05_pwm_led_fade.py) | Fade an LED with PWM duty sweep. |
| 06 | [02_analog_pwm/06_servo_sweep.py](02_analog_pwm/06_servo_sweep.py) | Sweep a hobby servo 0-180° with PWM. |
| 07 | [02_analog_pwm/07_adc_potentiometer.py](02_analog_pwm/07_adc_potentiometer.py) | Read an analog voltage with the ADC. |
| 08 | [03_buses/08_i2c_scanner.py](03_buses/08_i2c_scanner.py) | Print the address of every device on the I2C bus. |
| 09 | [03_buses/09_i2c_sensor.py](03_buses/09_i2c_sensor.py) | Read temperature + humidity from a DHT22. |
| 10 | [03_buses/10_i2c_oled_display.py](03_buses/10_i2c_oled_display.py) | Draw text and shapes on an SSD1306 OLED. |
| 11 | [03_buses/11_spi_sd_card.py](03_buses/11_spi_sd_card.py) | Mount an SD card, write and read a file. |
| 12 | [04_networking/12_wifi_connect.py](04_networking/12_wifi_connect.py) | Connect to WiFi with timeout + retry. |
| 13 | [04_networking/13_http_get.py](04_networking/13_http_get.py) | Fetch JSON from a public weather API. |
| 14 | [04_networking/14_simple_web_server.py](04_networking/14_simple_web_server.py) | Serve a one-page site that toggles the LED. |
| 15 | [04_networking/15_mqtt_publish.py](04_networking/15_mqtt_publish.py) | Publish ADC readings to an MQTT broker. |
| 16 | [05_neopixels/16_neopixel_blink.py](05_neopixels/16_neopixel_blink.py) | Blink a single WS2812 NeoPixel through R/G/B/off. |
| 17 | [05_neopixels/17_neopixel_strip.py](05_neopixels/17_neopixel_strip.py) | Walk a pixel along a strip and rainbow-cycle the colors. |
| 18 | [05_neopixels/18_matrix_xy.py](05_neopixels/18_matrix_xy.py) | Address pixels on a 2D matrix using xy() with serpentine wiring. |
| 19 | [05_neopixels/19_matrix_scan.py](05_neopixels/19_matrix_scan.py) | Sweep a single pixel across every cell of the matrix. |
| 20 | [05_neopixels/20_matrix_animation.py](05_neopixels/20_matrix_animation.py) | Heartbeat ripple expanding from the center of the matrix. |
| 21 | [06_async/21_async_blink.py](06_async/21_async_blink.py) | Blink an LED with `await asyncio.sleep_ms()` instead of blocking. |
| 22 | [06_async/22_async_two_tasks.py](06_async/22_async_two_tasks.py) | Run two concurrent blink rates with `asyncio.gather()`. |
| 23 | [06_async/23_async_button_event.py](06_async/23_async_button_event.py) | Bridge a hardware IRQ into an async task via `ThreadSafeFlag`. |
| 24 | [06_async/24_async_pipeline.py](06_async/24_async_pipeline.py) | Producer/consumer DHT22 → queue → printer with heartbeat. |
| 25 | [06_async/25_async_web_server.py](06_async/25_async_web_server.py) | Non-blocking HTTP server using `asyncio.start_server()`. |

## Board support

Tutorials target **ESP32** and **RP2040 (Pico / Pico W)**. Pin assignments are centralized in [lib/pins.py](../lib/pins.py) — auto-detected via `sys.platform`. If your wiring differs from the defaults, edit that one file.

| Section | ESP32 | RP2040 (Pico W) | RP2040 (Pico, no WiFi) |
|---|---|---|---|
| 01-11 | yes | yes | yes |
| 12-15 (networking) | yes | yes | no |
| 16-20 (NeoPixels) | yes | yes | yes |
| 21-24 (asyncio) | yes | yes | yes |
| 25 (async web server) | yes | yes | no |

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

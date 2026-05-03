# 03 — Communication Buses

Sensors, displays, and storage rarely sit on a single GPIO. They speak over **buses** — protocols that share a few wires across many devices. This section covers the two you'll meet 99% of the time: **I2C** and **SPI**.

## Concepts

### I2C (Inter-Integrated Circuit)

Two wires (SDA, SCL) plus power and ground. Up to ~127 devices share the bus, each with a unique 7-bit **address**. The MCU is the controller; everything else is a peripheral. Slow but cheap (typical: 100 kHz or 400 kHz).

```python
from machine import I2C, Pin
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400_000)
addrs = i2c.scan()                   # list of devices found
i2c.writeto(0x3C, b"\x00\xAE")       # send bytes to device at 0x3C
```

A scanner script (`08_i2c_scanner.py`) is your first move whenever something doesn't work — if `scan()` returns `[]`, you have a wiring problem, not a software problem.

### SPI (Serial Peripheral Interface)

Four wires (SCK, MOSI, MISO, CS) — one CS per device. Much faster than I2C (often 10+ MHz), used for SD cards, displays with frame buffers, flash chips. You drive CS LOW for the device you want to talk to, exchange bytes, drive CS HIGH again.

```python
from machine import SPI, Pin
spi = SPI(1, baudrate=10_000_000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5, Pin.OUT, value=1)
```

### Drivers

You rarely talk to a sensor at the byte level. Each chip has a **driver** — a Python module that wraps the I2C/SPI calls. You install drivers once per board with `mip`:

```sh
uvx mpremote mip install ssd1306    # OLED
uvx mpremote mip install sdcard     # SD card
```

DHT22 is a special case: it uses a single-wire protocol that's built into MicroPython as the `dht` module — no install needed.

## Wiring

```
I2C (4 wires shared across all I2C devices)        SPI / SD card (6 wires)

  3V3 ── VCC                                         3V3 ── VCC
  GND ── GND                                         GND ── GND
  SDA ─┬─ SDA                                        SCK ── SCK
       └─ SDA                                        MOSI ── DI
  SCL ─┬─ SCL                                        MISO ── DO
       └─ SCL                                        CS   ── CS
```

I2C lines need pull-up resistors (typically 4.7 kΩ to 3V3). Most breakout boards include them — if `i2c.scan()` returns `[]` and wiring looks right, check for missing pull-ups.

## Board notes

- **ESP32**: I2C(0) and I2C(1) are both bit-banged software I2C unless you use specific pins; the constants in [lib/pins.py](../../lib/pins.py) work for either. For SPI, `SPI(1)` is HSPI, `SPI(2)` is VSPI; the S3 only has `SPI(2)`.
- **RP2040**: I2C(0) defaults to GP4/GP5 (SDA/SCL). SPI(0) and SPI(1) each map to specific GPIO sets — see the Pico pinout if you change pins.
- **SD cards** want a card formatted FAT32. Some Class 10 cards work poorly at low SPI clocks — start at 1 MHz to confirm wiring, then ratchet up.

## Try changing

- `08_i2c_scanner.py`: bus-power one device at a time and confirm the address changes between them.
- `09_i2c_sensor.py`: move from DHT22 to BME280 (`mip install bme280`) — also gives you barometric pressure.
- `10_i2c_oled_display.py`: combine with `07_adc_potentiometer.py` from section 2 to draw a knob value as a bar.
- `11_spi_sd_card.py`: log a timestamp + ADC value once per second instead of writing once.

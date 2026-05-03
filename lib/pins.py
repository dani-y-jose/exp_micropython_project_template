# Per-board pin map for the tutorial series. Auto-detects ESP32 vs RP2 from
# sys.platform; edit the values below if your wiring differs from the defaults.

import sys

PLATFORM = sys.platform

if PLATFORM == "esp32":
    # Generic ESP32 DevKit. ESP32-S3/C3 may differ — adjust LED in particular.
    LED = 2
    BUTTON = 0           # BOOT button on most dev boards
    PWM_LED = 4
    SERVO = 13
    ADC = 34             # ADC1 (input-only pins 32-39 are safe with WiFi)
    I2C_ID = 0
    I2C_SCL = 22
    I2C_SDA = 21
    SPI_ID = 1           # HSPI; SPI(2) on S3
    SPI_SCK = 18
    SPI_MOSI = 23
    SPI_MISO = 19
    SPI_CS = 5
    # NeoPixel / WS2812. NEOPIXEL is a single pixel; MATRIX_PIN feeds an array
    # of MATRIX_WIDTH × MATRIX_HEIGHT pixels. ESP32-S3-Matrix board uses GP14,
    # 8×8. Generic ESP32 has no onboard NeoPixel — wire one to GP14 to test.
    NEOPIXEL = 14
    MATRIX_PIN = 14
    MATRIX_WIDTH = 8
    MATRIX_HEIGHT = 8
elif PLATFORM == "rp2":
    # LED conventions vary across RP2 boards:
    #   - Pico W:                 Pin("LED") — wired to the WiFi chip
    #   - Pico (non-W):           GP25 onboard LED
    #   - RP2040-Zero / -Matrix:  no plain LED — wire an external one to LED below
    # The detection below picks Pico W if available, otherwise defaults to GP15
    # (a free, edge-exposed pin on the Zero). Wire an LED + 220Ω resistor from
    # GP15 to GND, or change LED here to whichever GPIO you've used.
    try:
        from machine import Pin as _Pin
        _Pin("LED")
        LED = "LED"
    except (ValueError, TypeError):
        LED = 15
    BUTTON = 14
    PWM_LED = 15
    SERVO = 16
    ADC = 26             # GP26 = ADC0
    I2C_ID = 0
    I2C_SCL = 5
    I2C_SDA = 4
    SPI_ID = 1
    SPI_SCK = 10
    SPI_MOSI = 11
    SPI_MISO = 12
    SPI_CS = 13
    # NeoPixel / WS2812. RP2040-Zero onboard NeoPixel and Waveshare RP2040-Matrix
    # both use GP16. Matrix defaults to 5×5 (Waveshare); change to 1×1 if you
    # only have the Zero's single pixel and are running matrix scripts.
    NEOPIXEL = 16
    MATRIX_PIN = 16
    MATRIX_WIDTH = 5
    MATRIX_HEIGHT = 5
else:
    raise RuntimeError("unsupported platform: " + PLATFORM)

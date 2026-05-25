# 04 — Display (Pico Explorer Base LCD)

The Pimoroni Pico Explorer Base ships with a 240×240 ST7789 SPI LCD wired to the host RP2040. This section teaches the panel in isolation — initializing it, drawing with `framebuf`, animating, and reading the four onboard buttons. The motor-control dashboard project that this work is building toward lives elsewhere; here we stay focused on display fundamentals.

## Hardware

| Signal | GPIO | Note |
|---|---|---|
| SPI peripheral | SPI0 | Separate from the SPI_* breadboard pins (SPI1) defined in `lib/pins.py`. |
| SCK | GP18 | |
| MOSI | GP19 | |
| CS  | GP17 | |
| DC  | GP16 | data/command select |
| BL  | GP20 | PWM-able backlight |
| Reset | — | tied to 3v3 on the board; we do a software reset only |
| Buttons | GP12 / GP13 / GP14 / GP15 | A / B / X / Y, active-low |

## Driver

A small ST7789 driver is vendored at [lib/st7789.py](../../lib/st7789.py). No `mip install` step. Two entry points:

- `ST7789(spi, cs, dc, bl, width, height)` — init the panel and own the BL pin (as PWM).
- `lcd.show(buf)` — burst the bytes of a `framebuf.FrameBuffer(buf, W, H, framebuf.RGB565)` to the panel.

The driver also provides `lcd.fill(color)` for fast solid fills that don't need a framebuffer allocated, and `color565(r, g, b)` to pack 8-8-8 RGB into the byte-swapped 16-bit value that framebuf-then-SPI expects.

## Memory note

A 240×240 RGB565 framebuffer is **115 200 bytes**. The RP2040 has 264 KB of SRAM, so one full-screen buffer is fine but is a meaningful chunk of total memory. If you need a second buffer (e.g. for partial-update tricks), consider strip rendering — see [display/rp2350_amoled_draw.py](../../display/rp2350_amoled_draw.py) for the row-strip pattern used on the larger AMOLED panel.

## Scripts

| Script | What it does |
|---|---|
| [01_display_hello.py](01_display_hello.py) | Bring the panel up, sweep RGB/white/black, draw "hello, world". |
| [02_display_primitives.py](02_display_primitives.py) | Lines, rectangles (filled and outlined), pixels, text — every primitive `framebuf` gives you. |
| [03_display_animation.py](03_display_animation.py) | Bouncing ball with a live FPS readout. Shows the redraw-loop cost. |
| [04_display_buttons.py](04_display_buttons.py) | Read the four onboard buttons and render their state. Foundation for menu/mode-switch UIs. |
| [05_encoder_gauge.py](05_encoder_gauge.py) | Live motor-position needle gauge. Combines the hard-IRQ quadrature decoder from [02_analog_pwm/11_encoder_hard_irq.py](../02_analog_pwm/11_encoder_hard_irq.py) with the LCD — first script in the folder that bridges to the motor work. |
| [06_motor_rpm_gauge.py](06_motor_rpm_gauge.py) | Bipolar RPM gauge with serial control. Three asyncio tasks: read float power commands from stdin, drive the DRV8833, stream CSV status, redraw the LCD. Builds on [02_analog_pwm/14_motor_serial.py](../02_analog_pwm/14_motor_serial.py). |

## Board support

These scripts assume the Pico Explorer Base. The ST7789 pins are only defined under the `rp2` branch of [lib/pins.py](../../lib/pins.py). Other boards would need their own panel driver and pinout.

## Things to try

- Lower the SPI baudrate in 03 from `31_250_000` to `8_000_000` — watch the FPS drop. Above ~31 MHz the panel itself becomes flaky.
- In 04, hold two buttons simultaneously. The polling loop already handles it; an IRQ-based implementation would need extra care.
- Combine: feed a value from a potentiometer (see [02_analog_pwm/07_adc_potentiometer.py](../02_analog_pwm/07_adc_potentiometer.py)) into the ball position in 03 to make a manual pong paddle.

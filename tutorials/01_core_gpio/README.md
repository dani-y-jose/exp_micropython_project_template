# 01 — Core System & GPIO

This section covers the four building blocks that every embedded program uses: turning a pin on, reading a pin, reacting to a pin change without polling, and running periodic work without `sleep()` blocking your main loop.

## Concepts

### GPIO (General Purpose Input/Output)

A GPIO pin is a single wire the MCU can drive HIGH (≈3.3 V) or LOW (0 V) as an **output**, or sense as HIGH/LOW as an **input**. In MicroPython:

```python
from machine import Pin
led = Pin(2, Pin.OUT)         # output
led.value(1)                  # drive HIGH
button = Pin(0, Pin.IN, Pin.PULL_UP)
state = button.value()        # 0 or 1
```

Inputs need a known idle state. A **pull-up resistor** (internal: `Pin.PULL_UP`) ties the pin HIGH when nothing is connected, so a button to GND reads LOW when pressed. The opposite — `PULL_DOWN`, button to 3V3 — also works.

### Debouncing

Mechanical buttons "bounce" — a single press generates dozens of HIGH/LOW transitions over a few milliseconds. Without debouncing, polling sees one press as ten. The simple fix is to ignore further changes for ~50 ms after a transition. We do this with `time.ticks_ms()` and `time.ticks_diff()` (which handle the 30-bit counter wraparound that `time.time()` does not).

### Interrupts (IRQ)

Polling means the CPU asks the pin "are you pressed yet?" thousands of times per second. An **interrupt** flips that around: the pin tells the CPU when something changes. You attach a handler with `pin.irq()`:

```python
button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)
```

The handler runs in **interrupt context**, which has hard rules:
- No `print()`, no allocation, no long work — keep it microseconds.
- Set a flag (boolean or counter), let the main loop do the real work.

### Hardware timers

`time.sleep(0.5)` blocks the CPU for half a second. If you want an LED blinking *while* the main loop also reads sensors, you need a **hardware timer** — a peripheral that fires a callback on its own:

```python
from machine import Timer
Timer(0).init(period=500, mode=Timer.PERIODIC, callback=lambda t: led.value(not led.value()))
```

The callback runs at interrupt level, same rules as IRQ handlers.

## Wiring

```
Button on BUTTON pin (default: GPIO 0 ESP32 / GP14 RP2)

   3V3 ──┐
         │ (internal pull-up — no external resistor needed)
        BTN
         │
        GND
```

The onboard LED is already wired on most dev boards, no external parts needed for `01_blink.py`.

## Board notes

- **ESP32**: `Timer(0)` through `Timer(3)` are general-purpose hardware timers. `BUTTON = 0` is the BOOT button — held LOW during boot puts the chip in download mode, but in normal run it's just a button.
- **RP2040 (Pico W)**: `Timer()` (no ID) uses a software-multiplexed timer that's plenty for blinking. The onboard LED on Pico W is *not* on a regular GPIO — `Pin("LED")` is the special name; on a non-W Pico it's GPIO 25.

## Try changing

- `02_button_polling.py`: change the debounce window from 50 ms — what's the smallest value before you see double-counts?
- `03_button_interrupts.py`: add a counter and print it from the main loop. Can you reproduce a missed press?
- `04_hardware_timers.py`: change `mode=Timer.PERIODIC` to `Timer.ONE_SHOT` — what happens?

# 02 — Analog Signals & PWM

GPIO is binary — HIGH or LOW. Many real-world devices need something in between: dim an LED, position a servo, read a knob. This section covers the two ways to bridge that gap: **PWM** for output, **ADC** for input.

## Concepts

### PWM (Pulse Width Modulation)

A PWM signal is a fast square wave where the **duty cycle** — the fraction of time spent HIGH — is adjustable. Drive an LED at 30% duty and your eye sees 30% brightness; drive a heater at 50% duty and it gets half power. The MCU never has to produce a true analog voltage.

Two parameters matter:
- **Frequency**: how fast the wave repeats. LEDs want ≥500 Hz so you don't see flicker. Hobby servos want exactly 50 Hz.
- **Duty**: how much of each cycle is HIGH. MicroPython exposes this as `duty_u16(0..65535)` — a 16-bit value where 0 is always LOW and 65535 is always HIGH.

```python
from machine import PWM, Pin
pwm = PWM(Pin(4), freq=1000)
pwm.duty_u16(32768)        # 50% — LED at half brightness
```

### Servos

A hobby servo reads a 50 Hz pulse and positions its arm based on the **pulse width**:
- ~1.0 ms HIGH → 0°
- ~1.5 ms HIGH → 90° (center)
- ~2.0 ms HIGH → 180°

A 50 Hz period is 20 ms, so 1 ms of HIGH = 5% duty = `duty_u16` ≈ 3277. The script `06_servo_sweep.py` maps degrees to that range.

### ADC (Analog-to-Digital Converter)

The reverse of PWM: read a continuous voltage and get a number. A potentiometer between 3V3 and GND with the wiper to the ADC pin gives you a knob whose position you can read in code.

```python
from machine import ADC, Pin
adc = ADC(Pin(34))
value = adc.read_u16()     # 0..65535
```

## Wiring

```
LED (PWM_LED pin)                  Servo (SERVO pin)             Pot (ADC pin)
                                                                 
  pin ── 220Ω ── LED ── GND          pin ── orange (signal)        3V3 ─┐
                                     5V  ── red    (power)            ┌┴┐
                                     GND ── brown  (ground)           │ │
                                                                      └┬┘  wiper → ADC
                                                                       │
                                                                      GND
```

Servos draw real current (200 mA+ on stall) — power them from a 5 V rail, **not** the board's 3V3 line, or you'll brown out the MCU.

## Board notes

- **ESP32**: ADC inputs are non-linear at the rails and need attenuation set explicitly: `ADC.atten(ADC.ATTN_11DB)` extends the input range to ~3.1 V. ADC1 pins (32-39) work with WiFi; ADC2 pins do not.
- **RP2040**: ADC pins are GP26-29; range is 0-3.3 V with no attenuation knob. `ADC(Pin(26))` or `ADC(0)` both work.
- **PWM channel limits**: ESP32 has 16 hardware PWM channels (8 on C3); RP2040 has 16 channels paired across GPIOs. Plenty for these tutorials, but worth knowing if you start adding many PWM outputs.

## Try changing

- `05_pwm_led_fade.py`: drop `freq` to 50 Hz — can you see the flicker?
- `06_servo_sweep.py`: tweak `MIN_US`/`MAX_US` to calibrate to *your* servo's actual end-stops.
- `07_adc_potentiometer.py`: feed the ADC reading into PWM duty for the LED — combine an input and output script into a knob-controlled dimmer.

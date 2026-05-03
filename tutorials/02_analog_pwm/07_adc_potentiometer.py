import sys
import time
from machine import ADC, Pin

from lib.pins import ADC as ADC_PIN

adc = ADC(Pin(ADC_PIN))

# ESP32 needs explicit attenuation to read the full 0-3.3 V range.
if sys.platform == "esp32":
    adc.atten(ADC.ATTN_11DB)

while True:
    raw = adc.read_u16()
    volts = raw * 3.3 / 65535
    print("raw:", raw, " volts:", "{:.2f}".format(volts))
    time.sleep_ms(200)

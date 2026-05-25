from machine import UART, Pin
import time

# HiLink LD2410 / Ai-Thinker Rd-03 normal-mode report frame:
#   F4 F3 F2 F1                              header
#   LL LL                                    payload length (uint16 LE) = 13
#   02 AA                                    data type + head marker
#   ST                                       target state (0/1/2/3)
#   MD MD                                    moving target distance, cm (uint16 LE)
#   ME                                       moving target energy 0..100
#   SD SD                                    still target distance, cm (uint16 LE)
#   SE                                       still target energy 0..100
#   DD DD                                    detection distance, cm (uint16 LE)
#   55 00                                    tail + check
#   F8 F7 F6 F5                              frame end

HEADER = b"\xF4\xF3\xF2\xF1"
FOOTER = b"\xF8\xF7\xF6\xF5"
FRAME_LEN = 23

STATE = {0: "no target", 1: "moving", 2: "still", 3: "moving+still"}

Pin(6, Pin.OUT).value(1)
time.sleep(0.5)

uart = UART(1, baudrate=256000, rx=4, tx=5)

print("-" * 60)
print("  LD2410 / Rd-03 presence radar  ")
print("-" * 60)


def u16(b, o):
    return b[o] | (b[o + 1] << 8)


buf = bytearray()

while True:
    chunk = uart.read()
    if chunk:
        buf.extend(chunk)

        while True:
            start = buf.find(HEADER)
            if start < 0:
                if len(buf) > 3:
                    buf = bytearray(buf[-3:])
                break
            if len(buf) - start < FRAME_LEN:
                if start > 0:
                    buf = bytearray(buf[start:])
                break
            frame = bytes(buf[start:start + FRAME_LEN])
            buf = bytearray(buf[start + FRAME_LEN:])

            if frame[-4:] != FOOTER or frame[6:8] != b"\x02\xAA":
                continue

            state = frame[8]
            m_dist = u16(frame, 9)
            m_energy = frame[11]
            s_dist = u16(frame, 12)
            s_energy = frame[14]
            det_dist = u16(frame, 15)

            print("[{:>8} ms] {:<13}  moving: {:>3} cm @ {:>3}%  still: {:>3} cm @ {:>3}%  detect: {:>3} cm".format(
                time.ticks_ms(),
                STATE.get(state, "?"),
                m_dist, m_energy,
                s_dist, s_energy,
                det_dist,
            ))

    time.sleep_ms(40)

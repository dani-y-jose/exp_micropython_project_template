import framebuf
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C

from lib.mesh import MeshNode

# Change this per board before flashing.
NODE_ID = "NEO"

WIDTH = 72
HEIGHT = 40
X_OFFSET = 30  # 72x40 panel sits offset inside the SSD1306's 128-pixel row

ID_BAND = 24   # height reserved for the NODE_ID line
COUNT_BAND = HEIGHT - ID_BAND


class OLED72x40(SSD1306_I2C):
    def show(self):
        self.write_cmd(0x21)
        self.write_cmd(X_OFFSET)
        self.write_cmd(X_OFFSET + self.width - 1)
        self.write_cmd(0x22)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


def best_scale(text, max_w, max_h):
    """Largest integer scale so text fits in a max_w x max_h area."""
    return max(1, min(max_w // (8 * len(text)), max_h // 8))


def draw_scaled(display, text, x, y, scale):
    """Render `text` at `(x,y)` scaled up by integer `scale` from the 8x8 font."""
    if scale == 1:
        display.text(text, x, y, 1)
        return
    w = 8 * len(text)
    buf = bytearray(w)  # MONO_VLSB: 1 byte per column for 8-tall
    fb = framebuf.FrameBuffer(buf, w, 8, framebuf.MONO_VLSB)
    fb.text(text, 0, 0, 1)
    for ty in range(8):
        for tx in range(w):
            if fb.pixel(tx, ty):
                display.fill_rect(x + tx * scale, y + ty * scale, scale, scale, 1)


def render(oled, counter):
    oled.fill(0)
    draw_scaled(oled, NODE_ID, 0, 0, best_scale(NODE_ID, WIDTH, ID_BAND))
    txt = str(counter)
    draw_scaled(oled, txt, 0, ID_BAND, best_scale(txt, WIDTH, COUNT_BAND))
    oled.show()


i2c = I2C(0, sda=Pin(5), scl=Pin(6), freq=400_000)
oled = OLED72x40(WIDTH, HEIGHT, i2c)

mesh = MeshNode(NODE_ID, channel=1, ttl=3)
print("mesh oled node", NODE_ID, "active")

counter = 0
render(oled, counter)

while True:
    pkt = mesh.recv(timeout_ms=2000)
    if pkt and pkt.get("id") != NODE_ID:
        print("rx:", pkt)
    counter += 1
    status = "alert" if counter % 5 == 0 else "ok"
    mesh.broadcast({"count": counter, "status": status})
    render(oled, counter)

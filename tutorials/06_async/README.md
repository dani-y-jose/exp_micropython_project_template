# 06 — asyncio (Cooperative Multitasking)

Sections 1-5 used a single `while True:` loop and `time.sleep()`. That model breaks down the moment your project needs to do **two things at once** — read a sensor while serving HTTP, blink a heartbeat while listening for a button, debounce ten inputs while pushing data to MQTT.

This section introduces `asyncio` — the single most leveraged tool in modern MicroPython. After this, every other tutorial in this repo can be re-implemented twice as cleanly.

## Concepts

### Cooperative vs preemptive

Threads are **preemptive**: the OS interrupts your code at any instruction to switch tasks. asyncio is **cooperative**: tasks only switch at explicit `await` points. No locks, no race conditions on local variables — but if any task blocks without `await`, *every other task stops too*.

```python
import asyncio

async def blink():
    while True:
        led.toggle()
        await asyncio.sleep_ms(500)   # yield here — other tasks get to run

asyncio.run(blink())
```

`async def` declares a coroutine. `await` is the *only* way to pause without freezing everything. `asyncio.run()` starts the event loop and returns when the top-level coroutine finishes.

### Three ways to start tasks

```python
asyncio.run(coro)                  # entry point — call this once at module bottom
asyncio.create_task(coro)          # schedule to run alongside (fire-and-forget)
await asyncio.gather(c1, c2, c3)   # run several, wait for all to finish
```

In MicroPython tutorials we typically use `gather` for "run forever in parallel" — three blink tasks, a sensor task, a server task — and let the program never return.

### The cardinal sin: blocking calls in coroutines

```python
async def bad():
    time.sleep(1)        # WRONG — freezes every other task for 1 second
    await asyncio.sleep(1)  # right — yields to the loop
```

This includes `urequests.get()`, blocking `socket.recv()`, even `dht.DHT22.measure()` (which busy-waits ~20 ms reading the pulse train). Any millisecond you spend in a non-async call is a millisecond no other task runs.

For unavoidable short blocking calls (like DHT22), the rule of thumb: keep them under ~50 ms and don't worry. For longer blocking work, you'd need to offload to a thread or rewrite the driver.

### Inter-task communication

Three primitives matter:

```python
flag = asyncio.Event()
await flag.wait()      # one task awaits
flag.set()             # another sets — both unblock

queue = asyncio.Queue()
await queue.put(item)  # producer
item = await queue.get()  # consumer (blocks until available)

irq_flag = asyncio.ThreadSafeFlag()
# ↑ the only one safe to call from an IRQ handler
```

`Event` / `Queue` are the standard patterns. `ThreadSafeFlag` is MicroPython's bridge between hardware interrupts and async code — see [23_async_button_event.py](23_async_button_event.py).

### MicroPython specifics

- The module is **`asyncio`** on modern firmware (was `uasyncio`); both names usually work but stick to `asyncio`.
- `asyncio.start_server(handler, host, port)` gives you a non-blocking TCP server — used in [25_async_web_server.py](25_async_web_server.py).
- CPython features that don't exist on MicroPython: `asyncio.subprocess`, `loop.run_in_executor`, `async with` context managers for arbitrary objects (some work, some don't), `asyncio.to_thread()`.
- `asyncio.sleep(seconds_float)` and `asyncio.sleep_ms(int)` both work; the `_ms` variant is more idiomatic in embedded code.

## Wiring

No new wiring beyond what previous sections used:
- Onboard LED (script 21, 22, 23, 25).
- Button on `BUTTON` pin (script 23) — same as section 1's button tutorials.
- DHT22 on `I2C_SDA` pin (script 24) — same as script 09.
- WiFi credentials in `lib/secrets.py` (script 25).

## Board notes

- **ESP32 / ESP32-S3 / ESP32-C3**: `asyncio` and `asyncio.start_server` are built in. `ThreadSafeFlag` works as documented.
- **RP2040 (Pico W)**: same — RP2 firmware ships full `asyncio`. WiFi adds latency but doesn't block the loop if you stick to async sockets.
- **RP2040 (no WiFi)**: scripts 21-24 work; script 25 needs WiFi.

## Try changing

- `21_async_blink.py`: replace `await asyncio.sleep_ms(500)` with `time.sleep_ms(500)` — the program still works (only one task), but you've lost the ability to add more.
- `22_async_two_tasks.py`: add a third task at a third rate — note how trivial it is vs the equivalent in `04_hardware_timers.py`.
- `23_async_button_event.py`: try setting the flag from inside a regular `Event` instead of `ThreadSafeFlag` — what crashes, and why?
- `24_async_pipeline.py`: add a second consumer reading from the same queue. Items are distributed across consumers — useful for parallel processing.
- `25_async_web_server.py`: open two browser tabs, refresh both at once. Compare to [04_networking/14_simple_web_server.py](../04_networking/14_simple_web_server.py) — the sync version serializes; this one doesn't.

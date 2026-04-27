import collections
import espnow
import json
import network
import random
import time

BROADCAST = b"\xff" * 6


class MeshNode:
    """Flood-and-suppress mesh layer over ESP-NOW broadcast.

    Each packet carries (id, seq, ttl). Receivers dedup on (id, seq), then
    rebroadcast with ttl-1 while ttl > 0. Out-of-range nodes reach the
    gateway via intermediate hops.
    """

    def __init__(self, node_id, channel=1, ttl=3, dedup=64):
        self.id = node_id
        self.channel = channel
        self.ttl = ttl
        self.seq = 0
        self._seen = collections.deque((), dedup)
        self._sta = network.WLAN(network.STA_IF)
        self._sta.active(True)
        self._sta.config(channel=channel)
        self._e = espnow.ESPNow()
        self._e.active(True)
        self._e.add_peer(BROADCAST)

    def broadcast(self, data):
        self.seq += 1
        # Suppress our own echoes via dedup before sending.
        self._seen.append((self.id, self.seq))
        pkt = {"id": self.id, "seq": self.seq, "ttl": self.ttl, "data": data}
        self._send(pkt)

    def recv(self, timeout_ms=None):
        # Loop internally so duplicates/parse-errors don't shortcut the timeout
        # — caller's `timeout_ms` means "wait this long for a *new* packet".
        if timeout_ms is None:
            while True:
                pkt = self._handle(*self._e.recv())
                if pkt is not None:
                    return pkt
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        while True:
            remaining = time.ticks_diff(deadline, time.ticks_ms())
            if remaining <= 0:
                return None
            host, raw = self._e.recv(remaining)
            pkt = self._handle(host, raw)
            if pkt is not None:
                return pkt

    def _handle(self, host, raw):
        if not raw:
            return None
        try:
            pkt = json.loads(raw)
        except Exception:
            return None
        key = (pkt.get("id"), pkt.get("seq"))
        if key[0] is None or key[1] is None or key in self._seen:
            return None
        self._seen.append(key)
        ttl = pkt.get("ttl", 0)
        if ttl > 0:
            # Jitter to avoid synchronized collisions across relays.
            time.sleep_ms(random.randint(5, 30))
            relay = dict(pkt)
            relay["ttl"] = ttl - 1
            self._send(relay)
        return pkt

    def _send(self, pkt):
        self._e.send(BROADCAST, json.dumps(pkt))

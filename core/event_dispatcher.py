"""
core/event_dispatcher.py
─────────────────────────
Lightweight pub/sub event dispatcher for CAN signal changes.

Widgets subscribe to signal names. When a new CAN frame is decoded,
the dispatcher fires callbacks only for changed signals.
This replaces the current polling model (widget reads model every tick)
with a push model (dispatcher calls widget when value actually changes).

Usage
-----
    from core.event_dispatcher import dispatcher

    # Subscribe — typically in widget __init__
    dispatcher.subscribe("speed", self._on_speed_change)
    dispatcher.subscribe("fuel",  self._on_fuel_change)

    # Publish — called from main_window _tick after decode
    dispatcher.publish("speed", 72.0)

    # Callback signature
    def _on_speed_change(self, value: float):
        self.speedometer.set_value(value)

Threshold
---------
Set min_delta per signal to avoid repaints for tiny floating-point noise.
Default is 0.0 (fire on any change).
"""

from __future__ import annotations
from typing import Callable


class EventDispatcher:

    def __init__(self):
        # { signal_name: [callback, ...] }
        self._subs:     dict[str, list[Callable]] = {}
        # { signal_name: float }  — last published value
        self._last:     dict[str, float] = {}
        # { signal_name: float }  — minimum change to re-fire
        self._deltas:   dict[str, float] = {}

    # ── Configuration ─────────────────────────────────────────────────────────

    def set_min_delta(self, signal_name: str, delta: float):
        """
        Suppress callbacks unless value changes by at least `delta`.
        Useful to avoid repainting on sub-integer noise.
        e.g. dispatcher.set_min_delta("speed", 0.5)
        """
        self._deltas[signal_name] = delta

    # ── Subscribe ─────────────────────────────────────────────────────────────

    def subscribe(self, signal_name: str, callback: Callable):
        """
        Register a callback for a named signal.
        callback(value: float) will be called on each significant change.
        Multiple subscribers per signal are supported.
        """
        if signal_name not in self._subs:
            self._subs[signal_name] = []
        if callback not in self._subs[signal_name]:
            self._subs[signal_name].append(callback)

    def unsubscribe(self, signal_name: str, callback: Callable):
        """Remove a specific callback."""
        if signal_name in self._subs:
            try:
                self._subs[signal_name].remove(callback)
            except ValueError:
                pass

    def unsubscribe_all(self, signal_name: str):
        """Remove all callbacks for a signal."""
        self._subs.pop(signal_name, None)

    # ── Publish ───────────────────────────────────────────────────────────────

    def publish(self, signal_name: str, value: float):
        """
        Publish a new signal value.
        Fires registered callbacks only if value changed beyond min_delta.
        """
        last  = self._last.get(signal_name)
        delta = self._deltas.get(signal_name, 0.0)

        if last is not None and abs(value - last) < delta:
            return   # below threshold — skip

        self._last[signal_name] = value

        for cb in self._subs.get(signal_name, []):
            try:
                cb(value)
            except Exception as e:
                # Don't let a bad subscriber crash the CAN pipeline
                print(f"[EventDispatcher] Error in {signal_name} callback: {e}")

    def publish_all(self, signals: dict):
        """
        Convenience: publish a dict of {signal_name: value} pairs.
        Called with the output of decode_frame().
        """
        for name, value in signals.items():
            self.publish(name, value)

    # ── Introspection ─────────────────────────────────────────────────────────

    def last_value(self, signal_name: str, default: float = 0.0) -> float:
        """Return most recently published value for a signal."""
        return self._last.get(signal_name, default)

    def subscribed_signals(self) -> list:
        return list(self._subs.keys())

    def subscriber_count(self, signal_name: str) -> int:
        return len(self._subs.get(signal_name, []))

    def reset(self):
        """Clear all state — useful for testing."""
        self._subs.clear()
        self._last.clear()
        self._deltas.clear()

    def __repr__(self) -> str:
        return (f"EventDispatcher("
                f"signals={list(self._subs.keys())}, "
                f"last={self._last})")


# ── Singleton — import this everywhere ────────────────────────────────────────
dispatcher = EventDispatcher()

# Set sensible noise thresholds for the current signals
dispatcher.set_min_delta("speed", 0.5)   # don't repaint for < 0.5 km/h jitter
dispatcher.set_min_delta("fuel",  0.5)   # fuel changes slowly
dispatcher.set_min_delta("temp",  1.0)   # temp in whole degrees is fine
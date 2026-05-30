"""
core/signal_registry.py
────────────────────────
Signal map: CAN ID (int) → list[SignalDef]

This is the software equivalent of a DBC file — hardcoded now,
designed to be swapped with file-based config in Stage 8.

Each SignalDef describes how to extract one physical value from a CAN frame:
  - which byte(s) to read
  - scale / offset to convert raw → engineering units
  - name used by the event dispatcher and vehicle state

Usage
-----
    from core.signal_registry import REGISTRY

    for sig in REGISTRY.get(0x100, []):
        value = sig.extract(frame)
        print(sig.name, value, sig.unit)

Adding real signals later (Stage 6 reverse engineering)
-------------------------------------------------------
    Just add more SignalDef entries to REGISTRY.
    e.g. REGISTRY[0x130] = [SignalDef("real_speed", byte_idx=0, ...)]
"""


class SignalDef:
    """
    Defines one signal extracted from a CAN frame.

    Parameters
    ----------
    name     : str    Signal name, matches VehicleState attribute where possible
    byte_idx : int    Primary byte to read (0-based)
    scale    : float  raw_value * scale = physical value
    offset   : float  physical_value + offset
    unit     : str    Display unit string
    min_val  : float  Clamp minimum after scaling
    max_val  : float  Clamp maximum after scaling
    """

    def __init__(self, name: str, byte_idx: int,
                 scale: float = 1.0, offset: float = 0.0,
                 unit: str = "", min_val: float = None, max_val: float = None):
        self.name     = name
        self.byte_idx = byte_idx
        self.scale    = scale
        self.offset   = offset
        self.unit     = unit
        self.min_val  = min_val
        self.max_val  = max_val

    def extract(self, frame) -> float:
        """
        Extract physical value from a CANFrame.
        Returns float, clamped to [min_val, max_val] if set.
        """
        raw = frame.byte(self.byte_idx)
        val = raw * self.scale + self.offset
        if self.min_val is not None:
            val = max(self.min_val, val)
        if self.max_val is not None:
            val = min(self.max_val, val)
        return val

    def __repr__(self) -> str:
        return (f"SignalDef(name={self.name!r}, byte={self.byte_idx}, "
                f"scale={self.scale}, offset={self.offset}, unit={self.unit!r})")


# ── Signal Registry ───────────────────────────────────────────────────────────
# Keyed by CAN ID (int).
# Mirrors the current fake_data.py / decoder.py signal layout exactly.
# When real hardware arrives, update byte indices + scale/offset here only.

REGISTRY: dict = {

    # 0x100 — Speed frame
    # byte[0] = speed in km/h (raw == physical, 1:1)
    0x100: [
        SignalDef(
            name     = "speed",
            byte_idx = 0,
            scale    = 1.0,
            offset   = 0.0,
            unit     = "km/h",
            min_val  = 0.0,
            max_val  = 255.0,
        ),
    ],

    # 0x200 — Fuel frame
    # byte[1] = fuel level 0-100%
    0x200: [
        SignalDef(
            name     = "fuel",
            byte_idx = 1,
            scale    = 1.0,
            offset   = 0.0,
            unit     = "%",
            min_val  = 0.0,
            max_val  = 100.0,
        ),
    ],

    # 0x300 — Temperature frame
    # byte[0] = (temp - 40), so physical = raw + 40
    0x300: [
        SignalDef(
            name     = "temp",
            byte_idx = 0,
            scale    = 1.0,
            offset   = 40.0,       # matches decoder.py: bytes_list[0] + 40
            unit     = "°C",
            min_val  = 40.0,
            max_val  = 120.0,
        ),
    ],
}


def get_signals(can_id: int) -> list:
    """Return list of SignalDef for a given CAN ID. Empty list if unknown."""
    return REGISTRY.get(can_id, [])


def all_signal_names() -> list:
    """Return sorted list of all known signal names across all IDs."""
    names = []
    for sigs in REGISTRY.values():
        for s in sigs:
            names.append(s.name)
    return sorted(names)
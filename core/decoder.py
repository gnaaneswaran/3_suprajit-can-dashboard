"""
core/decoder.py
───────────────
Upgraded CAN decoder — replaces the old flat decode() function.

TWO interfaces provided:
  1. decode_frame(frame: CANFrame) → dict[str, float]
     Modern path: takes a CANFrame, returns all extracted signals.

  2. decode(can_id: str, data: str) → dict   ← LEGACY SHIM
     Keeps main_window.py working with zero changes.

Both paths go through SignalRegistry, so adding new signals
only requires editing signal_registry.py.

Drop into: core/decoder.py  (replaces existing file)
"""

from core.can_frame import CANFrame
from core.signal_registry import get_signals


# ── Modern API ────────────────────────────────────────────────────────────────

def decode_frame(frame: CANFrame) -> dict:
    """
    Decode all signals from a CANFrame.

    Returns
    -------
    dict mapping signal_name → physical float value
    e.g. {"speed": 72.0}
         {"fuel": 84.0}
         {"temp": 85.0}

    Returns empty dict for unknown CAN IDs.
    """
    result = {}
    for sig in get_signals(frame.can_id):
        result[sig.name] = sig.extract(frame)
    return result


# ── Legacy shim ───────────────────────────────────────────────────────────────
# main_window.py calls: decode(can_id_str, data_str)
# e.g. decode("0x100", "1A FF 00 00 00 00 00 00")
# Returns: {"type": "speed", "value": 26}

def decode(can_id: str, data: str) -> dict:
    """
    Legacy interface — maintains backward compatibility with main_window.py.

    Parameters
    ----------
    can_id : str   e.g. "0x100"
    data   : str   e.g. "1A FF 00 00 00 00 00 00"

    Returns
    -------
    {"type": signal_name, "value": float}  — first signal found
    {"type": "unknown",   "value": 0}      — if CAN ID not in registry
    """
    try:
        can_id_int = int(can_id, 16)
        data_bytes = [int(b, 16) for b in data.split()]
        frame = CANFrame(can_id=can_id_int, data=data_bytes)
        signals = decode_frame(frame)
        if signals:
            # Return first signal — legacy callers only expect one per frame
            name, value = next(iter(signals.items()))
            return {"type": name, "value": value}
    except (ValueError, IndexError):
        pass

    return {"type": "unknown", "value": 0}
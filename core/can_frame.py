"""
core/can_frame.py
─────────────────
Lightweight CAN frame object.
Represents one raw frame as it would arrive from hardware or fake_data.

Drop into: core/can_frame.py
"""

import time


class CANFrame:
    """
    Attributes
    ----------
    timestamp : float       Unix seconds (ms precision)
    can_id    : int         e.g. 0x100
    dlc       : int         Data Length Code (0-8)
    data      : list[int]   Byte values, len == dlc
    raw       : str         Original hex string e.g. "1A FF 00 ..."
    """

    __slots__ = ("timestamp", "can_id", "dlc", "data", "raw")

    def __init__(self, can_id: int, data: list,
                 timestamp: float = None, raw: str = ""):
        self.can_id    = can_id
        self.dlc       = len(data)
        self.data      = data
        self.raw       = raw
        self.timestamp = timestamp if timestamp is not None else time.time()

    # ── Parse from fake_data string format ────────────────────────────────────
    # Format: "1713000000000,0x100,8,1A FF 00 00 00 00 00 00"

    @classmethod
    def from_string(cls, line: str) -> "CANFrame":
        parts = line.strip().split(",", 3)
        if len(parts) < 4:
            raise ValueError(f"Malformed CAN line: {line!r}")
        ts_ms  = int(parts[0])
        can_id = int(parts[1], 16)
        raw    = parts[3].strip()
        data   = [int(b, 16) for b in raw.split()]
        return cls(can_id=can_id, data=data,
                   timestamp=ts_ms / 1000.0, raw=raw)

    def byte(self, index: int, default: int = 0) -> int:
        """Safe byte access — returns default if out of range."""
        if 0 <= index < self.dlc:
            return self.data[index]
        return default

    def to_dict(self) -> dict:
        return {
            "timestamp": round(self.timestamp, 3),
            "can_id":    hex(self.can_id),
            "dlc":       self.dlc,
            "data":      [f"{b:02X}" for b in self.data],
        }

    def __repr__(self) -> str:
        data_str = " ".join(f"{b:02X}" for b in self.data)
        return (f"CANFrame(id={hex(self.can_id)}, dlc={self.dlc}, "
                f"data=[{data_str}], ts={self.timestamp:.3f})")
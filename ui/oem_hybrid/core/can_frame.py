from dataclasses import dataclass
from typing import List


@dataclass
class CANFrame:

    can_id: int

    data: List[int]

    timestamp: float

    dlc: int
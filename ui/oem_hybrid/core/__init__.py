# ui/oem_hybrid/core/__init__.py
#
# MIGRATED — vehicle state and serial reader have moved to the top-level
# core/ and hardware/ packages.  This file re-exports them for any legacy
# import paths that may still reference ui.oem_hybrid.core.*
#
# DO NOT add new state or hardware logic here.
# All clusters must read from core.vehicle_state directly.

from core.vehicle_state  import VehicleState          # noqa: F401
from core.vehicle_state  import vehicle_state          # noqa: F401
from hardware.serial_reader import SerialReader        # noqa: F401
# legacy compatibility
from core.vehicle_state import VehicleState
from core.vehicle_state import vehicle_state
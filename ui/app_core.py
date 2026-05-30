from ui.oem_hybrid.core.vehicle_state import (
    VehicleState
)

from ui.oem_hybrid.core.vehicle_simulator import (
    VehicleSimulator
)


class AppCore:

    def __init__(self):

        self.vehicle_state = VehicleState()

        self.vehicle_simulator = VehicleSimulator(
            self.vehicle_state
        )


CORE = AppCore()

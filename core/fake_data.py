import random
import time
from core.vehicle_model import VehicleModel

model = VehicleModel()


def fake_data_generator():
    """
    Yields CAN frames as fast as the caller polls (no sleep inside).
    Physics (model.update) is called once per three frames so the
    main_window QTimer drives the pace entirely – no added latency.
    """
    _frame = 0
    while True:
        ts = str(int(time.time() * 1000))

        if _frame % 3 == 0:
            # Update physics once per full cycle
            model.update()

        phase = _frame % 3

        if phase == 0:
            speed_byte = int(model.speed) & 0xFF
            data = (f"{speed_byte:02X} " +
                    " ".join(f"{random.randint(0,255):02X}" for _ in range(7)))
            yield f"{ts},0x100,8,{data}"

        elif phase == 1:
            fuel_byte = int(model.fuel) & 0xFF
            data = (f"{random.randint(0,255):02X} {fuel_byte:02X} " +
                    " ".join(f"{random.randint(0,255):02X}" for _ in range(6)))
            yield f"{ts},0x200,8,{data}"

        else:
            temp_byte = int(model.temp - 40) & 0xFF
            data = (f"{temp_byte:02X} " +
                    " ".join(f"{random.randint(0,255):02X}" for _ in range(7)))
            yield f"{ts},0x300,8,{data}"

        _frame += 1
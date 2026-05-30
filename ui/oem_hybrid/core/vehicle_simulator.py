from PyQt5.QtCore import QObject, QTimer

import random


class VehicleSimulator(QObject):

    def __init__(self, state):

        super().__init__()

        self.state = state

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_vehicle
        )

        self.timer.start(50)

    def update_vehicle(self):

        self.state.throttle = (
            self.state.throttle + 1
        ) % 100

        self.state.speed += (
            self.state.throttle * 0.02
        )

        if self.state.speed > 120:
            self.state.speed = 0

        self.state.rpm = int(
            1200 + self.state.speed * 55
        )

        self.state.engine_temp = int(
            40 + self.state.speed * 0.35
        )

        self.state.fuel -= 0.005

        if self.state.fuel < 0:
            self.state.fuel = 100

        self.state.range_km = int(
            self.state.fuel * 2.6
        )

        self.state.trip += (
            self.state.speed / 10000
        )

        self.state.odo += (
            self.state.speed / 10000
        )
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout
)

from ui.controls.toggle_button import ToggleButton


class VehicleStatePanel(QWidget):

    def __init__(self):

        super().__init__()

        grid = QGridLayout(self)

        self.ignition = ToggleButton(
            "IGNITION",
            "#22c55e"
        )

        self.headlight = ToggleButton(
            "HEADLIGHT",
            "#f59e0b"
        )

        self.left = ToggleButton(
            "LEFT",
            "#38bdf8"
        )

        self.right = ToggleButton(
            "RIGHT",
            "#38bdf8"
        )

        self.horn = ToggleButton(
            "HORN",
            "#ef4444"
        )

        self.regen = ToggleButton(
            "REGEN",
            "#8b5cf6"
        )

        grid.addWidget(
            self.ignition, 0, 0
        )

        grid.addWidget(
            self.headlight, 0, 1
        )

        grid.addWidget(
            self.left, 1, 0
        )

        grid.addWidget(
            self.right, 1, 1
        )

        grid.addWidget(
            self.horn, 2, 0
        )

        grid.addWidget(
            self.regen, 2, 1
        )
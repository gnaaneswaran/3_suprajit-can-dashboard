from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout
)

from ui.controls.toggle_button import ToggleButton


class DriveModePanel(QWidget):

    def __init__(self):

        super().__init__()

        lay = QHBoxLayout(self)

        self.eco = ToggleButton(
            "ECO",
            "#22c55e"
        )

        self.normal = ToggleButton(
            "NORMAL",
            "#38bdf8"
        )

        self.sport = ToggleButton(
            "SPORT",
            "#ef4444"
        )

        self.normal.setChecked(True)

        lay.addWidget(self.eco)
        lay.addWidget(self.normal)
        lay.addWidget(self.sport)

    def get_mode(self):

        if self.eco.isChecked():
            return "ECO"

        if self.sport.isChecked():
            return "SPORT"

        return "NORMAL"
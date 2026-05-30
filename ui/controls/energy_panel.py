from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)


class EnergyPanel(QWidget):

    def __init__(
        self,
        energy_model,
        digital_cluster=True
    ):

        super().__init__()

        self.energy = energy_model

        self.digital_cluster = digital_cluster

        self.setStyleSheet("""
            QWidget{
                background:#0f172a;
                border:1px solid #1e293b;
                border-radius:14px;
            }

            QLabel{
                color:#94a3b8;
                font-size:11px;
                font-weight:bold;
                letter-spacing:1px;
                border:none;
            }

            QPushButton{
                background:#111827;
                color:white;
                border:none;
                border-radius:10px;
                padding:12px;
                font-size:12px;
                font-weight:bold;
            }

            QPushButton:hover{
                background:#1e293b;
            }
        """)

        lay = QVBoxLayout(self)

        self.title = QLabel(
            "ENERGY CONTROL"
        )

        lay.addWidget(self.title)

        # --------------------------
        # REFUEL BUTTON
        # --------------------------

        self.refuel_btn = QPushButton(
            "⛽ REFUEL"
        )

        self.refuel_btn.clicked.connect(
            self.energy.refuel
        )

        lay.addWidget(
            self.refuel_btn
        )

        # --------------------------
        # CHARGE BUTTON
        # --------------------------

        self.charge_btn = QPushButton(
            "⚡ RECHARGE"
        )

        self.charge_btn.clicked.connect(
            self.energy.recharge
        )

        lay.addWidget(
            self.charge_btn
        )

        # --------------------------
        # INFO
        # --------------------------

        self.info = QLabel(
            "Fuel/Battery instantly resets to 100%"
        )

        lay.addWidget(
            self.info
        )
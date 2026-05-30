from PyQt5.QtWidgets import QPushButton


class ControlButton(QPushButton):

    def __init__(
        self,
        text,
        color="#38bdf8"
    ):

        super().__init__(text)

        self.setFixedHeight(42)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #0f172a;
                color: {color};
                border: 1px solid #1e293b;
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
                padding: 8px 14px;
            }}

            QPushButton:hover {{
                background-color: #172033;
                border: 1px solid {color};
            }}

            QPushButton:pressed {{
                background-color: {color};
                color: black;
            }}
        """)
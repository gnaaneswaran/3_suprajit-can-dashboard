from PyQt5.QtWidgets import QPushButton


class ToggleButton(QPushButton):

    def __init__(
        self,
        label,
        color="#38bdf8"
    ):

        super().__init__(label)

        self.setCheckable(True)

        self.setFixedHeight(38)

        self.setStyleSheet(f"""
            QPushButton {{
                background:#0f172a;
                color:#64748b;
                border:1px solid #1e293b;
                border-radius:8px;
                font-size:10px;
                font-weight:bold;
                letter-spacing:1px;
            }}

            QPushButton:checked {{
                background:{color};
                color:white;
                border:1px solid {color};
            }}
        """)
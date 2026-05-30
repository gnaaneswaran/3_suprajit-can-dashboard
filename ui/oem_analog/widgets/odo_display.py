from PyQt5.QtGui import *
from PyQt5.QtCore import *


class OdoDisplay:

    def __init__(self):

        self.value = 0.0

    def set_odo(self, v):

        self.value = v

    def draw(self, p, x, y):

        x = int(x)
        y = int(y)

        rect = QRectF(
            x,
            y,
            170,
            38
        )

        p.setPen(QPen(QColor(70, 70, 70), 1))

        p.setBrush(QColor("#101010"))

        p.drawRoundedRect(rect, 4, 4)

        txt = f"{int(self.value):06d}"

        p.setFont(QFont("Consolas", 24, QFont.Bold))

        for i, ch in enumerate(txt):

            digit_rect = QRectF(
                int(x + 8 + (i * 24)),
                int(y + 3),
                22,
                30
            )

            p.setPen(Qt.NoPen)

            p.setBrush(QColor("#050505"))

            p.drawRect(digit_rect)

            p.setPen(QColor("#dfe8f2"))

            p.drawText(
                digit_rect,
                Qt.AlignCenter,
                ch
            )

        p.setPen(QColor("#d0d0d0"))

        p.setFont(QFont("Segoe UI", 11))

        p.drawText(
            int(x + 135),
            int(y + 27),
            "km"
        )
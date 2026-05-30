from PyQt5.QtGui import (
    QColor, QFont, QPen, QPainterPath
)
from PyQt5.QtCore import QRect, QRectF, Qt

_BG   = QColor(6,  12, 22)
_CARD = QColor(18, 28, 48)
_SEL  = QColor(22, 34, 58)
_WHITE = QColor(240, 240, 240)
_DIM   = QColor(120, 140, 175)
_GREEN = QColor(0, 230, 120)

def _font(size, bold=False):
    f = QFont("Arial", size)
    if bold: f.setBold(True)
    return f

def _card(p, x, y, w, h, r=12, color=None):
    color = color or _CARD
    path = QPainterPath()
    path.addRoundedRect(QRectF(x, y, w, h), r, r)
    p.fillPath(path, color)
    p.setPen(QPen(QColor(255,255,255,18), 1))
    p.drawPath(path)


class MenuScreen:

    def render(self, painter, state):
        p = painter
        viewport = painter.viewport()

        W = viewport.width()
        H = viewport.height()
        p.fillRect(QRect(0, 0, W, H), _BG)

        p.setPen(_DIM)
        p.setFont(_font(13))
        p.drawText(QRect(20, 10, 200, 24), Qt.AlignLeft, state.time_string)

        p.setPen(_WHITE)
        p.setFont(_font(18, bold=True))
        p.drawText(QRect(0, 10, W, 30), Qt.AlignCenter, "MENU")

        p.setPen(_DIM)
        p.setFont(_font(18))
        p.drawText(QRect(20, 540, 60, 40), Qt.AlignCenter, "←")

        _card(p, 60, 54, 900, 460, r=14)

        items = [
            ("📊", "Ride Statistics"),
            ("🗺",  "Navigation"),
            ("🏍",  "My Vehicle"),
            ("⚙",  "Settings"),
            ("✦",  "Bluetooth"),
        ]

        ry = 65
        for icon, label in items:
            # row highlight (first item active demo)
            row_bg = _SEL if ry == 65 else _CARD
            _card(p, 70, ry + 2, 878, 68, r=8, color=row_bg)
            p.setPen(_DIM)
            p.setFont(_font(18))
            p.drawText(QRect(82, ry + 2, 40, 68), Qt.AlignCenter, icon)
            p.setPen(_WHITE)
            p.setFont(_font(16))
            p.drawText(QRect(132, ry + 2, 700, 68),
                       Qt.AlignLeft | Qt.AlignVCenter, label)
            p.setPen(_DIM)
            p.setFont(_font(14))
            p.drawText(QRect(900, ry + 2, 40, 68), Qt.AlignCenter, "›")
            ry += 78
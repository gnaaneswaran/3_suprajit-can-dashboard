from PyQt5.QtGui import (
    QColor, QFont, QPen, QPainterPath
)
from PyQt5.QtCore import QRect, QRectF, Qt

_BG    = QColor(6,  12, 22)
_CARD  = QColor(18, 28, 48)
_GREEN = QColor(0, 230, 120)
_WHITE = QColor(240, 240, 240)
_DIM   = QColor(120, 140, 175)
_BLUE  = QColor(30, 100, 220)
_AMBER = QColor(255, 180, 40)

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

def _row(p, x, y, w, icon, label, badge="", has_arrow=True):
    p.setPen(_DIM)
    p.setFont(_font(16))
    p.drawText(QRect(x + 12, y + 8, 28, 32), Qt.AlignCenter, icon)
    p.setPen(_WHITE)
    p.setFont(_font(15))
    p.drawText(QRect(x + 46, y + 10, 400, 28), Qt.AlignLeft | Qt.AlignVCenter, label)
    if badge:
        bw = 50
        bx = x + 46 + 200
        path = QPainterPath()
        path.addRoundedRect(QRectF(bx, y + 13, bw, 22), 6, 6)
        p.fillPath(path, _GREEN)
        p.setPen(QColor(0, 0, 0))
        p.setFont(_font(10, bold=True))
        p.drawText(QRect(bx, y + 13, bw, 22), Qt.AlignCenter, badge)
    if has_arrow:
        p.setPen(_DIM)
        p.setFont(_font(14))
        p.drawText(QRect(x + w - 30, y + 10, 24, 28), Qt.AlignCenter, "›")
    p.setPen(QPen(QColor(255,255,255,10), 1))
    p.drawLine(x + 46, y + 46, x + w - 12, y + 46)


class VehicleScreen:

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
        p.drawText(QRect(0, 10, W, 30), Qt.AlignCenter, "MY VEHICLE")

        # Back
        p.setPen(_DIM)
        p.setFont(_font(18))
        p.drawText(QRect(20, 540, 60, 40), Qt.AlignCenter, "←")

        # ── Card ─────────────────────────────────────────────────────────────
        _card(p, 60, 54, 900, 460, r=14)

        items = [
            ("ℹ",  "Vehicle Info",       "",     True),
            ("⬆",  "Software Update",    "New",  True),
            ("📄", "Documents",          "",     True),
            ("⊙",  "Tyre Pressure",      "",     True),
            ("⚙",  "Service Information","",     True),
        ]

        ry = 65
        for icon, label, badge, arrow in items:
            _row(p, 70, ry, 878, icon, label, badge, arrow)
            ry += 84
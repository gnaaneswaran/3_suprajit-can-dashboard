from PyQt5.QtGui import (
    QColor, QFont, QPen, QPainterPath
)
from PyQt5.QtCore import QRect, QRectF, Qt

_BG    = QColor(6,  12, 22)
_CARD  = QColor(18, 28, 48)
_GREEN = QColor(0, 230, 120)
_WHITE = QColor(240, 240, 240)
_DIM   = QColor(120, 140, 175)

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

def _toggle(p, x, y, on=False):
    bg = _GREEN if on else QColor(60, 70, 90)
    path = QPainterPath()
    path.addRoundedRect(QRectF(x, y, 44, 24), 12, 12)
    p.fillPath(path, bg)
    cx = x + 26 if on else x + 16
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(255,255,255))
    p.drawEllipse(cx - 10, y + 2, 20, 20)

def _row(p, x, y, w, label, right="", toggle=None, arrow=False):
    p.setPen(_WHITE)
    p.setFont(_font(15))
    p.drawText(QRect(x + 16, y + 10, 500, 28), Qt.AlignLeft | Qt.AlignVCenter, label)
    if right:
        p.setPen(_DIM)
        p.setFont(_font(13))
        p.drawText(QRect(x + w - 130, y + 10, 110, 28), Qt.AlignRight | Qt.AlignVCenter, right)
    if toggle is not None:
        _toggle(p, x + w - 60, y + 10, on=toggle)
    if arrow:
        p.setPen(_DIM)
        p.setFont(_font(14))
        p.drawText(QRect(x + w - 30, y + 10, 24, 28), Qt.AlignCenter, "›")
    p.setPen(QPen(QColor(255,255,255,10), 1))
    p.drawLine(x + 16, y + 46, x + w - 16, y + 46)


class BluetoothScreen:

    def render(self, painter, state):
        p = painter
        W, H = 1024, 600

        p.fillRect(QRect(0, 0, W, H), _BG)

        p.setPen(_DIM)
        p.setFont(_font(13))
        p.drawText(QRect(20, 10, 200, 24), Qt.AlignLeft, state.time_string)

        p.setPen(_WHITE)
        p.setFont(_font(18, bold=True))
        p.drawText(QRect(0, 10, W, 30), Qt.AlignCenter, "BLUETOOTH")

        p.setPen(_DIM)
        p.setFont(_font(18))
        p.drawText(QRect(20, 540, 60, 40), Qt.AlignCenter, "←")

        _card(p, 60, 54, 900, 390, r=14)

        _row(p, 70, 65,  878, "Paired Devices",    arrow=True)
        _row(p, 70, 115, 878, "Pair New Device",   arrow=True)
        _row(p, 70, 165, 878, "Call & SMS Alerts",  toggle=state.bluetooth)
        _row(p, 70, 215, 878, "Music Control",      toggle=True)
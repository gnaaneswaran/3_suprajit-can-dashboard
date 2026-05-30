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

def _stat_row(p, x, y, w, label, value, unit):
    p.setPen(_DIM)
    p.setFont(_font(14))
    p.drawText(QRect(x, y, 220, 32), Qt.AlignLeft | Qt.AlignVCenter, label)
    p.setPen(_WHITE)
    p.setFont(_font(22, bold=True))
    p.drawText(QRect(x + 220, y, 160, 32), Qt.AlignRight | Qt.AlignVCenter, str(value))
    p.setPen(_DIM)
    p.setFont(_font(14))
    p.drawText(QRect(x + 386, y, 80, 32), Qt.AlignLeft | Qt.AlignVCenter, unit)
    # divider
    p.setPen(QPen(QColor(255,255,255,12), 1))
    p.drawLine(x, y + 36, x + w, y + 36)


class RideStatsScreen:

    def render(self, painter, state):
        p = painter
        viewport = painter.viewport()

        W = viewport.width()
        H = viewport.height()

        p.fillRect(QRect(0, 0, W, H), _BG)

        # Header
        p.setPen(_DIM)
        p.setFont(_font(13))
        p.drawText(QRect(20, 10, 200, 24), Qt.AlignLeft, state.time_string)

        p.setPen(_WHITE)
        p.setFont(_font(18, bold=True))
        p.drawText(QRect(0, 10, W, 30), Qt.AlignCenter, "RIDE STATISTICS")

        # Back arrow
        p.setPen(_DIM)
        p.setFont(_font(18))
        p.drawText(QRect(20, 540, 60, 40), Qt.AlignCenter, "←")

        # ── Time period tabs ─────────────────────────────────────────────────
        tabs    = ["Day", "Week", "Month", "All Time"]
        tab_x   = 60
        tab_y   = 54
        tab_w   = 180
        tab_h   = 38

        for i, tab in enumerate(tabs):
            tx = tab_x + i * (tab_w + 8)
            is_active = (i == 0)
            bg = _BLUE if is_active else QColor(18, 28, 48)
            _card(p, tx, tab_y, tab_w, tab_h, r=8, color=bg)
            p.setPen(_WHITE if is_active else _DIM)
            p.setFont(_font(13, bold=is_active))
            p.drawText(QRect(tx, tab_y, tab_w, tab_h), Qt.AlignCenter, tab)

        # ── Stats card ───────────────────────────────────────────────────────
        _card(p, 60, 110, 900, 380, r=14)

        rows = [
            ("Distance",       f"{state.stat_distance:.1f}",  "km"),
            ("Avg. Speed",     f"{state.stat_avg_speed:.0f}",  "km/h"),
            ("Avg. Efficiency",f"{state.stat_avg_efficiency:.0f}", "Wh/km"),
            ("Top Speed",      f"{state.stat_top_speed:.0f}",  "km/h"),
        ]

        ry = 130
        for label, value, unit in rows:
            _stat_row(p, 80, ry, 860, label, value, unit)
            ry += 80

        # Graph placeholder
        _card(p, 80, ry + 10, 860, 60, r=8, color=QColor(14, 22, 40))
        p.setPen(_DIM)
        p.setFont(_font(12))
        p.drawText(QRect(80, ry + 10, 860, 60), Qt.AlignCenter,
                   "Graph  (Day / Week / Month)")
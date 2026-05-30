"""
ui/oem_analog/widgets/fuel_gauge.py
──────────────────────────────────────
Separate arc-style fuel gauge.
Reference: Honda Activa — standalone arc below the main speedometer.
Red/white arc, E and F labels, fuel pump icon, own center hub.

Used as a standalone QWidget inside analog_screen.py.
"""

import math
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore    import Qt, QRectF, QPointF, QSize
from PyQt5.QtGui     import (QPainter, QColor, QPen, QBrush,
                              QRadialGradient, QLinearGradient,
                              QPainterPath, QPixmap, QFont)


def _draw_fuel_pump(p: QPainter, cx: float, cy: float, s: float):
    """Draw a simple fuel-pump icon in white."""
    c = QColor("#b0c0d0")
    p.save()
    p.setPen(QPen(c, max(1, int(s // 6))))
    p.setBrush(Qt.NoBrush)
    p.drawRect(int(cx - s*.34), int(cy - s*.38),
               int(s * .48),    int(s * .76))
    p.drawLine(QPointF(cx + s*.14, cy - s*.28),
               QPointF(cx + s*.44, cy - s*.28))
    p.drawLine(QPointF(cx + s*.44, cy - s*.28),
               QPointF(cx + s*.44, cy + s*.06))
    p.restore()


class FuelGaugeWidget(QWidget):
    """
    Standalone arc fuel gauge.
    Arc sweep: 210° to 330° (120° total), E on left, F on right.
    """
    ARC_START = 210
    ARC_SPAN  = 120

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(160, 100)

        self._fuel   = 80.0
        self._cache: QPixmap = None
        self._csz    = QSize(0, 0)

    def set_fuel(self, v: float):
        new = max(0.0, min(100.0, v))
        if abs(new - self._fuel) > 0.8:
            self._fuel = new
            self._cache = None
            self.update()

    def _build(self, W: int, H: int) -> QPixmap:
        px = QPixmap(W, H)
        px.fill(QColor("#0a0d12"))
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)

        cx, cy = W / 2.0, H * 0.52
        R = min(W, H) * 0.48

        # Outer bezel ring
        for w2, col in [(8, "#2a3848"), (4, "#1a2535"), (2, "#111820")]:
            p.setPen(QPen(QColor(col), w2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QRectF(cx-R-4, cy-R-4, (R+4)*2, (R+4)*2))

        # Dial face
        face = QRadialGradient(cx, cy, R)
        face.setColorAt(0.0, QColor("#181818"))
        face.setColorAt(0.7, QColor("#0e0e0e"))
        face.setColorAt(1.0, QColor("#060606"))
        p.setBrush(QBrush(face)); p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(cx-R, cy-R, R*2, R*2))

        ar = R - 10
        frect = QRectF(cx-ar, cy-ar, ar*2, ar*2)

        # Background track
        p.setPen(QPen(QColor("#161616"), 12, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect,
                  int(self.ARC_START * 16),
                  int(self.ARC_SPAN  * 16))

        # Low-fuel red zone (E side, 0–25%)
        red_span = int(self.ARC_SPAN * 0.28)
        rc = QColor("#cc2020"); rc.setAlpha(50)
        p.setPen(QPen(rc, 16, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect, int(self.ARC_START * 16), red_span * 16)
        p.setPen(QPen(QColor("#cc2020"), 8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect, int(self.ARC_START * 16), red_span * 16)

        # White zone (25–100%)
        white_start = self.ARC_START + red_span
        white_span  = self.ARC_SPAN  - red_span
        wc = QColor("#b8c8d8"); wc.setAlpha(40)
        p.setPen(QPen(wc, 16, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect, int(white_start * 16), int(white_span * 16))
        p.setPen(QPen(QColor("#c0d0e0"), 8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect, int(white_start * 16), int(white_span * 16))

        # Fuel level fill
        filled_span = int((self._fuel / 100.0) * self.ARC_SPAN)
        fc = ("#cc2020" if self._fuel < 20 else
              "#d48020" if self._fuel < 40 else "#c0d0e0")
        gc = QColor(fc); gc.setAlpha(45)
        p.setPen(QPen(gc, 16, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect, int(self.ARC_START * 16), int(filled_span * 16))
        p.setPen(QPen(QColor(fc), 10, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(frect, int(self.ARC_START * 16), int(filled_span * 16))

        # Tick marks
        for i in range(5):
            ratio = i / 4
            deg   = self.ARC_START + ratio * self.ARC_SPAN
            ang   = math.radians(deg)
            ca, sa = math.cos(ang), math.sin(ang)
            t_out = R - 12; t_in = R - 20
            p.setPen(QPen(QColor("#405060"), 1.5))
            p.drawLine(QPointF(cx + ca * t_in,  cy - sa * t_in),
                       QPointF(cx + ca * t_out, cy - sa * t_out))

        # E label
        ea = math.radians(self.ARC_START + 6)
        p.setFont(QFont("Segoe UI", max(7, int(R * 0.16)), QFont.Bold))
        p.setPen(QPen(QColor("#cc3030")))
        p.drawText(QRectF(cx + math.cos(ea)*(R-6) - 10, cy - math.sin(ea)*(R-6) - 7, 20, 14),
                   Qt.AlignCenter, "E")

        # F label
        fa = math.radians(self.ARC_START + self.ARC_SPAN - 6)
        p.setPen(QPen(QColor("#c0d0e0")))
        p.drawText(QRectF(cx + math.cos(fa)*(R-6) - 10, cy - math.sin(fa)*(R-6) - 7, 20, 14),
                   Qt.AlignCenter, "F")

        # Fuel pump icon
        _draw_fuel_pump(p, cx, cy - R * 0.30, int(R * 0.38))

        # Needle
        needle_deg = self.ARC_START + (self._fuel / 100.0) * self.ARC_SPAN
        na  = math.radians(needle_deg)
        nca = math.cos(na); nsa = math.sin(na)
        nl  = ar - 4
        p.setPen(QPen(QColor("#e03030"), 2, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx - nca * 10, cy + nsa * 10),
                   QPointF(cx + nca * nl,  cy - nsa * nl))

        # Hub
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#080808")))
        p.drawEllipse(QRectF(cx-11, cy-11, 22, 22))
        hg = QRadialGradient(cx-2, cy-2, 10)
        hg.setColorAt(0, QColor("#282828")); hg.setColorAt(1, QColor("#080808"))
        p.setBrush(QBrush(hg))
        p.drawEllipse(QRectF(cx-9, cy-9, 18, 18))
        p.setBrush(QBrush(QColor("#303030")))
        p.drawEllipse(QRectF(cx-3, cy-3, 6, 6))

        p.end()
        return px

    def paintEvent(self, _):
        W, H = self.width(), self.height()
        sz   = QSize(W, H)
        if self._cache is None or self._csz != sz:
            self._cache = self._build(W, H)
            self._csz   = sz
        p = QPainter(self)
        p.drawPixmap(0, 0, self._cache)
        p.end()
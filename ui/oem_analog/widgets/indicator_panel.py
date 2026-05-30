"""
ui/oem_analog/widgets/indicator_panel.py
──────────────────────────────────────────
Left and right turn indicator panels.
Reference: Honda Activa — triangular arrow panels on left/right
of the cluster, green arrows with glow when active.
"""

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore    import Qt, QRectF, QPointF, QTimer
from PyQt5.QtGui     import QPainter, QColor, QPen, QBrush, QPainterPath


ARROW_ON  = "#22cc44"   # bright green active
ARROW_OFF = "#0d1a0d"   # very dark off
PANEL_BG  = "#0c1018"
BEZEL_COL = "#1e2a35"


class IndicatorPanel(QWidget):
    """
    A single turn-indicator panel (left OR right).
    direction: "left" | "right"
    """
    def __init__(self, direction: str = "left", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setFixedSize(52, 44)
        self._direction = direction
        self._active    = False
        self._blink     = False

        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._do_blink)
        self._timer.start()

    def set_active(self, on: bool):
        if on != self._active:
            self._active = on
            self.update()

    def _do_blink(self):
        self._blink = not self._blink
        if self._active:
            self.update()

    def paintEvent(self, _):
        W, H = self.width(), self.height()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(0, 0, W, H, QColor(PANEL_BG))

        on = self._active and self._blink

        # Panel trapezoid shape
        panel = QPainterPath()
        if self._direction == "left":
            panel.moveTo(2, H//2)
            panel.lineTo(8, 4)
            panel.lineTo(W-2, 4)
            panel.lineTo(W-2, H-4)
            panel.lineTo(8, H-4)
            panel.closeSubpath()
        else:
            panel.moveTo(W-2, H//2)
            panel.lineTo(W-8, 4)
            panel.lineTo(2, 4)
            panel.lineTo(2, H-4)
            panel.lineTo(W-8, H-4)
            panel.closeSubpath()

        # Panel background
        bg_col = QColor("#0e1e0e") if on else QColor("#0a100a")
        p.setBrush(QBrush(bg_col)); p.setPen(Qt.NoPen)
        p.drawPath(panel)
        p.setPen(QPen(QColor(BEZEL_COL), 1.5)); p.setBrush(Qt.NoBrush)
        p.drawPath(panel)

        # Arrow
        cx, cy = W / 2, H / 2
        aw = W * 0.35; ah = H * 0.38

        if on:
            glow = QColor(ARROW_ON); glow.setAlpha(55)
            p.setPen(Qt.NoPen); p.setBrush(QBrush(glow))
            gpath = QPainterPath()
            if self._direction == "left":
                gpath.addEllipse(QRectF(cx-aw-8, cy-ah-6, (aw+8)*2, (ah+6)*2))
            else:
                gpath.addEllipse(QRectF(cx-aw-8, cy-ah-6, (aw+8)*2, (ah+6)*2))
            p.drawPath(gpath)

        arrow_col = QColor(ARROW_ON) if on else QColor(ARROW_OFF)
        p.setPen(QPen(arrow_col, 2))
        p.setBrush(QBrush(arrow_col))

        if self._direction == "left":
            pts = [QPointF(cx - aw, cy),
                   QPointF(cx + aw * 0.3, cy - ah),
                   QPointF(cx + aw * 0.3, cy + ah)]
        else:
            pts = [QPointF(cx + aw, cy),
                   QPointF(cx - aw * 0.3, cy - ah),
                   QPointF(cx - aw * 0.3, cy + ah)]
        p.drawPolygon(*pts)
        p.end()
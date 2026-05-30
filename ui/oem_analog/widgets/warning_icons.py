"""
ui/oem_analog/widgets/warning_icons.py
────────────────────────────────────────
Warning / telltale icon widgets.
Reference: Honda Activa — headlight (blue), engine (amber),
drawn as compact icon badges on left/right of cluster.
All icons drawn with QPainter (no images or emoji).
"""

from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore    import Qt, QRectF, QPointF
from PyQt5.QtGui     import QPainter, QColor, QPen, QBrush, QPainterPath, QFont


# ── Icon colour presets ───────────────────────────────────────
ICON_BLUE   = "#3080e0"   # headlight / high beam
ICON_AMBER  = "#e09020"   # engine / check
ICON_GREEN  = "#22cc44"   # neutral / eco
ICON_RED    = "#e02020"   # danger


def _badge_bg(p: QPainter, cx: float, cy: float, r: float, on: bool, col: str):
    """Draw rounded square badge background."""
    c = QColor(col)
    if on:
        gc = QColor(c); gc.setAlpha(40)
        p.setBrush(QBrush(gc)); p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(cx-r-3, cy-r-3, (r+3)*2, (r+3)*2), 5, 5)
    bg = QColor("#0c1018") if not on else QColor("#0d1a10")
    p.setBrush(QBrush(bg))
    p.setPen(QPen(QColor(col if on else "#1e2a35"), 1.5))
    p.drawRoundedRect(QRectF(cx-r, cy-r, r*2, r*2), 4, 4)


class HeadlightIcon(QWidget):
    """Blue headlight (high-beam) indicator."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 36)
        self._on = False

    def set_on(self, v: bool):
        if v != self._on: self._on = v; self.update()

    def paintEvent(self, _):
        W, H = self.width(), self.height()
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(0, 0, W, H, QColor("#0a0d12"))
        cx, cy = W/2, H/2; r = min(W, H)*0.44
        col = ICON_BLUE if self._on else "#152030"
        _badge_bg(p, cx, cy, r, self._on, ICON_BLUE)
        # Headlight symbol: semi-circle + beams
        c = QColor(col)
        p.setPen(QPen(c, max(1, int(r*0.22))))
        p.setBrush(Qt.NoBrush)
        p.drawArc(QRectF(cx-r*0.5, cy-r*0.5, r, r), 90*16, 180*16)
        # Beam lines
        for i, dy in enumerate([-r*0.22, 0, r*0.22]):
            p.drawLine(QPointF(cx+r*0.15, cy+dy),
                       QPointF(cx+r*0.7,  cy+dy))
        p.end()


class EngineIcon(QWidget):
    """Amber engine-check indicator."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 36)
        self._on = False

    def set_on(self, v: bool):
        if v != self._on: self._on = v; self.update()

    def paintEvent(self, _):
        W, H = self.width(), self.height()
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(0, 0, W, H, QColor("#0a0d12"))
        cx, cy = W/2, H/2; r = min(W, H)*0.42
        col = ICON_AMBER if self._on else "#201808"
        _badge_bg(p, cx, cy, r, self._on, ICON_AMBER)
        # Engine block outline
        c = QColor(col)
        p.setPen(QPen(c, max(1, int(r*0.18)))); p.setBrush(Qt.NoBrush)
        s = r * 0.45
        # Block body
        p.drawRect(QRectF(cx-s*0.9, cy-s*0.5, s*1.8, s*1.0))
        # Exhaust pipe left
        p.drawLine(QPointF(cx-s*0.9, cy-s*0.2), QPointF(cx-s*1.3, cy-s*0.2))
        p.drawLine(QPointF(cx-s*1.3, cy-s*0.2), QPointF(cx-s*1.3, cy+s*0.4))
        # Piston top
        p.drawLine(QPointF(cx-s*0.35, cy-s*0.5), QPointF(cx-s*0.35, cy-s*0.9))
        p.drawLine(QPointF(cx+s*0.35, cy-s*0.5), QPointF(cx+s*0.35, cy-s*0.9))
        p.drawLine(QPointF(cx-s*0.6, cy-s*0.9), QPointF(cx+s*0.6, cy-s*0.9))
        p.end()


class GenericWarningIcon(QWidget):
    """Generic warning badge — label text inside coloured badge."""
    def __init__(self, label: str, color: str = ICON_AMBER, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 32)
        self._label = label
        self._color = color
        self._on    = False

    def set_on(self, v: bool):
        if v != self._on: self._on = v; self.update()

    def paintEvent(self, _):
        W, H = self.width(), self.height()
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(0, 0, W, H, QColor("#0a0d12"))
        col = self._color if self._on else "#1a2030"
        p.setPen(QPen(QColor(col), 1.5))
        if self._on:
            gc = QColor(self._color); gc.setAlpha(35)
            p.setBrush(QBrush(gc))
        else:
            p.setBrush(QBrush(QColor("#0c1018")))
        p.drawRoundedRect(QRectF(2, 2, W-4, H-4), 4, 4)
        f = QFont("Segoe UI", max(6, int(H*0.28)), QFont.Bold)
        p.setFont(f); p.setPen(QPen(QColor(col)))
        p.drawText(QRectF(0, 0, W, H), Qt.AlignCenter, self._label)
        p.end()
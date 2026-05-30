# widgets/painter_icons.py — Suprajit Hybrid Cluster
# Pure QPainter icon helpers (no emoji, no image files).
# Also houses the tiny QWidget subclasses that wrap each icon for layout use.

from PyQt5.QtCore  import Qt, QRectF, QPointF
from PyQt5.QtGui   import QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget

from ui.oem_hybrid.core.palette import P


# ─────────────────────────────────────────────────────────────────────────────
#  DRAW HELPERS  — stateless functions, accept a live QPainter
# ─────────────────────────────────────────────────────────────────────────────

def draw_fuel_icon(painter: QPainter, cx: float, cy: float,
                   size: int, color: str):
    """Simple fuel-pump silhouette."""
    c = QColor(color)
    s = size
    painter.setPen(QPen(c, max(1, s // 6)))
    painter.setBrush(Qt.NoBrush)
    # body rectangle
    painter.drawRect(int(cx - s*0.35), int(cy - s*0.4),
                     int(s * 0.5),      int(s * 0.8))
    # nozzle arm (right side)
    painter.drawLine(QPointF(cx + s*0.15, cy - s*0.30),
                     QPointF(cx + s*0.45, cy - s*0.30))
    painter.drawLine(QPointF(cx + s*0.45, cy - s*0.30),
                     QPointF(cx + s*0.45, cy + s*0.05))
    # horizontal slot inside body
    painter.setPen(QPen(c, max(1, s // 8)))
    painter.drawLine(QPointF(cx - s*0.12, cy - s*0.15),
                     QPointF(cx + s*0.12, cy - s*0.15))


def draw_location_icon(painter: QPainter, cx: float, cy: float,
                        size: int, color: str):
    """Map-pin / teardrop drop."""
    c = QColor(color)
    painter.setPen(QPen(c, max(1, size // 7)))
    painter.setBrush(Qt.NoBrush)
    r    = size * 0.35
    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy - size * 0.1), r, r)
    path.moveTo(cx, cy - size * 0.1 + r)
    path.lineTo(cx, cy + size * 0.45)
    painter.drawPath(path)


def draw_thermometer(painter: QPainter, cx: float, cy: float,
                      size: int, color: str):
    """Minimal thermometer stem + bulb."""
    c = QColor(color)
    painter.setPen(QPen(c, max(1, size // 7)))
    painter.setBrush(Qt.NoBrush)
    # stem
    painter.drawLine(QPointF(cx, cy - size*0.42),
                     QPointF(cx, cy + size*0.15))
    # filled bulb
    painter.setBrush(QBrush(c))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(QRectF(cx - size*0.18, cy + size*0.14,
                                size*0.36,      size*0.36))


def draw_stand_icon(painter: QPainter, cx: float, cy: float,
                     size: int, color: str):
    """Side-stand triangle."""
    c = QColor(color)
    painter.setPen(QPen(c, max(1, size // 7)))
    painter.setBrush(Qt.NoBrush)
    pts = [
        QPointF(cx,              cy - size*0.42),
        QPointF(cx + size*0.30,  cy + size*0.42),
        QPointF(cx - size*0.30,  cy + size*0.42),
    ]
    painter.drawPolygon(*pts)


def draw_bluetooth_icon(painter: QPainter, cx: float, cy: float,
                         size: int, color: str):
    """Simplified Bluetooth 'B' lightning bolt."""
    c = QColor(color)
    s = size * 0.4
    painter.setPen(QPen(c, 2))
    painter.setBrush(Qt.NoBrush)
    painter.drawLine(QPointF(cx, cy - s),        QPointF(cx, cy + s))
    painter.drawLine(QPointF(cx, cy - s),        QPointF(cx + s*0.6, cy - s*0.4))
    painter.drawLine(QPointF(cx + s*0.6, cy - s*0.4), QPointF(cx, cy))
    painter.drawLine(QPointF(cx, cy),             QPointF(cx + s*0.6, cy + s*0.4))
    painter.drawLine(QPointF(cx + s*0.6, cy + s*0.4), QPointF(cx, cy + s))


# ─────────────────────────────────────────────────────────────────────────────
#  ICON LABEL WIDGETS  — tiny QWidget wrappers for use inside QLayouts
# ─────────────────────────────────────────────────────────────────────────────

class BTIconWidget(QWidget):
    """Bluetooth icon, fixed-size, muted color."""
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_bluetooth_icon(p, self.width()/2, self.height()/2,
                            min(self.width(), self.height()), P["lcd_muted"])
        p.end()


class FuelIconWidget(QWidget):
    """Fuel-pump icon, fixed-size, muted color."""
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_fuel_icon(p, self.width()/2, self.height()/2,
                       int(min(self.width(), self.height()) * 0.85),
                       P["lcd_muted"])
        p.end()


class LocIconWidget(QWidget):
    """Location pin icon, fixed-size, muted color."""
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_location_icon(p, self.width()/2, self.height()/2,
                           int(min(self.width(), self.height()) * 0.85),
                           P["lcd_muted"])
        p.end()


class ThermIconWidget(QWidget):
    """Thermometer icon, fixed-size, muted color."""
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_thermometer(p, self.width()/2, self.height()/2,
                         min(self.width(), self.height()), P["lcd_muted"])
        p.end()


class StandIconWidget(QWidget):
    """Side-stand triangle icon, fixed-size, muted color."""
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        draw_stand_icon(p, self.width()/2, self.height()/2,
                        min(self.width(), self.height()), P["lcd_muted"])
        p.end()

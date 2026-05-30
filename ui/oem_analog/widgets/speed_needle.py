"""
ui/oem_analog/widgets/speed_needle.py
──────────────────────────────────────
Tapered needle, hub, and NeedlePhysics (spring-damper) for the
centre speedometer dial.

Needle angle is derived from the same ARC_QT_START / ARC_QT_SPAN
constants as speed_arc.py, guaranteeing the tip always tracks
the filled arc edge precisely.
"""

import math

from PyQt5.QtGui  import QPen, QColor, QBrush, QRadialGradient, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF

from .speed_arc import ARC_QT_START, ARC_QT_SPAN, SPEED_MAX


# ─────────────────────────────────────────────────────────────────────────────
# Physics
# ─────────────────────────────────────────────────────────────────────────────

class NeedlePhysics:
    """
    Simple spring-damper to make the needle overshoot and settle.
    Call tick(target_speed) every frame; it returns the smoothed speed.
    """

    def __init__(self):
        self._pos = 0.0        # current displayed speed
        self._vel = 0.0        # current velocity (speed units / frame)

        # Tune these for desired feel:
        self.spring   = 0.04   # restoring force  (higher = faster response)
        self.damping  = 0.85   # velocity decay   (lower = more overshoot)

    def tick(self, target: float) -> float:
        error       = target - self._pos
        self._vel  += error * self.spring
        self._vel  *= self.damping
        self._pos  += self._vel
        self._pos   = max(0.0, min(SPEED_MAX, self._pos))
        return self._pos

    def reset(self):
        self._pos = 0.0
        self._vel = 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Angle helper
# ─────────────────────────────────────────────────────────────────────────────

def _needle_math_angle(speed: float) -> float:
    """
    Standard math angle (radians, CCW from east / 3-o'clock axis)
    for the needle tip at the given speed.

    Derivation:
      qt_angle  = ARC_QT_START + (speed / SPEED_MAX) * ARC_QT_SPAN
      math_angle = radians(90 - qt_angle)
        (because Qt 0° = east, math 0° = east; but Qt y-axis is flipped,
         so the sign of the y component must be inverted when drawing)
    """
    pct      = max(0.0, min(1.0, speed / SPEED_MAX))
    qt_angle = ARC_QT_START + pct * ARC_QT_SPAN
    return math.radians(90.0 - qt_angle)


# ─────────────────────────────────────────────────────────────────────────────
# Drawing
# ─────────────────────────────────────────────────────────────────────────────

def draw_needle(p, cx: float, cy: float, R: float, speed: float):
    """
    Draw a tapered needle (wide at base, pointed at tip).
    Tip follows the arc track at radius (R - 19).
    """
    ang   = _needle_math_angle(speed)
    cos_a = math.cos(ang)
    sin_a = math.sin(ang)

    tip_r  = R - 19      # tip  distance from pivot
    tail_r = 22          # tail distance from pivot (behind centre)
    hw     = 3.5         # half-width of needle at tail

    # Perpendicular direction (for widening the tail)
    perp_x =  sin_a      #  90° CCW rotation of (cos_a, -sin_a) in screen space
    perp_y =  cos_a

    tip   = QPointF(cx + cos_a * tip_r,  cy - sin_a * tip_r)
    base1 = QPointF(cx - cos_a * tail_r + perp_x * hw,
                    cy + sin_a * tail_r + perp_y * hw)
    base2 = QPointF(cx - cos_a * tail_r - perp_x * hw,
                    cy + sin_a * tail_r - perp_y * hw)

    poly = QPolygonF([tip, base1, base2])

    # Drop shadow
    p.save()
    shadow_off = QPointF(2, 2)
    shadow_poly = QPolygonF([tip + shadow_off, base1 + shadow_off, base2 + shadow_off])
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(0, 0, 0, 80))
    p.drawPolygon(shadow_poly)
    p.restore()

    # Needle body
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#d82020"))
    p.drawPolygon(poly)

    # Highlight stripe along top edge of needle
    hi_tip   = QPointF(cx + cos_a * tip_r,       cy - sin_a * tip_r)
    hi_base  = QPointF(cx - cos_a * tail_r + perp_x * (hw * 0.5),
                       cy + sin_a * tail_r + perp_y * (hw * 0.5))
    p.setPen(QPen(QColor(255, 80, 80, 90), 1.5, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(hi_base, hi_tip)


def draw_hub(p, cx: float, cy: float):
    """
    Multi-layer hub at needle pivot centre.
    """
    # Outer shadow ring
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#030507"))
    p.drawEllipse(QRectF(cx - 20, cy - 20, 40, 40))

    # Bezel ring
    p.setPen(QPen(QColor("#1e2c3c"), 3))
    p.setBrush(QColor("#0a0c10"))
    p.drawEllipse(QRectF(cx - 17, cy - 17, 34, 34))

    # Outer hub face
    p.setPen(QPen(QColor("#243040"), 1.5))
    p.setBrush(QColor("#0d0d0d"))
    p.drawEllipse(QRectF(cx - 14, cy - 14, 28, 28))

    # Inner hub with radial gradient
    hg = QRadialGradient(cx - 3, cy - 3, 11)
    hg.setColorAt(0.0, QColor("#2e2e2e"))
    hg.setColorAt(0.6, QColor("#141414"))
    hg.setColorAt(1.0, QColor("#060606"))
    p.setPen(Qt.NoPen)
    p.setBrush(hg)
    p.drawEllipse(QRectF(cx - 12, cy - 12, 24, 24))

    # Centre screw dot
    p.setBrush(QColor("#050505"))
    p.drawEllipse(QRectF(cx - 4, cy - 4, 8, 8))

    # Tiny specular highlight on hub
    p.setBrush(QColor(255, 255, 255, 18))
    p.drawEllipse(QRectF(cx - 8, cy - 10, 10, 6))
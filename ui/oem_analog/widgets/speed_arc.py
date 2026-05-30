"""
ui/oem_analog/widgets/speed_arc.py
────────────────────────────────────
Draws the blue (0-80) and red (80-120) speed arcs on the centre dial.

Arc geometry (shared with ticks + needle):
  Qt arc convention: 0° = 3-o'clock, positive = CCW
  0 km/h  → Qt 75°   (= 15° CW from 12-o'clock)
  120 km/h→ Qt -75°  (= 165° CW from 12-o'clock)
  span    = -150° (clockwise sweep)
"""

from PyQt5.QtGui  import QPen, QColor
from PyQt5.QtCore import Qt, QRectF

# ── Shared arc constants ──────────────────────────────────────────────────────
# Import these in speed_ticks.py and speed_needle.py too.
ARC_QT_START = -75      # Qt degrees: 0 km/h on LEFT (traditional cluster)
ARC_QT_SPAN  =  150     # Qt degrees: positive = CCW → sweeps left to right
SPEED_MAX    = 120.0    # km/h


def _qt_span_for_speed(speed: float) -> float:
    """Filled span (Qt degrees) from start to the given speed."""
    pct = max(0.0, min(1.0, speed / SPEED_MAX))
    return ARC_QT_SPAN * pct


def draw_speed_arcs(p, cx: float, cy: float, R: float):
    """
    Draw the two-tone speed arc track:
      • Full background track (dark)
      • Blue  segment: 0 – 80 km/h
      • Red   segment: 80 – 120 km/h
    """
    arc_r   = R - 15          # radius of the arc track
    rect    = QRectF(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
    lw      = 10              # track line width

    # ── background track ────────────────────────────────────────────
    p.setPen(QPen(QColor("#141414"), lw + 2, Qt.SolidLine, Qt.RoundCap))
    p.setBrush(Qt.NoBrush)
    p.drawArc(rect, ARC_QT_START * 16, ARC_QT_SPAN * 16)

    # ── blue zone: 0 → 80 km/h ──────────────────────────────────────
    blue_span = _qt_span_for_speed(80.0)        # fraction of total span

    p.setPen(QPen(QColor("#1878b8"), lw, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(rect, ARC_QT_START * 16, int(blue_span) * 16)

    # highlight stripe on blue arc
    p.setPen(QPen(QColor(60, 140, 210, 70), 3, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(rect, ARC_QT_START * 16, int(blue_span) * 16)

    # ── red zone: 80 → 120 km/h ─────────────────────────────────────
    # Red arc starts where blue ends.
    red_qt_start = ARC_QT_START + int(blue_span)
    red_span     = ARC_QT_SPAN - int(blue_span)   # remaining span (negative)

    p.setPen(QPen(QColor("#922020"), lw, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(rect, red_qt_start * 16, int(red_span) * 16)

    # highlight stripe on red arc
    p.setPen(QPen(QColor(190, 60, 60, 70), 3, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(rect, red_qt_start * 16, int(red_span) * 16)
"""
ui/oem_analog/widgets/speed_ticks.py
─────────────────────────────────────
Draws major, medium, and fine tick marks + speed labels on the centre dial.
All geometry derives from the same ARC_QT_START / ARC_QT_SPAN constants
as speed_arc.py so ticks are always exactly aligned with the arcs.
"""

import math

from PyQt5.QtGui  import QPen, QColor, QFont
from PyQt5.QtCore import Qt, QPointF, QRectF

from .speed_arc import ARC_QT_START, ARC_QT_SPAN, SPEED_MAX


def _qt_angle_for_speed(speed: float) -> float:
    """Qt arc-degrees for the given speed value."""
    pct = max(0.0, min(1.0, speed / SPEED_MAX))
    return ARC_QT_START + pct * ARC_QT_SPAN


def _math_angle(speed: float) -> float:
    """Standard math angle (radians, CCW from east) for a speed value."""
    qt_deg = _qt_angle_for_speed(speed)
    return math.radians(90.0 - qt_deg)


def draw_speed_ticks(p, cx: float, cy: float, R: float):
    """
    Draw tick marks at every 1 km/h interval (fine), 10 km/h (medium),
    and 20 km/h (major). Labels at every 20 km/h.
    """
    p.setBrush(Qt.NoBrush)

    for v in range(0, int(SPEED_MAX) + 1):
        is_major = (v % 20 == 0)
        is_med   = (v % 10 == 0) and not is_major
        is_fine  = (v %  5 == 0) and not is_med and not is_major

        if not (is_major or is_med or is_fine):
            continue

        ang = _math_angle(v)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)

        if is_major:
            outer = R - 8
            inner = R - 26
            lw    = 2.0
            color = "#c04040" if v >= 80 else "#4898c8"
        elif is_med:
            outer = R - 8
            inner = R - 18
            lw    = 1.5
            color = "#702828" if v >= 80 else "#2a6090"
        else:
            outer = R - 8
            inner = R - 13
            lw    = 1.0
            color = "#242e38"

        p.setPen(QPen(QColor(color), lw, Qt.SolidLine, Qt.FlatCap))
        p.drawLine(
            QPointF(cx + cos_a * inner, cy - sin_a * inner),
            QPointF(cx + cos_a * outer, cy - sin_a * outer)
        )

    # ── speed labels at major ticks ──────────────────────────────────
    label_r = R - 36      # radius for label centres

    for v in range(0, int(SPEED_MAX) + 1, 20):
        ang   = _math_angle(v)
        tx    = cx + math.cos(ang) * label_r
        ty    = cy - math.sin(ang) * label_r
        color = "#c85050" if v >= 80 else "#90bcd8"

        p.setPen(QColor(color))
        p.setFont(QFont("Bahnschrift", 10, QFont.Bold))
        p.drawText(
            QRectF(tx - 16, ty - 9, 32, 18),
            Qt.AlignHCenter | Qt.AlignVCenter,
            str(v)
        )

    # ── "km/h" unit label ────────────────────────────────────────────
    p.setPen(QColor("#607888"))
    p.setFont(QFont("Bahnschrift", 9))
    # Place between arc centre and dial centre, slightly above pivot
    label_y = cy - R * 0.20
    p.drawText(
        QRectF(cx - 24, label_y - 7, 48, 14),
        Qt.AlignHCenter | Qt.AlignVCenter,
        "km/h"
    )
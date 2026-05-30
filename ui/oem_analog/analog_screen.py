"""
ui/oem_analog/analog_screen.py
────────────────────────────────────────────────────────────────
Single-widget OEM cluster renderer.
"""

import math

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import (QPainter, QColor, QPen, QBrush,
                              QRadialGradient, QLinearGradient,
                              QFont, QPainterPath)
from PyQt5.QtCore    import Qt, QRectF, QPointF, QTimer

from ui.oem_analog.widgets.speed_arc    import draw_speed_arcs
from ui.oem_analog.widgets.speed_ticks  import draw_speed_ticks
from ui.oem_analog.widgets.speed_needle import (draw_needle,
                                                draw_hub,
                                                NeedlePhysics)
from ui.oem_analog.widgets.odo_display  import OdoDisplay


# ─────────────────────────────────────────────────────────────────────────────
# Shared arc geometry constants
# ─────────────────────────────────────────────────────────────────────────────
SPEED_ARC_QT_START  = -75      # Qt degrees — 0 km/h on LEFT (traditional)
SPEED_ARC_QT_SPAN   =  150     # Qt degrees — positive = CCW → sweeps left→right
SPEED_MAX           = 120.0


def _speed_qt_angle(speed: float) -> float:
    pct = max(0.0, min(1.0, speed / SPEED_MAX))
    return SPEED_ARC_QT_START + pct * SPEED_ARC_QT_SPAN


def _speed_painter_angle(speed: float) -> float:
    qt_angle = _speed_qt_angle(speed)
    return 90.0 - qt_angle


def _speed_math_angle(speed: float) -> float:
    qt_angle = _speed_qt_angle(speed)
    return math.radians(90.0 - qt_angle)


# ─────────────────────────────────────────────────────────────────────────────
# Arc-gauge helper (side lobes: RPM, eng-temp)
# arc_start / arc_span use Qt convention:
#   arc_start = where the arc begins (Qt degrees, CCW from 3-o'clock)
#   arc_span  = NEGATIVE for clockwise sweep
#
# OEM side gauge:  start at 210° Qt  (= bottom-left, ~7 o'clock)
#                  span  = -240°     (clockwise sweep to bottom-right)
# ─────────────────────────────────────────────────────────────────────────────

def _arc_needle_angle_qt(qt_start: float, qt_span_filled: float) -> float:
    qt_end = qt_start + qt_span_filled
    return math.radians(-qt_end)


def _draw_arc_gauge(p, cx, cy, R, value,
                    arc_start, arc_span,
                    track_color, fill_color,
                    label_top, label_val, unit=""):
    """
    OEM arc gauge.
    arc_start : Qt degrees (CCW from east).  210 = bottom-left (~7 o'clock)
    arc_span  : NEGATIVE = clockwise.        -240 sweeps from 7→5 o'clock CW
    value     : 0-100 %
    """
    rect  = QRectF(cx - R, cy - R, R * 2, R * 2)
    inner = rect.adjusted(8, 8, -8, -8)

    # ── bezel layers ──────────────────────────────────────────────
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#040608"))
    p.drawEllipse(QRectF(cx - R - 6, cy - R - 6, (R + 6) * 2, (R + 6) * 2))

    p.setPen(QPen(QColor("#1e2c3a"), 10))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QRectF(cx - R - 2, cy - R - 2, (R + 2) * 2, (R + 2) * 2))

    p.setPen(QPen(QColor("#2e4258"), 2))
    p.drawEllipse(QRectF(cx - R, cy - R, R * 2, R * 2))

    p.setPen(QPen(QColor("#121c28"), 3))
    p.drawEllipse(rect.adjusted(-1, -1, 1, 1))

    # ── dial face ─────────────────────────────────────────────────
    face = QRadialGradient(cx, cy - R * 0.1, R * 1.1)
    face.setColorAt(0.0,  QColor("#141414"))
    face.setColorAt(0.75, QColor("#0a0a0a"))
    face.setColorAt(1.0,  QColor("#040404"))
    p.setPen(Qt.NoPen)
    p.setBrush(face)
    p.drawEllipse(rect)

    # ── background track (full span, dark) ────────────────────────
    p.setPen(QPen(QColor(track_color), 9, Qt.SolidLine, Qt.RoundCap))
    p.setBrush(Qt.NoBrush)
    p.drawArc(inner, int(arc_start * 16), int(arc_span * 16))

    # ── filled arc (clockwise from arc_start) ─────────────────────
    # arc_span is negative → filled portion is also negative (CW)
    clamped = max(0.0, min(100.0, value))
    filled  = (clamped / 100.0) * arc_span   # same sign as arc_span (negative=CW)

    if abs(filled) > 1:
        glow = QColor(fill_color)
        glow.setAlpha(35)
        p.setPen(QPen(glow, 16, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(inner, int(arc_start * 16), int(filled * 16))

        p.setPen(QPen(QColor(fill_color), 7, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(inner, int(arc_start * 16), int(filled * 16))

        hi = QColor(fill_color)
        hi.setAlpha(80)
        p.setPen(QPen(hi, 2, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(inner, int(arc_start * 16), int(filled * 16))

    # ── tick marks ────────────────────────────────────────────────
    for i in range(5):
        qt_deg   = arc_start + (i / 4.0) * arc_span
        math_deg = 90.0 - qt_deg
        ang      = math.radians(math_deg)
        outer_r  = R - 6
        inner_r  = R - 14 if i % 2 == 0 else R - 10
        p.setPen(QPen(QColor("#3a4a56"), 1.5 if i % 2 == 0 else 1))
        p.drawLine(
            QPointF(cx + math.cos(ang) * inner_r,
                    cy - math.sin(ang) * inner_r),
            QPointF(cx + math.cos(ang) * outer_r,
                    cy - math.sin(ang) * outer_r)
        )

    # ── needle ────────────────────────────────────────────────────
    na     = _arc_needle_angle_qt(arc_start, filled)
    nl     = R - 10
    nb     = 7
    tip_x  = cx + math.cos(na) * nl
    tip_y  = cy - math.sin(na) * nl
    tail_x = cx - math.cos(na) * nb
    tail_y = cy + math.sin(na) * nb
    perp_x = -math.sin(na)
    perp_y = -math.cos(na)
    hw     = 2.5
    poly   = [
        QPointF(tip_x, tip_y),
        QPointF(tail_x + perp_x * hw, tail_y + perp_y * hw),
        QPointF(tail_x - perp_x * hw, tail_y - perp_y * hw),
    ]
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#e03535"))
    p.drawPolygon(*poly)

    # ── hub ───────────────────────────────────────────────────────
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#080808"))
    p.drawEllipse(QRectF(cx - 7, cy - 7, 14, 14))
    hg = QRadialGradient(cx - 2, cy - 2, 6)
    hg.setColorAt(0, QColor("#282828"))
    hg.setColorAt(1, QColor("#060606"))
    p.setBrush(hg)
    p.drawEllipse(QRectF(cx - 5, cy - 5, 10, 10))
    p.setBrush(QColor("#040404"))
    p.drawEllipse(QRectF(cx - 2, cy - 2, 4, 4))

    # ── labels ────────────────────────────────────────────────────
    p.setPen(QColor("#5d6b78"))
    p.setFont(QFont("Bahnschrift", 7))
    p.drawText(QRectF(cx - R, cy - R * 0.46, R * 2, 14),
               Qt.AlignHCenter | Qt.AlignVCenter, label_top)

    p.setPen(QColor("#dfe7ef"))
    p.setFont(QFont("Bahnschrift", 10, QFont.Bold))
    p.drawText(QRectF(cx - R, cy + R * 0.30, R * 2, 18),
               Qt.AlignHCenter | Qt.AlignVCenter, label_val)

    if unit:
        p.setPen(QColor("#5d6b78"))
        p.setFont(QFont("Bahnschrift", 6))
        p.drawText(QRectF(cx - R, cy + R * 0.55, R * 2, 12),
                   Qt.AlignHCenter | Qt.AlignVCenter, unit)


# ─────────────────────────────────────────────────────────────────────────────
# Warning lamp
# ─────────────────────────────────────────────────────────────────────────────

def _draw_lamp(p, cx, cy, r, color, active, label):
    if active:
        halo = QColor(color)
        halo.setAlpha(40)
        p.setPen(QPen(halo, 5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r + 6, r + 6)

    bezel = QColor(color).darker(260) if active else QColor("#14202a")
    p.setPen(QPen(bezel, 1.5))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(cx, cy), r + 2, r + 2)

    face_g = QRadialGradient(cx, cy - r * 0.2, r)
    if active:
        face_g.setColorAt(0.0, QColor(color).lighter(160))
        face_g.setColorAt(0.5, QColor(color))
        face_g.setColorAt(1.0, QColor(color).darker(150))
    else:
        face_g.setColorAt(0.0, QColor("#1a2430"))
        face_g.setColorAt(1.0, QColor("#0a0f14"))
    p.setPen(Qt.NoPen)
    p.setBrush(face_g)
    p.drawEllipse(QPointF(cx, cy), r, r)

    p.setPen(QColor(color if active else "#253545"))
    p.setFont(QFont("Bahnschrift", 6,
                    QFont.Bold if active else QFont.Normal))
    p.drawText(QRectF(cx - 30, cy + r + 2, 60, 12),
               Qt.AlignHCenter | Qt.AlignVCenter, label)


# ─────────────────────────────────────────────────────────────────────────────
# Housing + lobe paths
# ─────────────────────────────────────────────────────────────────────────────

def _make_housing_path(w: float, h: float) -> QPainterPath:
    path = QPainterPath()
    m  = 8
    rx = w * 0.07
    ry = h * 0.16

    path.moveTo(m + rx, m)
    path.cubicTo(w * 0.30, m - 6,   w * 0.65, m - 4,   w - m - rx, m)
    path.quadTo(w - m,     m,        w - m,    m + ry)
    path.cubicTo(w - m - 2, h * 0.45, w - m - 6, h * 0.68, w - m - 8, h - m - ry)
    path.quadTo(w - m - 8, h - m,    w - m - 8 - rx, h - m)
    path.cubicTo(w * 0.65, h - m + 8, w * 0.30, h - m + 6, m + rx, h - m)
    path.quadTo(m,          h - m,    m,         h - m - ry)
    path.cubicTo(m + 2,    h * 0.68, m + 2,    h * 0.45, m, m + ry)
    path.quadTo(m, m, m + rx, m)
    path.closeSubpath()
    return path


def _make_lobe_path(cx, cy, rw, rh, side):
    path = QPainterPath()
    if side == "left":
        path.moveTo(cx - rw, cy)
        path.cubicTo(cx - rw, cy - rh * 0.75,
                     cx - rw * 0.15, cy - rh * 0.95,
                     cx + rw * 0.55, cy - rh * 0.42)
        path.cubicTo(cx + rw * 0.78, cy - rh * 0.08,
                     cx + rw * 0.78, cy + rh * 0.08,
                     cx + rw * 0.55, cy + rh * 0.42)
        path.cubicTo(cx - rw * 0.15, cy + rh * 0.95,
                     cx - rw, cy + rh * 0.75,
                     cx - rw, cy)
    else:
        path.moveTo(cx + rw, cy)
        path.cubicTo(cx + rw, cy - rh * 0.75,
                     cx + rw * 0.15, cy - rh * 0.95,
                     cx - rw * 0.55, cy - rh * 0.42)
        path.cubicTo(cx - rw * 0.78, cy - rh * 0.08,
                     cx - rw * 0.78, cy + rh * 0.08,
                     cx - rw * 0.55, cy + rh * 0.42)
        path.cubicTo(cx + rw * 0.15, cy + rh * 0.95,
                     cx + rw, cy + rh * 0.75,
                     cx + rw, cy)
    path.closeSubpath()
    return path


# ═════════════════════════════════════════════════════════════════════════════

class AnalogScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.speed      = 0.0
        self.fuel       = 82.0
        self.odo_value  = 0.0
        self.trip_value = 0.0
        self.needle = NeedlePhysics()
        self.odo    = OdoDisplay()
        self.setMinimumSize(560, 340)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(16)

    def set_speed(self, v):  self.speed      = float(v)
    def set_fuel(self, v):   self.fuel       = float(v)
    def set_odo(self, v):    self.odo_value  = float(v)
    def set_trip(self, v):   self.trip_value = float(v)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        W, H = float(self.width()), float(self.height())

        bg = QLinearGradient(0, 0, 0, H)
        bg.setColorAt(0, QColor("#0d1018"))
        bg.setColorAt(1, QColor("#04060a"))
        p.fillRect(self.rect(), bg)

        cx      = W * 0.50
        cy      = H * 0.54
        R       = min(W, H) * 0.39
        lobe_rw = W * 0.24
        lobe_rh = H * 0.26
        l_cx    = cx - R * 0.92
        r_cx    = cx + R * 0.92
        lobe_cy = cy

        # Housing
        housing = _make_housing_path(W, H)
        sg = QLinearGradient(0, 0, 0, H)
        sg.setColorAt(0.00, QColor("#1e2830"))
        sg.setColorAt(0.20, QColor("#111820"))
        sg.setColorAt(0.65, QColor("#0a1018"))
        sg.setColorAt(1.00, QColor("#050810"))
        p.setBrush(QBrush(sg))
        p.setPen(Qt.NoPen)
        p.drawPath(housing)
        p.setPen(QPen(QColor("#232e3a"), 2.5))
        p.setBrush(Qt.NoBrush)
        p.drawPath(housing)
        glare = QLinearGradient(0, 8, 0, 38)
        glare.setColorAt(0, QColor(255, 255, 255, 20))
        glare.setColorAt(1, QColor(255, 255, 255, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glare))
        p.drawPath(housing)
        bsh = QLinearGradient(0, H - 55, 0, H)
        bsh.setColorAt(0, QColor(0, 0, 0, 0))
        bsh.setColorAt(1, QColor(0, 0, 0, 100))
        p.setBrush(QBrush(bsh))
        p.drawPath(housing)

        # Side lobes
        l_path = _make_lobe_path(l_cx, lobe_cy, lobe_rw, lobe_rh, "left")
        r_path = _make_lobe_path(r_cx, lobe_cy, lobe_rw, lobe_rh, "right")
        for path, side_cx in [(l_path, l_cx), (r_path, r_cx)]:
            lf = QRadialGradient(side_cx, lobe_cy - lobe_rh * 0.1, lobe_rh)
            lf.setColorAt(0.0, QColor("#0c1018"))
            lf.setColorAt(0.7, QColor("#080c12"))
            lf.setColorAt(1.0, QColor("#030508"))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(lf))
            p.drawPath(path)
            p.setPen(QPen(QColor(0, 0, 0, 110), 9))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
            p.setPen(QPen(QColor("#1e2c3a"), 2))
            p.drawPath(path)

        # Lobe content
        self._draw_left_content(p, l_cx, lobe_cy, lobe_rw, lobe_rh, R)
        self._draw_right_content(p, r_cx, lobe_cy, lobe_rw, lobe_rh, R)

        # Centre dial on top
        self._draw_centre_dial(p, cx, cy, R)

    # ─────────────────────────────────────────────────────────────

    def _draw_centre_dial(self, p, cx, cy, R):
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#030507"))
        p.drawEllipse(QPointF(cx, cy), R + 30, R + 30)

        p.setPen(QPen(QColor("#0d1620"), 20))
        p.setBrush(QColor("#08090e"))
        p.drawEllipse(QPointF(cx, cy), R + 24, R + 24)

        bezel_layers = [
            (14, "#18232e"), (7, "#243040"), (3, "#304458"),
            (1.5, "#3a5870"), (1, "#1e2e40"),
        ]
        for lw, col in bezel_layers:
            p.setPen(QPen(QColor(col), lw))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(cx, cy), R + 10, R + 10)

        p.setPen(QPen(QColor("#4a6880"), 1))
        p.drawArc(QRectF(cx - R - 10, cy - R - 10, (R + 10) * 2, (R + 10) * 2),
                  40 * 16, 100 * 16)

        mid_g = QRadialGradient(cx, cy, R + 8)
        mid_g.setColorAt(0, QColor("#0d1216"))
        mid_g.setColorAt(1, QColor("#04060a"))
        p.setPen(QPen(QColor("#243040"), 4))
        p.setBrush(mid_g)
        p.drawEllipse(QPointF(cx, cy), R + 5, R + 5)

        dial_g = QRadialGradient(cx, cy - R * 0.08, R * 1.05)
        dial_g.setColorAt(0.0,  QColor("#151515"))
        dial_g.setColorAt(0.55, QColor("#0c0c0c"))
        dial_g.setColorAt(0.85, QColor("#070707"))
        dial_g.setColorAt(1.0,  QColor("#030303"))
        p.setPen(QPen(QColor("#141e28"), 2))
        p.setBrush(dial_g)
        p.drawEllipse(QPointF(cx, cy), R, R)

        draw_speed_arcs(p, cx, cy, R)
        draw_speed_ticks(p, cx, cy, R)
        smooth = self.needle.tick(self.speed)
        draw_needle(p, cx, cy, R, smooth)
        draw_hub(p, cx, cy)

        self.odo.set_odo(self.odo_value)
        odo_x = cx - 85
        odo_y = cy + R * 0.44
        self.odo.draw(p, odo_x, odo_y)

        glass = QLinearGradient(cx - R * 0.3, cy - R, cx + R * 0.2, cy - R * 0.1)
        glass.setColorAt(0.0, QColor(255, 255, 255, 28))
        glass.setColorAt(0.5, QColor(255, 255, 255, 8))
        glass.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(glass)
        p.drawEllipse(QPointF(cx - 6, cy - 10), R - 12, R * 0.50)

    # ─────────────────────────────────────────────────────────────
    # Left lobe — warning lamps + eng-temp arc
    # arc_start=210, arc_span=-120  → CW from bottom-left
    # ─────────────────────────────────────────────────────────────

    def _draw_left_content(self, p, cx, cy, rw, rh, R):
        p.setPen(QColor("#3a4e5c"))
        p.setFont(QFont("Bahnschrift", 7))
        p.drawText(QRectF(cx - rw * 0.7, cy - rh * 0.92, rw * 1.4, 13),
                   Qt.AlignHCenter | Qt.AlignVCenter, "VEHICLE STATUS")

        p.setPen(QPen(QColor("#1a2730"), 1))
        p.drawLine(QPointF(cx - rw * 0.65, cy - rh * 0.75),
                   QPointF(cx - rw * 0.05, cy - rh * 0.75))

        lamps = [
            ("ENGINE",     "#e0a020", self.speed > 90),
            ("ABS",        "#ff4040", self.speed > 60),
            ("SIDE STAND", "#d09030", self.speed < 5),
            ("BATTERY",    "#40a0ff", self.speed < 5),
        ]
        lamp_r = max(7, int(rh * 0.18))
        cell_w = rw * 0.55
        cell_h = rh * 0.38
        x0     = cx - rw * 0.65 + cell_w * 0.5
        y0     = cy - rh * 0.60
        for idx, (name, color, active) in enumerate(lamps):
            lx = x0 + (idx % 2) * cell_w
            ly = y0 + (idx // 2) * cell_h
            _draw_lamp(p, lx, ly, lamp_r, color, active, name)

        temp  = 42 + int(self.speed * 0.35)
        t_pct = max(0.0, min(100.0, (temp - 40) / 60.0 * 100))
        arc_R = int(R * 0.72)

        _draw_arc_gauge(
            p,
            cx          = cx - rw * 0.28,
            cy          = cy + rh * 0.18,
            R           = arc_R,
            value       = t_pct,
            arc_start   = 210,    # bottom-left start
            arc_span    = -120,   # NEGATIVE = clockwise sweep
            track_color = "#161616",
            fill_color  = "#e06020",
            label_top   = "ENG TEMP",
            label_val   = f"{temp}°",
            unit        = "°C"
        )

    # ─────────────────────────────────────────────────────────────
    # Right lobe — RPM arc + telemetry bars
    # arc_start=210, arc_span=-240  → CW from bottom-left
    # ─────────────────────────────────────────────────────────────

    def _draw_right_content(self, p, cx, cy, rw, rh, R):
        p.setPen(QColor("#3a4e5c"))
        p.setFont(QFont("Bahnschrift", 7))
        p.drawText(QRectF(cx - rw * 0.6, cy - rh * 0.92, rw * 1.2, 13),
                   Qt.AlignHCenter | Qt.AlignVCenter, "LIVE TELEMETRY")

        p.setPen(QPen(QColor("#1a2730"), 1))
        p.drawLine(QPointF(cx + rw * 0.05, cy - rh * 0.75),
                   QPointF(cx + rw * 0.65, cy - rh * 0.75))

        rpm     = int(1200 + self.speed * 75)
        rpm_pct = min(100.0, (rpm - 1200) / (10200 - 1200) * 100.0)
        arc_R   = int(R * 0.72)

        _draw_arc_gauge(
            p,
            cx          = cx + rw * 0.28,
            cy          = cy - rh * 0.08,
            R           = arc_R,
            value       = rpm_pct,
            arc_start   = 210,    # bottom-left start
            arc_span    = -240,   # NEGATIVE = clockwise sweep
            track_color = "#161616",
            fill_color  = "#40c0ff",
            label_top   = "RPM",
            label_val   = f"{rpm // 100}",
            unit        = "×100"
        )

        accel = min(100, int((self.speed / 120) * 100))
        brake = max(0, 100 - accel)
        temp  = 42 + int(self.speed * 0.35)
        t_pct = max(0.0, min(100.0, (temp - 40) / 60.0 * 100))

        bars = [
            ("ACCEL", accel, "#40c0ff", f"{accel}%"),
            ("BRAKE", brake, "#ff4040", f"{brake}%"),
            ("TEMP",  t_pct, "#ffaa30", f"{temp}°C"),
        ]

        bx       = cx + rw * 0.06
        bw       = rw * 0.88
        by_start = cy + rh * 0.10
        b_step   = int(rh * 0.28)

        for i, (name, pct, color, val_str) in enumerate(bars):
            by = by_start + i * b_step
            p.setPen(QColor("#6a7e8c"))
            p.setFont(QFont("Bahnschrift", 7))
            p.drawText(int(bx), int(by + 1), name)
            p.setPen(QColor("#dfe7ef"))
            p.setFont(QFont("Bahnschrift", 7, QFont.Bold))
            p.drawText(int(bx + bw - 34), int(by + 1), val_str)
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#0a1016"))
            p.drawRoundedRect(QRectF(bx, by + 10, bw, 7), 3, 3)
            fw = bw * (max(0.0, min(100.0, pct)) / 100.0)
            if fw > 0:
                glow = QColor(color)
                glow.setAlpha(40)
                p.setBrush(glow)
                p.drawRoundedRect(QRectF(bx, by + 10, fw, 7), 3, 3)
                p.setBrush(QColor(color))
                p.drawRoundedRect(QRectF(bx, by + 10, fw, 7), 3, 3)
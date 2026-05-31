"""
ui/hybrid_cluster.py
────────────────────────────────────────────────────────────────
Suprajit CAN Bus Analyzer — HYBRID CLUSTER  v3.1

Changes vs v3.0
────────────────
  ✓ date_str: replaced %-d (Linux/macOS only) with tm_mday (cross-platform).
    Works on Windows, Linux, and macOS without ValueError.
  ✓ All data exclusively from core.vehicle_state singleton (vs).
────────────────────────────────────────────────────────────────
"""

import math
import time
import random
from collections import deque

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui  import (
    QPainter, QColor, QPen, QBrush,
    QLinearGradient, QRadialGradient,
    QFont, QPainterPath, QFontMetrics
)

# ── Shared vehicle state ──────────────────────────────────────────────────────
try:
    from core.vehicle_state import vehicle_state as vs
except ImportError:
    class _VS:
        speed = 0.0; fuel = 100.0; battery = 100.0; temp = 42.0
        rpm = 1200.0; odometer = 12458.3; trip = 0.0
        engine_temp = 42.0; lean = 0.0; throttle = 0.0; brake = 0.0
        ride_mode = 0; ride_mode_label = "ECO"
        left_indicator = False; right_indicator = False
        high_beam = False; park_assist_active = False
        _side_stand = True; bluetooth = False; mobile_signal = 3
        avg_speed = 0.0; top_speed = 0.0
        time_string = "07:20 PM"
    vs = _VS()

# ── Palette ───────────────────────────────────────────────────────────────────
C = {
    "bg":        "#05080f",
    "bg2":       "#080d18",
    "bg3":       "#0b1220",
    "card":      "#0d1525",
    "border":    "#1a2535",
    "accent":    "#38bdf8",
    "green":     "#22c55e",
    "yellow":    "#f59e0b",
    "orange":    "#f97316",
    "red":       "#ef4444",
    "text_hi":   "#e8f4ff",
    "text_med":  "#6080a0",
    "text_lo":   "#2a3a4a",
    "eco":       "#4ade80",
    "sport":     "#f87171",
    "city":      "#60a5fa",
    "can_green": "#34d399",
}

# ── Speedometer geometry ──────────────────────────────────────────────────────
_NEEDLE_START_DEG = 220.0     # 0 km/h  — 7 o'clock
_NEEDLE_END_DEG   = -40.0     # 140 km/h — 5 o'clock
_NEEDLE_SWEEP     = _NEEDLE_START_DEG - _NEEDLE_END_DEG   # 260°
_MAX_SPEED        = 140.0


def _speed_to_angle(speed: float) -> float:
    """Standard-maths degrees (CCW from 3-o'clock)."""
    ratio = max(0.0, min(1.0, speed / _MAX_SPEED))
    return _NEEDLE_START_DEG - ratio * _NEEDLE_SWEEP


# ── Cross-platform date helper ────────────────────────────────────────────────
def _fmt_date() -> str:
    """
    Return e.g. "Fri, 30 May" — no leading zero on the day.
    Uses tm_mday (plain int) so it works on Windows, Linux, and macOS.
    %-d  works only on POSIX.
    %#d  works only on Windows.
    tm_mday is an int on every platform.
    """
    t = time.localtime()
    return f"{time.strftime('%a')}, {t.tm_mday} {time.strftime('%b')}"


# ── Helpers ───────────────────────────────────────────────────────────────────
def _draw_text_c(p: QPainter, cx, cy, text, font, color):
    p.setFont(font)
    p.setPen(QColor(color))
    fm = QFontMetrics(font)
    w  = fm.horizontalAdvance(text)
    h  = fm.ascent()
    p.drawText(int(cx - w / 2), int(cy + h / 2), text)


def _temp_color(t: float) -> str:
    if t < 60:   return C["green"]
    if t < 90:   return C["yellow"]
    return C["red"]


def _bat_color(b: float) -> str:
    if b >= 80:  return C["green"]
    if b >= 40:  return C["accent"]
    if b >= 20:  return C["orange"]
    return C["red"]


def _mode_color(mode: str) -> str:
    if mode == "ECO":   return C["eco"]
    if mode == "SPORT": return C["sport"]
    return C["city"]


# ─────────────────────────────────────────────────────────────────────────────
#  Speedometer widget
# ─────────────────────────────────────────────────────────────────────────────
class _SpeedometerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._needle_angle  = _NEEDLE_START_DEG
        self._sweep_active  = True
        self._sweep_forward = True
        self.setMinimumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(16)

    def _tick(self):
        if self._sweep_active:
            step = 5.0
            if self._sweep_forward:
                self._needle_angle -= step
                if self._needle_angle <= _NEEDLE_END_DEG:
                    self._sweep_forward = False
            else:
                self._needle_angle += step
                if self._needle_angle >= _NEEDLE_START_DEG:
                    self._needle_angle = _NEEDLE_START_DEG
                    self._sweep_active = False
        else:
            target = _speed_to_angle(getattr(vs, "speed", 0.0))
            self._needle_angle += (target - self._needle_angle) * 0.18
        self.update()

    def set_speed(self, _):
        pass   # driven by vs.speed in _tick

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H   = self.width(), self.height()
        cx, cy = W / 2, H / 2
        r      = min(W, H) / 2 - 16
        speed   = getattr(vs, "speed",           0.0)
        battery = getattr(vs, "battery",         100.0)
        mode    = getattr(vs, "ride_mode_label", "ECO")
        self._bg(p, cx, cy, r)
        self._arc_track(p, cx, cy, r)
        self._arc_speed(p, cx, cy, r, speed)
        self._arc_battery(p, cx, cy, r * 0.63, battery)
        self._ticks(p, cx, cy, r)
        self._needle(p, cx, cy, r - 22)
        self._center(p, cx, cy, r, speed, battery, mode)
        self._glow(p, cx, cy, r, speed)
        p.end()

    def _bg(self, p, cx, cy, r):
        g = QRadialGradient(cx, cy, r)
        g.setColorAt(0.0,  QColor("#141e2e"))
        g.setColorAt(0.65, QColor("#080e1a"))
        g.setColorAt(1.0,  QColor("#040810"))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QPointF(cx, cy), r + 14, r + 14)
        p.setPen(QPen(QColor("#1a2f4a"), 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r + 13, r + 13)

    def _arc_track(self, p, cx, cy, r):
        rect     = QRectF(cx - r, cy - r, 2 * r, 2 * r)
        qt_start = int((90 - _NEEDLE_START_DEG) * 16)
        p.setPen(QPen(QColor("#1a2535"), 10, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, qt_start, -int(_NEEDLE_SWEEP * 16))

    def _arc_speed(self, p, cx, cy, r, speed):
        zones = [
            (0,   40,  C["green"]),
            (40,  80,  C["yellow"]),
            (80,  110, C["orange"]),
            (110, 140, C["red"]),
        ]
        rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
        for z0, z1, col in zones:
            if speed <= z0:
                break
            draw_to  = min(speed, z1)
            a_start  = _NEEDLE_START_DEG - (z0      / _MAX_SPEED) * _NEEDLE_SWEEP
            a_end    = _NEEDLE_START_DEG - (draw_to / _MAX_SPEED) * _NEEDLE_SWEEP
            qt_start = int((90 - a_start) * 16)
            qt_span  = int((a_start - a_end) * 16)
            p.setPen(QPen(QColor(col), 10, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(rect, qt_start, -qt_span)

    def _arc_battery(self, p, cx, cy, r_in, battery):
        ratio    = max(0.0, min(1.0, battery / 100.0))
        rect     = QRectF(cx - r_in, cy - r_in, 2 * r_in, 2 * r_in)
        qt_start = int((90 - _NEEDLE_START_DEG) * 16)
        p.setPen(QPen(QColor("#162030"), 6, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, qt_start, -int(_NEEDLE_SWEEP * 16))
        fill_sweep = ratio * _NEEDLE_SWEEP
        p.setPen(QPen(QColor(_bat_color(battery)), 6, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(rect, qt_start, -int(fill_sweep * 16))

    def _ticks(self, p, cx, cy, r):
        marks = [0, 20, 40, 60, 80, 100, 120, 140]
        font  = QFont("Consolas", 7, QFont.Bold)
        for spd in marks:
            ang_rad = math.radians(_speed_to_angle(spd))
            ox = cx + (r - 4)  * math.cos(ang_rad)
            oy = cy - (r - 4)  * math.sin(ang_rad)
            ix = cx + (r - 16) * math.cos(ang_rad)
            iy = cy - (r - 16) * math.sin(ang_rad)
            p.setPen(QPen(QColor("#2a3f55"), 1.5))
            p.drawLine(QPointF(ox, oy), QPointF(ix, iy))
            lx = cx + (r - 28) * math.cos(ang_rad)
            ly = cy - (r - 28) * math.sin(ang_rad)
            _draw_text_c(p, lx, ly, str(spd), font, C["text_med"])

    def _needle(self, p, cx, cy, r_needle):
        ang = math.radians(self._needle_angle)
        nx  = cx + r_needle * math.cos(ang)
        ny  = cy - r_needle * math.sin(ang)
        p.setPen(QPen(QColor(255, 255, 255, 35), 9, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx, cy), QPointF(nx, ny))
        p.setPen(QPen(QColor("#e8f4ff"), 2.5, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(cx, cy), QPointF(nx, ny))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(C["accent"])))
        p.drawEllipse(QPointF(cx, cy), 6, 6)
        p.setBrush(QBrush(QColor("#e8f4ff")))
        p.drawEllipse(QPointF(cx, cy), 2.5, 2.5)

    def _center(self, p, cx, cy, r, speed, battery, mode):
        _draw_text_c(p, cx, cy - 6, str(int(speed)),
                     QFont("Consolas", 40, QFont.Bold), C["text_hi"])
        _draw_text_c(p, cx, cy + 30, "km/h",
                     QFont("Segoe UI", 9), C["text_med"])
        # mode pill
        mc     = _mode_color(mode)
        pil_w, pil_h = 52, 18
        pil_x  = cx - pil_w / 2
        pil_y  = cy + 46
        path   = QPainterPath()
        path.addRoundedRect(QRectF(pil_x, pil_y, pil_w, pil_h), 9, 9)
        p.setPen(QPen(QColor(mc), 1))
        bg     = QColor(mc); bg.setAlpha(40)
        p.setBrush(QBrush(bg))
        p.drawPath(path)
        _draw_text_c(p, cx, pil_y + pil_h / 2 + 1, mode,
                     QFont("Segoe UI", 8, QFont.Bold), mc)
        # battery bar
        bar_w  = r * 0.72
        bar_h  = 8
        bar_x  = cx - bar_w / 2
        bar_y  = cy + 74
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#162030")))
        tp = QPainterPath()
        tp.addRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 4, 4)
        p.drawPath(tp)
        fill_w = max(4, bar_w * max(0, min(1, battery / 100.0)))
        fc     = QColor(_bat_color(battery))
        fill_g = QLinearGradient(bar_x, 0, bar_x + fill_w, 0)
        fill_g.setColorAt(0, fc.darker(120))
        fill_g.setColorAt(1, fc)
        p.setBrush(QBrush(fill_g))
        fp = QPainterPath()
        fp.addRoundedRect(QRectF(bar_x, bar_y, fill_w, bar_h), 4, 4)
        p.drawPath(fp)
        _draw_text_c(p, cx, bar_y + bar_h + 11, f"{int(battery)}%",
                     QFont("Consolas", 8, QFont.Bold), _bat_color(battery))

    def _glow(self, p, cx, cy, r, speed):
        if speed < 5:
            return
        alpha = int(25 * speed / _MAX_SPEED)
        col   = C["green"] if speed < 60 else (C["yellow"] if speed < 100 else C["red"])
        g     = QRadialGradient(cx, cy, r + 14)
        c1    = QColor(col); c1.setAlpha(alpha)
        c2    = QColor(col); c2.setAlpha(0)
        g.setColorAt(0.82, c1)
        g.setColorAt(1.0,  c2)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(g))
        p.drawEllipse(QPointF(cx, cy), r + 14, r + 14)


# ─────────────────────────────────────────────────────────────────────────────
#  Info card
# ─────────────────────────────────────────────────────────────────────────────
class _InfoCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(230)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        self._render(p)
        p.end()

    def _render(self, p):
        W, H = self.width(), self.height()
        PAD  = 18

        g = QLinearGradient(0, 0, 0, H)
        g.setColorAt(0,   QColor("#0e1a2e"))
        g.setColorAt(1.0, QColor("#060d1a"))
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, W, H), 14, 14)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(g))
        p.drawPath(path)
        p.setPen(QPen(QColor("#1e3a5f"), 1))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)

        y = PAD + 4

        # Clock
        ts_str = getattr(vs, "time_string", time.strftime("%I:%M %p"))
        _draw_text_c(p, W / 2, y + 12, ts_str,
                     QFont("Consolas", 16, QFont.Bold), C["text_hi"])
        y += 28

        # Date — cross-platform (no %-d / %#d)
        _draw_text_c(p, W / 2, y, _fmt_date(),
                     QFont("Segoe UI", 8), C["text_med"])
        y += 18

        self._div(p, PAD, W - PAD, y); y += 14

        # Big speed
        speed = getattr(vs, "speed", 0.0)
        _draw_text_c(p, W / 2, y + 34, str(int(speed)),
                     QFont("Consolas", 52, QFont.Bold), C["text_hi"])
        y += 64
        _draw_text_c(p, W / 2, y, "km/h", QFont("Segoe UI", 9), C["text_med"])
        y += 16

        self._div(p, PAD, W - PAD, y); y += 14

        # Stats rows
        odo     = getattr(vs, "odometer", 0.0)
        trip    = getattr(vs, "trip",     0.0)
        battery = getattr(vs, "battery",  100.0)
        rng     = max(0, round(battery * 0.85 * 3.5))
        temp    = getattr(vs, "temp",     42.0)

        rows = [
            ("ODO",   f"{odo:,.1f} km",  C["text_hi"]),
            ("TRIP",  f"{trip:.1f} km",  C["accent"]),
            ("RANGE", f"{int(rng)} km",  C["eco"] if rng > 50 else C["red"]),
            ("TEMP",  f"{int(temp)}°C",  _temp_color(temp)),
        ]
        lf    = QFont("Segoe UI", 8, QFont.Bold)
        vf    = QFont("Consolas", 12, QFont.Bold)
        row_h = 28
        for label, value, vcol in rows:
            p.setFont(lf)
            p.setPen(QColor(C["text_lo"]))
            p.drawText(PAD, int(y + 14), label)
            p.setFont(vf)
            p.setPen(QColor(vcol))
            fm = QFontMetrics(vf)
            p.drawText(int(W - PAD - fm.horizontalAdvance(value)),
                       int(y + 14), value)
            y += row_h

        self._div(p, PAD, W - PAD, y); y += 12

        # Side stand
        ss     = getattr(vs, "_side_stand", False)
        ss_on  = ss and speed < 1
        ss_lbl = "⚠  SIDE STAND DOWN" if ss_on else "SIDE STAND UP"
        _draw_text_c(p, W / 2, y + 9, ss_lbl,
                     QFont("Segoe UI", 8, QFont.Bold),
                     C["red"] if ss_on else C["green"])

    @staticmethod
    def _div(p, x1, x2, y):
        p.setPen(QPen(QColor("#1e3050"), 1))
        p.drawLine(QPointF(x1, y), QPointF(x2, y))


# ─────────────────────────────────────────────────────────────────────────────
#  Status icon bar
# ─────────────────────────────────────────────────────────────────────────────
class _StatusIconBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self._blink = False
        t = QTimer(self)
        t.timeout.connect(self._toggle)
        t.start(500)

    def _toggle(self):
        self._blink = not self._blink
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#060a14")))
        p.drawRect(0, 0, W, H)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.drawLine(0, 0, W, 0)

        speed = getattr(vs, "speed",           0.0)
        li    = getattr(vs, "left_indicator",  False)
        ri    = getattr(vs, "right_indicator", False)
        hb    = getattr(vs, "high_beam",       False)
        ss    = getattr(vs, "_side_stand",     False) and speed < 1
        brake = getattr(vs, "brake",           0.0) > 0.5
        bt    = getattr(vs, "bluetooth",       False)
        mode  = getattr(vs, "ride_mode_label", "ECO")

        icons = [
            ("ABS",        False, C["accent"],  False),
            ("◀",          li,    C["eco"],      True),
            ("HIGH BEAM",  hb,    C["accent"],   False),
            ("▶",          ri,    C["eco"],      True),
            ("SIDE STAND", ss,    C["yellow"],   True),
            ("BRAKE",      brake, C["red"],      False),
            ("BT",         bt,    C["accent"],   False),
        ]
        font_b = QFont("Segoe UI", 7, QFont.Bold)
        n      = len(icons)
        slot_w = (W - 80) / n
        for i, (lbl, active, col, do_blink) in enumerate(icons):
            cx  = slot_w * i + slot_w / 2
            vis = active and ((not do_blink) or self._blink)
            p.setFont(font_b)
            p.setPen(QColor(col if vis else C["text_lo"]))
            fm  = QFontMetrics(font_b)
            p.drawText(int(cx - fm.horizontalAdvance(lbl) / 2), 20, lbl)

        mc     = _mode_color(mode)
        pw, ph = 50, 16
        px     = W - 66
        py     = (H - ph) // 2
        path   = QPainterPath()
        path.addRoundedRect(QRectF(px, py, pw, ph), 8, 8)
        p.setPen(QPen(QColor(mc), 1))
        bg     = QColor(mc); bg.setAlpha(40)
        p.setBrush(QBrush(bg))
        p.drawPath(path)
        p.setFont(QFont("Segoe UI", 7, QFont.Bold))
        p.setPen(QColor(mc))
        fm    = QFontMetrics(QFont("Segoe UI", 7, QFont.Bold))
        mw    = fm.horizontalAdvance(mode)
        p.drawText(int(px + (pw - mw) / 2), py + 11, mode)
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  Telemetry bar
# ─────────────────────────────────────────────────────────────────────────────
class _TelemetryBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#060c18")))
        p.drawRect(0, 0, W, H)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.drawLine(0, 0, W, 0)

        rpm  = getattr(vs, "rpm",  1200.0)
        temp = getattr(vs, "temp", 42.0)
        items = [
            ("RPM",     f"{int(rpm)}",                                  C["accent"]),
            ("MOTOR",   f"{int(temp)}°C",                               _temp_color(temp)),
            ("AVG SPD", f"{getattr(vs, 'avg_speed', 0.0):.0f} km/h",   C["text_med"]),
            ("TOP SPD", f"{getattr(vs, 'top_speed',  0.0):.0f} km/h",  C["text_med"]),
        ]
        lf    = QFont("Segoe UI", 7, QFont.Bold)
        vf    = QFont("Consolas", 11, QFont.Bold)
        col_w = W / len(items)
        for i, (lbl, val, col) in enumerate(items):
            cx = col_w * i + col_w / 2
            if i:
                p.setPen(QPen(QColor(C["border"]), 1))
                p.drawLine(QPointF(col_w * i, 6), QPointF(col_w * i, H - 6))
            p.setFont(lf)
            p.setPen(QColor(C["text_lo"]))
            fm = QFontMetrics(lf)
            p.drawText(int(cx - fm.horizontalAdvance(lbl) / 2), 13, lbl)
            p.setFont(vf)
            p.setPen(QColor(col))
            fm2 = QFontMetrics(vf)
            p.drawText(int(cx - fm2.horizontalAdvance(val) / 2), 34, val)
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  CAN strip  (collapsible)
# ─────────────────────────────────────────────────────────────────────────────
class _CANStrip(QWidget):
    MAX_FRAMES = 80

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self._frames: deque = deque(maxlen=self.MAX_FRAMES)
        self._paused = False
        self._synth_ids = ["0x100", "0x101", "0x200", "0x201", "0x300", "0x301"]
        t = QTimer(self)
        t.timeout.connect(self._synth_tick)
        t.start(220)

    def push_frame(self, can_id, dlc, data, ts=""):
        if not self._paused:
            self._frames.appendleft((ts or time.strftime("%H:%M:%S"), can_id, dlc, data))
            self.update()

    def _synth_tick(self):
        if self._paused or len(self._frames) > 12:
            return
        cid  = random.choice(self._synth_ids)
        data = " ".join(f"{random.randint(0, 255):02X}" for _ in range(8))
        self.push_frame(cid, 8, data)

    def mousePressEvent(self, _):
        self._paused = not self._paused
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#03060d")))
        p.drawRect(0, 0, W, H)
        p.setBrush(QBrush(QColor("#070d1c")))
        p.drawRect(0, 0, W, 20)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.drawLine(0, 20, W, 20)
        hf = QFont("Segoe UI", 7, QFont.Bold)
        p.setFont(hf)
        p.setPen(QColor(C["text_lo"]))
        cols = [10, 85, 145, 200]
        for x, h in zip(cols, ["TIMESTAMP", "CAN ID", "DLC", "DATA"]):
            p.drawText(x, 14, h)
        p.setPen(QColor(C["can_green"]))
        p.drawText(W - 112, 14, "● CAN 500kbps")
        rf    = QFont("Consolas", 8)
        row_h = 18
        id_col = {
            "0x100": C["accent"], "0x101": C["accent"],
            "0x200": C["yellow"], "0x201": C["yellow"],
            "0x300": C["red"],    "0x301": C["red"],
        }
        for i, (ts, cid, dlc, data) in enumerate(list(self._frames)[:(H - 22) // row_h]):
            y   = 22 + i * row_h + 13
            col = id_col.get(cid, C["can_green"])
            if i % 2 == 0:
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(QColor("#050a14")))
                p.drawRect(0, y - 13, W, row_h)
            p.setFont(rf)
            p.setPen(QColor(C["text_lo"]));  p.drawText(cols[0], y, ts)
            p.setPen(QColor(col));           p.drawText(cols[1], y, cid)
            p.setPen(QColor(C["text_med"])); p.drawText(cols[2], y, str(dlc))
            p.setPen(QColor(C["text_hi"]));  p.drawText(cols[3], y, data)
        if self._paused:
            p.setPen(QColor(C["yellow"]))
            p.setFont(QFont("Segoe UI", 7, QFont.Bold))
            p.drawText(W - 64, H - 5, "⏸  PAUSED")
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  CAN toggle button
# ─────────────────────────────────────────────────────────────────────────────
class _CANToggle(QPushButton):
    def __init__(self, parent=None):
        super().__init__("  ⬛  CAN MONITOR", parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedHeight(22)
        self.setStyleSheet("""
            QPushButton {
                background: #060a14; color: #2a3a4a;
                border: none; border-top: 1px solid #1a2535;
                font-size: 8px; font-weight: bold;
                letter-spacing: 2px; text-align: center;
            }
            QPushButton:checked { color: #34d399; background: #060e18; }
            QPushButton:hover   { color: #38bdf8; }
        """)


# ─────────────────────────────────────────────────────────────────────────────
#  Header bar
# ─────────────────────────────────────────────────────────────────────────────
class _HeaderBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#060c18")))
        p.drawRect(0, 0, W, H)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.drawLine(0, H - 1, W, H - 1)
        p.setFont(QFont("Segoe UI", 11, QFont.Bold))
        p.setPen(QColor(C["accent"]))
        p.drawText(14, 23, "SUPRAJIT")
        p.setFont(QFont("Segoe UI", 7))
        p.setPen(QColor(C["text_lo"]))
        p.drawText(100, 23, "HYBRID CLUSTER")
        ts = getattr(vs, "time_string", time.strftime("%I:%M %p"))
        tf = QFont("Consolas", 10, QFont.Bold)
        p.setFont(tf)
        p.setPen(QColor(C["text_hi"]))
        fm = QFontMetrics(tf)
        p.drawText(W - fm.horizontalAdvance(ts) - 66, 23, ts)
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.setPen(QColor(C["green"]))
        p.drawText(W - 52, 23, "● LIVE")
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  Main composite widget
# ─────────────────────────────────────────────────────────────────────────────
class HybridCluster(QWidget):
    """
    Layout (top → bottom):
        [Header bar — brand / clock / LIVE badge]
        [Speedometer 60%  |  Info card 40%]
        [Telemetry bar — RPM / TEMP / AVG / TOP]
        [Status icon bar — indicators / mode]
        [CAN toggle button]
        [CAN strip — hidden by default]
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C['bg']}; border:none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header = _HeaderBar()
        root.addWidget(self._header)

        body = QHBoxLayout()
        body.setContentsMargins(10, 8, 10, 8)
        body.setSpacing(12)
        self._speedo = _SpeedometerWidget()
        self._card   = _InfoCard()
        body.addWidget(self._speedo, 60)
        body.addWidget(self._card,   40)
        body_w = QWidget()
        body_w.setLayout(body)
        body_w.setStyleSheet(f"background:{C['bg2']};")
        root.addWidget(body_w, 1)

        self._telem = _TelemetryBar()
        root.addWidget(self._telem)

        self._icons = _StatusIconBar()
        root.addWidget(self._icons)

        self._can_btn   = _CANToggle()
        self._can_strip = _CANStrip()
        self._can_strip.setVisible(False)
        self._can_btn.toggled.connect(self._can_strip.setVisible)
        self._can_btn.toggled.connect(
            lambda on: self._can_btn.setText(
                "  ▼  CAN MONITOR" if on else "  ⬛  CAN MONITOR"))
        root.addWidget(self._can_btn)
        root.addWidget(self._can_strip)

        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(20)

    def set_data(self, speed, fuel, temp, rpm=0, odo=0, trip=0):
        """Called by main_window._physics_tick — vs is already updated."""
        pass   # _SpeedometerWidget._tick() reads vs.speed directly

    def push_can_frame(self, can_id: str, dlc: int, data: str, ts: str = ""):
        self._can_strip.push_frame(can_id, dlc, data, ts)

    def _tick(self):
        self._header.update()
        self._card.update()
        self._telem.update()
        self._icons.update()


# Alias — drop-in replacement for old import
HybridClusterWidget = HybridCluster
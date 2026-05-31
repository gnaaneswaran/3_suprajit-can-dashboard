"""
ui/oem_digital/screens/home_screen.py
─────────────────────────────────────────────────────────────────────────────
Digital cluster home screen renderer.

Fix applied
────────────
  OLD: p.drawText(..., "ATHER")
  NEW: p.drawText(..., "SUPRAJIT")
─────────────────────────────────────────────────────────────────────────────
"""

from PyQt5.QtGui import (
    QColor, QFont, QLinearGradient, QPen,
    QPainterPath, QPolygonF,
)
from PyQt5.QtCore import QRect, QRectF, Qt, QPointF

# ── Colour palette ────────────────────────────────────────────────────────────
_BG        = QColor(6,   10,  20)
_CARD      = QColor(16,  24,  42)
_CARD2     = QColor(20,  30,  52)
_CARD3     = QColor(24,  36,  60)
_GREEN     = QColor(0,   210, 100)
_TEAL      = QColor(0,   180, 200)
_AMBER     = QColor(255, 180,  40)
_RED       = QColor(220,  50,  50)
_WHITE     = QColor(235, 240, 248)
_DIM       = QColor(100, 120, 160)
_DIM2      = QColor(60,   80, 120)
_BORDER    = QColor(255, 255, 255, 16)
_BLUE      = QColor(40,  110, 240)
_DIVIDER   = QColor(255, 255, 255, 12)

MAX_SPEED  = 90.0


def _font(size, bold=False):
    f = QFont("Arial", size)
    if bold:
        f.setBold(True)
    return f


def _card(p, x, y, w, h, r=12, color=None, border_color=None):
    color = color or _CARD
    path  = QPainterPath()
    path.addRoundedRect(QRectF(x, y, w, h), r, r)
    p.fillPath(path, color)
    bc = border_color or _BORDER
    p.setPen(QPen(bc, 1))
    p.drawPath(path)


def _battery_bar(p, x, y, w, h, pct):
    p.setPen(QPen(_DIM2, 1))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(QRect(x, y, w, h), 3, 3)
    nub_h = 5
    p.fillRect(QRect(x + w, y + (h - nub_h) // 2, 3, nub_h), _DIM2)
    fill_w   = int((w - 4) * max(0, min(1, pct / 100)))
    fill_col = _GREEN if pct > 50 else (_AMBER if pct > 20 else _RED)
    if fill_w > 0:
        p.fillRect(QRect(x + 2, y + 2, fill_w, h - 4), fill_col)


def _arrow_shape(p, cx, cy, size, direction, color):
    p.setPen(Qt.NoPen)
    p.setBrush(color)
    if direction == "left":
        pts = [QPointF(cx + size, cy - size),
               QPointF(cx - size, cy),
               QPointF(cx + size, cy + size)]
    elif direction == "right":
        pts = [QPointF(cx - size, cy - size),
               QPointF(cx + size, cy),
               QPointF(cx - size, cy + size)]
    else:
        pts = [QPointF(cx - size, cy + size),
               QPointF(cx,        cy - size),
               QPointF(cx + size, cy + size)]
    p.drawPolygon(QPolygonF(pts))


def _dropdown_geometry(W):
    PANEL_H = 96
    keys    = ["left_indicator", "right_indicator", "high_beam",
               "park_assist_active", "menu"]
    btn_w, btn_h = 110, 64
    panel_y      = 32
    slot_w       = W // len(keys)
    buttons      = {}
    for i, key in enumerate(keys):
        bx           = i * slot_w + (slot_w - btn_w) // 2
        by           = panel_y + (PANEL_H - btn_h) // 2
        buttons[key] = QRect(bx, by, btn_w, btn_h)
    return {
        "panel_x": 0, "panel_y": panel_y,
        "panel_w": W, "panel_h": PANEL_H,
        "buttons": buttons,
    }


class HomeScreen:

    def __init__(self, widgets=None):
        self.widgets         = widgets or {}
        self._dropdown_open  = False
        self._W              = 1024

    # ── Click handling ────────────────────────────────────────────────────────

    def handle_click(self, x, y, state, screen_manager):
        W = self._W
        H = 600

        # Chevron
        chevron = QRect(W // 2 - 24, 33, 48, 18)
        if chevron.contains(x, y):
            self._dropdown_open = not self._dropdown_open
            return True

        if self._dropdown_open:
            geo   = _dropdown_geometry(W)
            panel = QRect(geo["panel_x"], geo["panel_y"],
                          geo["panel_w"], geo["panel_h"])
            if panel.contains(x, y):
                for key, rect in geo["buttons"].items():
                    if rect.contains(x, y):
                        if key == "menu":
                            screen_manager.switch("menu")
                            self._dropdown_open = False
                        elif key == "left_indicator":
                            state.left_indicator  = not state.left_indicator
                            state.right_indicator = False
                        elif key == "right_indicator":
                            state.right_indicator = not state.right_indicator
                            state.left_indicator  = False
                        elif key == "high_beam":
                            state.high_beam = not state.high_beam
                        elif key == "park_assist_active":
                            state.park_assist_active = not state.park_assist_active
                return True
            else:
                self._dropdown_open = False
                return False

        # Bottom toolbar
        bar_y, bar_h, bar_x = H - 88, 58, 20
        bar_w = W - 40
        cx    = bar_x + bar_w // 2
        if QRect(bar_x, bar_y, bar_w, bar_h).contains(x, y):
            if abs(x - (bar_x + 88)) < 32:
                state.left_indicator  = not state.left_indicator
                state.right_indicator = False
                return True
            if abs(x - (bar_x + bar_w - 88)) < 32:
                state.right_indicator = not state.right_indicator
                state.left_indicator  = False
                return True
            if abs(x - cx) < 100:
                state.park_assist_active = not state.park_assist_active
                return True
            if x <= bar_x + 60:
                state.high_beam = not state.high_beam
                return True
            if x >= bar_x + bar_w - 60:
                screen_manager.switch("menu")
                return True

        # Right panel quick cards
        pw = int(W * 0.25)
        rx = W - 20 - pw
        ry = 38
        if QRect(rx + 10, ry + 166, pw - 20, 52).contains(x, y):
            screen_manager.switch("ride_stats")
            return True
        if QRect(rx + 10, ry + 226, pw - 20, 52).contains(x, y):
            screen_manager.switch("navigation")
            return True

        return False

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self, painter, state):
        p  = painter
        p.setRenderHint(p.Antialiasing)
        vp = p.viewport()
        W  = vp.width()  if vp.width()  > 0 else 1024
        H  = vp.height() if vp.height() > 0 else 600
        self._W = W

        grad = QLinearGradient(0, 0, 0, H)
        grad.setColorAt(0.0, QColor(6, 10, 20))
        grad.setColorAt(1.0, QColor(2,  5, 12))
        p.fillRect(QRect(0, 0, W, H), grad)

        self._draw_left_panel(p, state, W, H)
        self._draw_speed(p, state, W, H)
        self._draw_right_panel(p, state, W, H)
        self._draw_bottom_toolbar(p, state, W, H)
        if state.side_stand_down:
            self._draw_side_stand(p, W, H)

        self._draw_status_bar(p, state, W)
        self._draw_chevron(p, W)
        if self._dropdown_open:
            self._draw_dropdown(p, state, W)

    def _draw_status_bar(self, p, state, W):
        p.fillRect(QRect(0, 0, W, 32), QColor(4, 8, 18, 230))

        y = 7
        for i in range(4):
            bh    = 4 + i * 3
            alpha = 200 if i < state.mobile_signal else 35
            p.fillRect(QRect(14 + i * 7, y + (16 - bh), 5, bh),
                       QColor(180, 210, 240, alpha))

        p.setPen(_WHITE)
        p.setFont(_font(11, bold=True))
        p.drawText(QRect(48, y, 110, 18),
                   Qt.AlignLeft | Qt.AlignVCenter,
                   state.time_string)

        if state.bluetooth:
            p.setPen(_TEAL)
            p.setFont(_font(10))
            p.drawText(QRect(162, y, 20, 18), Qt.AlignCenter, "✦")

        # ── Brand name (was "ATHER", now "SUPRAJIT") ──────────────────────────
        p.setPen(_WHITE)
        p.setFont(_font(12, bold=True))
        p.drawText(QRect(0, y, W, 18), Qt.AlignCenter, "SUPRAJIT")
        # ─────────────────────────────────────────────────────────────────────

        motor_col = _GREEN if state.motor_on else QColor(200, 60, 60)
        p.setPen(motor_col)
        p.setFont(_font(9, bold=True))
        p.drawText(QRect(W - 130, y, 120, 18),
                   Qt.AlignRight | Qt.AlignVCenter,
                   "● MOTOR " + ("ON" if state.motor_on else "OFF"))

    def _draw_chevron(self, p, W):
        cx      = W // 2
        bw, bh  = 40, 16
        bx, by  = cx - bw // 2, 33
        path    = QPainterPath()
        path.addRoundedRect(QRectF(bx, by, bw, bh), 6, 6)
        bg = QColor(30, 50, 90, 210) if self._dropdown_open else QColor(18, 26, 50, 190)
        p.fillPath(path, bg)
        p.setPen(QPen(QColor(255, 255, 255, 55), 1))
        p.drawPath(path)
        p.setPen(_TEAL if self._dropdown_open else _DIM)
        p.setFont(_font(9, bold=True))
        p.drawText(QRect(bx, by, bw, bh), Qt.AlignCenter,
                   "∧" if self._dropdown_open else "∨")

    def _draw_dropdown(self, p, state, W):
        geo     = _dropdown_geometry(W)
        px, py  = geo["panel_x"], geo["panel_y"]
        pw, ph  = geo["panel_w"], geo["panel_h"]
        p.fillRect(QRect(px, py, pw, ph), QColor(7, 12, 26, 250))
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        p.drawLine(px, py + ph, px + pw, py + ph)

        icon_map = {
            "left_indicator":     ("◄", "LEFT",      _GREEN),
            "right_indicator":    ("►", "RIGHT",     _GREEN),
            "high_beam":          ("≡D", "HIGH BEAM", _BLUE),
            "park_assist_active": ("P",  "PARK",      _TEAL),
            "menu":               ("≡",  "MENU",      _DIM),
        }
        p.setPen(QPen(QColor(255, 255, 255, 10), 1))
        slot_w = pw // 5
        for i in range(1, 5):
            sx = px + i * slot_w
            p.drawLine(sx, py + 10, sx, py + ph - 10)

        for key, rect in geo["buttons"].items():
            active = bool(getattr(state, key, False)) if key != "menu" else False
            glyph, label, accent = icon_map[key]
            self._dd_tile(p, rect, active, accent, glyph, label)

    def _dd_tile(self, p, rect, active, accent, icon, label):
        if active:
            glow = QColor(accent); glow.setAlpha(22)
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect.adjusted(4, 4, -4, -4)), 8, 8)
            p.fillPath(path, glow)
        p.setPen(QColor(accent) if active else _DIM)
        p.setFont(_font(19, bold=active))
        p.drawText(QRect(rect.x(), rect.y() + 2,
                         rect.width(), rect.height() - 20),
                   Qt.AlignCenter, icon)
        p.setPen(_WHITE if active else _DIM)
        p.setFont(_font(8, bold=True))
        p.drawText(QRect(rect.x(), rect.y() + rect.height() - 16,
                         rect.width(), 14),
                   Qt.AlignCenter, label)
        if active:
            p.setBrush(QColor(accent))
            p.setPen(Qt.NoPen)
            bw = rect.width() - 24
            p.drawRoundedRect(
                QRect(rect.x() + 12, rect.y() + rect.height() - 4, bw, 3), 1, 1)

    def _draw_left_panel(self, p, state, W, H):
        pw   = int(W * 0.25)
        ph   = int(H * 0.54)
        x, y = 20, 38
        _card(p, x, y, pw, ph, r=14, color=_CARD)

        p.setPen(_GREEN)
        p.setFont(_font(9, bold=True))
        p.drawText(QRect(x + 14, y + 14, 120, 16), Qt.AlignLeft, "RANGE")

        p.setPen(_WHITE)
        p.setFont(_font(32, bold=True))
        p.drawText(QRect(x + 12, y + 28, 120, 48), Qt.AlignLeft,
                   f"{int(state.range_km)}")
        p.setPen(_DIM)
        p.setFont(_font(13))
        p.drawText(QRect(x + 76, y + 54, 36, 20), Qt.AlignLeft, "km")

        p.setPen(QPen(_DIVIDER, 1))
        p.drawLine(x + 12, y + 88, x + pw - 12, y + 88)

        p.setPen(_WHITE)
        p.setFont(_font(20, bold=True))
        p.drawText(QRect(x + 12, y + 96, 76, 28), Qt.AlignLeft,
                   f"{int(state.battery)}%")
        _battery_bar(p, x + int(pw * 0.44), y + 100, int(pw * 0.38), 14,
                     state.battery)

        p.setPen(QPen(_DIVIDER, 1))
        p.drawLine(x + 12, y + 138, x + pw - 12, y + 138)

        p.setPen(_GREEN)
        p.setFont(_font(9, bold=True))
        p.drawText(QRect(x + 14, y + 148, 120, 16), Qt.AlignLeft,
                   state.ride_mode_label)
        p.setPen(_WHITE)
        p.setFont(_font(16, bold=True))
        p.drawText(QRect(x + 12, y + 164, pw - 24, 26), Qt.AlignLeft,
                   str(state.ride_mode))

    def _draw_speed(self, p, state, W, H):
        cw  = int(W * 0.44)
        cx  = (W - cw) // 2
        sy  = int(H * 0.09)
        sh  = int(H * 0.40)
        uy  = sy + sh
        uh  = int(H * 0.08)

        spd_pct = state.speed / MAX_SPEED
        spd_col = (_GREEN  if spd_pct < 0.55
                   else (_AMBER if spd_pct < 0.82 else _RED))

        if state.speed > 0.5:
            glow = QColor(spd_col); glow.setAlpha(12)
            gr   = int(cw * 0.40)
            mcx  = cx + cw // 2
            mcy  = sy + sh // 2
            p.setBrush(glow)
            p.setPen(Qt.NoPen)
            p.drawEllipse(mcx - gr, mcy - gr, gr * 2, gr * 2)

        p.setPen(spd_col if state.speed > 0.5 else _WHITE)
        p.setFont(QFont("Arial", 108, QFont.Bold))
        p.drawText(QRect(cx, sy, cw, sh), Qt.AlignCenter, str(int(state.speed)))

        p.setPen(_DIM)
        p.setFont(_font(18))
        p.drawText(QRect(cx, uy, cw, uh), Qt.AlignCenter, "km/h")

        by2 = uy + uh + 2
        bw2 = int(cw * 0.66)
        bx2 = cx + (cw - bw2) // 2
        fw  = int(bw2 * spd_pct)
        p.setBrush(QColor(255, 255, 255, 15))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRect(bx2, by2, bw2, 4), 2, 2)
        if fw > 0:
            p.setBrush(spd_col)
            p.drawRoundedRect(QRect(bx2, by2, fw, 4), 2, 2)

        py2 = by2 + 12
        pw2 = int(cw * 0.27)
        gap = 8
        tot = pw2 * 2 + gap
        px2 = cx + (cw - tot) // 2
        p.setBrush(QColor(255, 255, 255, 10))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRect(px2, py2, pw2, 3), 1, 1)
        if state.speed > 0:
            tf = int(pw2 * min(1.0, state.speed / MAX_SPEED))
            if tf > 0:
                p.setBrush(_GREEN)
                p.drawRoundedRect(QRect(px2, py2, tf, 3), 1, 1)
        p.setBrush(QColor(255, 255, 255, 10))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRect(px2 + pw2 + gap, py2, pw2, 3), 1, 1)

    def _draw_right_panel(self, p, state, W, H):
        pw = int(W * 0.25)
        x  = W - 20 - pw
        y  = 38
        _card(p, x, y, pw, int(H * 0.54), r=14, color=_CARD)

        # TRIP A
        p.setPen(_DIM); p.setFont(_font(9, bold=True))
        p.drawText(QRect(x + 14, y + 14, 160, 16), Qt.AlignLeft, "TRIP A")
        p.setPen(_WHITE); p.setFont(_font(24, bold=True))
        p.drawText(QRect(x + 12, y + 28, 110, 38), Qt.AlignLeft,
                   f"{state.trip_a:.1f}")
        p.setPen(_DIM); p.setFont(_font(12))
        p.drawText(QRect(x + 12 + 86, y + 42, 32, 18), Qt.AlignLeft, "km")

        p.setPen(QPen(_DIVIDER, 1))
        p.drawLine(x + 12, y + 78, x + pw - 12, y + 78)

        # ODO
        p.setPen(_DIM); p.setFont(_font(9, bold=True))
        p.drawText(QRect(x + 14, y + 86, 160, 16), Qt.AlignLeft, "ODO")
        p.setPen(_WHITE); p.setFont(_font(24, bold=True))
        p.drawText(QRect(x + 12, y + 100, 130, 38), Qt.AlignLeft,
                   f"{int(state.odo)}")
        p.setPen(_DIM); p.setFont(_font(12))
        p.drawText(QRect(x + 12 + 92, y + 114, 32, 18), Qt.AlignLeft, "km")

        p.setPen(QPen(_DIVIDER, 1))
        p.drawLine(x + 12, y + 150, x + pw - 12, y + 150)

        # Ride stats card
        _card(p, x + 10, y + 158, pw - 20, 52, r=10, color=_CARD2,
              border_color=QColor(0, 200, 100, 35))
        p.setPen(_GREEN); p.setFont(_font(13))
        p.drawText(QRect(x + 16, y + 165, 24, 24), Qt.AlignCenter, "⚡")
        p.setPen(_WHITE); p.setFont(_font(11, bold=True))
        p.drawText(QRect(x + 44, y + 162, pw - 62, 20),
                   Qt.AlignLeft | Qt.AlignVCenter, "Ride Stats")
        p.setPen(_DIM); p.setFont(_font(9))
        p.drawText(QRect(x + 44, y + 180, pw - 62, 16), Qt.AlignLeft, "Today's ride")

        # Navigation card
        _card(p, x + 10, y + 218, pw - 20, 52, r=10, color=_CARD2,
              border_color=QColor(40, 110, 240, 45))
        p.setPen(_BLUE); p.setFont(_font(14))
        p.drawText(QRect(x + 16, y + 225, 24, 24), Qt.AlignCenter, "◎")
        p.setPen(_WHITE); p.setFont(_font(11, bold=True))
        p.drawText(QRect(x + 44, y + 222, pw - 62, 20),
                   Qt.AlignLeft | Qt.AlignVCenter, "Navigation")
        p.setPen(_DIM); p.setFont(_font(9))
        p.drawText(QRect(x + 44, y + 240, pw - 62, 16), Qt.AlignLeft, "Tap to open map")

    def _draw_bottom_toolbar(self, p, state, W, H):
        by = H - 88
        bh = 58
        bx = 20
        bw = W - 40
        cx = bx + bw // 2
        _card(p, bx, by, bw, bh, r=16, color=QColor(10, 16, 32))

        # High beam
        hb_col = _BLUE if state.high_beam else _DIM2
        p.setPen(QPen(hb_col, 2)); p.setFont(_font(17))
        p.drawText(QRect(bx + 16, by + 13, 42, 28), Qt.AlignCenter, "≡D")

        # Left indicator
        _arrow_shape(p, bx + 86, by + bh // 2, 11, "left",
                     _GREEN if state.left_indicator else _DIM2)

        # Park assist centre button
        pa_active = getattr(state, "park_assist_active", False)
        pa_col    = QColor(0, 140, 65) if pa_active else _BLUE
        path      = QPainterPath()
        path.addRoundedRect(QRectF(cx - 90, by + 9, 180, bh - 18), 10, 10)
        p.fillPath(path, pa_col)
        p.setPen(_WHITE); p.setFont(_font(12, bold=True))
        p.drawText(QRect(cx - 90, by + 9, 180, bh - 18),
                   Qt.AlignCenter,
                   "PARK ASSIST" + (" ●" if pa_active else ""))

        # Right indicator
        _arrow_shape(p, bx + bw - 86, by + bh // 2, 11, "right",
                     _GREEN if state.right_indicator else _DIM2)

        # Menu hamburger
        p.setPen(QPen(_DIM, 2))
        for dy in [-5, 0, 5]:
            yy = by + bh // 2 + dy
            p.drawLine(bx + bw - 50, yy, bx + bw - 26, yy)

    def _draw_side_stand(self, p, W, H):
        ww  = 240
        wx  = (W - ww) // 2
        wy  = H - 26
        path = QPainterPath()
        path.addRoundedRect(QRectF(wx, wy, ww, 20), 6, 6)
        p.fillPath(path, QColor(70, 44, 0, 210))
        p.setPen(_AMBER); p.setFont(_font(9, bold=True))
        p.drawText(QRect(wx, wy, ww, 20), Qt.AlignCenter, "⚠  SIDE STAND DOWN")
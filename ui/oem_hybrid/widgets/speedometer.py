# widgets/speedometer.py

import math

from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QTimer
)

from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QFont,
    QRadialGradient,
    QLinearGradient,
    QPainterPath
)

from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy
)

from ui.oem_hybrid.core.palette import P
from ui.oem_hybrid.widgets.painter_icons import (
    draw_fuel_icon
)


class SpeedometerWidget(QWidget):

    MAX_SPEED = 140.0

    SWEEP_DEG = 270.0

    START_DEG = -135.0

    def __init__(self, state, parent=None):

        super().__init__(parent)

        self.state = state

        self._speed_disp = 0.0

        self.setMinimumSize(260, 260)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self._smooth_timer = QTimer(self)

        self._smooth_timer.setInterval(16)

        self._smooth_timer.timeout.connect(
            self._smooth_tick
        )

        self._smooth_timer.start()

    # =========================================================
    # SMOOTHING
    # =========================================================

    def _smooth_tick(self):

        target = self.state.speed

        diff = target - self._speed_disp

        if abs(diff) > 0.1:

            self._speed_disp += diff * 0.12

            self.update()

    # =========================================================
    # ANGLE
    # =========================================================

    def _speed_to_angle(self, speed):

        return (
            self.START_DEG
            -
            (
                speed / self.MAX_SPEED
            ) * self.SWEEP_DEG
        )

    # =========================================================
    # PAINT
    # =========================================================

    def paintEvent(self, _):

        p = QPainter(self)

        p.setRenderHint(
            QPainter.Antialiasing
        )

        W = self.width()
        H = self.height()

        cx = W / 2
        cy = H / 2

        R = min(W, H) / 2 - 8

        self._draw_bezel(
            p,
            cx,
            cy,
            R
        )

        self._draw_face(
            p,
            cx,
            cy,
            R
        )

        self._draw_arc_zones(
            p,
            cx,
            cy,
            R
        )

        self._draw_ticks_labels(
            p,
            cx,
            cy,
            R
        )

        self._draw_fuel_gauge(
            p,
            cx,
            cy,
            R
        )

        self._draw_needle(
            p,
            cx,
            cy,
            R
        )

        self._draw_hub(
            p,
            cx,
            cy
        )

        self._draw_glare(
            p,
            cx,
            cy,
            R
        )

        p.end()

    # =========================================================
    # BEZEL
    # =========================================================

    def _draw_bezel(self, p, cx, cy, R):

        grad = QRadialGradient(
            cx,
            cy,
            R + 6
        )

        grad.setColorAt(
            0.82,
            QColor("#2d3f52")
        )

        grad.setColorAt(
            0.88,
            QColor("#4a6070")
        )

        grad.setColorAt(
            0.94,
            QColor("#1b2535")
        )

        grad.setColorAt(
            1.00,
            QColor("#0e1825")
        )

        p.setBrush(QBrush(grad))

        p.setPen(Qt.NoPen)

        p.drawEllipse(
            QRectF(
                cx - R - 6,
                cy - R - 6,
                (R + 6) * 2,
                (R + 6) * 2
            )
        )

    # =========================================================
    # FACE
    # =========================================================

    def _draw_face(self, p, cx, cy, R):

        face = QRadialGradient(
            cx,
            cy - R * 0.1,
            R
        )

        face.setColorAt(
            0.0,
            QColor("#0f161f")
        )

        face.setColorAt(
            0.6,
            QColor("#08101a")
        )

        face.setColorAt(
            1.0,
            QColor("#040810")
        )

        p.setBrush(QBrush(face))

        p.setPen(
            QPen(
                QColor("#101c28"),
                1.5
            )
        )

        p.drawEllipse(
            QRectF(
                cx - R,
                cy - R,
                R * 2,
                R * 2
            )
        )

    # =========================================================
    # ARC ZONES
    # =========================================================

    def _draw_arc_zones(self, p, cx, cy, R):

        ar = R - 10

        arect = QRectF(
            cx - ar,
            cy - ar,
            ar * 2,
            ar * 2
        )

        def zone(v0, v1, col, w=15):

            a0 = self._speed_to_angle(v0)

            span = -(
                (v1 - v0)
                /
                self.MAX_SPEED
            ) * self.SWEEP_DEG

            glow = QColor(col)

            glow.setAlpha(60)

            p.setPen(
                QPen(
                    glow,
                    w + 6,
                    Qt.SolidLine,
                    Qt.RoundCap
                )
            )

            p.setBrush(Qt.NoBrush)

            p.drawArc(
                arect,
                int(a0 * 16),
                int(span * 16)
            )

            p.setPen(
                QPen(
                    QColor(col),
                    w,
                    Qt.SolidLine,
                    Qt.RoundCap
                )
            )

            p.drawArc(
                arect,
                int(a0 * 16),
                int(span * 16)
            )

        zone(
            0,
            60,
            P["arc_green"]
        )

        zone(
            60,
            100,
            P["arc_amber"]
        )

        zone(
            100,
            140,
            P["arc_red"]
        )

    # =========================================================
    # TICKS
    # =========================================================

    def _draw_ticks_labels(self, p, cx, cy, R):

        t_out = R - 14
        t_maj = R - 30
        l_r = R - 46

        for val in range(0, 141, 20):

            ang = math.radians(
                self._speed_to_angle(val)
            )

            ca = math.cos(ang)
            sa = -math.sin(ang)

            p.setPen(
                QPen(
                    QColor(P["tick_major"]),
                    2.2
                )
            )

            p.drawLine(
                QPointF(
                    cx + ca * t_maj,
                    cy + sa * t_maj
                ),

                QPointF(
                    cx + ca * t_out,
                    cy + sa * t_out
                )
            )

            f = QFont(
                "Segoe UI",
                max(7, int(R * 0.088)),
                QFont.Bold
            )

            p.setFont(f)

            p.setPen(
                QColor(
                    P["tick_label"]
                )
            )

            p.drawText(
                QRectF(
                    cx + ca * l_r - 17,
                    cy + sa * l_r - 11,
                    34,
                    22
                ),

                Qt.AlignCenter,

                str(val)
            )

    # =========================================================
    # FUEL
    # =========================================================

    def _draw_fuel_gauge(self, p, cx, cy, R):

        fuel = self.state.fuel

        fr = R * 0.25

        fy = cy + R * 0.58

        start = -150
        span = -120

        frect = QRectF(
            cx - fr,
            fy - fr,
            fr * 2,
            fr * 2
        )

        p.setPen(
            QPen(
                QColor("#131e2a"),
                7,
                Qt.SolidLine,
                Qt.RoundCap
            )
        )

        p.drawArc(
            frect,
            int(start * 16),
            int(span * 16)
        )

        filled = (
            fuel / 100.0
        ) * span

        if fuel > 30:
            col = P["arc_green"]

        elif fuel > 15:
            col = P["arc_amber"]

        else:
            col = P["arc_red"]

        p.setPen(
            QPen(
                QColor(col),
                5,
                Qt.SolidLine,
                Qt.RoundCap
            )
        )

        p.drawArc(
            frect,
            int(start * 16),
            int(filled * 16)
        )

        draw_fuel_icon(
            p,
            cx,
            fy - fr * 0.45,
            int(fr * 0.75),
            P["tick_minor"]
        )

    # =========================================================
    # NEEDLE
    # =========================================================

    def _draw_needle(self, p, cx, cy, R):

        ang = math.radians(
            self._speed_to_angle(
                self._speed_disp
            )
        )

        ca = math.cos(ang)
        sa = -math.sin(ang)

        nl = R - 24

        perp_ca = -sa
        perp_sa = ca

        base_w = 5.0
        tip_w = 0.8

        bx = cx - ca * 12
        by = cy - sa * 12

        tx = cx + ca * nl
        ty = cy + sa * nl

        path = QPainterPath()

        path.moveTo(
            bx + perp_ca * base_w,
            by + perp_sa * base_w
        )

        path.lineTo(
            tx + perp_ca * tip_w,
            ty + perp_sa * tip_w
        )

        path.lineTo(
            tx - perp_ca * tip_w,
            ty - perp_sa * tip_w
        )

        path.lineTo(
            bx - perp_ca * base_w,
            by - perp_sa * base_w
        )

        path.closeSubpath()

        p.setPen(Qt.NoPen)

        p.setBrush(
            QColor(0, 0, 0, 80)
        )

        p.save()

        p.translate(2, 2)

        p.drawPath(path)

        p.restore()

        grad = QLinearGradient(
            bx + perp_ca * base_w,
            by + perp_sa * base_w,

            bx - perp_ca * base_w,
            by - perp_sa * base_w
        )

        grad.setColorAt(
            0.0,
            QColor("#ffffff")
        )

        grad.setColorAt(
            0.5,
            QColor("#d8e2ea")
        )

        grad.setColorAt(
            1.0,
            QColor("#90a5b8")
        )

        p.setBrush(QBrush(grad))

        p.drawPath(path)

    # =========================================================
    # HUB
    # =========================================================

    def _draw_hub(self, p, cx, cy):

        p.setPen(Qt.NoPen)

        p.setBrush(
            QColor("#020507")
        )

        p.drawEllipse(
            QRectF(
                cx - 14,
                cy - 14,
                28,
                28
            )
        )

        hub = QRadialGradient(
            cx - 2,
            cy - 2,
            12
        )

        hub.setColorAt(
            0.0,
            QColor("#3d5470")
        )

        hub.setColorAt(
            0.6,
            QColor("#1e2e3f")
        )

        hub.setColorAt(
            1.0,
            QColor("#0d1825")
        )

        p.setBrush(QBrush(hub))

        p.drawEllipse(
            QRectF(
                cx - 11,
                cy - 11,
                22,
                22
            )
        )

    # =========================================================
    # GLARE
    # =========================================================

    def _draw_glare(self, p, cx, cy, R):

        rect = QRectF(
            cx - R * 0.55,
            cy - R * 0.85,
            R * 1.1,
            R * 0.35
        )

        glare = QLinearGradient(
            0,
            cy - R * 0.85,
            0,
            cy - R * 0.5
        )

        glare.setColorAt(
            0.0,
            QColor(255, 255, 255, 18)
        )

        glare.setColorAt(
            1.0,
            QColor(255, 255, 255, 0)
        )

        p.setPen(Qt.NoPen)

        p.setBrush(QBrush(glare))

        p.drawEllipse(rect)
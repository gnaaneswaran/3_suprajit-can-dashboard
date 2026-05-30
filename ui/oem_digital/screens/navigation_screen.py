from PyQt5.QtGui import (
    QColor, QFont, QLinearGradient, QPen, QPainterPath, QPolygonF
)
from PyQt5.QtCore import QRect, QRectF, Qt, QPointF

_BG    = QColor(6,   10,  20)
_CARD  = QColor(16,  24,  42)
_GREEN = QColor(0,   210, 100)
_WHITE = QColor(235, 240, 248)
_DIM   = QColor(100, 120, 160)
_BLUE  = QColor(40,  110, 240)
_TEAL  = QColor(0,   180, 200)
_AMBER = QColor(255, 180,  40)


def _font(size, bold=False):
    f = QFont("Arial", size)
    if bold:
        f.setBold(True)
    return f


def _card(p, x, y, w, h, r=12, color=None):
    color = color or _CARD
    path = QPainterPath()
    path.addRoundedRect(QRectF(x, y, w, h), r, r)
    p.fillPath(path, color)
    p.setPen(QPen(QColor(255, 255, 255, 16), 1))
    p.drawPath(path)


class NavigationScreen:

    def render(self, painter, state):
        p = painter
        p.setRenderHint(p.Antialiasing)
        vp = p.viewport()
        W  = vp.width()  if vp.width()  > 0 else 1024
        H  = vp.height() if vp.height() > 0 else 600

        # ── Status bar ───────────────────────────────────────────────────────
        p.fillRect(QRect(0, 0, W, 32), QColor(4, 8, 18, 230))
        p.setPen(_DIM)
        p.setFont(_font(11))
        p.drawText(QRect(14, 7, 120, 18),
                   Qt.AlignLeft | Qt.AlignVCenter, state.time_string)
        if state.bluetooth:
            p.setPen(_TEAL)
            p.drawText(QRect(140, 7, 20, 18), Qt.AlignCenter, "✦")
        p.setPen(_WHITE)
        p.setFont(_font(13, bold=True))
        p.drawText(QRect(0, 7, W, 18), Qt.AlignCenter, "NAVIGATION")

        # ── Turn instruction card ────────────────────────────────────────────
        card_x = 20
        card_w = W - 40
        _card(p, card_x, 38, card_w, 88, r=12, color=QColor(16, 26, 46))

        # Arrow
        turn = state.next_turn.upper()
        arrow_col = _GREEN
        if "LEFT" in turn:
            pts = [QPointF(card_x + 42, 68), QPointF(card_x + 24, 82),
                   QPointF(card_x + 42, 96)]
        elif "RIGHT" in turn:
            pts = [QPointF(card_x + 24, 68), QPointF(card_x + 42, 82),
                   QPointF(card_x + 24, 96)]
        else:
            pts = [QPointF(card_x + 27, 96), QPointF(card_x + 33, 56),
                   QPointF(card_x + 39, 96)]
        p.setPen(Qt.NoPen)
        p.setBrush(arrow_col)
        p.drawPolygon(QPolygonF(pts))

        p.setPen(_WHITE)
        p.setFont(_font(18, bold=True))
        p.drawText(QRect(card_x + 60, 44, 500, 30),
                   Qt.AlignLeft | Qt.AlignVCenter, state.next_turn)
        p.setPen(_TEAL)
        p.setFont(_font(26, bold=True))
        p.drawText(QRect(card_x + 60, 74, 260, 40),
                   Qt.AlignLeft | Qt.AlignVCenter, state.distance_to_turn)

        # ETA right
        p.setPen(_DIM)
        p.setFont(_font(10))
        p.drawText(QRect(W - 220, 46, 190, 18), Qt.AlignRight, "ETA")
        p.setPen(_WHITE)
        p.setFont(_font(18, bold=True))
        p.drawText(QRect(W - 220, 62, 190, 28), Qt.AlignRight, state.eta_time)
        p.setPen(_DIM)
        p.setFont(_font(10))
        p.drawText(QRect(W - 220, 96, 190, 18), Qt.AlignRight,
                   f"{state.nav_duration}  •  {state.total_nav_distance}")

        # ── Bottom bar ───────────────────────────────────────────────────────
        bot_y = H - 60
        _card(p, 20, bot_y, W - 40, 50, r=12, color=QColor(10, 18, 34))

        p.setPen(_WHITE)
        p.setFont(_font(16))
        p.drawText(QRect(36, bot_y, 40, 50), Qt.AlignCenter, "✕")

        p.setPen(_DIM)
        p.setFont(_font(11))
        p.drawText(QRect(80, bot_y, W - 160, 50),
                   Qt.AlignCenter, "Tap × to exit navigation")

        p.setPen(_DIM)
        p.setFont(_font(16))
        p.drawText(QRect(W - 60, bot_y, 44, 50), Qt.AlignCenter, "←")
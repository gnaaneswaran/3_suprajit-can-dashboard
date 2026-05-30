from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QPainter, QColor, QLinearGradient,
    QPainterPath, QBrush, QPen
)
from PyQt5.QtCore import Qt, QRectF, QTimer


class TFTScreen(QWidget):
    """
    The live TFT display surface.
    screens / state / screen_manager are injected by DigitalCluster.
    No screen imports here — keeps this file decoupled.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Injected by DigitalCluster
        self.state          = None
        self.screen_manager = None
        self.screens        = {}

        # Charging flag
        self.charging       = False

        # Clock timer
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(1000)

    # ── Clock ────────────────────────────────────────────────────────────────
    def _tick(self):
        if self.state:
            from datetime import datetime
            self.state.time_string = datetime.now().strftime("%I:%M %p")
        self.update()

    def sync(self):
        self.update()

    # ── Mouse / touch — navbar + quick-access regions ────────────────────────
    def mousePressEvent(self, event):
        if not self.screen_manager:
            return

        x, y = event.x(), event.y()

        # Hamburger menu (bottom-right of toolbar)
        if 916 <= x <= 996 and 500 <= y <= 564:
            self.screen_manager.switch("menu")
            self.update()
            return

        # Ride Statistics quick-access card (right panel)
        if 766 <= x <= 1006 and 236 <= y <= 304:
            self.screen_manager.switch("ride_stats")
            self.update()
            return

        # Back arrow — bottom-left on all sub-screens
        if 20 <= x <= 80 and 540 <= y <= 580:
            self.screen_manager.back()
            self.update()
            return

    # ── Paint ────────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        M = 0
        w, h = self.width(), self.height()

        rect = QRectF(0, 0, w, h)

        grad = QLinearGradient(0, rect.top(), 0, rect.bottom())
        grad.setColorAt(0.0, QColor(10, 16, 28))
        grad.setColorAt(1.0, QColor(2,   5, 12))

        path = QPainterPath()
        path.addRoundedRect(rect, 22, 22)

        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor(255, 255, 255, 20), 1.5))
        p.drawPath(path)

        # Clip to screen area
        p.setClipPath(path)

        # Offset so screen coords (0,0) = top-left of the display area

        if self.screen_manager and self.state:
            current = self.screen_manager.current_screen
            screen  = self.screens.get(current)
            if screen:
                screen.render(p, self.state)

        p.end()
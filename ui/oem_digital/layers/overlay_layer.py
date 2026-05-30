from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QRect, Qt


class OverlayLayer:
    """
    Renders persistent warning banners on top of any screen.
    Add warning strings to self.warnings; they clear automatically
    once the condition is resolved.

    Example warnings: "LOW BATTERY", "HIGH TEMP", "CHECK ENGINE"
    """

    def __init__(self):
        self.warnings = []

    def render(self, painter, state):

        # Auto-populate warnings from state
        active = []

        if state.battery < 15:
            active.append("LOW BATTERY")

        if state.temperature > 80:
            active.append("HIGH TEMP")

        active.extend(self.warnings)     # manual warnings

        if not active:
            return

        # Warning banner at top
        painter.fillRect(
            QRect(300, 10, 424, 36),
            QColor(180, 40, 40, 200)
        )

        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 14, QFont.Bold))

        painter.drawText(
            QRect(300, 10, 424, 36),
            Qt.AlignCenter,
            "  ⚠  " + "   |   ".join(active)
        )

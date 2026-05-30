from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QRect, Qt


class ChargingOverlay:
    """
    Drawn on top of the active screen when tft_screen.charging == True.
    Shows a centered charging indicator with battery percentage.
    """

    def render(self, painter, state):

        # Semi-transparent dark scrim
        painter.fillRect(
            QRect(0, 0, 1024, 600),
            QColor(0, 0, 0, 160)
        )

        # Lightning bolt (text fallback — replace with asset if available)
        painter.setPen(QColor(80, 200, 255))
        painter.setFont(QFont("Arial", 72, QFont.Bold))
        painter.drawText(
            QRect(0, 160, 1024, 120),
            Qt.AlignCenter,
            "⚡"
        )

        # Percentage
        painter.setPen(QColor(240, 240, 240))
        painter.setFont(QFont("Arial", 48, QFont.Bold))
        painter.drawText(
            QRect(0, 300, 1024, 80),
            Qt.AlignCenter,
            f"{int(state.battery)} %"
        )

        # Label
        painter.setPen(QColor(120, 140, 180))
        painter.setFont(QFont("Arial", 20))
        painter.drawText(
            QRect(0, 390, 1024, 40),
            Qt.AlignCenter,
            "CHARGING"
        )

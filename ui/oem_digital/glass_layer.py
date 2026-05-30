from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QLinearGradient,
    QPainterPath
)
from PyQt5.QtCore import QRectF


class GlassLayer(QWidget):

    def paintEvent(self, e):

        p = QPainter(self)

        w = self.width()
        h = self.height()

        glass = QRectF(60, 60, w - 120, h - 120)

        path = QPainterPath()
        path.addRoundedRect(glass, 24, 24)

        top_reflect = QLinearGradient(0, 0, 0, h * 0.35)

        top_reflect.setColorAt(
            0.0,
            QColor(255,255,255,40)
        )

        top_reflect.setColorAt(
            0.2,
            QColor(255,255,255,10)
        )

        top_reflect.setColorAt(
            1.0,
            QColor(255,255,255,0)
        )

        p.fillPath(path, top_reflect)
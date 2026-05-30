from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QLinearGradient,
    QPainterPath
)
from PyQt5.QtCore import Qt, QRectF


class ClusterShell(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.glass = None
        self.setMinimumSize(1200, 650)

    def paintEvent(self, e):
        if self.glass:
            self.glass.resize(self.size())
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        p.fillRect(self.rect(), QColor("#05070A"))

        outer = QRectF(20, 20, w - 40, h - 40)

        shell_grad = QLinearGradient(0, 0, 0, h)

        shell_grad.setColorAt(0.0, QColor("#1A1D22"))
        shell_grad.setColorAt(0.5, QColor("#0D1015"))
        shell_grad.setColorAt(1.0, QColor("#05070A"))

        path = QPainterPath()
        path.addRoundedRect(outer, 40, 40)

        p.fillPath(path, QBrush(shell_grad))

        p.setPen(QPen(QColor(255,255,255,20), 2))
        p.drawPath(path)

        bezel = QRectF(45, 45, w - 90, h - 90)

        bezel_grad = QLinearGradient(0, 0, 0, h)

        bezel_grad.setColorAt(0.0, QColor("#232830"))
        bezel_grad.setColorAt(1.0, QColor("#0C0F14"))

        bezel_path = QPainterPath()
        bezel_path.addRoundedRect(bezel, 28, 28)

        p.fillPath(bezel_path, QBrush(bezel_grad))

        p.setPen(QPen(QColor(255,255,255,12), 1))
        p.drawPath(bezel_path)
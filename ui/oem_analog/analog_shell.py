"""
ui/oem_analog/analog_shell.py
───────────────────────────────
Outer molded housing shell widget.
Reference: Honda Activa — wide oval black plastic housing,
matte textured, with subtle top glare and inner shadow.
Children are laid on top of this backdrop.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import (QPainter, QColor, QPen, QBrush,
                              QLinearGradient, QRadialGradient,
                              QPainterPath)


class AnalogShell(QWidget):
    """
    Paints the outer asymmetric oval cluster housing.
    All cluster widgets sit inside this as children via a layout.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def paintEvent(self, _):
        W, H = self.width(), self.height()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # ── Outer oval housing path ───────────────────────────
        # Reference: wide oval, tapered left/right, chin at bottom
        path = QPainterPath()
        m = 6; rx = W * 0.08; ry = H * 0.14

        path.moveTo(m + rx, m)
        # Top: slight upward bow
        path.cubicTo(W*0.28, m - 8,  W*0.62, m - 6,  W-m-rx, m)
        # Top-right
        path.quadTo(W-m, m, W-m, m + ry)
        # Right side: slight inward taper
        path.cubicTo(W-m-4, H*0.45, W-m-8, H*0.65, W-m-10, H-m-ry)
        # Bottom-right
        path.quadTo(W-m-10, H-m, W-m-10-rx, H-m)
        # Bottom: chin curve
        path.cubicTo(W*0.62, H-m+10, W*0.28, H-m+8, m+rx, H-m)
        # Bottom-left
        path.quadTo(m, H-m, m, H-m-ry)
        # Left side
        path.cubicTo(m+4, H*0.65, m+4, H*0.45, m, m+ry)
        path.quadTo(m, m, m+rx, m)
        path.closeSubpath()

        # Shell fill: matte dark plastic gradient
        sg = QLinearGradient(0, 0, 0, H)
        sg.setColorAt(0.00, QColor("#202830"))
        sg.setColorAt(0.25, QColor("#131b24"))
        sg.setColorAt(0.60, QColor("#0c1218"))
        sg.setColorAt(1.00, QColor("#060a0e"))
        p.setBrush(QBrush(sg)); p.setPen(Qt.NoPen)
        p.drawPath(path)

        # Outer rim — thin metallic border
        p.setPen(QPen(QColor("#283848"), 2.5))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)

        # Inner shadow rim
        p.setPen(QPen(QColor("#101820"), 4))
        p.drawPath(path)

        # Top glare stripe
        glare = QLinearGradient(0, m, 0, m+30)
        glare.setColorAt(0, QColor(255, 255, 255, 22))
        glare.setColorAt(1, QColor(255, 255, 255, 0))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(glare))
        p.drawPath(path)

        # Bottom ambient shadow
        bs = QLinearGradient(0, H-50, 0, H)
        bs.setColorAt(0, QColor(0, 0, 0, 0))
        bs.setColorAt(1, QColor(0, 0, 0, 90))
        p.setBrush(QBrush(bs)); p.drawPath(path)

        p.end()
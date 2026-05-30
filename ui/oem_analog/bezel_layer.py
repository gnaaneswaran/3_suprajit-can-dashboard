"""
ui/oem_analog/bezel_layer.py
──────────────────────────────
Chrome/metallic bezel ring drawn around the speedometer dial.
Reference: Honda Activa — subtle metallic ring, not chrome-flashy,
more of a matte dark ring with a thin highlight.
Drawn into the QPixmap static cache of the main dial.
"""

from PyQt5.QtGui  import QPainter, QColor, QPen, QBrush, QRadialGradient
from PyQt5.QtCore import Qt, QRectF


def draw_bezel_rings(p: QPainter, cx: float, cy: float, R: float):
    """
    Draw concentric metallic bezel rings around the dial.
    Called inside the static QPixmap cache builder.

    Layers (outer → inner):
        1. Wide dark outer ring (housing edge shadow)
        2. Mid metallic ring (highlight)
        3. Inner dark separator
    """
    for width, col in [
        (14, "#1a2230"),   # outer housing shadow
        (8,  "#2a3a4a"),   # mid bezel body
        (4,  "#3a5060"),   # inner highlight rim
        (2,  "#1a2535"),   # separator
    ]:
        p.setPen(QPen(QColor(col), width))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(cx - R - 5, cy - R - 5,
                             (R + 5) * 2, (R + 5) * 2))

    # Subtle top glare on bezel
    glare_grad = QRadialGradient(cx, cy - R - 3, R * 0.3)
    glare_grad.setColorAt(0.0, QColor(255, 255, 255, 18))
    glare_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(glare_grad))
    p.drawEllipse(QRectF(cx - R - 5, cy - R - 5,
                         (R + 5) * 2, (R + 5) * 2))
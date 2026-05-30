# hybrid_shell.py — Suprajit Hybrid Cluster
# ClusterHousing: matte charcoal asymmetric dashboard shell.
# Pure QPainter — no child widgets, just a painted background.
# Designed to be the parent widget of the analog+LCD HBox.

from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath
from PyQt5.QtWidgets import QWidget, QSizePolicy

from ui.oem_hybrid.core.palette import P


class ClusterHousing(QWidget):
    """
    Paints the outer matte-charcoal housing behind the cluster body.
    Asymmetric shape: right edge tapers inward slightly (OEM dashboard feel).
    Add child layout via standard QLayout on this widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        W, H = self.width(), self.height()

        path = self._housing_path(W, H)

        # Outer shell gradient (dark top → darker bottom)
        shell_g = QLinearGradient(0, 0, 0, H)
        shell_g.setColorAt(0.0, QColor("#141922"))
        shell_g.setColorAt(0.5, QColor("#0c1016"))
        shell_g.setColorAt(1.0, QColor("#07090d"))
        p.setBrush(QBrush(shell_g))
        p.setPen(QPen(QColor("#1b2430"), 2))
        p.drawPath(path)

        # Subtle top glare stripe (glass reflection)
        pad = 6
        glare_g = QLinearGradient(0, pad, 0, pad + 18)
        glare_g.setColorAt(0.0, QColor(255, 255, 255, 22))
        glare_g.setColorAt(1.0, QColor(255, 255, 255,  0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(glare_g))
        p.drawPath(path)

        p.end()

    # ── Path ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _housing_path(W: int, H: int) -> QPainterPath:
        """Asymmetric trapezoid with rounded corners."""
        pad, r = 6, 24
        path = QPainterPath()

        path.moveTo(pad + r, pad)
        path.lineTo(W - pad - r, pad)
        path.quadTo(W - pad,     pad,     W - pad,     pad + r)
        # right side tapers in by 10 px toward the bottom
        path.lineTo(W - pad - 10, H - pad - r)
        path.quadTo(W - pad - 10, H - pad, W - pad - 10 - r, H - pad)
        path.lineTo(pad + r, H - pad)
        path.quadTo(pad, H - pad, pad, H - pad - r)
        path.lineTo(pad, pad + r)
        path.quadTo(pad, pad, pad + r, pad)
        path.closeSubpath()

        return path


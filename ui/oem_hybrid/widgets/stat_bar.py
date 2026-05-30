# widgets/stat_bar.py — Suprajit Hybrid Cluster
# Bottom statistics bar: AVG SPEED | TOP SPEED | CO₂ SAVED | TRIP DIST

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel
from ui.oem_hybrid.core.palette import P


class StatBar(QFrame):
    """
    Fixed-height 30-px bar at the very bottom of the cluster.
    Call update_stats(avg, top, co2, dist) every physics tick.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet(
            f"background: {P['shell_inner']};"
            f" border-top: 1px solid {P['bezel_outer']};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(28)

        self._avg  = self._stat("AVG SPEED", "0 km/h")
        self._top  = self._stat("TOP SPEED", "0 km/h")
        self._co2  = self._stat("CO₂ SAVED", "0.0 kg")
        self._dist = self._stat("TRIP DIST", "0.0 km")

        for w in [self._avg, self._top, self._co2, self._dist]:
            lay.addWidget(w)
        lay.addStretch()

    # ── Public ────────────────────────────────────────────────────────────────

    def update_stats(self, avg: float, top: float,
                     co2: float, dist: float):
        self._set(self._avg,  f"{int(avg)} km/h")
        self._set(self._top,  f"{int(top)} km/h")
        self._set(self._co2,  f"{co2:.1f} kg")
        self._set(self._dist, f"{dist:.1f} km")

    # ── Builders ──────────────────────────────────────────────────────────────

    def _stat(self, label: str, value: str) -> QFrame:
        """Return a small QFrame holding a label + value QLabel pair."""
        f  = QFrame()
        f.setStyleSheet("background: transparent; border: none;")
        fl = QHBoxLayout(f)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(4)

        lbl = QLabel(label + ":")
        lbl.setStyleSheet(
            f"color: {P['bezel_inner']}; font-size: 8px;"
            " font-weight: bold; background: transparent;")

        val = QLabel(value)
        val.setStyleSheet(
            f"color: {P['text_muted']}; font-size: 9px;"
            " font-weight: bold; background: transparent;")
        val.setObjectName("val")

        fl.addWidget(lbl)
        fl.addWidget(val)
        return f

    def _set(self, frame: QFrame, text: str):
        frame.findChild(QLabel, "val").setText(text)

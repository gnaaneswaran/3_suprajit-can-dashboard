# widgets/indicator_strip.py — Suprajit Hybrid Cluster
# Top warning icon strip with blinking left/right turn indicators.
# Icons: ◄  BEAM  ENGINE  TEMP  ECO  ABS  ►

from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel

from ui.oem_hybrid.core.palette import P


class IndicatorStrip(QFrame):
    """
    Slim 28-px bar across the top of the cluster.
    Left/right arrow indicators blink at 500 ms when active.
    Warning icons (BEAM, ENGINE, TEMP, ECO, ABS) are toggled via setters.
    """

    _BLINK_MS = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setStyleSheet(
            f"background: {P['shell_inner']};"
            f" border-bottom: 1px solid {P['bezel_outer']};")

        self._left_on  = False
        self._right_on = False
        self._blink    = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(0)

        # Turn indicators
        self._l_arrow = self._arrow("◄")
        self._r_arrow = self._arrow("►")

        # Warning badges
        self._ic_beam   = self._badge("BEAM",   P["bezel_outer"])
        self._ic_engine = self._badge("ENGINE", P["bezel_outer"])
        self._ic_temp   = self._badge("TEMP",   P["bezel_outer"])
        self._ic_eco    = self._badge("ECO",    P["arc_green"])
        self._ic_abs    = self._badge("ABS",    P["arc_green"])

        lay.addWidget(self._l_arrow)
        lay.addSpacing(10)
        for ic in [self._ic_beam, self._ic_engine, self._ic_temp, self._ic_eco]:
            lay.addWidget(ic)
            lay.addSpacing(14)
        lay.addStretch()
        lay.addWidget(self._ic_abs)
        lay.addSpacing(10)
        lay.addWidget(self._r_arrow)

        # Blink timer
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(self._BLINK_MS)
        self._blink_timer.timeout.connect(self._do_blink)
        self._blink_timer.start()

    # ── Public setters ────────────────────────────────────────────────────────

    def set_left_indicator(self, on: bool):
        self._left_on = on

    def set_right_indicator(self, on: bool):
        self._right_on = on

    def set_temp_warn(self, on: bool):
        self._set_badge_color(self._ic_temp,
                               P["arc_amber"] if on else P["bezel_outer"])

    def set_engine_warn(self, on: bool):
        self._set_badge_color(self._ic_engine,
                               P["arc_red"] if on else P["bezel_outer"])

    # ── Internal ──────────────────────────────────────────────────────────────

    def _do_blink(self):
        self._blink = not self._blink

        lc = P["arc_amber"] if (self._left_on  and self._blink) else P["bezel_outer"]
        rc = P["arc_amber"] if (self._right_on and self._blink) else P["bezel_outer"]

        self._l_arrow.setStyleSheet(
            f"color: {lc}; font-size: 15px; font-weight: bold;"
            " background: transparent;")
        self._r_arrow.setStyleSheet(
            f"color: {rc}; font-size: 15px; font-weight: bold;"
            " background: transparent;")

    def _set_badge_color(self, badge: QLabel, color: str):
        badge.setStyleSheet(
            f"color: {color}; font-size: 8px; font-weight: bold;"
            " letter-spacing: 1px; background: transparent;")

    # ── Widget factories ──────────────────────────────────────────────────────

    def _arrow(self, glyph: str) -> QLabel:
        lbl = QLabel(glyph)
        lbl.setStyleSheet(
            f"color: {P['bezel_outer']}; font-size: 15px;"
            " font-weight: bold; background: transparent;")
        return lbl

    def _badge(self, text: str, color: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {color}; font-size: 8px; font-weight: bold;"
            " letter-spacing: 1px; background: transparent;")
        return lbl

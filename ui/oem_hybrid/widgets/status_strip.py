# widgets/status_strip.py — Suprajit Hybrid Cluster
# Bottom LCD strip: TEMP  |  SIDE STAND  |  MODE
# Each cell has a QPainter icon + label row + value row.

from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QPainter, QFont
from PyQt5.QtWidgets import (QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel)

from ui.oem_hybrid.core.palette          import P
from ui.oem_hybrid.widgets.painter_icons import ThermIconWidget, StandIconWidget


class StatusStrip(QWidget):
    """
    Three-cell strip rendered at the bottom of the LCD panel.
    Cells: TEMP  |  SIDE STAND  |  MODE
    Call update(speed, temp) to refresh displayed values.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {P['strip_bg']},
                    stop:1 #8fa6ba
                );
                border: none;
                border-bottom-left-radius:  8px;
                border-bottom-right-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._temp_val,  temp_cell  = self._make_icon_cell("TEMP",       "45°C", P["lcd_text"],  ThermIconWidget)
        self._stand_val, stand_cell = self._make_icon_cell("SIDE STAND", "UP",   P["eco_green"], StandIconWidget)
        self._mode_val,  mode_cell  = self._make_mode_cell()

        lay.addWidget(temp_cell,  1)
        lay.addWidget(self._vline())
        lay.addWidget(stand_cell, 1)
        lay.addWidget(self._vline())
        lay.addWidget(mode_cell,  1)

    # ── Public update ─────────────────────────────────────────────────────────

    def update(self, speed: float, temp: float):
        # Temperature — color-coded
        if temp < 70:
            tc = P["lcd_text"]
        elif temp < 90:
            tc = P["warn_amber"]
        else:
            tc = P["danger_red"]
        self._temp_val.setText(f"{int(temp)}°C")
        self._temp_val.setStyleSheet(
            f"color:{tc}; font-size:12px; font-weight:bold;")

        # Drive mode — derived from speed
        if speed < 40:
            mode, mc = "ECO",   P["eco_green"]
        elif speed < 80:
            mode, mc = "CITY",  "#0a3a7a"
        else:
            mode, mc = "SPORT", P["danger_red"]
        self._mode_val.setText(mode)
        self._mode_val.setStyleSheet(
            f"color:{mc}; border: 2px solid {mc}; border-radius: 3px;"
            f" padding: 1px 6px; font-size: 12px; font-weight: bold;")

    # ── Cell builders ─────────────────────────────────────────────────────────

    def _make_icon_cell(self, label_text, value_text, val_color, IconClass):
        """Cell with a tiny QPainter icon + label on top, value below."""
        cell = QWidget()
        cell.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(cell)
        cl.setContentsMargins(4, 3, 4, 3)
        cl.setSpacing(1)

        # top row: icon + label text
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(3)

        icon = IconClass()
        icon.setFixedSize(14, 14)
        top.addWidget(icon)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(
            f"color: {P['lcd_muted']}; font-size: 8px; font-weight: bold;")
        top.addWidget(lbl)
        top.addStretch()
        cl.addLayout(top)

        # value
        val = QLabel(value_text)
        val.setAlignment(Qt.AlignCenter)
        val.setFont(QFont("Segoe UI", 12, QFont.Bold))
        val.setStyleSheet(f"color: {val_color};")
        cl.addWidget(val)

        return val, cell

    def _make_mode_cell(self):
        """MODE cell — no icon, value has a colored border box."""
        cell = QWidget()
        cell.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(cell)
        cl.setContentsMargins(4, 3, 4, 3)
        cl.setSpacing(1)

        lbl = QLabel("MODE")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"color: {P['lcd_muted']}; font-size: 8px; font-weight: bold;")

        val = QLabel("ECO")
        val.setAlignment(Qt.AlignCenter)
        val.setFont(QFont("Segoe UI", 12, QFont.Bold))
        val.setStyleSheet(
            f"color: {P['eco_green']}; border: 2px solid {P['eco_green']};"
            f" border-radius: 3px; padding: 1px 6px;")

        cl.addWidget(lbl)
        cl.addWidget(val)
        return val, cell

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _vline(self):
        line = QFrame()
        line.setFixedWidth(1)
        line.setStyleSheet(f"background: {P['lcd_border']}; border: none;")
        return line

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QFrame
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from ui.oem_analog.analog_shell   import AnalogShell
from ui.oem_analog.analog_screen  import AnalogScreen

from ui.oem_analog.widgets.fuel_gauge      import FuelGaugeWidget
from ui.oem_analog.widgets.indicator_panel import IndicatorPanel

from ui.oem_analog.widgets.warning_icons import (
    HeadlightIcon,
    EngineIcon,
    GenericWarningIcon
)

# ── FIXED: use centralised vehicle state ─────────────────────────────────────
# (AnalogCluster does not import vs directly — it receives data via set_data()
#  called by main_window._physics_tick.  No duplicate import needed here.
#  If any internal sub-widget previously imported ui.oem_hybrid.core.vehicle_state
#  those must also be updated — see notes at bottom of file.)
# ─────────────────────────────────────────────────────────────────────────────


class AnalogCluster(QWidget):

    def __init__(self, energy_model=None, parent=None):

        super().__init__(parent)

        self.setStyleSheet("""
            background:#07090d;
            color:#d0e0f0;
        """)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # HEADER
        hdr = QFrame()
        hdr.setFixedHeight(40)
        hdr.setStyleSheet("""
            background:#0a0d14;
            border-bottom:1px solid #1a2535;
        """)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14, 0, 14, 0)

        logo = QLabel("SUPRAJIT")
        logo.setStyleSheet("""
            color:#d7e3ef;
            font-size:18px;
            font-weight:bold;
            letter-spacing:3px;
        """)

        sub = QLabel("ANALOG CLUSTER")
        sub.setStyleSheet("""
            color:#314156;
            font-size:8px;
            letter-spacing:2px;
        """)

        live = QLabel("● LIVE")
        live.setStyleSheet("""
            color:#22c55e;
            font-size:9px;
            font-weight:bold;
        """)

        hl.addWidget(logo)
        hl.addSpacing(10)
        hl.addWidget(sub)
        hl.addStretch()
        hl.addWidget(live)
        root.addWidget(hdr)

        # MAIN SHELL
        shell = AnalogShell()
        shell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body = QHBoxLayout(shell)
        body.setContentsMargins(14, 10, 14, 10)
        body.setSpacing(10)

        # LEFT COLUMN
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        left_col.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.left_ind     = IndicatorPanel("left")
        self.headlight_ic = HeadlightIcon()
        self.engine_ic    = EngineIcon()
        left_col.addWidget(self.left_ind)
        left_col.addSpacing(6)
        left_col.addWidget(self.headlight_ic)
        left_col.addWidget(self.engine_ic)
        left_col.addStretch()

        # MAIN DIAL
        self.dial = AnalogScreen()
        self.dial.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # RIGHT COLUMN
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        right_col.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.right_ind = IndicatorPanel("right")
        self.temp_ic   = GenericWarningIcon("TEMP", "#f59e0b")
        self.fuel_ic   = GenericWarningIcon("FUEL", "#ef4444")
        right_col.addWidget(self.right_ind)
        right_col.addSpacing(6)
        right_col.addWidget(self.temp_ic)
        right_col.addWidget(self.fuel_ic)
        right_col.addStretch()

        body.addLayout(left_col, 0)
        body.addWidget(self.dial, 1)
        body.addLayout(right_col, 0)
        root.addWidget(shell, 1)

        # BOTTOM STRIP
        bottom = QFrame()
        bottom.setFixedHeight(110)
        bottom.setStyleSheet("""
            background:#080b10;
            border-top:1px solid #151e28;
        """)
        bl = QHBoxLayout(bottom)
        bl.setContentsMargins(18, 6, 18, 6)
        bl.setSpacing(20)

        self.fuel_gauge = FuelGaugeWidget()
        self.fuel_gauge.setFixedWidth(140)

        stats_panel = QFrame()
        stats_panel.setStyleSheet("background:transparent; border:none;")
        sl = QVBoxLayout(stats_panel)
        sl.setContentsMargins(0, 4, 0, 4)
        sl.setSpacing(6)

        self.trip_lbl  = self.make_stat("TRIP A",   "0.0 km")
        self.range_lbl = self.make_stat("RANGE",    "250 km")
        self.temp_lbl  = self.make_stat("ENG TEMP", "45°C")
        self.rpm_lbl   = self.make_stat("RPM",      "800")

        sl.addWidget(self.trip_lbl)
        sl.addWidget(self.range_lbl)
        sl.addWidget(self.temp_lbl)
        sl.addWidget(self.rpm_lbl)

        bl.addWidget(self.fuel_gauge)
        bl.addWidget(stats_panel, 1)
        root.addWidget(bottom)

    # ─────────────────────────────

    def make_stat(self, label, value):
        frame = QFrame()
        frame.setStyleSheet("background:transparent; border:none;")
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lbl = QLabel(label + ":")
        lbl.setStyleSheet("color:#334155; font-size:9px; font-weight:bold;")

        val = QLabel(value)
        val.setObjectName("value")
        val.setStyleSheet("color:#d7e3ef; font-size:11px; font-weight:bold;")

        lay.addWidget(lbl)
        lay.addWidget(val)
        lay.addStretch()
        return frame

    def set_stat(self, frame, text):
        val = frame.findChild(QLabel, "value")
        val.setText(text)

    # ─────────────────────────────

    def set_data(self, speed, fuel, temp, rpm=0, odo=0, trip=0):
        self.dial.set_speed(speed)
        self.dial.set_odo(odo)
        self.dial.set_trip(trip)
        self.fuel_gauge.set_fuel(fuel)
        self.temp_ic.set_on(temp > 95)
        self.engine_ic.set_on(temp > 108)
        self.fuel_ic.set_on(fuel < 15)
        self.set_stat(self.trip_lbl,  f"{trip:.1f} km")
        self.set_stat(self.range_lbl, f"{int(fuel * 2.8)} km")
        self.set_stat(self.temp_lbl,  f"{int(temp)}°C")
        self.set_stat(self.rpm_lbl,   f"{int(rpm)}")

    def update_cluster(self, speed, fuel):
        self.set_data(speed, fuel, 45, 0, 0, 0)

    def set_left_indicator(self, on):
        self.left_ind.set_active(on)

    def set_right_indicator(self, on):
        self.right_ind.set_active(on)

    def set_headlight(self, on):
        self.headlight_ic.set_on(on)


# ── IMPORTANT: if any file inside ui/oem_analog/ imports vehicle_state, ──────
# replace:
#   from ui.oem_hybrid.core.vehicle_state import vehicle_state as vs
# with:
#   from core.vehicle_state import vehicle_state as vs
# ─────────────────────────────────────────────────────────────────────────────

AnalogClusterWidget = AnalogCluster
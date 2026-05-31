# hybrid_screen.py — Suprajit Hybrid Cluster

from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont
from PyQt5.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout,
                              QLabel, QSizePolicy)
from datetime        import datetime

import ui.oem_hybrid.core.palette
from core.vehicle_state import VehicleState
from core.vehicle_state import vehicle_state 
from ui.oem_hybrid.core.location           import _Loc
from ui.oem_hybrid.hybrid_shell            import ClusterHousing
from ui.oem_hybrid.widgets.speedometer     import SpeedometerWidget
from ui.oem_hybrid.widgets.lcd_panel       import LCDPanel
from ui.oem_hybrid.widgets.indicator_strip import IndicatorStrip
from ui.oem_hybrid.widgets.stat_bar        import StatBar


class HybridCluster(QWidget):

    def __init__(self, energy_model=None, parent=None):
        super().__init__(parent)
        self._energy_model = energy_model

        # ── Vehicle state FIRST — widgets need it ─────────────────────────────
        self.vehicle = VehicleState()

        self.setStyleSheet(
            f"QWidget {{ background: {ui.oem_hybrid.core.palette.P['shell_outer']};"
            f" color: {ui.oem_hybrid.core.palette.P['text_primary']}; font-family: 'Segoe UI'; }}"
            " QLabel { background: transparent; }")

        self._build_ui()
        self._start_timers()
        self._start_physics()
        self.setFocusPolicy(Qt.StrongFocus)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())
        self.ind = IndicatorStrip()
        root.addWidget(self.ind)
        root.addWidget(self._make_body(), 1)
        self.stat_bar = StatBar()
        root.addWidget(self.stat_bar)

    def _make_header(self) -> QFrame:
        hdr = QFrame()
        hdr.setFixedHeight(42)
        hdr.setStyleSheet(
            f"background: {ui.oem_hybrid.core.palette.P['shell_inner']};"
            f" border-bottom: 1px solid {ui.oem_hybrid.core.palette.P['bezel_outer']};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14, 0, 14, 0)

        logo = QLabel("SUPRAJIT")
        logo.setStyleSheet(
            f"color: {ui.oem_hybrid.core.palette.P['text_primary']}; font-size: 18px;"
            " font-weight: bold; letter-spacing: 3px; background: transparent;")

        tag = QLabel("HYBRID CLUSTER")
        tag.setStyleSheet(
            f"color: {ui.oem_hybrid.core.palette.P['text_muted']}; font-size: 8px;"
            " letter-spacing: 3px; background: transparent;")

        self._hdr_time = QLabel("--:--")
        self._hdr_time.setFont(QFont("Courier New", 12, QFont.Bold))
        self._hdr_time.setStyleSheet(
            f"color: {ui.oem_hybrid.core.palette.P['tick_label']}; background: transparent;")

        live = QLabel("● LIVE")
        live.setStyleSheet(
            f"color: {ui.oem_hybrid.core.palette.P['arc_green']}; font-size: 8px;"
            " font-weight: bold; background: transparent;")

        hl.addWidget(logo)
        hl.addSpacing(8)
        hl.addWidget(tag)
        hl.addStretch()
        hl.addWidget(self._hdr_time)
        hl.addSpacing(12)
        hl.addWidget(live)
        return hdr

    def _make_body(self) -> ClusterHousing:
        housing = ClusterHousing()
        hl = QHBoxLayout(housing)
        hl.setContentsMargins(14, 12, 14, 10)
        hl.setSpacing(16)

        # Pass vehicle state to widgets that need it
        self.speedo = SpeedometerWidget(self.vehicle)
        self.lcd    = LCDPanel(self.vehicle)

        hl.addWidget(self.speedo, 62)
        hl.addWidget(self.lcd,    38)
        return housing

    # ── Timers ────────────────────────────────────────────────────────────────

    def _start_timers(self):
        self._clk_timer = QTimer(self)
        self._clk_timer.timeout.connect(self._tick_clock)
        self._clk_timer.start(1000)
        self._tick_clock()

        self._loc_timer = QTimer(self)
        self._loc_timer.timeout.connect(_Loc.fetch)
        self._loc_timer.start(300_000)

    def _tick_clock(self):
        self._hdr_time.setText(datetime.now().strftime("%I:%M %p"))

    # ── Physics ───────────────────────────────────────────────────────────────

    def _start_physics(self):
        self._run_boot_animation()

    def _run_boot_animation(self):
        self._boot_stage = 0

        def _step():
            if self._boot_stage < 140:
                self._speed_disp(self._boot_stage)
                self._boot_stage += 4
            elif self._boot_stage < 280:
                self._speed_disp(280 - self._boot_stage)
                self._boot_stage += 4
            else:
                boot_t.stop()

        boot_t = QTimer(self)
        boot_t.timeout.connect(_step)
        boot_t.start(10)

    def _speed_disp(self, val):
        """Safe speed display — used during boot animation only."""
        self.vehicle.speed = val
        self.speedo.update()

    # ── External data feed ────────────────────────────────────────────────────

    def set_data(self, speed: float, fuel: float, temp: float,
                 rpm: float, odo: float, trip: float):
        """Called by main_window physics tick with live data."""
        self.vehicle.speed    = speed
        self.vehicle.fuel     = fuel
        self.vehicle.temp     = temp
        self.vehicle.engine_temp = temp
        self.vehicle.rpm      = rpm
        self.vehicle.odometer = odo
        self.vehicle.trip     = trip

        # Derived
        self.vehicle.top_speed = max(
            getattr(self.vehicle, "top_speed", 0.0), speed
        )

        self.speedo.update()
        self.lcd.refresh_ui()

        self.stat_bar.update_stats(
            getattr(self.vehicle, "avg_speed", 0.0),
            self.vehicle.top_speed,
            trip * 0.12,
            trip,
        )

        self.ind.set_temp_warn(temp > 90)
        self.ind.set_engine_warn(False)

    def update_cluster(self, speed: float, fuel: float):
        self.set_data(speed, fuel,
                      self.vehicle.temp, self.vehicle.rpm,
                      self.vehicle.odometer, self.vehicle.trip)

    # ── Keyboard ──────────────────────────────────────────────────────────────

    def keyPressEvent(self, e):
        key = e.key()
        if key == Qt.Key_Up:      self.vehicle.throttle = 1.0
        elif key == Qt.Key_Down:  self.vehicle.brake    = 1.0
        elif key == Qt.Key_Left:  self.vehicle.left_indicator  = not self.vehicle.left_indicator
        elif key == Qt.Key_Right: self.vehicle.right_indicator = not self.vehicle.right_indicator
        else:                     super().keyPressEvent(e)

    def keyReleaseEvent(self, e):
        key = e.key()
        if key == Qt.Key_Up:     self.vehicle.throttle = 0.0
        elif key == Qt.Key_Down: self.vehicle.brake    = 0.0
        else:                    super().keyReleaseEvent(e)


HybridClusterWidget = HybridCluster
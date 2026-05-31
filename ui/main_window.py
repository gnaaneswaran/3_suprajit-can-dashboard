"""
ui/main_window.py
─────────────────────────────────────────────────────────────────────────────
Suprajit CAN Bus Analyzer — Main Window

Fixes applied
─────────────────────────────────────────────────────────────────────────────
  ✓ SerialReader imported from hardware.serial_reader  (was ui.oem_analog.core.serial_reader)
  ✓ vehicle_state imported from core.vehicle_state     (was ui.oem_hybrid.core.vehicle_state)
  ✓ Duplicate import block removed (was imported twice)
  ✓ physics_engine.tick() called here — NOT inside DigitalClusterWidget
  ✓ All three clusters read the same vs singleton — hardware data visible everywhere
─────────────────────────────────────────────────────────────────────────────
"""

import time

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit,
    QHeaderView, QStackedWidget,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui  import QColor

from core.fake_data        import fake_data_generator
from core.decoder          import decode_frame
from core.can_frame        import CANFrame
from core.event_dispatcher import dispatcher
from core.logger           import can_logger
from core               import physics_engine           # physics tick lives here

# ── Single correct imports — no duplicates ────────────────────────────────────
from hardware.serial_reader import SerialReader          # fixed path
from core.vehicle_state     import vehicle_state as vs   # fixed path
# ─────────────────────────────────────────────────────────────────────────────

from ui.controls_panel                       import ControlsPanel
from ui.digital_cluster                      import DigitalClusterWidget
from ui.analog_cluster                       import AnalogClusterWidget
from ui.hybrid_cluster                       import HybridClusterWidget
from ui.oem_digital.widgets.osm_map_widget   import OSMMapWidget


STYLE = """
QMainWindow, QWidget {
    background-color: #08101e;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
}
#headerBar {
    background-color: #060c18;
    border-bottom: 1px solid #1e293b;
}
#brandLabel {
    color: #38bdf8;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 3px;
    padding-left: 16px;
}
#appLabel {
    color: #334155;
    font-size: 10px;
    letter-spacing: 2px;
    padding-left: 4px;
}
#viewBtn {
    background-color: #0f172a;
    color: #475569;
    padding: 5px 14px;
    border-radius: 5px;
    border: 1px solid #1e293b;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
}
#viewBtn:checked {
    background-color: #0ea5e9;
    color: white;
    border: 1px solid #0ea5e9;
}
#clusterBar   { background: transparent; border-bottom: 1px solid #0f172a; }
#clusterTag   { color: #1e3a5f; font-size: 9px; font-weight: bold; letter-spacing: 2px; }
#liveTag      { color: #22c55e; font-size: 9px; font-weight: bold; letter-spacing: 1px; }
QTableWidget  {
    background-color: #0a0f1e; gridline-color: #1e293b;
    border: none; font-size: 11px;
    selection-background-color: #1e3a5f;
}
QTableWidget::item   { padding: 3px 8px; border-bottom: 1px solid #0f172a; }
QHeaderView::section {
    background-color: #0f172a; color: #475569; font-size: 9px;
    font-weight: bold; padding: 5px 8px;
    border: none; border-right: 1px solid #1e293b;
}
#statusBar    { background-color: #060c18; border-top: 1px solid #1e293b; }
#statusLabel  { color: #334155; font-size: 9px; }
#statusValue  { color: #38bdf8; font-size: 10px; font-weight: bold; }
#ctrlPanel    { background-color: #060a14; border-left: 1px solid #1e293b; }
"""

ROW_COLORS = {
    "0x100": ("#0e2a3a", "#38bdf8"),
    "0x200": ("#2a1f0a", "#f59e0b"),
    "0x300": ("#2a0f0f", "#f87171"),
}

# Physics tick interval in milliseconds
_PHYSICS_INTERVAL_MS = 30


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # ── Hardware ──────────────────────────────────────────────────────────
        self.serial_reader = SerialReader()   # auto-detects COM port

        self.setWindowTitle("Suprajit CAN Bus Analyzer")
        self.setMinimumSize(1280, 760)
        self.setStyleSheet(STYLE)

        self.data_gen    = fake_data_generator()
        self._running    = False
        self._filter_id  = ""
        self._row_limit  = 200
        self._last_tick_s = time.perf_counter()

        # Physics timer — ONE loop for the entire app
        self._physics_timer = QTimer()
        self._physics_timer.setInterval(_PHYSICS_INTERVAL_MS)
        self._physics_timer.timeout.connect(self._physics_tick)

        # Navigation map overlay
        self.map_widget = OSMMapWidget(self)
        self.map_widget.setGeometry(36, 240, 1525, 525)
        self.map_widget.hide()
        self.map_widget.raise_()

        self._build_ui()
        self._start()

    # ─────────────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_lay = QVBoxLayout(root)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)
        root_lay.addWidget(self._make_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._make_centre_area(), 1)
        body.addWidget(self._make_controls_panel())
        body_w = QWidget()
        body_w.setLayout(body)
        root_lay.addWidget(body_w, 1)
        root_lay.addWidget(self._make_bottom_bar())

    def _make_header(self):
        bar = QWidget()
        bar.setObjectName("headerBar")
        bar.setFixedHeight(44)
        lay = QHBoxLayout(bar)
        brand = QLabel("SUPRAJIT"); brand.setObjectName("brandLabel")
        app   = QLabel("CAN BUS ANALYZER"); app.setObjectName("appLabel")
        lay.addWidget(brand); lay.addWidget(app); lay.addStretch()
        self.btn_table   = QPushButton("▦ TABLE VIEW")
        self.btn_cluster = QPushButton("⊙ CLUSTER VIEW")
        for btn in [self.btn_table, self.btn_cluster]:
            btn.setObjectName("viewBtn")
            btn.setCheckable(True)
        self.btn_cluster.setChecked(True)
        self.btn_table.clicked.connect(lambda: self._switch_view(0))
        self.btn_cluster.clicked.connect(lambda: self._switch_view(1))
        lay.addWidget(self.btn_table); lay.addWidget(self.btn_cluster)
        return bar

    def _make_centre_area(self):
        w   = QWidget()
        lay = QVBoxLayout(w)
        sub = QWidget(); sub.setObjectName("clusterBar"); sub.setFixedHeight(26)
        sl  = QHBoxLayout(sub)
        t1  = QLabel("INSTRUMENT CLUSTER"); t1.setObjectName("clusterTag")
        t2  = QLabel("● LIVE DATA");        t2.setObjectName("liveTag")
        sl.addWidget(t1); sl.addStretch(); sl.addWidget(t2)
        lay.addWidget(sub)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._make_table_page())
        self.stack.addWidget(self._make_cluster_page())
        self.stack.setCurrentIndex(1)
        lay.addWidget(self.stack, 1)
        return w

    def _make_table_page(self):
        w   = QWidget()
        lay = QVBoxLayout(w)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["TIMESTAMP", "CAN ID", "DLC", "DATA"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        lay.addWidget(self.table)
        filter_bar = QWidget()
        fl = QHBoxLayout(filter_bar)
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter by CAN ID")
        self.filter_edit.textChanged.connect(
            lambda t: setattr(self, "_filter_id", t.strip()))
        fl.addWidget(self.filter_edit)
        lay.addWidget(filter_bar)
        return w

    def _make_cluster_page(self):
        w    = QWidget()
        lay  = QVBoxLayout(w)
        tabs = QTabWidget()
        self.digital_cluster = DigitalClusterWidget()
        self.analog_cluster  = AnalogClusterWidget()
        self.hybrid_cluster  = HybridClusterWidget()
        tabs.addTab(self.digital_cluster, "⬡ DIGITAL")
        tabs.addTab(self.analog_cluster,  "◎ ANALOG")
        tabs.addTab(self.hybrid_cluster,  "⊕ HYBRID")
        lay.addWidget(tabs)
        return w

    def _make_controls_panel(self):
        w = QWidget(); w.setObjectName("ctrlPanel"); w.setFixedWidth(116)
        lay = QVBoxLayout(w)
        self.ctrl_panel = ControlsPanel()
        lay.addWidget(self.ctrl_panel)
        self.ctrl_panel.throttle_btn.stateChanged.connect(
            lambda v: setattr(vs, "throttle", float(v)))
        self.ctrl_panel.brake_btn.stateChanged.connect(
            lambda v: setattr(vs, "brake", float(v)))
        return w

    def _make_bottom_bar(self):
        bar = QWidget(); bar.setObjectName("statusBar"); bar.setFixedHeight(38)
        lay = QHBoxLayout(bar)
        for key in ["SPEED", "FUEL", "TEMP", "BUS"]:
            col = QVBoxLayout()
            lbl = QLabel(key);  lbl.setObjectName("statusLabel")
            val = QLabel("--"); val.setObjectName("statusValue")
            col.addWidget(lbl); col.addWidget(val)
            setattr(self, f"_status_{key.lower()}", val)
            cw = QWidget(); cw.setLayout(col)
            lay.addWidget(cw)
        return bar

    # ─────────────────────────────────────────────────────────────────────────
    # View switching
    # ─────────────────────────────────────────────────────────────────────────

    def _switch_view(self, idx: int) -> None:
        self.stack.setCurrentIndex(idx)
        self.btn_table.setChecked(idx == 0)
        self.btn_cluster.setChecked(idx == 1)

    # ─────────────────────────────────────────────────────────────────────────
    # Navigation map
    # ─────────────────────────────────────────────────────────────────────────

    def _update_navigation_map(self) -> None:
        try:
            current = self.digital_cluster._sm.current_screen
        except Exception:
            current = "home"
        if current == "navigation":
            self.map_widget.show(); self.map_widget.raise_()
        else:
            self.map_widget.hide()

    # ─────────────────────────────────────────────────────────────────────────
    # Start / stop
    # ─────────────────────────────────────────────────────────────────────────

    def _start(self) -> None:
        if self._running:
            return
        self._running = True
        can_logger.start()
        self._physics_timer.start()
        self.can_timer = QTimer()
        self.can_timer.timeout.connect(self._can_tick)
        self.can_timer.start(80)
        self._status_bus.setText("ON")

    def _stop(self) -> None:
        if hasattr(self, "can_timer"):
            self.can_timer.stop()
        self._physics_timer.stop()
        self._running = False
        self._status_bus.setText("OFF")

    # ─────────────────────────────────────────────────────────────────────────
    # Physics tick — THE ONLY PLACE physics_engine.tick() is called
    # ─────────────────────────────────────────────────────────────────────────

    def _physics_tick(self) -> None:
        now  = time.perf_counter()
        dt   = now - self._last_tick_s
        self._last_tick_s = now
        dt   = min(dt, 0.1)   # cap at 100 ms to avoid jumps

        sr  = self.serial_reader
        adc = sr.value

        if adc < 150:
            adc = 0
        adc = max(0, min(4095, adc))

        # ── Hardware-driven speed target ──────────────────────────────────────
        # Potentiometer ADC → 0-85 km/h target.
        # physics_engine.tick() will then ramp vs.speed toward this.
        vs.throttle = (adc / 4095.0) * 100.0   # 0-100 %

        # Brake from controls panel (already set by stateChanged signal)
        if vs.brake:
            vs.speed *= (1.0 - 0.15 * (dt / 0.030))

        # ── Physics step — odometry, battery, range, efficiency ───────────────
        # This is the single call to physics_engine.tick() for the whole app.
        physics_engine.tick(dt)

        # ── Derived thermal / electrical values ───────────────────────────────
        vs.temp        = 42.0 + vs.speed * 0.75
        vs.rpm         = 1200.0 + vs.speed * 75.0
        vs.engine_temp = vs.temp
        vs.lean        = 0.0

        # Voltage / current (live telemetry bar in hybrid cluster)
        vs.voltage = 48.0 + (vs.speed / 90.0) * 4.0     # 48-52 V
        vs.current = (vs.speed / 90.0) * 25.0            # 0-25 A

        # Fuel mirrors battery (analog cluster shows fuel gauge)
        vs.fuel    = vs.battery
        vs.odo     = vs.odometer                          # keep alias in sync

        if sr.connected:
            print(f"[HW] ADC={adc:4d}  THROTTLE={vs.throttle:.1f}%  SPEED={vs.speed:.1f}")

        # ── Update controls panel LED indicators ──────────────────────────────
        self.ctrl_panel.update_indicators(bool(vs.throttle), bool(vs.brake))

        # ── Repaint all three clusters ────────────────────────────────────────
        # Digital: pure renderer — just call update()
        self.digital_cluster.update()

        # Analog: uses push model via set_data()
        self.analog_cluster.set_data(
            vs.speed, vs.fuel, vs.temp, vs.rpm, vs.odometer, vs.trip)

        # Hybrid: uses push model via set_data() (writes into vs singleton)
        self.hybrid_cluster.set_data(
            vs.speed, vs.fuel, vs.temp, vs.rpm, vs.odometer, vs.trip)

        # ── Bottom status bar ─────────────────────────────────────────────────
        self._status_speed.setText(f"{int(vs.speed)} km/h")
        self._status_fuel.setText(f"{int(vs.fuel)}%")
        self._status_temp.setText(f"{int(vs.temp)}°C")

        self._update_navigation_map()

    # ─────────────────────────────────────────────────────────────────────────
    # CAN tick — feeds table view and hybrid cluster CAN strip
    # ─────────────────────────────────────────────────────────────────────────

    def _can_tick(self) -> None:
        line = next(self.data_gen)
        try:
            frame = CANFrame.from_string(line)
        except ValueError:
            return

        signals = decode_frame(frame)
        dispatcher.publish_all(signals)
        can_logger.log(frame, signals)

        parts = line.split(",")
        if len(parts) == 4:
            ts, can_id, dlc, data = parts
            try:
                self.hybrid_cluster.push_can_frame(can_id, int(dlc), data, ts)
            except Exception:
                pass

        if self.stack.currentIndex() == 0:
            if len(parts) != 4:
                return
            ts, can_id, dlc, data = parts
            if self._filter_id == "" or self._filter_id.lower() in can_id.lower():
                bg_col, fg_col = ROW_COLORS.get(can_id, ("#0a0f1e", "#e2e8f0"))
                row = self.table.rowCount()
                if row >= self._row_limit:
                    self.table.removeRow(0)
                    row = self.table.rowCount()
                self.table.insertRow(row)
                for col_i, text in enumerate([ts, can_id, dlc, data]):
                    item = QTableWidgetItem(text)
                    item.setForeground(QColor(fg_col))
                    item.setBackground(QColor(bg_col))
                    self.table.setItem(row, col_i, item)
                self.table.scrollToBottom()

    # ─────────────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        can_logger.stop()
        if hasattr(self, "serial_reader"):
            self.serial_reader.stop()
        super().closeEvent(event)
import sys
import os
from datetime import datetime

# ── Fix import paths: add the project root to sys.path ───────────────────────
# main.py lives in:  .../1.Suprajit/files/
# screens/, services/, ui/ are siblings of main.py → same folder IS the root
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer

from ui.main_window import MainWindow
from screens.home_screen import HomeScreen
from screens.menu_screen import MenuScreen
from screens.navigation_screen import NavigationScreen
from screens.settings_screen import SettingsScreen
from screens.vehicle_screen import VehicleScreen
from screens.ride_stats_screen import RideStatsScreen
from screens.bluetooth_screen import BluetoothScreen
from services.screen_manager import ScreenManager

# ─────────────────────────────────────────────────────────────────────────────
# Physics / simulation constants
# ─────────────────────────────────────────────────────────────────────────────
TICK_MS            = 50            # timer interval ms  → 20 Hz physics
TICK_S             = TICK_MS / 1000.0

MAX_SPEED          = 90.0          # km/h
ACCEL_RATE         = 6.9           # km/h per second while throttle held
BRAKE_RATE         = 12.0          # km/h per second while brake held
COAST_RATE         = 1.4           # km/h per second natural decel

BATTERY_DRAIN_PER_KM = 100.0 / 85.0   # % per km

# ─────────────────────────────────────────────────────────────────────────────
# Live vehicle state
# ─────────────────────────────────────────────────────────────────────────────
class VehicleState:
    def __init__(self):
        self.speed             = 0.0
        self.battery           = 78.0
        self.range_km          = 85.0
        self.odo               = 1254.0
        self.trip_a            = 32.4
        self.ride_mode         = "SMART ECO"
        self.ride_mode_label   = "ECO"
        self.time_string       = ""
        self.mobile_signal     = 3
        self.bluetooth         = True
        self.motor_on          = True
        self.side_stand_down   = True
        self.left_indicator    = False
        self.right_indicator   = False
        self.high_beam         = False
        self._update_time()
        self._update_range()

    def _update_time(self):
        self.time_string = datetime.now().strftime("%I:%M %p").lstrip("0")

    def _update_range(self):
        self.range_km = max(0.0, round(self.battery * (85.0 / 78.0), 1))


# ─────────────────────────────────────────────────────────────────────────────
# Key state
# ─────────────────────────────────────────────────────────────────────────────
pressed  = {"up": False, "down": False}
throttle = {"value": 0}
brake    = {"value": 0}


# ─────────────────────────────────────────────────────────────────────────────
# Physics tick
# ─────────────────────────────────────────────────────────────────────────────
def _physics_tick(state):
    prev_speed = state.speed

    if pressed["up"]:
        state.speed = min(MAX_SPEED, state.speed + ACCEL_RATE * TICK_S)
    elif pressed["down"]:
        state.speed = max(0.0, state.speed - BRAKE_RATE * TICK_S)
    else:
        state.speed = max(0.0, state.speed - COAST_RATE * TICK_S)

    avg_kmh  = (prev_speed + state.speed) / 2.0
    dist_km  = avg_kmh * TICK_S / 3600.0

    state.odo    += dist_km
    state.trip_a += dist_km
    state.battery = max(0.0, state.battery - dist_km * BATTERY_DRAIN_PER_KM)
    state._update_range()

    if state.speed > 2.0:
        state.side_stand_down = False

    state._update_time()


# ─────────────────────────────────────────────────────────────────────────────
# Keyboard wiring
# ─────────────────────────────────────────────────────────────────────────────
def _wire_keys(win):
    def keyPressEvent(e):
        k = e.key()
        if k == Qt.Key_Up:
            pressed["up"] = True
            throttle["value"] = 100
        elif k == Qt.Key_Down:
            pressed["down"] = True
            brake["value"] = 100
        else:
            type(win).keyPressEvent(win, e)

    def keyReleaseEvent(e):
        k = e.key()
        if k == Qt.Key_Up:
            pressed["up"] = False
            throttle["value"] = 0
        elif k == Qt.Key_Down:
            pressed["down"] = False
            brake["value"] = 0
        else:
            type(win).keyReleaseEvent(win, e)

    win.keyPressEvent   = keyPressEvent
    win.keyReleaseEvent = keyReleaseEvent


# ─────────────────────────────────────────────────────────────────────────────
# main()
# ─────────────────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = MainWindow()
    win.setFocusPolicy(Qt.StrongFocus)

    state = VehicleState()
    _wire_keys(win)

    # ── Push state into window / screen manager ───────────────────────────────
    if hasattr(win, "state"):
        win.state = state
    if hasattr(win, "screen_manager"):
        sm = win.screen_manager
        if hasattr(sm, "state"):
            sm.state = state
        if hasattr(sm, "screens"):
            for scr in sm.screens.values():
                if hasattr(scr, "state"):
                    scr.state = state

    # ── Physics + repaint timer ───────────────────────────────────────────────
    def tick():
        _physics_tick(state)
        if hasattr(win, "update_state"):
            win.update_state(state)
        elif hasattr(win, "set_state"):
            win.set_state(state)
        win.update()

    timer = QTimer()
    timer.setInterval(TICK_MS)
    timer.timeout.connect(tick)
    timer.start()

    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
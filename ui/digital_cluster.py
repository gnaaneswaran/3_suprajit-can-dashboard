"""
ui/digital_cluster.py
─────────────────────────────────────────────────────────────────────────────
Digital instrument cluster widget.

Changes from previous version
──────────────────────────────
  • Physics-based ODO/trip:  distance_km = speed × dt / 3600  (every tick)
  • Range always visible:    battery_pct × 3.0 km  (100% = 300 km)
  • Battery drains per km based on ride mode + throttle load
  • Speed arc shows 0–130 km/h; motor is electronically limited to 90 km/h
  • 25/50/25 layout — no dead space, no fake ride-stats/nav cards

Update loop
──────────────────────────────
  Connect a QTimer(interval=16) → cluster_widget.update_tick()
  The timer calls physics_engine.tick(dt) then schedules a repaint.

Hardware path
──────────────────────────────
  ESP32 → CAN decoder → vehicle_state  →  this widget repaints
  No UI code changes required when real hardware arrives.
"""

import time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter
from PyQt5.QtCore    import Qt, QTimer

from core.vehicle_state import vehicle_state as vs
from core               import physics_engine          # <── NEW physics module

from ui.oem_digital.screens.home_screen       import HomeScreen
from ui.oem_digital.screens.menu_screen       import MenuScreen
from ui.oem_digital.screens.ride_stats_screen import RideStatsScreen
from ui.oem_digital.screens.navigation_screen import NavigationScreen
from ui.oem_digital.screens.vehicle_screen    import VehicleScreen
from ui.oem_digital.screens.settings_screen   import SettingsScreen
from ui.oem_digital.screens.bluetooth_screen  import BluetoothScreen


# ── Model adapter ─────────────────────────────────────────────────────────────
# Thin proxy that reads from vehicle_state singleton.
# Add new properties here as CAN signals are decoded — zero UI changes needed.

class _ModelAdapter:
    """Read-only view of vehicle_state for all screen renderers."""

    # Core display
    @property
    def speed(self):               return vs.speed
    @property
    def battery(self):             return vs.battery
    @property
    def range_km(self):
        # Always computed dynamically; never zero while battery exists
        return vs.range_km          # set by physics_engine.tick()
    @property
    def odo(self):                 return vs.odometer
    @property
    def trip_a(self):              return vs.trip
    @property
    def ride_mode(self):           return vs.ride_mode
    @property
    def ride_mode_label(self):     return vs.ride_mode_label
    @property
    def time_string(self):         return vs.time_string
    @property
    def mobile_signal(self):       return vs.mobile_signal
    @property
    def bluetooth(self):           return vs.bluetooth
    @property
    def motor_on(self):            return bool(vs.throttle) or vs.speed > 0
    @property
    def side_stand_down(self):     return vs.speed < 1.0 and vs._side_stand
    @property
    def motor_power_kw(self):      return getattr(vs, 'motor_power_kw', 0.0)
    @property
    def regen(self):               return getattr(vs, 'regen', 0)

    # Indicators (read/write)
    @property
    def left_indicator(self):       return vs.left_indicator
    @left_indicator.setter
    def left_indicator(self, v):    vs.left_indicator = v
    @property
    def right_indicator(self):      return vs.right_indicator
    @right_indicator.setter
    def right_indicator(self, v):   vs.right_indicator = v
    @property
    def high_beam(self):            return vs.high_beam
    @high_beam.setter
    def high_beam(self, v):         vs.high_beam = v
    @property
    def park_assist_active(self):   return vs.park_assist_active
    @park_assist_active.setter
    def park_assist_active(self, v):vs.park_assist_active = v

    # Ride stats
    @property
    def stat_distance(self):        return vs.trip
    @property
    def stat_avg_speed(self):       return vs.avg_speed
    @property
    def stat_avg_efficiency(self):  return vs.stat_avg_efficiency
    @property
    def stat_top_speed(self):       return vs.top_speed

    # Navigation (populated by nav module when active)
    @property
    def next_turn(self):            return vs.next_turn
    @property
    def distance_to_turn(self):     return vs.distance_to_turn
    @property
    def eta_time(self):             return vs.eta_time
    @property
    def total_nav_distance(self):   return vs.total_nav_distance
    @property
    def nav_duration(self):         return vs.nav_duration

    # Settings
    @property
    def brightness(self):           return vs.brightness
    @property
    def wifi(self):                 return vs.wifi


_adapter = _ModelAdapter()


# ── Screen manager ────────────────────────────────────────────────────────────

class _ScreenManager:
    def __init__(self):
        self.current_screen = "home"
        self._history: list[str] = []

    def switch(self, screen: str) -> None:
        self._history.append(self.current_screen)
        self.current_screen = screen

    def back(self) -> None:
        if self._history:
            self.current_screen = self._history.pop()


# ── Main widget ───────────────────────────────────────────────────────────────

class DigitalClusterWidget(QWidget):
    """
    Main instrument cluster widget.

    Connect a 60 Hz QTimer to update_tick() for live physics simulation.
    When real hardware feeds vehicle_state directly, update_tick() still
    handles odometry accumulation and repaint scheduling correctly.
    """

    # Gauge arc constants (must match HomeScreen renderer)
    GAUGE_MAX_KMH    = 130   # arc full-scale speed
    MOTOR_MAX_KMH    =  90   # electronic speed limiter

    def __init__(self, parent=None):
        super().__init__(parent)

        self._sm = _ScreenManager()
        self._home = HomeScreen()
        self._screens: dict[str, object] = {
            "home":       self._home,
            "menu":       MenuScreen(),
            "ride_stats": RideStatsScreen(),
            "navigation": NavigationScreen(),
            "vehicle":    VehicleScreen(),
            "settings":   SettingsScreen(),
            "bluetooth":  BluetoothScreen(),
        }
        self._menu_destinations = [
            "ride_stats", "navigation", "vehicle", "settings", "bluetooth",
        ]

        # Physics tick timer (16 ms ≈ 60 fps)
        self._last_tick_ns: int = time.perf_counter_ns()
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._physics_and_repaint)
        self._timer.start()

    # ── Physics loop ──────────────────────────────────────────────────────────

    def _physics_and_repaint(self) -> None:
        now_ns = time.perf_counter_ns()
        dt     = (now_ns - self._last_tick_ns) / 1e9   # seconds
        self._last_tick_ns = now_ns

        # Advance physics; updates vs.odometer, vs.trip, vs.battery, vs.range_km
        physics_engine.tick(dt)

        # Schedule repaint
        self.update()

    # ── Public API (called externally if needed) ───────────────────────────────

    def set_data(self, speed: float, fuel: float = 100, temp: float = 40,
                 rpm: int = 0, odo: float = 0, trip: float = 0) -> None:
        """
        Legacy shim for any code that calls set_data().
        When CAN hardware is active, update vehicle_state directly instead.
        Physics engine will compute odometry from vs.speed each tick.
        """
        vs.speed = float(speed)
        # fuel/temp/rpm ignored — not used by physics or renderer

    def set_throttle(self, pct: int) -> None:
        """Set throttle 0-100. Physics engine ramps speed accordingly."""
        vs.throttle = max(0, min(100, int(pct)))

    def set_brake(self, pct: int) -> None:
        """Set brake 0-100. Physics engine decelerates accordingly."""
        vs.brake = max(0, min(100, int(pct)))

    def reset_trip(self) -> None:
        physics_engine.reset_trip()

    # ── Qt paint ──────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        screen = self._screens.get(self._sm.current_screen, self._home)
        screen.render(p, _adapter)
        p.end()

    def mousePressEvent(self, event) -> None:
        x, y    = event.x(), event.y()
        current = self._sm.current_screen
        if current == "home":
            self._home.handle_click(x, y, _adapter, self._sm)
        else:
            if x < 80 and y > 520:
                self._sm.back()
            elif current == "menu":
                self._handle_menu_click(x, y)
        self.update()

    def _handle_menu_click(self, x: int, y: int) -> None:
        if not (70 <= x <= 948):
            return
        idx = (y - 67) // 78
        if 0 <= idx < len(self._menu_destinations):
            self._sm.switch(self._menu_destinations[idx])
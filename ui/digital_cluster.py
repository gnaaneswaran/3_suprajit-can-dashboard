"""
ui/digital_cluster.py
─────────────────────────────────────────────────────────────────────────────
Digital instrument cluster widget — pure renderer.

Reads live data from the shared vehicle_state singleton every paint cycle.
physics_engine is called ONLY from main_window._physics_tick — never here.
No internal QTimer, no physics calls, no duplicate state.

Hardware path
─────────────────────────────────────────────────────────────────────────────
  ESP32 → CAN decoder → vehicle_state → main_window calls dc.update() → repaint
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QPainter
from PyQt5.QtCore    import Qt

from core.vehicle_state import vehicle_state as vs

from ui.oem_digital.screens.home_screen       import HomeScreen
from ui.oem_digital.screens.menu_screen       import MenuScreen
from ui.oem_digital.screens.ride_stats_screen import RideStatsScreen
from ui.oem_digital.screens.navigation_screen import NavigationScreen
from ui.oem_digital.screens.vehicle_screen    import VehicleScreen
from ui.oem_digital.screens.settings_screen   import SettingsScreen
from ui.oem_digital.screens.bluetooth_screen  import BluetoothScreen


# ── Model adapter ─────────────────────────────────────────────────────────────

class _ModelAdapter:
    """Read-only proxy into the vehicle_state singleton."""

    # Core display
    @property
    def speed(self):                return vs.speed
    @property
    def battery(self):              return vs.battery
    @property
    def range_km(self):             return vs.range_km
    @property
    def odo(self):                  return vs.odometer
    @property
    def trip_a(self):               return vs.trip
    @property
    def ride_mode(self):            return vs.ride_mode
    @property
    def ride_mode_label(self):      return vs.ride_mode_label
    @property
    def time_string(self):          return vs.time_string
    @property
    def mobile_signal(self):        return vs.mobile_signal
    @property
    def bluetooth(self):            return vs.bluetooth
    @property
    def motor_on(self):             return bool(vs.throttle) or vs.speed > 0
    @property
    def side_stand_down(self):      return vs.speed < 1.0 and vs._side_stand
    @property
    def motor_power_kw(self):       return getattr(vs, 'motor_power_kw', 0.0)
    @property
    def regen(self):                return getattr(vs, 'regen', 0)

    # Indicators (read / write)
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

    # Navigation
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
        self._history: list = []

    def switch(self, screen: str) -> None:
        self._history.append(self.current_screen)
        self.current_screen = screen

    def back(self) -> None:
        if self._history:
            self.current_screen = self._history.pop()


# ── Main widget ───────────────────────────────────────────────────────────────

class DigitalClusterWidget(QWidget):
    """
    Pure renderer. Reads vs every repaint.
    main_window._physics_tick() writes vs values then calls dc.update().
    No internal timer, no physics calls here — one physics loop in main_window.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sm   = _ScreenManager()
        self._home = HomeScreen()
        self._screens = {
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

    def set_data(self, speed=0, fuel=100, temp=40, rpm=0, odo=0, trip=0):
        """Legacy shim — vs is already updated upstream. update() repaints."""
        pass

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        screen = self._screens.get(self._sm.current_screen, self._home)
        screen.render(p, _adapter)
        p.end()

    def mousePressEvent(self, event):
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
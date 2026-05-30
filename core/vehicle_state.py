"""
ui/oem_hybrid/core/vehicle_state.py
Single shared VehicleState object used by ALL clusters and main.py.
Import `vehicle_state` everywhere — never create a new VehicleState().
"""
from datetime import datetime


class VehicleState:

    def __init__(self):
        # ── Core signals (written by serial/physics tick) ──────────────────
        self.speed       = 0.0
        self.rpm         = 1200.0
        self.fuel        = 100.0
        self.temp        = 42.0
        self.engine_temp = 42.0
        self.throttle    = 0.0
        self.brake       = 0.0

        # ── Odometry ──────────────────────────────────────────────────────
        self.odo         = 12458.3
        self.odometer    = 12458.3
        self.trip        = 0.0

        # ── Derived / display ─────────────────────────────────────────────
        self.range_km    = 268.0
        self.battery     = 100.0   # alias for fuel (EV display)
        self.avg_speed   = 0.0
        self.top_speed   = 0.0
        self.lean        = 0.0

        # ── Warnings ──────────────────────────────────────────────────────
        self.temp_warning    = False
        self.engine_warning  = False

        # ── Modes / flags ─────────────────────────────────────────────────
        self.eco_mode        = True
        self.ride_mode       = "SMART ECO"
        self.ride_mode_label = "ECO"
        self.motor_on        = True
        self._side_stand     = True
        self.side_stand      = True
        self.side_stand_down = True

        # ── Indicators ────────────────────────────────────────────────────
        self.left_indicator  = False
        self.right_indicator = False
        self.high_beam       = False
        self.park_assist_active = False

        # ── Connectivity ──────────────────────────────────────────────────
        self.bluetooth    = True
        self.mobile_signal = 3
        self.wifi         = False
        self.brightness   = 80

        # ── Navigation ────────────────────────────────────────────────────
        self.next_turn         = "Head southeast"
        self.distance_to_turn  = "120 m"
        self.eta_time          = "12:44 PM"
        self.total_nav_distance = "4.2 km"
        self.nav_duration      = "12 min"

        # ── Ride stats ────────────────────────────────────────────────────
        self.stat_distance       = 0.0
        self.stat_avg_speed      = 0.0
        self.stat_avg_efficiency = 34.0
        self.stat_top_speed      = 0.0

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_range(self):
        self.range_km = max(0.0, round(self.battery * (85.0 / 100.0), 1))

    def _update_time(self):
        pass  # time is read live in _ModelAdapter

    @property
    def time_string(self):
        return datetime.now().strftime("%I:%M %p").lstrip("0")


# ── Singleton — import this everywhere ────────────────────────────────────────
vehicle_state = VehicleState()
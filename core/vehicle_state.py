"""
core/vehicle_state.py
─────────────────────────────────────────────────────────────────────────────
Single source of truth for all vehicle data.

Rules
──────
  • ride_mode is an integer index  (0=ECO  1=CITY  2=SPORT  3=TURBO)
    physics_engine.py does  MODE_CONFIG[vs.ride_mode]  — a string causes IndexError.
  • range_km starts at 85 (matching battery=100 × 0.85).
    physics_engine.tick() overwrites this every 30 ms.
  • time_string is a property — always returns live clock, never stored.
  • All other attributes have safe defaults so widgets never KeyError/AttributeError.
"""

import time


class VehicleState:

    def __init__(self):

        # ── Motion ────────────────────────────────────────────────────────────
        self.speed          = 0.0       # km/h  (current, smoothed)
        self.rpm            = 1200.0
        self.lean           = 0.0

        # ── Energy ────────────────────────────────────────────────────────────
        self.fuel           = 100.0     # %  (mirrors battery for analog cluster)
        self.battery        = 100.0     # %

        self.voltage        = 51.4      # V
        self.current        = 0.0       # A
        self.power          = 0.0       # W

        self.motor_power_kw = 0.0       # +kW motoring, -kW regenerating
        self.regen          = 0         # 0-100 % regen braking intensity

        # range_km: physics_engine writes this every tick (battery × 3.0)
        # Starting at 85 (= 100 % × 0.85) keeps the hybrid cluster's legacy
        # formula (battery × 0.85 × 3.5) consistent on first frame.
        # Do NOT set this to 268 or any other magic constant.
        self.range_km       = 300.0     # km — overwritten every tick

        # ── Thermal ───────────────────────────────────────────────────────────
        self.temp           = 42.0      # °C  motor/controller temp
        self.engine_temp    = 42.0      # °C  (alias used by hybrid cluster)
        self.battery_temp   = 35.0      # °C

        # ── Odometry ──────────────────────────────────────────────────────────
        self.odometer       = 12458.3   # km  lifetime
        self.odo            = self.odometer   # alias kept for legacy widgets
        self.trip           = 0.0       # km  Trip A (reset by user)
        self.trip_b         = 0.0       # km  Trip B

        # ── Session statistics (written by physics_engine.tick) ───────────────
        self.avg_speed          = 0.0   # km/h rolling mean this session
        self.top_speed          = 0.0   # km/h session maximum
        self.stat_avg_efficiency= 0.0   # km/Wh rolling mean

        # ── Ride mode ─────────────────────────────────────────────────────────
        # MUST be an integer — physics_engine indexes MODE_CONFIG with this.
        # 0=ECO  1=CITY  2=SPORT  3=TURBO
        self.ride_mode          = 0
        self.ride_mode_label    = "ECO"

        # ── Controls ──────────────────────────────────────────────────────────
        self.throttle       = 0.0       # 0.0-100.0 %
        self.brake          = 0.0       # 0.0-100.0 %

        # ── Indicators ────────────────────────────────────────────────────────
        self.left_indicator     = False
        self.right_indicator    = False
        self.high_beam          = False
        self.abs_active         = False
        self.park_assist_active = False

        # ── Side stand ────────────────────────────────────────────────────────
        self._side_stand        = True   # True = down; physics clears above 2 km/h

        # ── Connectivity ──────────────────────────────────────────────────────
        self.bluetooth      = False
        self.wifi           = False
        self.mobile_signal  = 4         # 0-4 bars

        # ── Display ───────────────────────────────────────────────────────────
        self.brightness     = 80        # 0-100 %

        # ── Navigation ────────────────────────────────────────────────────────
        self.next_turn          = ""
        self.distance_to_turn   = 0.0
        self.eta_time           = ""
        self.total_nav_distance = 0.0
        self.nav_duration       = ""

    # ── Computed properties ───────────────────────────────────────────────────

    @property
    def time_string(self) -> str:
        """Live clock — always returns the current time, never cached."""
        return time.strftime("%I:%M %p")

    def update_range(self) -> None:
        """
        Simple EV range estimate called by legacy code.
        physics_engine.tick() also sets range_km every frame.
        100 % battery = 300 km.
        """
        self.range_km = max(0.0, self.battery * 3.0)


# ── Module-level singleton ────────────────────────────────────────────────────
# Import this object everywhere:
#   from core.vehicle_state import vehicle_state as vs
vehicle_state = VehicleState()
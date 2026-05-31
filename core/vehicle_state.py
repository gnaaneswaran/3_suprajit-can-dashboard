import time


class VehicleState:
    def __init__(self):

        # ───────────────── Motion ─────────────────
        self.speed = 0.0
        self.rpm = 1200.0
        self.lean = 0.0

        # ───────────────── Energy ─────────────────
        self.fuel = 100.0
        self.battery = 100.0

        self.voltage = 51.4
        self.current = 0.0
        self.power = 0.0

        self.motor_power_kw = 0.0
        self.regen = 0
        self.range_km = 300.0

        # ───────────────── Thermal ─────────────────
        self.temp = 42.0
        self.engine_temp = 42.0
        self.battery_temp = 35.0

        # ───────────────── Odometer ─────────────────
        self.odometer = 12458.3
        self.odo = self.odometer

        self.trip = 0.0
        self.trip_b = 0.0

        self.avg_speed = 0.0
        self.top_speed = 0.0
        self.stat_avg_efficiency = 0.0

        # ───────────────── Ride Mode ─────────────────
        self.ride_mode = 0
        self.ride_mode_label = "ECO"

        # ───────────────── Controls ─────────────────
        self.throttle = 0.0
        self.brake = 0.0

        # ───────────────── Indicators ─────────────────
        self.left_indicator = False
        self.right_indicator = False
        self.high_beam = False

        self.abs_active = False
        self.park_assist_active = False

        # ───────────────── Side Stand ─────────────────
        self._side_stand = True

        # ───────────────── Connectivity ─────────────────
        self.bluetooth = False
        self.wifi = False
        self.mobile_signal = 4

        # ───────────────── Display ─────────────────
        self.brightness = 80

        # ───────────────── Navigation ─────────────────
        self.next_turn = ""
        self.distance_to_turn = 0.0
        self.eta_time = ""
        self.total_nav_distance = 0.0
        self.nav_duration = ""

    @property
    def time_string(self):
        return time.strftime("%I:%M %p")

    def update_range(self):
        """
        Simple EV range estimate.
        100% battery = 300 km
        """

        self.range_km = max(0.0, self.battery * 3.0)


vehicle_state = VehicleState()
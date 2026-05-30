class UIState:

    def __init__(self):

        # Vehicle
        self.speed = 0
        self.battery = 78
        self.range_km = 85
        self.temperature = 42

        # Ride
        self.trip_a = 0.0
        self.trip_b = 0.0
        self.odo = 12458

        # Modes
        self.ride_mode = "ECO"

        # Indicators
        self.left_indicator = False
        self.right_indicator = False
        self.high_beam = False

        # Warnings
        self.side_stand = False
        self.motor_fault = False
        self.overheat = False

        # Connectivity
        self.bluetooth = True
        self.wifi = False

        # Navigation
        self.navigation_active = False
        self.next_turn = "LEFT"
        self.distance_to_turn = "120m"

        # UI
        self.current_screen = "home"
        self.notification = None

        # System
        self.time_string = "09:18 AM"
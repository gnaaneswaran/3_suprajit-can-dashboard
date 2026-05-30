class VehicleModel:

    def __init__(self):

        # INPUT STATES

        self.throttle = False
        self.brake = False

        # VEHICLE STATES

        self.speed = 0.0

        self.fuel = 100.0

        self.temp = 42.0

        self.rpm = 1200.0

        self.odometer = 0.0

        self.trip = 0.0

    # OPTIONAL LEGACY UPDATE

    def update(self, dt=0.03):

        pass


model = VehicleModel()
class EnergyModel:

    def __init__(self):

        self.fuel = 100.0
        self.battery = 100.0

    # ----------------------------------
    # VERY SLOW FUEL DROP
    # ----------------------------------

    def update(
        self,
        speed,
        digital_mode=False
    ):

        drain = speed * 0.0000045

        if digital_mode:

            self.battery -= drain

            self.battery = max(
                0,
                min(100, self.battery)
            )

        else:

            self.fuel -= drain

            self.fuel = max(
                0,
                min(100, self.fuel)
            )

    # ----------------------------------
    # REFUEL
    # ----------------------------------

    def refuel(self):

        self.fuel = 100.0

    # ----------------------------------
    # RECHARGE
    # ----------------------------------

    def recharge(self):

        self.battery = 100.0
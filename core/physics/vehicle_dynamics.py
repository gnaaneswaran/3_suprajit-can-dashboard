class VehicleDynamics:

    def __init__(self):

        # ----------------------------
        # VEHICLE STATE
        # ----------------------------

        self.speed = 0.0

        # ----------------------------
        # TARGETS
        # ----------------------------

        self.max_speed = 90.0

        # 0 → 90 around 16 sec
        self.acceleration_rate = 0.095

        # coasting slowdown
        # 80 → 0 around 15 sec
        self.coast_drag = 0.090

        # brake slowdown
        # 80 → 0 around 5–8 sec
        self.brake_force = 0.22

    def update(
        self,
        throttle,
        brake,
        mode="NORMAL",
        regen=False
    ):

        # -----------------------------------
        # DRIVE MODES
        # -----------------------------------

        mode_mult = 1.0

        if mode == "ECO":
            mode_mult = 0.78

        elif mode == "SPORT":
            mode_mult = 1.12

        # -----------------------------------
        # ACCELERATION
        # -----------------------------------

        if throttle > 0:

            accel = (
                throttle *
                self.acceleration_rate *
                mode_mult
            )

            # gradual taper near top speed
            taper = (
                1.0 -
                (self.speed / self.max_speed)
            )

            taper = max(0.15, taper)

            self.speed += accel * taper

        # -----------------------------------
        # NATURAL COASTING
        # -----------------------------------

        else:

            drag = (
                self.coast_drag +
                (self.speed * 0.0018)
            )

            self.speed -= drag

        # -----------------------------------
        # REGEN BRAKING
        # -----------------------------------

        if regen and throttle < 0.05:

            self.speed -= 0.06

        # -----------------------------------
        # MANUAL BRAKING
        # -----------------------------------

        if brake > 0:

            braking = (
                brake *
                self.brake_force
            )

            braking += (
                self.speed * 0.002
            )

            self.speed -= braking

        # -----------------------------------
        # CLAMP
        # -----------------------------------

        self.speed = max(
            0.0,
            min(self.max_speed, self.speed)
        )

        return self.speed
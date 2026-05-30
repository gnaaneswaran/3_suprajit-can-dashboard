class ThermalModel:

    def __init__(self):

        self.temp = 42.0

    def update(self, speed):

        target = 42 + (
            speed / 140
        ) * 55

        self.temp += (
            target - self.temp
        ) * 0.012

        self.temp = max(
            40,
            min(110, self.temp)
        )

        return self.temp
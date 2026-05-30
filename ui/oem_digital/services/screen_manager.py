class ScreenManager:

    VALID_SCREENS = {
        "home",
        "menu",
        "ride_stats",
        "navigation",
        "vehicle",
        "settings",
        "bluetooth",
    }

    def __init__(self):
        self.current_screen = "home"
        self.history = []

    def switch(self, screen):
        if screen not in self.VALID_SCREENS:
            return
        self.history.append(self.current_screen)
        self.current_screen = screen

    def back(self):
        if self.history:
            self.current_screen = self.history.pop()
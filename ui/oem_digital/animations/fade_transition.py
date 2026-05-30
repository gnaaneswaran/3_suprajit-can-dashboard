from PyQt5.QtCore import QTimer


class FadeTransition:
    """
    Drives a simple alpha fade between screen switches.

    Usage:
        self.fade = FadeTransition(steps=8, interval_ms=30)
        self.fade.start(on_tick=self.update, on_done=None)

    Read self.fade.alpha (0–255) in paintEvent to apply opacity.
    """

    def __init__(self, steps: int = 8, interval_ms: int = 30):

        self.steps       = steps
        self.interval_ms = interval_ms
        self.alpha       = 255
        self._step       = 0
        self._fading_in  = False
        self._on_tick    = None
        self._on_done    = None
        self._timer      = QTimer()
        self._timer.timeout.connect(self._tick)

    def start(self, on_tick=None, on_done=None):

        self._on_tick   = on_tick
        self._on_done   = on_done
        self._step      = 0
        self._fading_in = False
        self.alpha      = 255
        self._timer.start(self.interval_ms)

    def _tick(self):

        self._step += 1
        progress = self._step / self.steps

        if not self._fading_in:
            self.alpha = int(255 * (1.0 - progress))
            if self._step >= self.steps:
                self._fading_in = True
                self._step = 0
        else:
            self.alpha = int(255 * progress)
            if self._step >= self.steps:
                self._timer.stop()
                self.alpha = 255
                if self._on_done:
                    self._on_done()

        if self._on_tick:
            self._on_tick()

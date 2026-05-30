class RouteProvider:
    """
    Stub for GPS / navigation data.
    In production, replace the body of tick() with real GPS parsing.
    Writes directly into VehicleState so NavigationScreen stays read-only.
    """

    DEMO_ROUTE = [
        ("LEFT",  "200 m"),
        ("RIGHT", "500 m"),
        ("STRAIGHT", "1.2 km"),
        ("LEFT",  "50 m"),
        ("ARRIVED", "0 m"),
    ]

    def __init__(self):
        self._step = 0

    def tick(self, state):
        """Call this once per second to advance the demo route."""
        turn, dist = self.DEMO_ROUTE[self._step % len(self.DEMO_ROUTE)]
        state.next_turn         = turn
        state.distance_to_turn  = dist

    def advance(self):
        self._step += 1

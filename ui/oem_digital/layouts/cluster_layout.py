from PyQt5.QtWidgets import QWidget, QVBoxLayout

from oem.cluster_shell      import ClusterShell
from oem.glass_layer        import GlassLayer
from oem.tft_screen         import TFTScreen
from oem.services.screen_manager  import ScreenManager
from oem.services.vehicle_state   import VehicleState
from oem.touch.touch_handler      import TouchHandler
from oem.overlays.charging_overlay import ChargingOverlay

# Screens
from oem.screens.home_screen       import HomeScreen
from oem.screens.navigation_screen import NavigationScreen
from oem.screens.ride_stats_screen import RideStatsScreen
from oem.screens.settings_screen   import SettingsScreen
from oem.screens.vehicle_screen    import VehicleScreen

# Widgets
from oem.widgets.battery_card   import BatteryCard
from oem.widgets.bottom_navbar  import BottomNavbar
from oem.widgets.speed_display  import SpeedDisplay
from oem.widgets.status_bar     import StatusBarWidget
from oem.widgets.trip_panel     import TripPanel


def build_cluster(parent: QWidget = None) -> ClusterShell:
    """
    Factory function.  Call once from main.py:

        cluster = build_cluster()
        cluster.show()

    Returns the fully-wired ClusterShell widget.
    """

    # ── State & routing ─────────────────────────
    state          = VehicleState()
    screen_manager = ScreenManager()
    touch          = TouchHandler()

    # ── Widgets ─────────────────────────────────
    widgets = {
        "status_bar": StatusBarWidget(),
        "battery":    BatteryCard(),
        "speed":      SpeedDisplay(),
        "trip":       TripPanel(),
        "bottom_nav": BottomNavbar(),
    }

    # ── Screens ─────────────────────────────────
    screens = {
        "home":       HomeScreen(widgets),
        "navigation": NavigationScreen(),
        "ride_stats": RideStatsScreen(),
        "settings":   SettingsScreen(),
        "vehicle":    VehicleScreen(),
    }

    # ── TFT display ─────────────────────────────
    tft                  = TFTScreen(parent)
    tft.state            = state
    tft.screen_manager   = screen_manager
    tft.screens          = screens
    tft.charging_overlay = ChargingOverlay()

    # Wire touch → screen manager
    _orig_mouse = tft.mousePressEvent

    def _on_click(event):
        if touch.handle(event.x(), event.y(), screen_manager):
            tft.update()

    tft.mousePressEvent = _on_click

    # ── Shell (outer bezel) ──────────────────────
    shell       = ClusterShell(parent)
    glass       = GlassLayer(shell)
    glass.setAttribute(__import__("PyQt5.QtCore", fromlist=["Qt"]).Qt.WA_TransparentForMouseEvents)
    shell.glass = glass

    # Embed TFT inside shell
    tft.setParent(shell)
    tft.resize(shell.width(), shell.height())

    # Expose state/screen_manager for external CAN updates
    shell.state          = state
    shell.screen_manager = screen_manager
    shell.tft            = tft

    return shell

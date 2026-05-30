"""
main.py — Suprajit CAN Bus Analyzer
Single entry point. Run this file only.

Hardware path:
  ESP32 → USB Serial → SerialReader (background thread) → vehicle_state
  → _physics_tick (30 ms QTimer) → all clusters

Fallback (no hardware):
  keyboard Up/Down → _physics_tick → all clusters
"""
import sys
import os

ROOT    = os.path.dirname(os.path.abspath(__file__))
OEM_DIR = os.path.join(ROOT, "ui", "oem_digital")
for p in (ROOT, OEM_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore    import Qt, QTimer

from ui.main_window                          import MainWindow
from ui.oem_hybrid.core.vehicle_state        import vehicle_state as vs

# ── Constants ─────────────────────────────────────────────────────────────────
TICK_MS   = 30
TICK_S    = TICK_MS / 1000.0
MAX_SPEED = 85.0

# ── Keyboard state (fallback when no hardware) ────────────────────────────────
pressed = {"up": False, "down": False}


# ── Keyboard wiring ───────────────────────────────────────────────────────────
def _wire_keys(win):
    def kp(e):
        k = e.key()
        if k == Qt.Key_Up:      pressed["up"]   = True
        elif k == Qt.Key_Down:  pressed["down"] = True
        else:                   type(win).keyPressEvent(win, e)

    def kr(e):
        k = e.key()
        if k == Qt.Key_Up:      pressed["up"]   = False
        elif k == Qt.Key_Down:  pressed["down"] = False
        else:                   type(win).keyReleaseEvent(win, e)

    win.keyPressEvent   = kp
    win.keyReleaseEvent = kr


# ── Physics tick ──────────────────────────────────────────────────────────────
def _physics_tick(win):
    sr = win.serial_reader

    if sr.connected and sr.serial and sr.serial.is_open:
        # ── HARDWARE PATH (Potentiometer via ESP32) ──────────────────────
        adc    = sr.value
        POT_MIN = 300
        POT_MAX = 4255
        adc_clamped = max(POT_MIN, min(POT_MAX, adc))
        target = ((adc_clamped - POT_MIN) / (POT_MAX - POT_MIN)) * MAX_SPEED

        vs.speed += (target - vs.speed) * 0.18

        if vs.brake:
            vs.speed *= 0.82

        vs.speed = max(0.0, min(MAX_SPEED, vs.speed))

        if adc > 150:
            vs.fuel = max(0.0, min(100.0, vs.fuel - vs.speed * 0.0008))

        vs.battery     = vs.fuel
        vs.temp        = 42.0 + vs.speed * 0.75
        vs.rpm         = 1200.0 + vs.speed * 75.0
        vs.lean        = 0.0
        vs.engine_temp = vs.temp

        print(f"ADC={adc:4d}  TARGET={target:5.1f}  SPEED={vs.speed:5.1f}")

    else:
        # ── KEYBOARD FALLBACK ────────────────────────────────────────────
        if pressed["up"]:
            vs.speed = min(MAX_SPEED, vs.speed + 6.9 * TICK_S)
        elif pressed["down"]:
            vs.speed = max(0.0, vs.speed - 12.0 * TICK_S)
        else:
            vs.speed = max(0.0, vs.speed - 1.4 * TICK_S)

        vs.temp    = 42.0 + vs.speed * 0.75
        vs.rpm     = 1200.0 + vs.speed * 75.0

        if vs.fuel > 0 and vs.speed > 1:
            vs.fuel    = max(0.0, vs.fuel - vs.speed * 0.0008)
            vs.battery = vs.fuel

    # ── Shared derived values ─────────────────────────────────────────────
    dist_km        = (vs.speed * TICK_S) / 3600.0
    vs.odometer   += dist_km
    vs.odo         = vs.odometer
    vs.trip       += dist_km
    vs.top_speed   = max(vs.top_speed, vs.speed)
    vs.engine_temp = vs.temp
    vs._update_range()

    if vs.speed > 2.0:
        vs._side_stand     = False
        vs.side_stand      = False
        vs.side_stand_down = False

    _push_to_clusters(win)


# ── Push state to every cluster widget ───────────────────────────────────────
def _push_to_clusters(win):
    s = vs

    dc = getattr(win, "digital_cluster", None)
    if dc:
        dc.update()

    ac = getattr(win, "analog_cluster", None)
    if ac:
        try:
            ac.set_data(s.speed, s.fuel, s.temp, s.rpm, s.odometer, s.trip)
        except Exception as e:
            print(f"[Analog] {e}")

    hc = getattr(win, "hybrid_cluster", None)
    if hc:
        try:
            hc.set_data(s.speed, s.fuel, s.temp, s.rpm, s.odometer, s.trip)
        except Exception as e:
            print(f"[Hybrid] {e}")

    cp = getattr(win, "ctrl_panel", None)
    if cp:
        try:
            cp.update_indicators(bool(s.throttle), bool(s.brake))
        except Exception:
            pass

    for attr, text in [
        ("_status_speed", f"{int(s.speed)} km/h"),
        ("_status_fuel",  f"{int(s.fuel)}%"),
        ("_status_temp",  f"{int(s.temp)}°C"),
    ]:
        lbl = getattr(win, attr, None)
        if lbl:
            lbl.setText(text)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = MainWindow()
    win.setFocusPolicy(Qt.StrongFocus)

    _wire_keys(win)

    if hasattr(win, "_physics_timer"):
        win._physics_timer.stop()

    print(f"[Main] Serial connected: {win.serial_reader.connected}")
    if win.serial_reader.connected:
        print(f"[Main] Hardware path active — ESP32 pot driving clusters")
    else:
        print(f"[Main] Fallback path active — use UP/DOWN keys to simulate speed")

    timer = QTimer()
    timer.setInterval(TICK_MS)
    timer.timeout.connect(lambda: _physics_tick(win))
    timer.start()

    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
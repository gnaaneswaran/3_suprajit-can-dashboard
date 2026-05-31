"""
core/physics_engine.py
─────────────────────────────────────────────────────────────────────────────
Real-time physics engine for the EV digital cluster.

Reads and writes directly to the shared vehicle_state singleton.
Call PhysicsEngine.tick(dt_seconds) from your main update loop or a QTimer.

Physics model
─────────────────────────────────────────────────────────────────────────────
  Speed        → Throttle drives gradual acceleration toward (throttle% × maxSpeed).
                 Brake drives deceleration. Coast uses regen-assisted rolloff.

  Odometer     → distance_km = speed_kmh × dt_seconds / 3600
                 Accumulated each tick. Never faked or interpolated.

  Battery      → Drains per km based on mode consumption rate + throttle load.
                 Regen braking recovers a fraction of kinetic energy.

  Range        → (battery_pct / 100) × 300 km  (100% = 300 km, linear)

  Efficiency   → km / (Wh equivalent consumed), rolling average.

Hardware path (future)
─────────────────────────────────────────────────────────────────────────────
  ESP32 → CAN decoder → vehicle_state → (this engine is bypassed for speed/batt)
  When real CAN data arrives, disable tick() and feed vehicle_state directly.
  Odometry and stats will still work correctly as they read vehicle_state.speed.
"""

from core.vehicle_state import vehicle_state as vs

# ── Mode configuration ────────────────────────────────────────────────────────
# accel / decel in km/h per second
# consumption in % battery per km (realistic: drains ~1% per ~30 km)
# regen_frac: fraction of consumption recovered during braking
MODE_CONFIG = {
    "ECO":   dict(max_speed=60,  accel=5.0,  decel=12, consumption=0.00008, regen_frac=0.35),
    "CITY":  dict(max_speed=85,  accel=7.0,  decel=14, consumption=0.00010, regen_frac=0.30),
    "SPORT": dict(max_speed=110, accel=10.0, decel=16, consumption=0.00012, regen_frac=0.25),
    "TURBO": dict(max_speed=140, accel=14.0, decel=18, consumption=0.00015, regen_frac=0.20),

}
MAX_POWER_KW = {"ECO": 5.5, "CITY": 8.0, "SPORT": 12.0, "TURBO": 18.0}

# Mode name lookup — vehicle_state.ride_mode is an int (0=ECO, 1=CITY, 2=SPORT, 3=TURBO)
MODE_NAMES = ["ECO", "CITY", "SPORT", "TURBO"]

# Internal accumulators (not stored on vehicle_state to keep it clean)
_speed_sum     = 0.0
_speed_samples = 0
_dist_total    = 0.0
_energy_used   = 0.0   # % battery equivalent


def tick(dt: float) -> None:
    """
    Advance the physics simulation by `dt` seconds.

    Call this from a 60 Hz QTimer (dt ≈ 0.0167 s) or any fixed-step loop.
    Safe to call with dt up to ~0.1 s (capped internally to avoid jumps).

    Parameters
    ----------
    dt : float
        Elapsed time since last tick, in seconds.
    """
    global _speed_sum, _speed_samples, _dist_total, _energy_used

    dt = min(dt, 0.10)        # cap to 80 ms — avoids physics explosion on tab resume

    # ── Resolve ride mode (int index or string both accepted) ─────────────────
    mode_name = (
        MODE_NAMES[vs.ride_mode]
        if isinstance(vs.ride_mode, int) and 0 <= vs.ride_mode < len(MODE_NAMES)
        else "ECO"
    )
    mode = MODE_CONFIG[mode_name]

    throttle_pct = max(0.0, min(1.0, vs.throttle / 100.0))
    brake_pct    = max(0.0, min(1.0, vs.brake    / 100.0))

    # ── 1. Speed dynamics ─────────────────────────────────────────────────────
    desired_speed = throttle_pct * mode["max_speed"]

    if vs.speed < desired_speed:
        # Accelerating: ramp rate proportional to throttle position
        accel_rate = mode["accel"] * throttle_pct
        vs.speed   = min(desired_speed, vs.speed + accel_rate * dt)

    elif brake_pct > 0:
        # Active braking
        vs.speed = max(0.0, vs.speed - mode["decel"] * brake_pct * dt)

    else:
        # Coasting: rolling resistance + passive regen
        coast_decel = 3.0 + mode["regen_frac"] * vs.speed * 0.05
        vs.speed    = max(desired_speed, vs.speed - coast_decel * dt)

    vs.speed = max(0.0, min(mode["max_speed"], vs.speed))

    # ── 2. Odometry ───────────────────────────────────────────────────────────
    dist_km      = vs.speed * dt / 3600.0
    vs.odometer += dist_km
    vs.odo       = vs.odometer          # keep legacy alias in sync
    vs.trip     += dist_km
    vs.trip = round(vs.trip, 2)
    vs.odometer = round(vs.odometer, 1)
    vs.odo = vs.odometer

    # ── 3. Battery consumption ────────────────────────────────────────────────
    throttle_load = 0.1 + throttle_pct * 0.9         # 0.1 idle → 1.0 full throttle
    batt_used       = dist_km * mode["consumption"] * throttle_load

    regen_active    = (brake_pct > 0) or (vs.speed > desired_speed + 2)
    regen_intensity = brake_pct if brake_pct > 0 else 0.3
    batt_recovered  = dist_km * mode["regen_frac"] * regen_intensity if regen_active else 0.0

    vs.battery = max(0.0, min(100.0, vs.battery - batt_used + batt_recovered))

    # ── 4. Range ──────────────────────────────────────────────────────────────
    vs.range_km = round(vs.battery * 3.0, 1)

    # ── 5. Regen indicator ────────────────────────────────────────────────────
    vs.regen = round(regen_intensity * 100) if regen_active else 0

    # ── 6. Motor power (kW) ───────────────────────────────────────────────────
    max_pw = MAX_POWER_KW.get(mode_name, 8.0)
    if regen_active:
        vs.motor_power_kw = round(-(regen_intensity * max_pw * 0.4), 1)
    else:
        speed_ratio = vs.speed / max(1.0, mode["max_speed"])
        vs.motor_power_kw = round(throttle_pct * max_pw * speed_ratio, 1)

    # ── 7. Trip statistics ────────────────────────────────────────────────────
    if vs.speed > 0:
        _speed_samples += 1
        _speed_sum     += vs.speed
        vs.avg_speed    = _speed_sum / _speed_samples

    if vs.speed > vs.top_speed:
        vs.top_speed = vs.speed

    # ── 8. Efficiency ─────────────────────────────────────────────────────────
    _dist_total  += dist_km
    _energy_used += batt_used
    if _energy_used > 0:
        # Scale: 1% battery ≈ 3 Wh for this model → km/Wh
        vs.stat_avg_efficiency = round(_dist_total / (_energy_used * 3.0), 2)

    # ── 9. Side stand ─────────────────────────────────────────────────────────
    if vs.speed > 5.0:
       vs._side_stand = False
    elif vs.speed < 1.0:
       vs._side_stand = True


def reset_trip() -> None:
    """Reset trip odometer and all session statistics."""
    global _speed_sum, _speed_samples, _dist_total, _energy_used
    vs.trip                = 0.0
    vs.top_speed           = 0.0
    vs.avg_speed           = 0.0
    vs.stat_avg_efficiency = 0.0
    _speed_sum             = 0.0
    _speed_samples         = 0
    _dist_total            = 0.0
    _energy_used           = 0.0
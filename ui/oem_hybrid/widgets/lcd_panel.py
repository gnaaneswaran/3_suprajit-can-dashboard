# widgets/lcd_panel.py — Suprajit Hybrid Cluster
# Recessed LCD panel: time/date, big speed, ODO, TRIP, RANGE, LOCATION,
# plus the StatusStrip at the bottom.

from PyQt5.QtCore    import Qt, QTimer
from PyQt5.QtGui     import QFont
from PyQt5.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                              QSizePolicy)
from datetime        import datetime

from ui.oem_hybrid.core.palette          import P
from ui.oem_hybrid.core.location         import _Loc
from ui.oem_hybrid.widgets.painter_icons import BTIconWidget, FuelIconWidget, LocIconWidget
from ui.oem_hybrid.widgets.status_strip  import StatusStrip
from ui.oem_hybrid.core.vehicle_state    import VehicleState


class LCDPanel(QWidget):

    def __init__(self, state: VehicleState, parent=None):
        super().__init__(parent)
        self.state = state
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Layer 1: outer dark bezel ─────────────────────────────────────────
        l1 = self._frame(f"""
            QFrame {{
                background: {P['bezel_outer']};
                border: 3px solid {P['bezel_rim']};
                border-radius: 14px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """, expanding=True)
        l1l = QVBoxLayout(l1)
        l1l.setContentsMargins(4, 4, 4, 4)
        l1l.setSpacing(0)

        # ── Layer 2: inner trim ring ──────────────────────────────────────────
        l2 = self._frame(f"""
            QFrame {{
                background: {P['bezel_inner']};
                border: 2px solid {P['bezel_rim']};
                border-radius: 11px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        l2l = QVBoxLayout(l2)
        l2l.setContentsMargins(3, 3, 3, 3)
        l2l.setSpacing(0)

        # ── Layer 3: inset LCD glass ──────────────────────────────────────────
        lcd = self._frame(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {P['lcd_bg_top']},
                    stop:1 {P['lcd_bg_bot']}
                );
                border: 1px solid {P['lcd_border']};
                border-radius: 9px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """, expanding=True)
        ll = QVBoxLayout(lcd)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)

        # ── Row 1: time + date + BT ───────────────────────────────────────────
        r1 = self._row(h=40)
        rl = QHBoxLayout(r1)
        rl.setContentsMargins(12, 0, 12, 0)

        self.time_lbl = QLabel("10:30 AM")
        self._style(self.time_lbl, 15, bold=True)

        self.date_lbl = QLabel("Mon 11 May")
        self._style(self.date_lbl, 10, color=P["lcd_muted"])

        bt = BTIconWidget()
        bt.setFixedSize(18, 18)

        rl.addWidget(self.time_lbl)
        rl.addSpacing(8)
        rl.addWidget(self.date_lbl)
        rl.addStretch()
        rl.addWidget(bt)
        ll.addWidget(r1)
        ll.addWidget(self._hline())

        # ── Row 2: big speed ──────────────────────────────────────────────────
        r2  = self._row()
        r2l = QVBoxLayout(r2)
        r2l.setContentsMargins(0, 2, 0, 2)
        r2l.setSpacing(0)

        self.spd_lbl = QLabel("0")
        self.spd_lbl.setAlignment(Qt.AlignCenter)
        self.spd_lbl.setFont(QFont("Courier New", 62, QFont.Bold))
        self.spd_lbl.setStyleSheet(f"color: {P['lcd_text']};")

        unit_lbl = QLabel("km/h")
        unit_lbl.setAlignment(Qt.AlignCenter)
        self._style(unit_lbl, 10, color=P["lcd_muted"])

        r2l.addWidget(self.spd_lbl)
        r2l.addWidget(unit_lbl)
        ll.addWidget(r2, 2)
        ll.addWidget(self._hline())

        # ── Rows 3-6: data rows ───────────────────────────────────────────────
        self.odo_val   = self._add_data_row(ll, "ODO",    "0.0 km")
        self.trip_val  = self._add_data_row(ll, "TRIP A", "0.0 km", alt=True)
        self.range_val = self._add_data_row(ll, None,     "300 km",
                                            icon="fuel",
                                            val_color=P["eco_green"])
        self.loc_val   = self._add_data_row(ll, None,     "-- --",
                                            alt=True, icon="loc",
                                            val_color=P["lcd_muted"],
                                            val_size=10)
        ll.addWidget(self._hline())

        # ── Status strip ──────────────────────────────────────────────────────
        self.strip = StatusStrip()
        ll.addWidget(self.strip)

        # Wire up bezel layers
        l2l.addWidget(lcd)
        l1l.addWidget(l2)
        root.addWidget(l1)

        # ── Timer-based refresh ───────────────────────────────────────────────
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_ui)
        self.refresh_timer.start(50)

    # ── Public refresh ────────────────────────────────────────────────────────

    def refresh_ui(self):
        now = datetime.now()
        self.time_lbl.setText(now.strftime("%I:%M %p").lstrip("0"))
        self.date_lbl.setText(now.strftime("%a %d %b"))

        self.spd_lbl.setText(str(int(getattr(self.state, "speed", 0))))
        self.odo_val.setText(f"{getattr(self.state, 'odometer', 0.0):.1f} km")
        self.trip_val.setText(f"{getattr(self.state, 'trip', 0.0):.1f} km")

        fuel = getattr(self.state, "fuel", 100.0)
        range_km = max(0.0, round(fuel * (300.0 / 100.0), 1))
        self.range_val.setText(f"{int(range_km)} km")

        try:
            loc = _Loc.city or "-- --"
        except Exception:
            loc = "-- --"
        self.loc_val.setText(loc)

        self.strip.update(
            getattr(self.state, "speed", 0),
            getattr(self.state, "temp",  42)
        )

    # ── Row builders ──────────────────────────────────────────────────────────

    def _add_data_row(self, parent_layout, label, value,
                      alt=False, icon=None,
                      val_color=None, val_size=15):
        if val_color is None:
            val_color = P["lcd_text"]

        row = QFrame()
        row.setFixedHeight(34)
        row.setStyleSheet(
            "QFrame { background: transparent; border: none; }"
            " QLabel { border: none; background: transparent; }")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(12, 0, 12, 0)

        if icon == "fuel":
            ic = FuelIconWidget()
            ic.setFixedSize(22, 22)
            rl.addWidget(ic)
            rl.addSpacing(4)
            lbl_w = QLabel("RANGE")
            self._style(lbl_w, 11, bold=True, color=P["lcd_muted"])
            rl.addWidget(lbl_w)
        elif icon == "loc":
            ic = LocIconWidget()
            ic.setFixedSize(22, 22)
            rl.addWidget(ic)
            rl.addSpacing(4)
            lbl_w = QLabel("LOCATION")
            self._style(lbl_w, 10, color=P["lcd_muted"])
            rl.addWidget(lbl_w)
        else:
            lbl_w = QLabel(label or "")
            self._style(lbl_w, 11, bold=True, color=P["lcd_muted"])
            rl.addWidget(lbl_w)

        rl.addStretch()

        val = QLabel(value)
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        val.setFont(QFont("Courier New", val_size, QFont.Bold))
        val.setStyleSheet(f"color: {val_color};")
        val.setObjectName("val")
        rl.addWidget(val)

        parent_layout.addWidget(row)
        parent_layout.addWidget(self._hline())
        return val

    # ── Style helpers ─────────────────────────────────────────────────────────

    def _frame(self, stylesheet: str, expanding: bool = False) -> QFrame:
        f = QFrame()
        f.setStyleSheet(stylesheet)
        if expanding:
            f.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return f

    def _style(self, lbl, size, bold=False, color=None):
        if color is None:
            color = P["lcd_text"]
        weight = QFont.Bold if bold else QFont.Normal
        lbl.setFont(QFont("Segoe UI", size, weight))
        lbl.setStyleSheet(f"color: {color};")

    def _row(self, h=None):
        f = QFrame()
        f.setStyleSheet(
            "QFrame { background: transparent; border: none; }"
            " QLabel { border: none; background: transparent; }")
        if h:
            f.setFixedHeight(h)
        return f

    def _hline(self):
        f = QFrame()
        f.setFixedHeight(1)
        f.setStyleSheet(f"background: {P['lcd_divider']}; border: none;")
        return f
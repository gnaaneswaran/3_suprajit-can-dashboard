from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt5.QtCore    import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui     import QPainter, QColor, QBrush, QPen, QFont, QRadialGradient, QLinearGradient


class ControlButton(QWidget):
    stateChanged = pyqtSignal(float)

    def __init__(self, label, icon, color, ramp_ms=1200, parent=None):
        super().__init__(parent)
        self.label    = label
        self.icon     = icon
        self.color    = QColor(color)
        self.ramp_ms  = ramp_ms
        self.intensity = 0.0
        self._held    = False
        self.setFixedSize(90, 90)
        self.setCursor(Qt.PointingHandCursor)

        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._ramp)

    def _ramp(self):
        if self._held:
            self.intensity = min(1.0, self.intensity + 30 / self.ramp_ms)
        else:
            self.intensity = max(0.0, self.intensity - 30 / (self.ramp_ms * 0.35))
        self.stateChanged.emit(self.intensity)
        self.update()
        if not self._held and self.intensity <= 0.0:
            self._timer.stop()

    def mousePressEvent(self, e):
        self._held = True
        self._timer.start()

    def mouseReleaseEvent(self, e):
        self._held = False

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy, r = 45, 45, 38

        # Outer glow
        if self.intensity > 0.05:
            glow = QRadialGradient(cx, cy, r + 18)
            gc = QColor(self.color)
            gc.setAlpha(int(100 * self.intensity))
            glow.setColorAt(0.0, gc)
            glow.setColorAt(1.0, QColor(0,0,0,0))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(glow))
            p.drawEllipse(cx-r-18, cy-r-18, (r+18)*2, (r+18)*2)

        # Base circle gradient
        grad = QRadialGradient(cx-8, cy-8, r*1.5)
        base_light = QColor("#1a2540")
        base_dark  = QColor("#060a14")
        grad.setColorAt(0.0, base_light)
        grad.setColorAt(1.0, base_dark)
        p.setBrush(QBrush(grad))

        # Border
        border = QColor(self.color)
        border.setAlpha(int(100 + 155 * self.intensity))
        p.setPen(QPen(border, 2.5))
        p.drawEllipse(cx-r, cy-r, r*2, r*2)

        # Active fill
        if self.intensity > 0:
            fill = QColor(self.color)
            fill.setAlpha(int(30 + 90 * self.intensity))
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(fill))
            p.drawEllipse(cx-r+3, cy-r+3, (r-3)*2, (r-3)*2)

        # Icon
        p.setPen(Qt.NoPen)
        icon_col = QColor(self.color)
        icon_col.setAlpha(int(160 + 95 * self.intensity))
        p.setPen(QPen(icon_col))
        p.setFont(QFont("Segoe UI Emoji", 18))
        p.drawText(0, 0, 90, 58, Qt.AlignCenter, self.icon)

        # Label
        p.setFont(QFont("Segoe UI", 7, QFont.Bold))
        lc = QColor("#94a3b8")
        if self.intensity > 0.1:
            lc = QColor(self.color)
        p.setPen(QPen(lc))
        p.drawText(0, 55, 90, 25, Qt.AlignCenter, self.label)
        p.end()


class ControlsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(110)
        self.setStyleSheet("background: transparent;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 20, 8, 20)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignTop)

        # Header
        hdr = QLabel("CONTROLS")
        hdr.setAlignment(Qt.AlignCenter)
        hdr.setStyleSheet("""
            color: #334155;
            font-size: 7px;
            font-weight: bold;
            letter-spacing: 2px;
            font-family: 'Segoe UI';
        """)
        lay.addWidget(hdr)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("color: #1e293b;")
        lay.addWidget(div)

        lay.addSpacing(8)

        # Throttle button
        self.throttle_btn = ControlButton("ACCEL", "🔼", "#22c55e", ramp_ms=1400)
        lay.addWidget(self.throttle_btn, alignment=Qt.AlignHCenter)

        lay.addSpacing(6)

        # Brake button
        self.brake_btn = ControlButton("BRAKE", "🔽", "#ef4444", ramp_ms=500)
        lay.addWidget(self.brake_btn, alignment=Qt.AlignHCenter)

        lay.addStretch()

        # Intensity bars
        lay.addWidget(self._bar_widget("ACCEL", "#22c55e", "throttle"))
        lay.addSpacing(6)
        lay.addWidget(self._bar_widget("BRAKE", "#ef4444", "brake"))

        lay.addSpacing(12)

        # Hint labels
        hint = QLabel("Hold to\nactivate")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color:#253350; font-size:8px; font-family:'Segoe UI';")
        lay.addWidget(hint)

    def _bar_widget(self, label, color, attr):
        w = QWidget()
        w.setFixedHeight(32)
        vl = QVBoxLayout(w)
        vl.setContentsMargins(0,0,0,0)
        vl.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{color}; font-size:7px; font-weight:bold; letter-spacing:1px;")
        lbl.setAlignment(Qt.AlignCenter)
        vl.addWidget(lbl)
        bar_lbl = QLabel("0%")
        bar_lbl.setAlignment(Qt.AlignCenter)
        bar_lbl.setStyleSheet(f"color:{color}; font-size:10px; font-weight:bold;")
        vl.addWidget(bar_lbl)
        setattr(self, f"{attr}_pct_lbl", bar_lbl)
        return w

    def update_indicators(self, throttle, brake):
        self.throttle_pct_lbl.setText(f"{int(throttle*100)}%")
        self.brake_pct_lbl.setText(f"{int(brake*100)}%")

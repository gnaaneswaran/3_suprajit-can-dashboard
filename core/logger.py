"""
core/logger.py
───────────────
Timestamped CAN frame logger.

Writes decoded frames to a rotating CSV log file.
Designed to be called from main_window._tick() with zero UI impact.

Features
--------
- CSV output: timestamp, can_id, dlc, raw_data, decoded_signals
- Configurable max file size with auto-rotation
- start() / stop() control — can be toggled from UI later
- Thread-safe write queue (won't block the 80ms CAN timer)

Usage
-----
    from core.logger import can_logger

    can_logger.start()                     # begin logging
    can_logger.log(frame, signals)         # call in _tick()
    can_logger.stop()                      # flush and close

File location: logs/can_YYYYMMDD_HHMMSS.csv
"""

import os
import csv
import time
import queue
import threading
from datetime import datetime

from core.can_frame import CANFrame


class CANLogger:

    # Max rows before rotating to a new file
    MAX_ROWS = 50_000

    def __init__(self, log_dir: str = "logs"):
        self._log_dir    = log_dir
        self._queue      = queue.Queue(maxsize=2000)
        self._running    = False
        self._worker     = None
        self._file       = None
        self._writer     = None
        self._row_count  = 0
        self._file_path  = ""

    # ── Public control ────────────────────────────────────────────────────────

    def start(self):
        """Start logging. Creates log directory and opens first file."""
        if self._running:
            return
        os.makedirs(self._log_dir, exist_ok=True)
        self._running = True
        self._open_new_file()
        self._worker = threading.Thread(
            target=self._write_loop,
            daemon=True,
            name="CANLogger"
        )
        self._worker.start()
        print(f"[CANLogger] Started → {self._file_path}")

    def stop(self):
        """Stop logging, flush remaining queue entries, close file."""
        if not self._running:
            return
        self._running = False
        self._queue.put(None)          # sentinel to unblock worker
        if self._worker:
            self._worker.join(timeout=3.0)
        self._close_file()
        print(f"[CANLogger] Stopped. {self._row_count} rows written.")

    def log(self, frame: CANFrame, signals: dict = None):
        """
        Enqueue a frame for logging. Non-blocking — drops if queue is full.

        Parameters
        ----------
        frame   : CANFrame
        signals : dict[str, float]  — decoded signal values (optional)
        """
        if not self._running:
            return
        try:
            self._queue.put_nowait((frame, signals or {}))
        except queue.Full:
            pass   # drop — never block the CAN timer

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def current_file(self) -> str:
        return self._file_path

    # ── Internal ──────────────────────────────────────────────────────────────

    def _open_new_file(self):
        self._close_file()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._file_path = os.path.join(self._log_dir, f"can_{ts}.csv")
        self._file      = open(self._file_path, "w", newline="", encoding="utf-8")
        self._writer    = csv.writer(self._file)
        self._writer.writerow([
            "timestamp_s", "can_id_hex", "dlc",
            "data_hex", "signals_json"
        ])
        self._row_count = 0

    def _close_file(self):
        if self._file:
            try:
                self._file.flush()
                self._file.close()
            except Exception:
                pass
            self._file   = None
            self._writer = None

    def _write_loop(self):
        """Worker thread — drains queue and writes to CSV."""
        while True:
            try:
                item = self._queue.get(timeout=1.0)
            except queue.Empty:
                if not self._running:
                    break
                continue

            if item is None:   # sentinel
                break

            frame, signals = item
            self._write_row(frame, signals)
            self._queue.task_done()

        # Drain remaining items after stop()
        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                if item is not None:
                    frame, signals = item
                    self._write_row(frame, signals)
            except queue.Empty:
                break

        self._close_file()

    def _write_row(self, frame: CANFrame, signals: dict):
        if self._writer is None:
            return

        # Rotate if needed
        if self._row_count >= self.MAX_ROWS:
            self._open_new_file()

        data_hex = " ".join(f"{b:02X}" for b in frame.data)

        # Compact signals string: "speed=72.0,fuel=84.0"
        sig_str = ",".join(
            f"{k}={v:.2f}" for k, v in signals.items()
        ) if signals else ""

        self._writer.writerow([
            f"{frame.timestamp:.3f}",
            hex(frame.can_id),
            frame.dlc,
            data_hex,
            sig_str,
        ])
        self._row_count += 1

        # Flush every 100 rows to avoid data loss without killing performance
        if self._row_count % 100 == 0:
            self._file.flush()


# ── Singleton ─────────────────────────────────────────────────────────────────
can_logger = CANLogger(log_dir="logs")
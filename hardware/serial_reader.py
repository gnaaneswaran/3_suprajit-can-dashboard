"""
ui/oem_analog/core/serial_reader.py
─────────────────────────────────────
Reads potentiometer value from ESP32 over USB Serial.
Protocol: ESP32 sends "POT:<0-4095>\n" at 115200 baud.

Exposes:
  .value      → raw ADC int (0–4095)
  .percent    → float 0–100 mapped from ADC
  .ax         → always 0.0 (stub)
  .connected  → bool
"""

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread


class SerialReader(QThread):

    def __init__(self, port: str = None, baud: int = 115200):
        super().__init__()
        self.value     = 0
        self.percent   = 0.0
        self.ax        = 0.0
        self.connected = False
        self.serial    = None

        self._port    = port or "COM8"
        self._baud    = baud
        self._running = True

        self.daemon = True
        self.start()

    def _auto_detect(self) -> str:
        keywords = [
            "CP210", "CH340", "CH341", "FTDI",
            "ESP32", "Silicon Labs", "USB Serial",
            "USB-SERIAL", "USB to UART"
        ]
        for p in serial.tools.list_ports.comports():
            desc = (p.description or "") + (p.manufacturer or "")
            if any(k.lower() in desc.lower() for k in keywords):
                print(f"[SerialReader] Auto-detected: {p.device} ({p.description})")
                return p.device
        print("[SerialReader] No ESP32 found — keyboard fallback active")
        return None

    def run(self):
        if not self._port:
            return

        try:
            self.serial    = serial.Serial(self._port, self._baud, timeout=1)
            self.connected = True
            print(f"[SerialReader] Connected on {self._port} @ {self._baud}")
        except Exception as e:
            print(f"[SerialReader] Failed to open {self._port}: {e}")
            return

        while self._running:
            try:
                line = self.serial.readline().decode("utf-8", errors="ignore").strip()

                if line.startswith("POT:"):
                    adc = int(line[4:])
                    adc = max(0, min(4095, adc))

                    if adc < 150:
                        adc = 0

                    self.value   = adc
                    self.percent = (adc / 4095.0) * 100.0

            except (ValueError, UnicodeDecodeError):
                pass
            except serial.SerialException as e:
                print(f"[SerialReader] Serial error: {e}")
                self.connected = False
                break
            except Exception as e:
                print(f"[SerialReader] Unexpected: {e}")
                break

        self.connected = False

    def stop(self):
        self._running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.wait(1000)
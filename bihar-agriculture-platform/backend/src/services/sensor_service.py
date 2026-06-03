from __future__ import annotations

import json
import os
import re
import time
from typing import Any

NPK_LINE_RE = re.compile(r"NPK_JSON:\s*(\{.*\})", re.IGNORECASE)

DEFAULT_BAUD = int(os.getenv("NPK_SERIAL_BAUD", "9600"))
DEFAULT_PORT = os.getenv("NPK_SERIAL_PORT", "").strip() or None
MGKG_TO_KGHA = float(os.getenv("NPK_MGKG_TO_KGHA", "2.0"))
READ_TIMEOUT_S = float(os.getenv("NPK_READ_TIMEOUT_S", "4.0"))


def _serial_available() -> bool:
    try:
        import serial  # noqa: F401
        return True
    except ImportError:
        return False


def list_serial_ports() -> list[dict[str, str]]:
    if not _serial_available():
        return []
    import serial.tools.list_ports

    return [
        {"device": p.device, "description": p.description or ""}
        for p in serial.tools.list_ports.comports()
    ]


def mgkg_to_kgha(n: float, p: float, k: float, factor: float | None = None) -> dict[str, float]:
    f = MGKG_TO_KGHA if factor is None else factor
    return {
        "n": round(n * f, 1),
        "p": round(p * f, 1),
        "k": round(k * f, 1),
    }


def _parse_npk_line(line: str) -> dict[str, Any] | None:
    line = line.strip()
    if not line:
        return None
    m = NPK_LINE_RE.search(line)
    payload = m.group(1) if m else (line if line.startswith("{") else None)
    if not payload:
        return None
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None
    n = float(data.get("n", 0))
    p = float(data.get("p", 0))
    k = float(data.get("k", 0))
    return {
        "raw_mgkg": {"n": n, "p": p, "k": k},
        "unit": str(data.get("unit", "mg/kg")),
        "soil_npk_kgha": mgkg_to_kgha(n, p, k),
    }


def read_npk_from_serial(
    port: str | None = None,
    baud: int | None = None,
    *,
    trigger_read: bool = True,
) -> dict[str, Any]:
    """
    Open the Arduino COM port, optionally send READ, wait for NPK_JSON line.
    """
    if not _serial_available():
        return {
            "ok": False,
            "error": "pyserial is not installed. Run: pip install pyserial",
        }

    import serial

    device = (port or DEFAULT_PORT or "").strip()
    if not device:
        ports = list_serial_ports()
        if not ports:
            return {"ok": False, "error": "No serial ports found. Plug in the Arduino USB cable."}
        device = ports[0]["device"]

    rate = baud or DEFAULT_BAUD
    deadline = time.time() + READ_TIMEOUT_S

    try:
        with serial.Serial(device, rate, timeout=0.2) as ser:
            time.sleep(0.3)
            ser.reset_input_buffer()
            if trigger_read:
                ser.write(b"READ\n")
                ser.flush()
            saw_wizard_firmware = False
            while time.time() < deadline:
                raw = ser.readline()
                if not raw:
                    continue
                try:
                    line = raw.decode("utf-8", errors="ignore")
                except Exception:
                    continue
                if "DIALOG INTERFACE" in line or "Enter Target Crop Type" in line:
                    saw_wizard_firmware = True
                if "NPK_ERROR" in line:
                    return {"ok": False, "error": line.strip(), "port": device}
                parsed = _parse_npk_line(line)
                if parsed:
                    return {
                        "ok": True,
                        "port": device,
                        "baud": rate,
                        "conversion_factor": MGKG_TO_KGHA,
                        **parsed,
                    }
    except serial.SerialException as exc:
        return {"ok": False, "error": str(exc), "port": device}

    if saw_wizard_firmware:
        return {
            "ok": False,
            "error": (
                "Arduino is running the old wizard sketch, not the web bridge. "
                "Upload hardware/npk_sensor/npk_sensor_web.ino in Arduino IDE, "
                "then close Serial Monitor and try again."
            ),
            "port": device,
        }

    return {
        "ok": False,
        "error": "Timed out waiting for NPK_JSON from sensor. Check wiring, 12V supply, and firmware.",
        "port": device,
    }

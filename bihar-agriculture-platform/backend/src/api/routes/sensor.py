from __future__ import annotations

import os

from fastapi import APIRouter, Query

from src.services.sensor_service import (
    MGKG_TO_KGHA,
    list_serial_ports,
    read_npk_from_serial,
)

router = APIRouter()


@router.get("/status")
def sensor_status():
    port = os.getenv("NPK_SERIAL_PORT", "").strip() or None
    ports = list_serial_ports()
    return {
        "pyserial_available": bool(ports) or port is not None,
        "configured_port": port,
        "conversion_factor_mgkg_to_kgha": MGKG_TO_KGHA,
        "ports": ports,
    }


@router.get("/ports")
def sensor_ports():
    return {"ports": list_serial_ports()}


@router.post("/read")
def sensor_read(
    port: str | None = Query(None, description="COM port, e.g. COM5"),
    baud: int | None = Query(None, description="Serial baud rate (default 9600)"),
):
    """
    Read live N, P, K from the Arduino NPK sensor over USB serial.
    Requires npk_sensor_web.ino flashed and NPK_SERIAL_PORT set or port query param.
    """
    result = read_npk_from_serial(port=port, baud=baud)
    return result

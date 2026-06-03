# NPK soil sensor (Modbus RS485) + Smart Crop Advisor

## Hardware

| Arduino | MAX485 / RS485 |
|---------|----------------|
| Pin 10  | RO (receiver)  |
| Pin 11  | DI (driver)    |
| Pin 3   | DE + RE        |

Upload **`npk_sensor_web.ino`** for website integration (JSON over USB at 9600 baud).

Your original sketch with crop wizard + fertilizer math can stay on the board when you are testing offline; use the web sketch when connecting to the portal.

## Website integration (two ways)

### A) Browser USB (recommended — Chrome / Edge)

1. Flash `npk_sensor_web.ino`
2. Open **Crop Recommendation** on the portal
3. Click **Connect NPK sensor** → choose the Arduino COM port
4. Click **Read from sensor** — N, P, K fields fill automatically
5. Click **Generate recommendation**

### B) Backend serial bridge (Python)

1. Set environment variable before starting the backend:
   ```text
   NPK_SERIAL_PORT=COM5
   NPK_SERIAL_BAUD=9600
   NPK_MGKG_TO_KGHA=2.0
   ```
2. Use **Read from sensor (via server)** on the crop page

## Units

The sensor reports **mg/kg** (same as ppm). The crop model expects **kg/ha** (like the training dataset).

Default conversion: `kg/ha = mg/kg × 2.0` (adjust `NPK_MGKG_TO_KGHA` after comparing with a lab soil test).

## Calibration

Edit `c_N`, `m_N`, `c_P`, `m_P`, `c_K`, `m_K` in the `.ino` file to match your sensor module and local soil tests.

# 3D Models (STEP)

| File | Part | Source |
|---|---|---|
| ESP32-S3-WROOM-1.STEP | ESP32-S3-WROOM-1 module | Espressif official kicad-libraries (PCM addon) |
| ESP32-S3-WROOM-1U.STEP | U.FL variant | same |
| ESP32-C6-WROOM-1.STEP | ESP32-C6-WROOM-1 module | same |
| ESP32-C6-WROOM-1U.STEP | U.FL variant | same |
| ESP32-C3-MINI-1.STEP | ESP32-C3-MINI-1 module | same |
| ESP32-C3-MINI-1U.STEP | U.FL variant | same |
| Sensirion_SCD4x.step | SCD41 CO2 sensor | Seeed/Sensirion official STEP |

The isometric 3D renders in `renders/*_3d.png` are produced from the actual
board placement data by `tools/render3d.py` using these models' dimensions
(module 3.1 mm, SCD41 6.5 mm, USB-C 3.2 mm, headers 8.5 mm, LEDs 1.6-1.8 mm).

Other passives/connectors: KiCad built-in 3D packages (R_0603, C_0603, SOT-23-5/6,
SOT-223) cover the rest; LCSC part pages provide SamacSys STEP for
TYPE-C-31-M-12, SK6812MINI-E, WS2812B-V5 (free account download).

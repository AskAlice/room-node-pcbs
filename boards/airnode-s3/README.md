# AirNode-S3 (rev A, 2026-08)

Air-quality room node on a 70 x 50 mm 2-layer SMD PCB: CO2 (SCD41), particulate
matter (PMS5003), VOC (SGP40), temperature/humidity (SHT40), ESP32-S3 module,
USB-C power, and a 3-LED air-quality "traffic light".

## Overview

| Block | Parts | Notes |
|---|---|---|
| MCU | U1 ESP32-S3-WROOM-1-N8R2 | Antenna at TOP edge; keepout y in [0,10] mm: no copper, vias or parts (B.Cu GND zone fill removed under antenna in KiCad) |
| Power in | J1 TYPE-C-31-M-12, R1/R2 5.1k (CC1/CC2), D1 USBLC6-2SC6 | 5 V only, no USB data |
| 3V3 rail | U2 AMS1117-3.3 (SOT-223) + C1/C2 10 uF | Must supply SCD41 heater pulses + module peaks (~800 mA budget); **thermal note**: SOT-223 tab on copper pour with thermal vias (see vias at U2) |
| CO2 | U3 SCD41 (LGA-20, 10.1x10.1) + C5 100 nF | Center-left, clearance around for airflow |
| VOC + T/RH | U4 SGP40 (DFN-6), U5 SHT40 (DFN-4) + C6/C7 | Grouped right of SCD41; SGP40 VOC algorithm needs SHT40 RH compensation |
| PM sensor | J2 8-pin 1.25 mm header | **PMS5003 is 5 V powered** (pin 1 = 5 V direct from USB rail, not via LDO); UART is 3.3 V logic on RX/TX |
| Status LEDs | D2-D4 SK6812MINI-E + C8-C10 100 nF, R3 470 R | Top-right, outside antenna keepout; data on IO12 via R3 |
| UI / debug | SW1 EN, SW2 BOOT, J3 UART 1x4 | R4/R5 10k pull-ups (EN, IO0) |

Track widths: 5 V rail 1.0 mm, 3V3 0.8 mm, I2C/UART/LED 0.4 mm. B.Cu GND zone
over the whole board with stitching vias (none in the antenna keepout).

I2C bus: IO8 = SDA, IO9 = SCL, R6/R7 4.7k pull-ups. Addresses: SCD41 0x62,
SGP40 0x59, SHT40 0x44. UART2: IO16 = RX2, IO17 = TX2 -> PMS5003 (9600 8N1).

## Airflow / cutout note

Keep the area around SCD41/SGP40/SHT40 free of tall parts (silk note
"AIRFLOW - KEEP CLEAR"). For enclosure designs, add intake/exhaust slots aligned
with the sensor cluster, and route the PMS5003 so its inlet draws outside air.
Optionally add a board cutout slot under/beside the SCD41 (offset from the LDO
and module) to reduce self-heating and improve CO2 response time.

## SCD41 reflow / handling warning

The SCD41 is a **moisture- and contamination-sensitive** photoacoustic NDIR
sensor (MSL-class device). Observe Sensirion's handling guide:
- Reflow **once only**, standard lead-free profile, peak <= 245 C, no wave solder.
- Do **not** wash the board after reflow (no solvents/ultrasonic); use no-clean flux.
- Avoid VOC outgassing sources (conformal coating, adhesives, some soldermask
  residues) near the sensor aperture; never tape over the aperture.
- Store in ESD/dry bag; bake per MSL if floor life is exceeded.

## BOM

| Ref | Part | Value | Footprint | LCSC | Datasheet |
|---|---|---|---|---|---|
| U1 | ESP32-S3-WROOM-1-N8R2 | 8 MB flash, 2 MB PSRAM | 18x25.5 castellated | C2913204 | https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf |
| U2 | AMS1117-3.3 | LDO 3.3 V 1 A | SOT-223 | C6186 | http://www.advanced-monolithic.com/pdf/ds1117.pdf |
| U3 | SCD41-D-R1 | CO2 + T/RH (photoacoustic NDIR) | LGA-20 10.1x10.1 | C3659362 | https://sensirion.com/resource/datasheet/scd41 |
| U4 | SGP40-D-R4 | VOC | DFN-6 | C2874215 | https://sensirion.com/resource/datasheet/sgp40 |
| U5 | SHT40-AD1B-R2 | Temp/RH | DFN-4 | C2909890 | https://sensirion.com/resource/datasheet/sht4x |
| J1 | TYPE-C-31-M-12 | USB-C 16p mid-mount | SMD | C165948 | https://www.lcsc.com/datasheet/lcsc_datasheet_2205311830_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf |
| J2 | 8-pin 1.25 mm PicoBlade header | to PMS5003 cable | SMD | - (PMS5003 module) | https://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf |
| J3 | 1x4 2.54 mm header | UART debug | SMD/TH | - | - |
| D1 | USBLC6-2SC6 | USB ESD | SOT-23-6 | C7519 | https://www.st.com/resource/en/datasheet/usblc6-2.pdf |
| D2-D4 | SK6812MINI-E | RGB LED 3535 (5 V) | 3535 | C5149201 | https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf |
| SW1/SW2 | Tact switch | EN / BOOT | 4.6x4.6 | C720477 | - |
| R1/R2 | Resistor 0603 | 5.1k (USB-C CC) | 0603 | - | - |
| R3 | Resistor 0603 | 470R (LED data) | 0603 | - | - |
| R4/R5 | Resistor 0603 | 10k (EN/IO0 pull-up) | 0603 | C25804 | - |
| R6/R7 | Resistor 0603 | 4.7k (I2C pull-up) | 0603 | - | - |
| C1/C2 | Capacitor 0805 | 10 uF | 0805 | C19702 | - |
| C3-C10 | Capacitor 0603 | 100 nF | 0603 | C14663 | - |

## 3D model sources

- ESP32-S3-WROOM-1: espressif/kicad-libraries (STEP + WRL) or SnapMagic
- SCD41 / SGP40 / SHT40: Sensirion website CAD download (STEP), or SnapMagic
- TYPE-C-31-M-12, AMS1117 SOT-223, USBLC6 SOT-23-6: LCSC part pages (STEP)
  / SnapMagic
- SK6812MINI-E: SnapMagic / Adafruit CAD repo
- PMS5003: GrabCAD community STEP models

## Firmware

See `firmware/airnode-s3.yaml` (ESPHome).

## Rebuild

```
python3 boards/airnode-s3/build.py   # writes .kicad_pcb/.kicad_sch/.kicad_pro + renders
```

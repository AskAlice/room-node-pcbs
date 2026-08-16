# RoomNode-C3-Mini (rev A, 2026-08)

Ultra-compact budget room node, 40 x 35 mm, 2-layer, all-SMD (except pin
headers). Built around the ESP32-C3-MINI-1-N4 module with USB-C power/data,
SHT40 temperature/humidity, analog light sensor, PIR motion input, one
SK6812MINI-E addressable RGB LED, EN/BOOT buttons and a UART header.

Regenerate files / renders:

```
python3 build.py    # writes .kicad_pcb/.kicad_sch/.kicad_pro + renders/
```

## Features / pin map

| Function | GPIO / net |
|---|---|
| I2C SDA / SCL (SHT40 @ 0x44, 4.7k pull-ups R6/R7) | GPIO6 / GPIO7 |
| SK6812MINI-E data (via R3 470R) | GPIO10 |
| ALS-PT19 analog light (R8 10k load to GND) | GPIO3 (ADC1_CH3) |
| PIR (AM312) via J3 | GPIO4 |
| BOOT button SW2 | GPIO9 |
| EN button SW1 / pull-up R4 | EN |
| UART header J2 (3V3/TX/RX/GND) | GPIO20(RX0)/GPIO21(TX0) at module edge pads |
| USB D+/D- (via D1 ESD) | GPIO18/19 |

## Antenna keepout (important)

The ESP32-C3-MINI-1 antenna faces the TOP board edge. The region
**y = 0..8 mm across the full board width carries NO copper on any layer**
(no tracks, no vias, no zone fill, no parts) per Espressif guidelines
(>=15 mm clearance preferred; the module overhangs the keepout). The B.Cu GND
zone polygon is clipped at y = 8.5 mm. Silkscreen text in the keepout is ink
only and is acceptable.

## BOM (budget, LCSC)

| Ref | Part | LCSC | ~Qty cost (USD) |
|---|---|---|---|
| U1 | ESP32-C3-MINI-1-N4 | C2838502 | $1.60 |
| U2 | ME6211C33M5G-N LDO 3.3V SOT-23-5 | C82942 | $0.04 |
| U3 | SHT40-AD1B-R2 | C2909890 | $1.30 |
| U4 | ALS-PT19-315C-L177-TR 0603 | (C146220 alt.) | $0.10 |
| D1 | USBLC6-2SC6 SOT-23-6 | C7519 | $0.10 |
| D2 | SK6812MINI-E 3535 | C5149201 | $0.10 |
| J1 | USB-C TYPE-C-31-M-12 16p mid-mount | C165948 | $0.10 |
| SW1/SW2 | Tact button 3x4 | C720477 | $0.04 |
| R1/R2 | 5.1k 0603 | ~C23186 | $0.01 |
| R3 | 470R 0603 | ~C23138 | $0.01 |
| R4/R5/R8 | 10k 0603 | C25804 | $0.01 |
| R6/R7 | 4.7k 0603 | ~C23162 | $0.01 |
| C1/C2 | 10uF 0805 | C19702 | $0.02 |
| C3/C4/C5 | 100nF 0603 | C14663 | $0.01 |
| J2/J3 | Pin headers 1x4 + 1x3 2.54mm | generic | $0.05 |
| PIR | AM312 module (AS312 sensor C90465) | module | $0.60 |

**Cheapest build estimate: ~$4.10 components + ~$2 PCB (JLCPCB 5pcs/2-layer)
=> roughly $5-6 per node** at small quantity. Drop D1 (ESD) and the PIR to
save another ~$0.70.

## Datasheets

- ESP32-C3-MINI-1: https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf
- ME6211: https://datasheet.lcsc.com/szlcsc/Nanjing-Micro-One-Elec-ME6211C33M5G-N_C82942.pdf
- SHT40: https://sensirion.com/resource/datasheet/sht4x
- ALS-PT19: https://cdn.sparkfun.com/datasheets/Components/General%20IC/ALS-PT19-315C-L177-TR_datasheet.pdf
- USBLC6-2SC6: https://www.st.com/resource/en/datasheet/usblc6-2.pdf
- SK6812MINI-E: https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf
- TYPE-C-31-M-12: https://www.lcsc.com/datasheet/lcsc_datasheet_2205311830_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf

## 3D model sources

- ESP32-C3-MINI-1 STEP/WRL: https://github.com/espressif/kicad-libraries
  (modules/ESP32-C3-MINI-1.step) — assign to footprint U1.
- USB-C TYPE-C-31-M-12, SOT-23-5/6, 0603/0805 passives, tact switch:
  official KiCad 8 3D packages (kicad-packages3D) or SnapMagic/ComponentSearchEngine.
- SK6812MINI-E / SHT40 DFN-4: SnapMagic or GrabCAD community models.

## Design notes

- 2-layer, 1.6 mm, track widths 0.4 mm (signal) / 0.8 mm (power), vias
  0.8/0.4 mm, single B.Cu GND zone (clipped at the antenna keepout).
- ME6211 EN tied to VIN; C1/C2 10uF on output/input, C3 100nF at the module
  3V3 pad, C4/C5 decoupling for module/LED.
- CC1/CC2 5.1k pulldowns (R1/R2) for USB-C 5V detection; USBLC6-2SC6 (D1)
  protects D+/D-.
- Firmware: `firmware/roomnode-c3-mini.yaml` (ESPHome).

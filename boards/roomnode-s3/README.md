# RoomNode-S3 (rev A)

Flagship multi-function room node: ESP32-S3 + environmental sensors (temp/RH, VOC,
lux), mmWave presence, PIR motion, and 4x addressable RGB LEDs — all on a 65 x 50 mm
2-layer SMD board powered/programmed via USB-C. Designed for ESPHome.

Generated with `tools/kicad_gen.py` — run `python3 build.py` in this folder to
regenerate `roomnode-s3.kicad_pcb`, `roomnode-s3.kicad_sch`, `roomnode-s3.kicad_pro`
and the PNG renders in `../../renders/`.

## Features
- ESP32-S3-WROOM-1-N8R2 (8 MB flash, 2 MB PSRAM), PCB antenna overhanging top edge
- USB-C (5 V in), ME6211 3.3 V LDO, ESD protection, 5.1k CC pull-downs
- SHT40 (temp/RH, 0x44), SGP40 (VOC, 0x59), BH1750 (lux, 0x23) on I2C (GPIO8 SDA / GPIO9 SCL, 4.7k pull-ups)
- HLK-LD2450 mmWave presence header (J2, 5 V + UART GPIO17/18)
- AM312 PIR header (J3, GPIO16)
- 4x SK6812MINI-E addressable RGB LEDs (GPIO4, 470R series, 100 nF each)
- EN + BOOT buttons, 1x4 UART header (J4)

## BOM
| Ref | Part | Value | Footprint | LCSC |
|---|---|---|---|---|
| U1 | ESP32-S3-WROOM-1-N8R2 | MCU module | 18x25.5 castellated | C2913204 |
| U2 | ME6211C33M5G-N | LDO 3.3V 500mA | SOT-23-5 | C82942 |
| U3 | SHT40-AD1B-R2 | Temp/RH | DFN-4 | C2909890 |
| U4 | SGP40-D-R4 | VOC | DFN-6 | C2874215 |
| U5 | BH1750FVI-TR | Lux | WSOF6I | C2071 |
| J1 | TYPE-C-31-M-12 | USB-C 16p mid-mount | SMD | C165948 |
| J2 | HLK-LD2450 | mmWave module | 1x4 2.54 header | module |
| J3 | AM312 | PIR sensor | 1x3 2.54 header | C90465 (AS312) |
| J4 | pin header 1x4 | UART (GND,3V3,TX,RX) | 1x4 2.54 | - |
| D1 | USBLC6-2SC6 | USB ESD | SOT-23-6 | C7519 |
| D2-D5 | SK6812MINI-E | RGB LED | 3535 | C5149201 |
| SW1/SW2 | tact 3x4 | EN / BOOT | 3x4 SMD | C720477 |
| R1/R2 | 5.1k | CC1/CC2 pull-down | 0603 | C25804 series |
| R3 | 470R | LED DIN series | 0603 | - |
| R4/R5 | 10k | EN / IO0 pull-up | 0603 | C25804 |
| R6/R7 | 4.7k | I2C SDA/SCL pull-up | 0603 | - |
| C1/C2 | 10uF | LDO in/out | 0805 | C19702 |
| C3/C4 | 100nF | module decoupling | 0603 | C14663 |
| C6-C9 | 100nF | LED decoupling | 0603 | C14663 |

## Datasheets
- ESP32-S3-WROOM-1: https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- SHT40: https://sensirion.com/resource/datasheet/sht4x
- SGP40: https://sensirion.com/resource/datasheet/sgp40
- BH1750FVI: https://fscdn.rohm.com/en/products/databook/datasheet/ic/sensor/light/bh1750fvi-e.pdf
- LD2450: https://h.hlktech.com/Mobile/download/fdetail/294.html
- ME6211: https://datasheet.lcsc.com/szlcsc/Nanjing-Micro-One-Elec-ME6211C33M5G-N_C82942.pdf
- TYPE-C-31-M-12: https://www.lcsc.com/datasheet/lcsc_datasheet_2205311830_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf
- USBLC6-2SC6: https://www.st.com/resource/en/datasheet/usblc6-2.pdf
- SK6812MINI-E: https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf

## 3D model sources
- ESP32-S3-WROOM-1: https://github.com/espressif/kicad-libraries (STEP + WRL) or SnapMagic (C2913204)
- Most LCSC parts: SnapMagic (snapmagic.com) or componentsearchengine.com, searched by LCSC part number
- USB-C TYPE-C-31-M-12: SnapMagic / LCSC ECAD model C165948

## Antenna keep-out
The module is placed with its antenna end at the TOP board edge, antenna overhanging.
Per Espressif guidelines (>=15 mm clearance, no copper under antenna): **no F.Cu zone
is used**; the GND zone is on B.Cu only, and all tracks/pads are kept out of the
y = 0..10 mm strip at the top of the board (marked "ANTENNA KEEP-OUT" in silkscreen).

## JLCPCB order notes
- 2-layer, 1.6 mm, HASL lead-free, any color; 65 x 50 mm fits the cheap small-board tier
- All SMD parts are on the TOP side (single-sided assembly = lower cost); headers can be hand-soldered or ordered as THT assembly
- Use JLCPCB parts numbers = LCSC numbers above; confirm TYPE-C-31-M-12 and SK6812MINI-E stock before ordering
- Gerber/drill export: F.Cu, B.Cu, F/B.Mask, F.SilkS, Edge.Cuts; no plated slots required

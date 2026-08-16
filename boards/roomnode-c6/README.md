# RoomNode-C6 (rev A, 2026-08)

WiFi 6 + BLE 5.3 + 802.15.4 (Thread/Zigbee) room-sensor node built around the
ESP32-C6-WROOM-1-N8. Primary role: **BLE presence tracker** (phone/beacon RSSI
tracking via `esp32_ble_tracker` / `ble_presence` in ESPHome) with full
environmental sensing. The C6's 802.15.4 radio also makes the node
**Thread border-router / Zigbee capable** (e.g. OpenThread Border Router or
Zigbee coordinator firmware), and WiFi 6 target-wake-time keeps idle power low
for dense deployments.

Board: 55 x 45 mm, 2-layer, all-SMD, single-sided assembly. USB-C powered
(5 V -> ME6211 3.3 V @ 500 mA).

## Features
- ESP32-C6-WROOM-1-N8 (8 MB flash): WiFi 6, BLE 5.3 (long range / 2 Mbps), 802.15.4
- SHT31-DIS-B temperature/humidity (I2C 0x44, left edge, away from module heat)
- BH1750FVI ambient light (I2C 0x23, top-left, outside RF keepout)
- BME280 pressure/temp/RH (I2C 0x76, right-mid)
- AM312 PIR motion header (J2, right edge, 5 V / OUT / GND, 3.3 V logic out)
- 2x WS2812B-V5 status/presence RGB LEDs (bottom corners, daisy-chained, 470 ohm DIN)
- USB-C with 5.1k CC resistors (R1/R2) + USBLC6-2SC6 ESD (D1)
- EN + BOOT tactile switches, UART 1x4 header (J3), expansion 1x6 header
  (J4: 3V3, GND, SDA, SCL, GPIO20, GPIO21)

## Antenna keepout (IMPORTANT)
The ESP32-C6 antenna end faces the TOP board edge. The region **y in [0, 10] mm
is a full keepout: no copper, pads, tracks or vias on ANY layer**. The B.Cu GND
zone polygon is clipped at y = 10 mm in `roomnode-c6.kicad_pcb`; if you edit the
board in KiCad, keep the zone cutout and do not route into the keepout
(Espressif recommends >= 15 mm clearance around the antenna; with the module
overhanging the design edge region, the 10 mm board keepout plus module
overhang satisfies this). Silkscreen in the keepout is ink only and is fine.

## BOM
| Ref | Part | Value / Note | LCSC |
|---|---|---|---|
| U1 | ESP32-C6-WROOM-1-N8 | WiFi6/BLE5.3/802.15.4 module | C5366877 |
| U2 | ME6211C33M5G-N | 3.3 V 500 mA LDO, SOT-23-5 | C82942 |
| U3 | SHT31-DIS-B | Temp/RH, DFN-8, 0x44 | C80862 |
| U4 | BH1750FVI-TR | Lux, WSOF6I, 0x23 | C2071 |
| U5 | BME280 | T/RH/P, LGA-8, 0x76 | C92489 |
| J1 | TYPE-C-31-M-12 | USB-C 16p mid-mount | C165948 |
| D1 | USBLC6-2SC6 | USB ESD, SOT-23-6 | C7519 |
| D2,D3 | WS2812B-V5 | RGB LED 5050 (5 V) | C2846931 |
| J2 | AM312/AS312 header | PIR motion sensor (module) | C90465 |
| R1,R2 | 5.1k 0603 | USB-C CC1/CC2 pull-downs | - |
| R3 | 470R 0603 | LED DIN series | - |
| R4,R5 | 10k 0603 | EN / IO9 pull-ups | C25804 |
| R6,R7 | 4.7k 0603 | I2C SDA/SCL pull-ups | - |
| C1,C2 | 10uF 0805 | LDO in/out | C19702 |
| C3-C6 | 100nF 0603 | module + LED decoupling | C14663 |
| SW1,SW2 | Tact 3x4 | EN / BOOT | C720477 |
| J3 | 1x4 2.54 header | UART (3V3/TX/RX/GND) | - |
| J4 | 1x6 2.54 header | Expansion | - |

## Datasheets
- ESP32-C6-WROOM-1: https://www.espressif.com/sites/default/files/documentation/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf
- ME6211: https://datasheet.lcsc.com/szlcsc/Nanjing-Micro-One-Elec-ME6211C33M5G-N_C82942.pdf
- SHT31: https://sensirion.com/resource/datasheet/sht3x
- BH1750: https://fscdn.rohm.com/en/products/databook/datasheet/ic/sensor/light/bh1750fvi-e.pdf
- BME280: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
- USB-C-31-M-12: https://www.lcsc.com/datasheet/lcsc_datasheet_2205311830_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf
- USBLC6-2SC6: https://www.st.com/resource/en/datasheet/usblc6-2.pdf
- WS2812B-V5: https://datasheet.lcsc.com/lcsc/2304261807_Worldsemi-WS2812B-V5_C2846931.pdf

## 3D model sources
- ESP32-C6-WROOM-1: espressif/kicad-libraries (STEP + WRL)
- USB-C / passives / SOT / LEDs: KiCad 8 official 3D packages or SnapMagic
- SHT31 / BME280 / BH1750: SnapMagic / GrabCAD (DFN-8 2.5x2.5, LGA-8 2.5x2.5, WSOF6I)

## Files
- `build.py` - regenerates `roomnode-c6.kicad_pcb/.kicad_sch/.kicad_pro` and
  `renders/roomnode-c6_top.png` / `_bottom.png` (uses `tools/kicad_gen.py`)
- `firmware/roomnode-c6.yaml` - ESPHome configuration

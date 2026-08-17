# RoomNode-C3-Mini

Budget room node on the tiny ESP32-C3-MINI-1 (WiFi + BLE 5).

**MCU**: ESP32-C3-MINI-1-N4 (13.2 × 16.6 mm module) · [datasheet](../datasheets/esp32-c3-mini-1_datasheet_en.pdf) · [STEP model](https://github.com/AskAlice/room-node-pcbs/tree/main/models/ESP32-C3-MINI-1.STEP)

## Use case

- Climate: SHT40 temperature/humidity
- Light: ALS-PT19 analog ambient light
- Motion: AM312 PIR
- LED: SK6812MINI-E reverse-mount status LED
- BLE tracking: ESPHome `esp32_ble_tracker`

## ESP32-C3 pin mapping

| Function | GPIO | Notes |
|---|---|---|
| I2C SDA | GPIO6 | SHT40 (0x44); R6 4.7k pull-up |
| I2C SCL | GPIO7 | R7 4.7k pull-up |
| ALS analog in | GPIO3 | ADC1_CH3, R8 10k load |
| PIR input | GPIO4 | J3 header |
| SK6812 data | GPIO10 | via R3 470Ω |
| USB D+/D- | GPIO19/18 | USB-Serial-JTAG (console + flashing) |

Strapping pins GPIO2/8 avoided; GPIO9 only used by BOOT button.

## Power

USB-C 5V with 5.1kΩ CC pull-downs → ME6211C33M5G LDO.

## Renders

| Raytraced 3D (KiCad) | Routing |
|---|---|
| ![3d](../../renders/roomnode-c3-mini_kicad3d.png) | ![routing](../../renders/roomnode-c3-mini_routing.svg) |

[Schematic (SVG)](../../renders/roomnode-c3-mini_schematic.svg) · [Schematic (PDF)](../../renders/roomnode-c3-mini_schematic.pdf)

## Fabrication

JLCPCB-ready package: `fab/roomnode-c3-mini_jlcpcb.zip`. Design source: `boards/roomnode-c3-mini/build.py`.

## Component datasheets

| Part | LCSC | Datasheet |
|---|---|---|
| ESP32-C3-MINI-1-N4 | C2838502 | [pdf](../datasheets/esp32-c3-mini-1_datasheet_en.pdf) |
| ESP32-C3 (SoC) | — | [pdf](../datasheets/esp32-c3_datasheet_en.pdf) |
| SK6812MINI-E | C5149201 | [pdf](../datasheets/4960_SK6812MINI-E_REV02_EN.pdf) |
| ALS-PT19 | — | [pdf](../datasheets/ALS-PT19-315C-L177-TR_datasheet.pdf) |

SHT40 datasheet: [Sensirion link](https://sensirion.com/media/documents/33FD6951/662A593A/Sensirion_Datasheet_SHT4x.pdf).

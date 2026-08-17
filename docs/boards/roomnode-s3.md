# RoomNode-S3

Flagship multi-function room node. One per room: presence, air quality, light, LED control, BLE tracking.

**MCU**: ESP32-S3-WROOM-1-N8R2 (WiFi + BLE 5, 8MB flash, 2MB PSRAM) · [datasheet](../datasheets/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) · [STEP model](https://github.com/AskAlice/room-node-pcbs/tree/main/models/ESP32-S3-WROOM-1.STEP)

## Use case

- Human presence: HLK-LD2450 mmWave radar (multi-target tracking, UART)
- Air quality: SGP40 VOC index (compensated by on-board SHT40)
- Climate: SHT40 temperature/humidity
- Light: BH1750 lux
- LED control: WS2812B-V5 status LED + header for external strip
- BLE tracking: ESPHome `esp32_ble_tracker` / `ble_presence`
- Motion: PIR header (AM312/AS312)

## ESP32 pin mapping

| Function | GPIO | Notes |
|---|---|---|
| I2C SDA | GPIO8 | SHT40 (0x44), SGP40 (0x59), BH1750 (0x23); R6 4.7k pull-up |
| I2C SCL | GPIO9 | R7 4.7k pull-up |
| UART2 RX | GPIO17 | LD2450 TX (3.3V logic, 256000 baud) |
| UART2 TX | GPIO18 | LD2450 RX |
| PIR input | GPIO16 | J3 header, 3.3V logic |
| WS2812B data | GPIO4 | via R3 470Ω |
| USB D+ | GPIO20 | via USBLC6 ESD |
| USB D- | GPIO19 | via USBLC6 ESD |

## Power

USB-C 5V (J1, TYPE-C-31-M-12, [C165948](https://www.lcsc.com/product-detail/C165948.html)) with R1/R2 5.1kΩ CC pull-downs and USBLC6-2SC6 ESD ([datasheet](../datasheets/usblc6-2.pdf)) → AMS1117-3.3 ([datasheet](../datasheets/ds1117.pdf)).

## Renders

| Raytraced 3D (KiCad) | Routing |
|---|---|
| ![3d](../../renders/roomnode-s3_kicad3d.png) | ![routing](../../renders/roomnode-s3_routing.svg) |

[Schematic (SVG)](../../renders/roomnode-s3_schematic.svg) · [Schematic (PDF)](../../renders/roomnode-s3_schematic.pdf)

## Fabrication

JLCPCB-ready package: `fab/roomnode-s3_jlcpcb.zip` (gerbers, drill, pick&place, BOM). Design source: `boards/roomnode-s3/build.py` (hardware-as-code; regenerates all KiCad files).

## Component datasheets

| Part | LCSC | Datasheet |
|---|---|---|
| ESP32-S3-WROOM-1-N8R2 | C2913204 | [pdf](../datasheets/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) |
| SGP40 | C2874215 | [pdf](../datasheets/SGP40_datasheet.pdf) |
| BH1750 | C2071 | [link](https://www.mouser.com/datasheet/2/348/bh1750fvi-e-1862271.pdf) |
| HLK-LD2450 | — | [link](https://www.hlktech.net/index.php?id=1157) |
| WS2812B-V5 | C2846931 | [pdf](../datasheets/WS2812B.pdf) |
| AMS1117-3.3 | C6186 | [pdf](../datasheets/ds1117.pdf) |
| USBLC6-2SC6 | C7519 | [pdf](../datasheets/usblc6-2.pdf) |

SHT40 datasheet: [Sensirion link](https://sensirion.com/media/documents/33FD6951/662A593A/Sensirion_Datasheet_SHT4x.pdf) (CDN-blocked; fetched by `tools/fetch-assets.sh` when available).

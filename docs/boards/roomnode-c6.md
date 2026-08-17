# RoomNode-C6

Matter/Thread-capable room node built on the ESP32-C6 (WiFi 6 + BLE 5.3 + 802.15.4 for Thread/Zigbee/Matter).

**MCU**: ESP32-C6-WROOM-1-N8 · [datasheet](../datasheets/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf) · [STEP model](https://github.com/AskAlice/room-node-pcbs/tree/main/models/ESP32-C6-WROOM-1.STEP)

## Use case

- Climate: SHT31 temp/humidity + BME280 temp/humidity/pressure
- Light: BH1750 lux
- Motion: AM312 PIR
- LED control: WS2812B-V5 status LED
- Matter/Thread/Zigbee commissioning via 802.15.4 radio; BLE provisioning

## ESP32-C6 pin mapping

| Function | GPIO | Notes |
|---|---|---|
| I2C SDA | GPIO6 | SHT31 (0x44), BME280 (0x76), BH1750 (0x23); R6 4.7k pull-up |
| I2C SCL | GPIO7 | R7 4.7k pull-up |
| PIR input | GPIO22 | J2 header, AM312 3.3V output |
| WS2812B data | GPIO15 | via R3 470Ω (strapping pin — DIN is high-Z, safe) |
| UART0 RX/TX | GPIO17/16 | J4 debug header |
| USB D+/D- | GPIO13/12 | USB-Serial-JTAG, via USBLC6 |

## Power

USB-C 5V with 5.1kΩ CC pull-downs → ME6211C33M5G LDO ([C82942](https://www.lcsc.com/product-detail/C82942.html)).

## Renders

| Raytraced 3D (KiCad) | Routing |
|---|---|
| ![3d](../../renders/roomnode-c6_kicad3d.png) | ![routing](../../renders/roomnode-c6_routing.svg) |

[Schematic (SVG)](../../renders/roomnode-c6_schematic.svg) · [Schematic (PDF)](../../renders/roomnode-c6_schematic.pdf)

## Fabrication

JLCPCB-ready package: `fab/roomnode-c6_jlcpcb.zip`. Design source: `boards/roomnode-c6/build.py`.

## Component datasheets

| Part | LCSC | Datasheet |
|---|---|---|
| ESP32-C6-WROOM-1-N8 | C5366877 | [pdf](../datasheets/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf) |
| BME280 | C92489 | [pdf](../datasheets/bst-bme280-ds002.pdf) |
| BH1750 | C2071 | [link](https://www.mouser.com/datasheet/2/348/bh1750fvi-e-1862271.pdf) |
| AM312 PIR | C90465 | [link](https://www.lcsc.com/datasheet/C90465.pdf) |
| WS2812B-V5 | C2846931 | [pdf](../datasheets/WS2812B.pdf) |

SHT31 datasheet: [Sensirion link](https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf).

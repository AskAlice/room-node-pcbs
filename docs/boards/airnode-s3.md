# AirNode-S3

Dedicated air-quality node: CO2, VOC, particulates, with a 3-LED air-quality traffic light.

**MCU**: ESP32-S3-WROOM-1-N8R2 (WiFi + BLE 5) · [datasheet](../datasheets/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) · [STEP model](https://github.com/AskAlice/room-node-pcbs/tree/main/models/ESP32-S3-WROOM-1.STEP)

## Use case

- CO2: SCD41 photoacoustic CO2 (+temp/humidity), ASC enabled
- VOC: SGP40 VOC index, compensated by on-board SHT40
- Particulates: PMS5003 PM1.0/PM2.5/PM10 (UART, 5V powered, 3.3V logic)
- Climate: SHT40
- Display: 3× SK6812MINI-E AQI traffic-light LEDs
- BLE tracking: ESPHome `esp32_ble_tracker`

## ESP32 pin mapping

| Function | GPIO | Notes |
|---|---|---|
| I2C SDA | GPIO8 | SCD41 (0x62), SGP40 (0x59), SHT40 (0x44); R6 4.7k pull-up |
| I2C SCL | GPIO9 | R7 4.7k pull-up |
| UART2 RX | GPIO16 | PMS5003 TX (9600 baud, 3.3V logic) |
| UART2 TX | GPIO17 | PMS5003 RX (set/reset) |
| SK6812 data | GPIO12 | via R3 470Ω, 3 LEDs chained |
| USB D+ | GPIO20 | via USBLC6 ESD |
| USB D- | GPIO19 | via USBLC6 ESD |

## Power

USB-C 5V (TYPE-C-31-M-12) with 5.1kΩ CC pull-downs → AMS1117-3.3 (1A, SOT-223 with thermal pour+vias) — sized for SCD41 measurement pulses. PMS5003 runs on 5V directly. Keep the sensor airflow zone clear (silkscreen marked).

## Renders

| Raytraced 3D (KiCad) | Routing |
|---|---|
| ![3d](../../renders/airnode-s3_kicad3d.png) | ![routing](../../renders/airnode-s3_routing.svg) |

[Schematic (SVG)](../../renders/airnode-s3_schematic.svg) · [Schematic (PDF)](../../renders/airnode-s3_schematic.pdf)

## Fabrication

JLCPCB-ready package: `fab/airnode-s3_jlcpcb.zip`. Design source: `boards/airnode-s3/build.py`.

## Component datasheets

| Part | LCSC | Datasheet |
|---|---|---|
| ESP32-S3-WROOM-1-N8R2 | C2913204 | [pdf](../datasheets/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) |
| SCD41 | C3659362 | [pdf](../datasheets/SCD4x_datasheet.pdf) · [STEP](https://github.com/AskAlice/room-node-pcbs/tree/main/models/Sensirion_SCD4x.step) |
| SGP40 | C2874215 | [pdf](../datasheets/SGP40_datasheet.pdf) |
| PMS5003 | — | [pdf](../datasheets/plantower-pms5003-manual_v2-3.pdf) |
| SK6812MINI-E | C5149201 | [pdf](../datasheets/4960_SK6812MINI-E_REV02_EN.pdf) |
| AMS1117-3.3 | C6186 | [pdf](../datasheets/ds1117.pdf) |

# Firmware

All boards run **ESPHome** (ESP-IDF framework). Configs live in `firmware/`:

| File | Board | Framework | Highlights |
|---|---|---|---|
| `roomnode-s3.yaml` | RoomNode-S3 | esp-idf | sht4x, sgp40 (compensated), bh1750, ld2450 presence, esp32_ble_tracker/ble_presence, neopixelbus |
| `roomnode-c6.yaml` | RoomNode-C6 | esp-idf | sht3xd, bme280, bh1750, PIR, neopixelbus — C6 gives WiFi6/BLE5.3/802.15.4 (Matter/Thread via future ESPHome or esp-matter port) |
| `roomnode-c3-mini.yaml` | RoomNode-C3-Mini | esp-idf | sht4x, adc (ALS-PT19), PIR, neopixelbus sk6812, USB-Serial-JTAG logging |
| `airnode-s3.yaml` | AirNode-S3 | esp-idf | scd4x (ASC), sgp40 compensated, pmsx003, esp32_rmt_led_strip AQI LEDs |

## Usage

```bash
pip install esphome
esphome secrets.yaml  # provide wifi_ssid, wifi_password, api_encryption_key, ota_password, ap_password
esphome run firmware/roomnode-c6.yaml
```

All boards expose a WiFi fallback AP + captive portal, native API (with encryption), and OTA updates.

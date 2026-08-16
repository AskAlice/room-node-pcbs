# Component Manifest (research output, verified 2026-08-16)

## MCUs / Modules
| Part | Mfr | Datasheet | LCSC | Footprint | 3D model |
|---|---|---|---|---|---|
| ESP32-S3-WROOM-1-N8R2 | Espressif | https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf | C2913204 | 25.5x18mm castellated | SnapMagic / espressif/kicad-libraries |
| ESP32-C6-WROOM-1-N8 | Espressif | https://www.espressif.com/sites/default/files/documentation/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf | C5366877 | 18x25.5mm castellated | espressif/kicad-libraries (STEP+WRL) |
| ESP32-C3-MINI-1-N4 | Espressif | https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf | C2838502 | 15.4x20.5mm castellated | espressif/kicad-libraries |
| ESP32-C3FH4 (bare QFN-32, ref) | Espressif | https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf | C2858491 | QFN-32-1EP 5x5 | SnapMagic |

## Sensors
| Part | Function | I2C addr | Datasheet | LCSC | ESPHome |
|---|---|---|---|---|---|
| SHT40-AD1B-R2 | Temp/RH DFN-4 | 0x44 | https://sensirion.com/resource/datasheet/sht4x | C2909890 | sht4x |
| SHT31-DIS-B | Temp/RH DFN-8 | 0x44 | https://sensirion.com/resource/datasheet/sht3x | C80862 | sht3xd |
| SGP40-D-R4 | VOC DFN-6 | 0x59 | https://sensirion.com/resource/datasheet/sgp40 | C2874215 | sgp40 |
| SCD41-D-R1 | CO2 LGA-20 | 0x62 | https://sensirion.com/resource/datasheet/scd41 | C3659362 | scd4x |
| BME280 | T/RH/P LGA-8 | 0x76 | https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf | C92489 | bme280_i2c |
| BH1750FVI-TR | Lux WSOF6I | 0x23 | https://fscdn.rohm.com/en/products/databook/datasheet/ic/sensor/light/bh1750fvi-e.pdf | C2071 | bh1750 |
| HLK-LD2450 | mmWave presence (5V, UART 256000 3.3V logic) | - | https://h.hlktech.com/Mobile/download/fdetail/294.html | module | ld2450 |
| AM312/AS312 | PIR (2.7-12V, 3.3V out) | - | Senba datasheet | C90465 (AS312) | gpio binary_sensor |
| ALS-PT19-315C | Analog light 0603 | - | https://cdn.sparkfun.com/datasheets/Components/General%20IC/ALS-PT19-315C-L177-TR_datasheet.pdf | - | adc |
| PMS5003 | PM (5V, UART 9600 3.3V logic, 8p PicoBlade) | - | https://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf | module | pmsx003 |

## Power / Interface / LEDs
| Part | Function | Datasheet | LCSC |
|---|---|---|---|
| ME6211C33M5G-N | LDO 3.3V 500mA SOT-23-5 | https://datasheet.lcsc.com/szlcsc/Nanjing-Micro-One-Elec-ME6211C33M5G-N_C82942.pdf | C82942 |
| AMS1117-3.3 | LDO 3.3V 1A SOT-223 | http://www.advanced-monolithic.com/pdf/ds1117.pdf | C6186 |
| TYPE-C-31-M-12 | USB-C 16p mid-mount (5.1k on CC1/CC2) | https://www.lcsc.com/datasheet/lcsc_datasheet_2205311830_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf | C165948 |
| USBLC6-2SC6 | USB ESD SOT-23-6 | https://www.st.com/resource/en/datasheet/usblc6-2.pdf | C7519 |
| WS2812B-V5 | RGB LED 5050 (5V) | https://datasheet.lcsc.com/lcsc/2304261807_Worldsemi-WS2812B-V5_C2846931.pdf | C2846931 |
| SK6812MINI-E | RGB LED 3535 (5V) | https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf | C5149201 |

Passives: 0603 R (10k=C25804, 5.1k, 470R, 1k), 0603 C 100nF=C14663, 10uF 0805=C19702. Tact button C720477. I2C pull-ups 4.7k 0603.
Antenna keepout (Espressif): >=15mm clearance all directions, NO copper/vias/parts on any layer under antenna; antenna overhang board edge preferred.
# <BOARD-NAME> — Component Datasheets
<!-- assembly: smd -->
<!-- board: <directory name under boards/> -->

| Designator(s) | Part Number | Manufacturer | Datasheet URL | Notes |
|---|---|---|---|---|
| U1 | ESP32-S3-WROOM-1-N16R8 | Espressif | https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf | MCU module |
| U2 | SCD41 | Sensirion | https://sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf | CO2 sensor |
| U3 | SHT40-AD1B | Sensirion | https://sensirion.com/media/documents/33FD6951/662A593A/HT_DS_Datasheet_SHT4x.pdf | Temp/RH |
| U4 | HLK-LD2450 | Hi-Link | https://drive.google.com/drive/folders/1a4d4ZKYZ8z3T05iFRXi0vBNJWgqKPRkf | mmWave presence |
| J1 | USB4085-GF-A | Global Connector Technology | https://gct.co/files/drawings/usb4085.pdf | USB-C connector |
| R1–R10, C1–C10 | 0603 generic | Yageo | https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_12.pdf | Commodity passives, one row per series |

Guidelines:
- One row per unique part number, designators grouped.
- `TBD` in the URL column fails CI — find the sheet before merging.
- Modules (e.g. ESP32-S3-WROOM) count as components: they need a row too.

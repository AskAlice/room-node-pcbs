# RoomNode-S3

Flagship room node: ESP32-S3-WROOM-1-N8R2 (WiFi + BLE 5), SHT40, SGP40 VOC, BH1750 lux, HLK-LD2450 mmWave presence, PIR header, 4x SK6812MINI-E LEDs. USB-C power (AMS1117-3.3).

**Docs:** https://askalice.github.io/room-node-pcbs/boards/roomnode-s3/

## Regenerate

```bash
python3 build.py
```

Writes `roomnode-s3.kicad_pcb` / `.kicad_sch` / `.kicad_pro` plus PIL renders into `../../renders/`.

## Fabrication

JLCPCB-ready package: `../../fab/roomnode-s3_jlcpcb.zip` (gerbers, drill, pick&place CSV, BOM CSV), rebuilt by CI from `fab/roomnode-s3/`.

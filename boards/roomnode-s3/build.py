#!/usr/bin/env python3
"""RoomNode-S3 board generator (KiCad 8) using tools/kicad_gen.py."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from kicad_gen import Board, Footprint, Schematic, project_file

HERE = os.path.dirname(os.path.abspath(__file__))
RENDERS = os.path.join(HERE, "..", "..", "renders")
os.makedirs(RENDERS, exist_ok=True)

BW, BH = 65.0, 50.0
b = Board("roomnode-s3")
b.rect_edge(BW, BH, 0, 0)

# ---------- helpers ----------
def r0603(ref, value, x, y):
    fp = Footprint(ref, x, y, ref=ref, value=value)
    fp.pad("1", -0.8, 0, 0.9, 0.9)
    fp.pad("2",  0.8, 0, 0.9, 0.9)
    fp.silk_rect(1.6, 0.9)
    return b.add(fp)

def r0805(ref, value, x, y):
    fp = Footprint(ref, x, y, ref=ref, value=value)
    fp.pad("1", -1.0, 0, 1.0, 1.2)
    fp.pad("2",  1.0, 0, 1.0, 1.2)
    fp.silk_rect(2.0, 1.25)
    return b.add(fp)

def header(ref, value, x, y, n, labels, vertical=True):
    fp = Footprint(ref, x, y, ref=ref, value=value)
    for i in range(n):
        px, py = (0, i * 2.54) if vertical else (i * 2.54, 0)
        fp.pad(str(i + 1), px, py, 1.7, 1.7, shape="circle", layers=("F.Cu", "B.Cu"), drill=1.0)
    w, h = (2.54, n * 2.54) if vertical else (n * 2.54, 2.54)
    fp.silk_rect(w + 0.6, h + 0.6)
    return b.add(fp)

# ---------- U1 ESP32-S3-WROOM-1-N8R2 (18 x 25.5) ----------
# antenna end at TOP: module top edge at y=12 (antenna zone y 12..17 near edge, overhang)
UX, UY = 32.5, 24.75  # center
u1 = Footprint("U1", UX, UY, ref="U1", value="ESP32-S3-WROOM-1-N8R2")
for i in range(16):  # long-edge castellated pads, pitch 1.27
    py = -10.5 + i * 1.27
    u1.pad(f"L{i+1}", -9.0 + 0.35, py, 1.0, 0.7)
    u1.pad(f"R{i+1}",  9.0 - 0.35, py, 1.0, 0.7)
for i in range(5):   # bottom edge pads
    u1.pad(f"B{i+1}", -2.54 + i * 1.27, 12.75 - 0.35, 0.7, 1.0)
u1.silk_rect(18, 25.5)
b.add(u1)

# ---------- J1 USB-C at bottom center ----------
j1 = Footprint("J1", 32.5, 47.0, ref="J1", value="TYPE-C-31-M-12")
for i in range(8):
    j1.pad(f"A{i+1}", -3.5 + i * 1.0, -0.9, 0.6, 0.5)
    j1.pad(f"B{i+1}", -3.5 + i * 1.0,  0.3, 0.6, 0.5)
for sx in (-4.4, 4.4):
    j1.pad(f"S{1 if sx<0 else 2}", sx, -1.0, 0.8, 1.0)
    j1.pad(f"S{3 if sx<0 else 4}", sx,  1.0, 0.8, 1.0)
j1.silk_rect(9.0, 3.6)
b.add(j1)

r0603("R1", "5.1k", 26.5, 43.0)   # CC1 pull-down
r0603("R2", "5.1k", 29.5, 43.0)   # CC2 pull-down

# D1 USBLC6-2SC6 SOT-23-6
d1 = Footprint("D1", 38.5, 43.0, ref="D1", value="USBLC6-2SC6")
for i in range(3):
    d1.pad(str(i+1), -0.95, -0.95 + i * 0.95, 0.7, 0.6)
    d1.pad(str(i+4),  0.95,  0.95 - i * 0.95, 0.7, 0.6)
d1.silk_rect(2.9, 2.8)
b.add(d1)

# ---------- U2 LDO + caps ----------
u2 = Footprint("U2", 45.0, 39.0, ref="U2", value="ME6211C33M5G")
for i in range(3):
    u2.pad(str(i+1), -0.95, -0.95 + i * 0.95, 0.7, 0.6)
u2.pad("4", 0.95, -0.95, 0.7, 0.6)
u2.pad("5", 0.95,  0.95, 0.7, 0.6)
u2.silk_rect(2.9, 2.8)
b.add(u2)
r0805("C1", "10uF", 45.0, 43.5)   # input cap
r0805("C2", "10uF", 49.5, 35.5)   # output cap

# ---------- U3 SHT40 DFN-4 (left edge mid) ----------
u3 = Footprint("U3", 8.0, 24.0, ref="U3", value="SHT40")
u3.pad("1", -0.55, -0.4, 0.5, 0.5)
u3.pad("2", -0.55,  0.4, 0.5, 0.5)
u3.pad("3",  0.55,  0.4, 0.5, 0.5)
u3.pad("4",  0.55, -0.4, 0.5, 0.5)
u3.silk_rect(1.5, 1.5)
b.add(u3)

# ---------- U4 SGP40 DFN-6 ----------
u4 = Footprint("U4", 8.0, 31.0, ref="U4", value="SGP40")
for i in range(3):
    u4.pad(str(i+1), -0.55, -0.5 + i * 0.5, 0.5, 0.35)
    u4.pad(str(i+4),  0.55,  0.5 - i * 0.5, 0.5, 0.35)
u4.silk_rect(1.7, 1.7)
b.add(u4)

# ---------- U5 BH1750 WSOF6I (top-left, outside y<10 keepout) ----------
u5 = Footprint("U5", 9.0, 14.5, ref="U5", value="BH1750FVI")
for i in range(3):
    u5.pad(str(i+1), -0.65, -0.95 + i * 0.95, 0.6, 0.6)
    u5.pad(str(i+4),  0.65,  0.95 - i * 0.95, 0.6, 0.6)
u5.silk_rect(3.0, 1.6)
b.add(u5)

# ---------- Headers ----------
header("J2", "LD2450", 60.0, 16.0, 4, ["5V", "GND", "TX", "RX"])
header("J3", "AM312-PIR", 60.0, 29.0, 3, ["VCC", "OUT", "GND"])
header("J4", "UART", 47.0, 46.5, 4, ["GND", "3V3", "TX", "RX"], vertical=False)

# ---------- D2-D5 SK6812MINI-E row along bottom + caps ----------
led_x = [7.0, 13.0, 19.0, 25.0]
for i, lx in enumerate(led_x):
    led = Footprint(f"D{i+2}", lx, 44.0, ref=f"D{i+2}", value="SK6812MINI-E")
    led.pad("1", -1.0, -1.0, 0.9, 0.9)
    led.pad("2",  1.0, -1.0, 0.9, 0.9)
    led.pad("3",  1.0,  1.0, 0.9, 0.9)
    led.pad("4", -1.0,  1.0, 0.9, 0.9)
    led.silk_rect(3.5, 3.5)
    b.add(led)
    r0603(f"C{6+i}", "100nF", lx, 40.3)
r0603("R3", "470R", 31.0, 41.0)  # DIN series resistor

# ---------- Switches ----------
def tact(ref, x, y):
    fp = Footprint(ref, x, y, ref=ref, value="TACT-3x4")
    fp.pad("1", -1.5, -1.0, 0.9, 0.7)
    fp.pad("2",  1.5, -1.0, 0.9, 0.7)
    fp.pad("3", -1.5,  1.0, 0.9, 0.7)
    fp.pad("4",  1.5,  1.0, 0.9, 0.7)
    fp.silk_rect(3.0, 4.0)
    return b.add(fp)
tact("SW1", 56.0, 40.0)  # EN / reset
tact("SW2", 56.0, 34.0)  # BOOT

# ---------- Decoupling + pull-ups ----------
r0603("C3", "100nF", 24.0, 31.0)
r0603("C4", "100nF", 24.0, 35.0)
r0603("R4", "10k", 50.5, 40.0)   # EN pull-up
r0603("R5", "10k", 50.5, 34.0)   # IO0 pull-up
r0603("R6", "4.7k", 15.0, 19.0)  # SDA pull-up
r0603("R7", "4.7k", 15.0, 22.0)  # SCL pull-up

# ---------- Tracks (all y >= 10: antenna keepout) ----------
# 5V: USB VBUS -> LDO VIN, 0.8mm
b.track(32.5, 45.5, 32.5, 44.3, 0.8, "F.Cu", "5V")
b.track(32.5, 44.3, 44.0, 44.3, 0.8, "F.Cu", "5V")
b.track(44.0, 44.3, 44.0, 40.0, 0.8, "F.Cu", "5V")
b.track(44.0, 40.0, 44.05, 38.05, 0.8, "F.Cu", "5V")
# 3V3 rail along bottom from LDO VOUT
b.track(45.95, 39.95, 45.95, 46.0, 0.8, "F.Cu", "3V3")
b.track(45.95, 46.0, 7.0, 46.0, 0.8, "F.Cu", "3V3")
b.track(7.0, 46.0, 7.0, 45.0, 0.8, "F.Cu", "3V3")  # to LED VDD row start
b.track(31.0, 41.7, 31.0, 46.0, 0.4, "F.Cu", "3V3")  # R3 stub area feed
# 3V3 up right side to module / pull-ups
b.track(50.5, 46.0, 50.5, 41.0, 0.8, "F.Cu", "3V3")
b.track(50.5, 33.0, 50.5, 30.0, 0.4, "F.Cu", "3V3")
b.track(50.5, 30.0, 41.5, 30.0, 0.4, "F.Cu", "3V3")
b.track(41.5, 30.0, 41.15, 30.0, 0.4, "F.Cu", "3V3")  # to module R pad row
# I2C trunk left edge (module left pads -> sensors), 0.4mm
b.track(23.15, 21.75, 14.0, 21.75, 0.4, "F.Cu", "SDA")
b.track(14.0, 21.75, 8.55, 21.75, 0.4, "F.Cu", "SDA")   # BH1750/SHT40 stubs
b.track(8.55, 21.75, 8.55, 23.6, 0.4, "F.Cu", "SDA")
b.track(23.15, 24.3, 14.5, 24.3, 0.4, "F.Cu", "SCL")
b.track(14.5, 24.3, 8.55, 24.3, 0.4, "F.Cu", "SCL")
b.track(8.55, 24.3, 8.55, 31.0, 0.4, "F.Cu", "SCL")     # down to SGP40
b.track(8.55, 31.0, 8.0, 31.0, 0.4, "F.Cu", "SDA-SGP")
# LED data chain IO4 -> R3 -> D2..D5
b.track(41.15, 34.9, 41.15, 41.0, 0.4, "F.Cu", "LEDDATA")
b.track(41.15, 41.0, 31.8, 41.0, 0.4, "F.Cu", "LEDDATA")
b.track(30.2, 41.0, 25.0, 41.0, 0.4, "F.Cu", "LEDDATA")
b.track(25.0, 41.0, 25.0, 43.0, 0.4, "F.Cu", "LEDDATA")
for i in range(3):
    b.track(led_x[3-i] - 1.0, 45.0, led_x[2-i] + 1.0, 45.0, 0.4, "F.Cu", "LEDCHAIN")
# UART to J2 / J4
b.track(41.15, 27.4, 58.0, 27.4, 0.4, "F.Cu", "TX")
b.track(58.0, 27.4, 58.0, 21.08, 0.4, "F.Cu", "TX")
b.track(41.15, 28.7, 57.0, 28.7, 0.4, "F.Cu", "RX")
b.track(57.0, 28.7, 57.0, 23.62, 0.4, "F.Cu", "RX")
# PIR out
b.track(60.0, 31.54, 60.0, 37.5, 0.4, "F.Cu", "PIR")
b.track(60.0, 37.5, 41.15, 37.5, 0.4, "F.Cu", "PIR")
b.track(41.15, 37.5, 41.15, 33.3, 0.4, "F.Cu", "PIR")

# ---------- GND vias (B.Cu zone tie points) ----------
for vx, vy in [(20, 46), (40, 46), (12, 34), (54, 46), (20, 12), (47, 20)]:
    b.via(vx, vy, 0.8, 0.4, "GND")

# ---------- Zones: B.Cu GND only (no F.Cu zone, antenna keepout) ----------
b.zone("GND", "B.Cu")

# ---------- Silk text ----------
b.text("RoomNode-S3", 15.0, 48.0, 1.4)
b.text("rev A 2026-08", 14.0, 37.0, 1.0)
b.text("ESPHome", 14.0, 12.5, 1.0)
b.text("ANTENNA KEEP-OUT", 32.5, 5.0, 0.9)

# ---------- Write outputs ----------
pcb = os.path.join(HERE, "roomnode-s3.kicad_pcb")
with open(pcb, "w") as f:
    f.write(b.to_kicad())

# ---------- Schematic ----------
s = Schematic("RoomNode-S3 rev A")
s.symbol("U1", "ESP32-S3-WROOM-1-N8R2", 80, 70, 40, 45, pins=[
    ("3V3", "L", 4), ("GND", "L", 9), ("EN", "L", 14), ("IO0", "L", 19),
    ("IO8_SDA", "L", 24), ("IO9_SCL", "L", 29),
    ("IO4_LED_DATA", "R", 4), ("IO17_RX", "R", 9), ("IO18_TX", "R", 14), ("IO16_PIR", "R", 19)])
s.symbol("U2", "ME6211C33M5G", 40, 30, 20, 15, pins=[("VIN", "L", 4), ("VOUT", "R", 4), ("GND", "L", 10)])
s.symbol("J1", "USB-C TYPE-C-31-M-12", 20, 55, 18, 20, pins=[("VBUS", "R", 4), ("CC1", "R", 9), ("CC2", "R", 14), ("D+", "R", 19), ("D-", "L", 4), ("GND", "L", 9)])
s.symbol("U3", "SHT40", 20, 95, 16, 12, pins=[("SDA", "R", 4), ("SCL", "R", 9), ("3V3", "L", 4), ("GND", "L", 9)])
s.symbol("U4", "SGP40", 50, 95, 16, 12, pins=[("SDA", "R", 4), ("SCL", "R", 9), ("3V3", "L", 4), ("GND", "L", 9)])
s.symbol("U5", "BH1750", 80, 95, 16, 12, pins=[("SDA", "R", 4), ("SCL", "R", 9), ("3V3", "L", 4), ("GND", "L", 9)])
s.symbol("J2", "HLK-LD2450", 130, 60, 18, 18, pins=[("5V", "L", 4), ("GND", "L", 9), ("TX", "L", 14), ("RX", "R", 4)])
s.symbol("J3", "AM312 PIR", 130, 90, 18, 14, pins=[("VCC", "L", 4), ("OUT", "L", 9), ("GND", "L", 13)])
s.symbol("D2-D5", "SK6812MINI-E x4", 130, 30, 22, 16, pins=[("DIN", "L", 4), ("5V", "L", 9), ("GND", "L", 13), ("DOUT", "R", 4)])
s.symbol("SW1", "EN", 100, 110, 12, 10, pins=[("EN", "L", 4), ("GND", "R", 4)])
s.symbol("SW2", "BOOT", 120, 110, 12, 10, pins=[("IO0", "L", 4), ("GND", "R", 4)])
for net, x, y in [("3V3", 60, 50), ("GND", 60, 52.5), ("SDA", 60, 55), ("SCL", 60, 57.5),
                  ("5V", 20, 45), ("LED_DATA", 105, 70)]:
    s.label(net, x, y)
sch = os.path.join(HERE, "roomnode-s3.kicad_sch")
with open(sch, "w") as f:
    f.write(s.to_kicad())

with open(os.path.join(HERE, "roomnode-s3.kicad_pro"), "w") as f:
    f.write(project_file("roomnode-s3"))

# ---------- Renders ----------
top = b.render(os.path.join(RENDERS, "roomnode-s3_top.png"), side="top", scale=14)
bot = b.render(os.path.join(RENDERS, "roomnode-s3_bottom.png"), side="bottom", scale=14)
print("wrote", pcb, sch)
print("renders:", top, bot)

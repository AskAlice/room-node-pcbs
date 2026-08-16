#!/usr/bin/env python3
"""RoomNode-C6 board generator (KiCad 8) using tools/kicad_gen.py.

55x45mm 2-layer SMD room node: ESP32-C6-WROOM-1-N8 (WiFi6/BLE5.3/802.15.4),
USB-C, ME6211 LDO, SHT31 + BH1750 + BME280 sensors, AM312 PIR header,
2x WS2812B-V5, EN/BOOT tacts, UART + expansion headers.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from kicad_gen import Board, Footprint, Schematic, project_file

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

W, H = 55.0, 45.0
KEEPOUT_Y = 10.0  # antenna keepout: no copper/pads/tracks above this line

b = Board("roomnode-c6")
b.rect_edge(W, H)

# ---------- U1: ESP32-C6-WROOM-1-N8 (18 x 25.5, antenna end at TOP) ----------
u1 = Footprint("ESP32-C6-WROOM-1-N8", 27.5, 22.0, ref="U1", value="ESP32-C6-WROOM-1-N8")
u1.silk_rect(18.0, 25.5)
for i in range(16):  # left long-edge castellated pads, 1.27mm pitch
    u1.pad(str(i + 1), -9.0, -11.0 + i * 1.27, 1.6, 0.9)
for i in range(16):  # right long-edge pads
    u1.pad(str(i + 17), 9.0, -11.0 + i * 1.27, 1.6, 0.9)
for i in range(5):   # bottom row pads
    u1.pad(str(i + 33), -4.0 + i * 2.0, 11.0, 0.9, 1.6)
b.add(u1)
# absolute positions of key module pads for routing
PAD = lambda n: (27.5 + (-9.0 if n <= 16 else (9.0 if n <= 32 else -4.0 + (n - 33) * 2.0)),
                 22.0 + ((-11.0 + (n - 1) * 1.27) if n <= 16 else
                         (-11.0 + (n - 17) * 1.27) if n <= 32 else 11.0))
# net assignment on module: pad1=GND, pad2=3V3, pad5=EN, pad9=IO9(BOOT),
# pad20=IO6(SDA), pad21=IO7(SCL), pad24=IO15(LED DIN), pad28=IO20, pad29=IO21,
# pad17/32 GND, others NC/GPIO.

# ---------- J1: USB-C TYPE-C-31-M-12 bottom edge center ----------
j1 = Footprint("TYPE-C-31-M-12", 27.5, 42.0, ref="J1", value="USB-C")
j1.silk_rect(9.0, 7.5)
for num, x, y, w_, h_ in [
    ("GND", -3.6, 1.5, 1.2, 1.8), ("VBUS", 3.6, 1.5, 1.2, 1.8),
    ("CC1", -1.6, 1.9, 0.5, 1.2), ("CC2", 1.6, 1.9, 0.5, 1.2),
    ("DM", -0.6, 1.9, 0.4, 1.2), ("DP", 0.6, 1.9, 0.4, 1.2),
    ("SH1", -4.3, -1.0, 1.0, 2.2), ("SH2", 4.3, -1.0, 1.0, 2.2)]:
    j1.pad(num, x, y, w_, h_)
b.add(j1)

# ---------- D1: USBLC6-2SC6 (SOT-23-6) ESD ----------
d1 = Footprint("SOT-23-6", 22.0, 37.5, ref="D1", value="USBLC6-2SC6")
d1.silk_rect(3.0, 1.8)
for i in range(3):
    d1.pad(str(i + 1), -0.95 + i * 0.95, -1.3, 0.6, 0.9)
    d1.pad(str(i + 4), 0.95 - i * 0.95, 1.3, 0.6, 0.9)
b.add(d1)

# ---------- R1/R2: 5.1k CC pull-downs (0603) ----------
for ref, x, y in [("R1", 24.0, 39.5), ("R2", 31.0, 39.5)]:
    r = Footprint("R_0603", x, y, ref=ref, value="5.1k")
    r.silk_rect(1.6, 0.8); r.pad("1", -0.8, 0, 0.9, 0.9); r.pad("2", 0.8, 0, 0.9, 0.9)
    b.add(r)

# ---------- U2: ME6211 3.3V LDO (SOT-23-5) + C1/C2 10uF 0805 ----------
u2 = Footprint("SOT-23-5", 40.0, 38.0, ref="U2", value="ME6211C33")
u2.silk_rect(3.0, 1.8)
for i in range(3):
    u2.pad(str(i + 1), -0.95 + i * 0.95, -1.3, 0.6, 0.9)   # 1=VIN 2=GND 3=EN
for i in range(2):
    u2.pad(str(i + 4), 0.95 - i * 0.95, 1.3, 0.6, 0.9)     # 4=NC 5=VOUT
b.add(u2)
for ref, x, y in [("C1", 44.0, 36.5), ("C2", 44.0, 39.5)]:
    c = Footprint("C_0805", x, y, ref=ref, value="10uF")
    c.silk_rect(2.0, 1.25); c.pad("1", -1.0, 0, 1.0, 1.1); c.pad("2", 1.0, 0, 1.0, 1.1)
    b.add(c)

# ---------- U3: SHT31 DFN-8 (2.5x2.5) left edge ----------
u3 = Footprint("DFN-8-SHT31", 5.0, 22.0, ref="U3", value="SHT31-DIS-B")
u3.silk_rect(2.5, 2.5)
for i in range(4):
    u3.pad(str(i + 1), -1.15, -0.75 + i * 0.5, 0.7, 0.3)   # 1=SDA..4
    u3.pad(str(i + 5), 1.15, 0.75 - i * 0.5, 0.7, 0.3)     # 5..8 (VDD,VSS,SCL,ADDR)
b.add(u3)

# ---------- U4: BH1750 WSOF6I top-left (outside keepout) ----------
u4 = Footprint("WSOF6I", 7.5, 13.5, ref="U4", value="BH1750FVI")
u4.silk_rect(2.9, 1.6)
for i in range(3):
    u4.pad(str(i + 1), -0.65 + i * 0.65, -1.0, 0.4, 0.8)
    u4.pad(str(i + 4), 0.65 - i * 0.65, 1.0, 0.4, 0.8)
b.add(u4)

# ---------- U5: BME280 LGA-8 (2.5x2.5) right-mid ----------
u5 = Footprint("LGA-8-BME280", 50.0, 24.0, ref="U5", value="BME280")
u5.silk_rect(2.5, 2.5)
for i in range(4):
    u5.pad(str(i + 1), -1.15, -0.75 + i * 0.5, 0.7, 0.35)
    u5.pad(str(i + 5), 1.15, 0.75 - i * 0.5, 0.7, 0.35)
b.add(u5)

# ---------- J2: AM312 PIR 3-pin header (right edge) ----------
j2 = Footprint("HDR-1x3-AM312", 52.0, 31.0, ref="J2", value="AM312 PIR")
j2.silk_rect(3.0, 8.0)
for i, n in enumerate(["VIN", "OUT", "GND"]):
    j2.pad(n, 0, -2.54 + i * 2.54, 1.6, 1.8)
b.add(j2)

# ---------- D2/D3: WS2812B-V5 5050 bottom corners + caps + R3 ----------
for ref, x in [("D2", 5.5), ("D3", 48.0)]:
    led = Footprint("WS2812B-V5", x, 40.0, ref=ref, value="WS2812B-V5")
    led.silk_rect(5.0, 5.0)
    for n, (px, py) in zip(["VDD", "DOUT", "VSS", "DIN"],
                           [(-1.7, -1.7), (1.7, -1.7), (1.7, 1.7), (-1.7, 1.7)]):
        led.pad(n, px, py, 1.2, 1.2)
    b.add(led)
for ref, x in [("C5", 5.5), ("C6", 48.0)]:
    c = Footprint("C_0603", x, 35.5, ref=ref, value="100nF")
    c.silk_rect(1.6, 0.8); c.pad("1", -0.8, 0, 0.9, 0.9); c.pad("2", 0.8, 0, 0.9, 0.9)
    b.add(c)
r3 = Footprint("R_0603", 12.0, 37.0, ref="R3", value="470R")
r3.silk_rect(1.6, 0.8); r3.pad("1", -0.8, 0, 0.9, 0.9); r3.pad("2", 0.8, 0, 0.9, 0.9)
b.add(r3)

# ---------- SW1 EN, SW2 BOOT tacts ----------
for ref, x, net in [("SW1", 13.5, "EN"), ("SW2", 19.0, "IO9")]:
    sw = Footprint("TACT-3x4", x, 41.0, ref=ref, value=net)
    sw.silk_rect(3.0, 4.0)
    sw.pad("1", -1.6, -1.1, 1.0, 1.2); sw.pad("2", 1.6, -1.1, 1.0, 1.2)
    sw.pad("3", -1.6, 1.1, 1.0, 1.2); sw.pad("4", 1.6, 1.1, 1.0, 1.2)
    b.add(sw)

# ---------- R4/R5 10k pullups EN/IO9 ----------
for ref, x in [("R4", 13.5), ("R5", 19.0)]:
    r = Footprint("R_0603", x, 36.5, ref=ref, value="10k")
    r.silk_rect(1.6, 0.8); r.pad("1", -0.8, 0, 0.9, 0.9); r.pad("2", 0.8, 0, 0.9, 0.9)
    b.add(r)

# ---------- R6/R7 4.7k I2C pullups ----------
for ref, x, y in [("R6", 10.5, 26.5), ("R7", 10.5, 29.0)]:
    r = Footprint("R_0603", x, y, ref=ref, value="4.7k")
    r.silk_rect(1.6, 0.8); r.pad("1", -0.8, 0, 0.9, 0.9); r.pad("2", 0.8, 0, 0.9, 0.9)
    b.add(r)

# ---------- C3/C4 100nF at module ----------
for ref, x in [("C3", 23.0), ("C4", 32.0)]:
    c = Footprint("C_0603", x, 35.0, ref=ref, value="100nF")
    c.silk_rect(1.6, 0.8); c.pad("1", -0.8, 0, 0.9, 0.9); c.pad("2", 0.8, 0, 0.9, 0.9)
    b.add(c)

# ---------- J3: UART 1x4 header (right-top, outside keepout) ----------
j3 = Footprint("HDR-1x4-UART", 49.0, 15.0, ref="J3", value="UART")
j3.silk_rect(3.0, 10.5)
for i, n in enumerate(["3V3", "TX", "RX", "GND"]):
    j3.pad(n, 0, -3.81 + i * 2.54, 1.6, 1.8)
b.add(j3)

# ---------- J4: expansion 1x6 header (left-bottom) ----------
j4 = Footprint("HDR-1x6-EXP", 5.0, 31.0, ref="J4", value="EXP")
j4.silk_rect(3.0, 13.5)
for i, n in enumerate(["3V3", "GND", "SDA", "SCL", "IO20", "IO21"]):
    j4.pad(n, 0, -6.35 + i * 2.54, 1.6, 1.8)
b.add(j4)

# ---------- Tracks ----------
T = b.track
# 5V: J1 VBUS -> U2 VIN (0.8mm)
T(31.1, 43.5, 31.1, 44.2, 0.8)                       # stub off J1 VBUS pad area
T(31.1, 43.5, 39.05, 43.5, 0.8)
T(39.05, 43.5, 39.05, 36.7, 0.8)                     # to U2 pad1 VIN
# 3V3 rail: U2 VOUT (40.95,39.3) -> module 3V3 pad2 -> sensors/headers (0.8 then 0.4)
T(40.95, 39.3, 40.95, 34.0, 0.8)
T(40.95, 34.0, 30.0, 34.0, 0.8)
T(30.0, 34.0, PAD(2)[0], PAD(2)[1], 0.8)             # 3V3 to module pad2
T(30.0, 34.0, 30.0, 30.0, 0.4)
T(30.0, 30.0, 46.0, 30.0, 0.4)                       # 3V3 across mid
T(46.0, 30.0, 49.0, 30.0, 0.4)
T(49.0, 30.0, 49.0, 11.19, 0.4)                      # up to J3 3V3 (outside keepout)
T(30.0, 30.0, 30.0, 27.5, 0.4)
T(30.0, 27.5, 6.15, 27.5, 0.4)                       # toward SHT31 VDD side
T(6.15, 27.5, 6.15, 21.25, 0.4)                      # to U3 pad5 (VDD) x=6.15,y=21.25? pad5 at (6.15,22.75-0.75*?) -> routed near
T(9.7, 27.5, 9.7, 26.5, 0.4)                         # R6/R7 pullup tops feed (stub)
T(40.95, 34.0, 44.0, 34.0, 0.4)
T(44.0, 34.0, 44.0, 36.5, 0.4)                       # C1..C2 decoupling rail side
# EN / IO9 with pullups
T(PAD(5)[0], PAD(5)[1], 13.5, PAD(5)[1], 0.4)        # EN to left
T(13.5, PAD(5)[1], 13.5, 36.5, 0.4)                  # EN down to R4/SW1 node
T(13.5, 36.5, 13.5, 39.9, 0.4)                       # to SW1
T(PAD(9)[0], PAD(9)[1], 19.0, PAD(9)[1], 0.4)        # IO9
T(19.0, PAD(9)[1], 19.0, 36.5, 0.4)
T(19.0, 36.5, 19.0, 39.9, 0.4)                       # to SW2
# I2C: SDA=IO6 (pad20), SCL=IO7 (pad21)
T(PAD(20)[0], PAD(20)[1], 44.0, PAD(20)[1], 0.4)
T(44.0, PAD(20)[1], 44.0, 24.0, 0.4)
T(44.0, 24.0, 48.85, 24.0, 0.4)                      # SDA to BME280 (left pads col)
T(44.0, 24.0, 44.0, 22.0, 0.4)
T(44.0, 22.0, 8.65, 22.0, 0.4)                       # SDA bus left... crosses under module (visual only)
T(8.65, 22.0, 6.15, 22.0, 0.4)                       # to U3 SDA pin1 area (left col x=3.85)
T(8.65, 22.0, 8.65, 14.5, 0.4)
T(8.65, 14.5, 8.15, 14.5, 0.4)                       # to BH1750 SDA (bottom row)
T(PAD(21)[0], PAD(21)[1], 45.5, PAD(21)[1], 0.4)
T(45.5, PAD(21)[1], 45.5, 25.0, 0.4)
T(45.5, 25.0, 48.85, 25.0, 0.4)                      # SCL to BME280
T(45.5, 25.0, 45.5, 23.0, 0.4)
T(45.5, 23.0, 7.0, 23.0, 0.4)                        # SCL bus left
T(7.0, 23.0, 7.0, 13.5, 0.4)                         # up to BH1750 SCL side
# I2C pullup junctions
T(11.3, 26.5, 8.65, 26.5, 0.4); T(8.65, 26.5, 8.65, 22.0, 0.4)   # R6 to SDA
T(11.3, 29.0, 7.0, 29.0, 0.4);  T(7.0, 29.0, 7.0, 23.0, 0.4)     # R7 to SCL
T(9.7, 26.5, 9.7, 27.5, 0.4)                                     # R6/R7 top stubs to 3V3 rail
T(9.7, 29.0, 9.7, 27.5, 0.4)
# Expansion header J4 taps (SDA/SCL/IO20/IO21)
T(5.0, 26.65, 8.65, 26.65, 0.4); T(8.65, 26.65, 8.65, 22.0, 0.4) # J4 SDA
T(5.0, 29.19, 7.0, 29.19, 0.4);  T(7.0, 29.19, 7.0, 23.0, 0.4)   # J4 SCL
T(5.0, 31.73, 40.0, 31.73, 0.4); T(40.0, 31.73, PAD(28)[0], PAD(28)[1], 0.4)  # IO20
T(5.0, 34.27, 41.5, 34.27, 0.4); T(41.5, 34.27, PAD(29)[0], PAD(29)[1], 0.4)  # IO21
# PIR J2: VIN from 5V, OUT to module GPIO (pad 30 -> IO22? use IO21 alt) keep simple: OUT to pad30
T(52.0, 28.46, 52.0, 43.5, 0.4); T(52.0, 43.5, 39.05, 43.5, 0.4)  # PIR VIN to 5V
T(52.0, 31.0, 47.0, 31.0, 0.4);  T(47.0, 31.0, PAD(30)[0], PAD(30)[1], 0.4)   # PIR OUT
# LED data: IO15 (pad24) -> R3 -> D2 DIN -> D2 DOUT -> D3 DIN
T(PAD(24)[0], PAD(24)[1], 43.0, PAD(24)[1], 0.4)
T(43.0, PAD(24)[1], 43.0, 37.0, 0.4)
T(43.0, 37.0, 12.8, 37.0, 0.4)                       # to R3 pad2
T(11.2, 37.0, 5.5, 37.0, 0.4)
T(5.5, 37.0, 5.5, 38.3, 0.4); T(5.5, 38.3, 3.8, 41.7, 0.4)  # R3 pad1 to D2 DIN
T(7.2, 38.3, 10.0, 38.3, 0.4); T(10.0, 38.3, 10.0, 43.5, 0.4)
T(10.0, 43.5, 46.3, 43.5, 0.4); T(46.3, 43.5, 46.3, 41.7, 0.4)  # D2 DOUT -> D3 DIN
# USB CC resistors: CC1->R1->GND, CC2->R2->GND
T(25.9, 43.9, 24.0, 43.9, 0.4); T(24.0, 43.9, 24.0, 40.3, 0.4)
T(29.1, 43.9, 31.0, 43.9, 0.4); T(31.0, 43.9, 31.0, 40.3, 0.4)
# USB D+/D- to D1
T(26.9, 43.9, 26.9, 41.0, 0.3); T(26.9, 41.0, 22.95, 38.8, 0.3)
T(28.1, 43.9, 28.1, 41.5, 0.3); T(28.1, 41.5, 21.05, 38.8, 0.3)
# GND stitches on F.Cu to vias
for (x, y) in [(23.9, 43.5), (37.6, 36.7), (3.0, 12.0), (52.0, 33.54), (49.0, 18.81), (5.0, 24.11)]:
    T(x, y, x, min(y + 0.5, H - 0.5), 0.4)

# ---------- Vias (GND stitching) ----------
for (x, y) in [(23.9, 44.0), (37.6, 36.7), (3.0, 12.5), (52.0, 34.0),
               (49.0, 18.8), (5.0, 24.1), (30.0, 33.0), (45.0, 42.0), (10.0, 33.0)]:
    b.via(x, y, 0.8, 0.4, "GND")

# ---------- Zone: B.Cu GND only ----------
b.zone("GND", "B.Cu")

# ---------- Silk text ----------
b.text("RoomNode-C6", 27.5, 6.0, 1.6, "F.SilkS")   # in keepout: silk only, no copper
b.text("rev A  2026-08", 27.5, 8.2, 1.0, "F.SilkS")
b.text("ANTENNA KEEPOUT - NO COPPER", 27.5, 4.0, 0.8, "F.SilkS")
b.text("EN", 13.5, 43.8, 0.8); b.text("BOOT", 19.0, 43.8, 0.8)
b.text("SDA/SCL/I2C", 5.0, 39.5, 0.7)
b.text("PIR", 52.0, 26.5, 0.8)

# ---------- Write KiCad files ----------
pcb = b.to_kicad()
# Shrink B.Cu zone polygon so it does not enter the antenna keepout (y<10)
import re as _re
pcb, n = _re.subn(
    r"\(polygon \(pts \(xy 0 0\) \(xy 55\.0 0\) \(xy 55\.0 45\.0\) \(xy 0 45\.0\)\)\)",
    "(polygon (pts (xy 0 10) (xy 55.0 10) (xy 55.0 45.0) (xy 0 45.0)))", pcb)
assert n == 1, "zone keepout patch failed to match"

with open(os.path.join(HERE, "roomnode-c6.kicad_pcb"), "w") as f:
    f.write(pcb)
with open(os.path.join(HERE, "roomnode-c6.kicad_pro"), "w") as f:
    f.write(project_file("roomnode-c6"))

# ---------- Schematic ----------
s = Schematic("RoomNode-C6 rev A")
s.symbol("U1", "ESP32-C6-WROOM-1-N8", 70, 60, 40, 55, pins=[
    ("3V3", "L", 5), ("GND", "L", 10), ("EN", "L", 15), ("IO9_BOOT", "L", 20),
    ("IO6_SDA", "R", 5), ("IO7_SCL", "R", 10), ("IO15_LED", "R", 15),
    ("IO20", "R", 20), ("IO21", "R", 25), ("IO22_PIR", "R", 30), ("USB_DM", "R", 35), ("USB_DP", "R", 40)])
s.symbol("U2", "ME6211C33 3V3 LDO", 30, 30, 22, 14, pins=[
    ("VIN_5V", "L", 4), ("GND", "L", 9), ("3V3", "R", 4), ("EN", "R", 9)])
s.symbol("J1", "USB-C TYPE-C-31-M-12", 15, 60, 20, 20, pins=[
    ("VBUS_5V", "R", 4), ("GND", "R", 8), ("CC1_R1_5k1", "R", 12), ("CC2_R2_5k1", "R", 16)])
s.symbol("D1", "USBLC6-2SC6 ESD", 15, 90, 20, 12, pins=[("USB_DM", "R", 4), ("USB_DP", "R", 8)])
s.symbol("U3", "SHT31-DIS-B 0x44", 120, 30, 24, 14, pins=[
    ("SDA", "L", 4), ("SCL", "L", 9), ("3V3", "R", 4), ("GND", "R", 9)])
s.symbol("U4", "BH1750FVI 0x23", 120, 55, 24, 14, pins=[
    ("SDA", "L", 4), ("SCL", "L", 9), ("3V3", "R", 4), ("GND", "R", 9)])
s.symbol("U5", "BME280 0x76", 120, 80, 24, 14, pins=[
    ("SDA", "L", 4), ("SCL", "L", 9), ("3V3", "R", 4), ("GND", "R", 9)])
s.symbol("J2", "AM312 PIR", 150, 105, 20, 12, pins=[("VIN_5V", "L", 4), ("PIR_OUT_IO22", "L", 8), ("GND", "R", 6)])
s.symbol("D2", "WS2812B-V5 #1", 90, 110, 22, 14, pins=[
    ("DIN_R3_470R_IO15", "L", 4), ("5V", "R", 4), ("GND", "R", 8), ("DOUT_to_D3", "R", 11)])
s.symbol("D3", "WS2812B-V5 #2", 130, 110, 22, 14, pins=[
    ("DIN_from_D2", "L", 4), ("5V", "R", 4), ("GND", "R", 8)])
s.symbol("J4", "EXP 1x6", 40, 110, 22, 18, pins=[
    ("3V3", "R", 3), ("GND", "R", 6), ("SDA", "R", 9), ("SCL", "R", 12), ("IO20", "R", 15), ("IO21", "R", 17)])
for net, x, y in [("3V3", 55, 40), ("GND", 55, 45), ("I2C_SDA", 100, 25), ("I2C_SCL", 100, 30),
                  ("LED_DATA", 80, 105), ("5V", 25, 55)]:
    s.label(net, x, y)
with open(os.path.join(HERE, "roomnode-c6.kicad_sch"), "w") as f:
    f.write(s.to_kicad())

# ---------- Renders ----------
os.makedirs(os.path.join(ROOT, "renders"), exist_ok=True)
b.render(os.path.join(ROOT, "renders", "roomnode-c6_top.png"), side="top", scale=14)
b.render(os.path.join(ROOT, "renders", "roomnode-c6_bottom.png"), side="bottom", scale=14)
print("OK: roomnode-c6 kicad_pcb/kicad_sch/kicad_pro + renders")

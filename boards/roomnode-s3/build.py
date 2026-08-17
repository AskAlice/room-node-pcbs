#!/usr/bin/env python3
"""RoomNode-S3 board generator (KiCad 8) using tools/kicad_gen.py.

65x50mm 2-layer SMD room node: ESP32-S3-WROOM-1-N8R2 (official Espressif
land pattern, antenna end over top edge with rule_area keepout y in [0,6]),
USB-C 16-pin mid-mount (C165948) + CC 5.1k + USBLC6-2SC6 ESD with D+/D-
routed to IO19/IO20, AMS1117-3.3 (C6186, SOT-223), SHT40/SGP40/BH1750
sensors, HLK-LD2450 + AM312 PIR + UART headers, 4x SK6812MINI-E, EN/BOOT.

Run:  python3 build.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from kicad_gen import Board, Footprint, Schematic, project_file
from esp_modules import esp32_s3_wroom, usb_c_16p_midmount

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RENDERS = os.path.join(ROOT, "renders")
NAME = "roomnode-s3"

BW, BH = 65.0, 50.0
b = Board(NAME)
b.rect_edge(BW, BH)
b.keepout(0, 0, BW, 6.0, "antenna keepout")   # rule_area, all layers

# ---------------------------------------------------------------- helpers
def r0603(name, x, y, ref, value, n1=None, n2=None, lcsc=None):
    fp = Footprint(name, x, y, ref=ref, value=value, lcsc=lcsc)
    fp.pad("1", -0.8, 0, 0.9, 0.9, net=n1)
    fp.pad("2", 0.8, 0, 0.9, 0.9, net=n2)
    return b.add(fp.silk_rect(1.6, 0.9))

def c0805(x, y, ref, value, n1=None, n2=None):
    fp = Footprint("C_0805", x, y, ref=ref, value=value, lcsc="C19702")
    fp.pad("1", -1.0, 0, 1.0, 1.2, net=n1)
    fp.pad("2", 1.0, 0, 1.0, 1.2, net=n2)
    return b.add(fp.silk_rect(2.0, 1.25))

def header(x, y, n, ref, value, nets, vertical=True):
    fp = Footprint("HDR_2.54", x, y, ref=ref, value=value)
    for i in range(n):
        px, py = (0, i * 2.54) if vertical else (i * 2.54, 0)
        fp.pad(str(i + 1), px, py, 1.7, 1.7, shape="circle", drill=1.0, net=nets[i])
    w, h = (2.54, n * 2.54) if vertical else (n * 2.54, 2.54)
    return b.add(fp.silk_rect(w + 0.6, h + 0.6))

def tact(x, y, ref, value, neta, netb):
    fp = Footprint("TACT_3x4", x, y, ref=ref, value=value, lcsc="C720477")
    fp.pad("1", -1.5, -1.0, 0.9, 0.7, net=neta)
    fp.pad("2", 1.5, -1.0, 0.9, 0.7, net=netb)
    fp.pad("3", -1.5, 1.0, 0.9, 0.7, net=neta)
    fp.pad("4", 1.5, 1.0, 0.9, 0.7, net=netb)
    return b.add(fp.silk_rect(3.0, 4.0))

# ---------------------------------------------------------------- U1 module
# Official ESP32-S3-WROOM-1 pattern; antenna end at/over the top edge.
# Origin (32.5,15.75): body top at y=0 (board edge), antenna keepout y 0..6.
u1 = esp32_s3_wroom(32.5, 15.75, nets={
    "2": "+3V3", "3": "EN", "4": "LED_DATA", "9": "PIR",
    "12": "SDA", "17": "SCL", "13": "USB_D-", "14": "USB_D+",
    "27": "IO0_BOOT", "36": "UART_RX", "37": "UART_TX",
    "1": "GND", "40": "GND", "41": "GND",
    **{str(n): "NC" for n in [5, 6, 7, 8, 10, 11, 15, 16, 18, 19, 20, 21, 22,
                              23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35,
                              38, 39]},
})
b.add(u1)
# abs pads: left col pad n (1..14): (23.75, 7.49+(n-1)*1.27)
#           short pad 15+i: (25.515+i*1.27, 25.25)
#           right col pad 27+i: (41.25, 24.0-i*1.27)
#  pad2 +3V3 (23.75,8.76)  pad3 EN (23.75,10.03)  pad4 LED (23.75,11.30)
#  pad9 PIR (23.75,17.65)  pad12 SDA (23.75,21.46) pad13 D- (23.75,22.73)
#  pad14 D+ (23.75,24.00)  pad17 SCL (28.055,25.25)
#  pad27 BOOT (41.25,24.0) pad36 RX (41.25,12.57) pad37 TX (41.25,11.30)

# ---------------------------------------------------------------- USB-C + ESD
b.add(usb_c_16p_midmount(32.5, 47.0))
# A row y=47.85: A1 GND 29.75, A4 +5V 31.25, A5 CC1 31.75, A6 D+ 32.25,
#                A7 D- 32.75, A9 +5V 33.75, A12 GND 35.25 ; B row y=48.95.
r0603("R_0603", 21.5, 48.5, "R1", "5.1k", "CC1", "GND")   # CC1 pulldown
r0603("R_0603", 25.5, 48.5, "R2", "5.1k", "CC2", "GND")   # CC2 pulldown
# D1 USBLC6-2SC6: 1/6=D-, 3/4=D+, 2=GND, 5=+5V
d1 = Footprint("SOT-23-6", 38.5, 43.0, ref="D1", value="USBLC6-2SC6", lcsc="C7519")
for i, yoff in enumerate([-0.95, 0, 0.95]):
    d1.pad(str(i + 1), -0.95, yoff, 0.7, 0.6)
    d1.pad(str(6 - i), 0.95, yoff, 0.7, 0.6)
d1.nets({"1": "USB_D-", "2": "GND", "3": "USB_D+", "4": "USB_D+",
         "5": "+5V", "6": "USB_D-"})
b.add(d1.silk_rect(2.9, 2.8))
# D1 abs: p1 (37.55,42.05) p2 (37.55,43.0) p3 (37.55,43.95)
#         p4 (39.45,43.95) p5 (39.45,43.0) p6 (39.45,42.05)

# ---------------------------------------------------------------- power
# U2 AMS1117-3.3 SOT-223 (C6186): 1=GND 2=VOUT 3=VIN 4=tab(VOUT)
u2 = Footprint("SOT-223", 45.0, 39.0, ref="U2", value="AMS1117-3.3", lcsc="C6186")
u2.pad("1", -2.3, 3.1, 1.5, 2.2, net="GND")
u2.pad("2", 0.0, 3.1, 1.5, 2.2, net="+3V3")
u2.pad("3", 2.3, 3.1, 1.5, 2.2, net="+5V")
u2.pad("4", 0.0, -3.1, 3.6, 2.2, net="+3V3")
b.add(u2.silk_rect(6.6, 7.0))
# abs: GND (42.7,42.1) VOUT (45,42.1) VIN (47.3,42.1) tab (45,35.9)
c0805(50.5, 42.1, "C1", "10uF", "+5V", "GND")     # input cap
c0805(49.5, 35.9, "C2", "10uF", "+3V3", "GND")    # output cap

# ---------------------------------------------------------------- sensors
u3 = Footprint("DFN-4-SHT40", 8.0, 24.0, ref="U3", value="SHT40", lcsc="C2909890")
u3.pad("1", -0.55, -0.4, 0.5, 0.5, net="SDA")
u3.pad("2", -0.55, 0.4, 0.5, 0.5, net="SCL")
u3.pad("3", 0.55, 0.4, 0.5, 0.5, net="+3V3")
u3.pad("4", 0.55, -0.4, 0.5, 0.5, net="GND")
b.add(u3.silk_rect(1.5, 1.5))
# abs: SDA (7.45,23.6) SCL (7.45,24.4) 3V3 (8.55,24.4) GND (8.55,23.6)

u4 = Footprint("DFN-6-SGP40", 8.0, 31.0, ref="U4", value="SGP40", lcsc="C2874215")
for i in range(3):
    u4.pad(str(i + 1), -0.55, -0.5 + i * 0.5, 0.5, 0.35)
    u4.pad(str(i + 4), 0.55, 0.5 - i * 0.5, 0.5, 0.35)
u4.nets({"1": "SDA", "2": "+3V3", "3": "GND", "4": "SCL", "5": "NC", "6": "NC"})
b.add(u4.silk_rect(1.7, 1.7))
# abs: 1 SDA (7.45,30.5) 2 3V3 (7.45,31) 3 GND (7.45,31.5)
#      4 SCL (8.55,31.5) 5 (8.55,31) 6 (8.55,30.5)

u5 = Footprint("WSOF6I", 9.0, 14.5, ref="U5", value="BH1750FVI", lcsc="C2071")
for i in range(3):
    u5.pad(str(i + 1), -0.65, -0.95 + i * 0.95, 0.6, 0.6)
    u5.pad(str(i + 4), 0.65, 0.95 - i * 0.95, 0.6, 0.6)
u5.nets({"1": "+3V3", "2": "GND", "3": "GND", "4": "SDA", "5": "NC", "6": "SCL"})
b.add(u5.silk_rect(3.0, 1.6))
# abs: 1 3V3 (8.35,13.55) 2 (8.35,14.5) 3 GND (8.35,15.45)
#      4 SDA (9.65,15.45) 5 (9.65,14.5) 6 SCL (9.65,13.55)

# ---------------------------------------------------------------- headers
header(61.5, 16.0, 4, "J2", "HLK-LD2450", ["+5V", "GND", "UART_TX", "UART_RX"])
# pads (60,16) (60,18.54) (60,21.08) (60,23.62)
header(61.5, 29.0, 3, "J3", "AM312-PIR", ["+5V", "PIR", "GND"])
# pads (60,29) (60,31.54) (60,34.08)
header(47.0, 46.5, 4, "J4", "UART", ["GND", "+3V3", "UART_TX", "UART_RX"],
       vertical=False)
# pads (47,46.5) (49.54,46.5) (52.08,46.5) (54.62,46.5)

# ---------------------------------------------------------------- LEDs
led_x = [7.0, 13.0, 19.0, 25.0]
for i, lx in enumerate(led_x):
    led = Footprint("SK6812MINI-E", lx, 44.0, ref=f"D{i+2}", value="SK6812MINI-E",
                    lcsc="C5149201")
    led.pad("1", -1.05, -0.85, 0.85, 0.85, net="+5V")        # VDD
    led.pad("2", 1.05, -0.85, 0.85, 0.85,
            net="LED_DIN" if i == 0 else f"LED_C{i+1}")     # DIN
    led.pad("3", 1.05, 0.85, 0.85, 0.85, net=f"LED_C{i+2}") # DOUT
    led.pad("4", -1.05, 0.85, 0.85, 0.85, net="GND")        # GND
    b.add(led.silk_rect(3.5, 3.5))
    r0603("C_0603", lx, 40.3, f"C{6+i}", "100nF", "+5V", "GND", lcsc="C14663")
r0603("R_0603", 31.0, 41.0, "R3", "470R", "LED_DATA", "LED_DIN")

# ---------------------------------------------------------------- switches etc
tact(56.0, 40.0, "SW1", "EN", "EN", "GND")
tact(56.0, 34.0, "SW2", "BOOT", "IO0_BOOT", "GND")
r0603("R_0603", 50.5, 40.0, "R4", "10k", "EN", "+3V3")       # EN pullup
r0603("R_0603", 50.5, 34.0, "R5", "10k", "IO0_BOOT", "+3V3") # BOOT pullup
r0603("C_0603", 61.0, 40.0, "C5", "100nF", "EN", "GND")      # EN cap to GND
r0603("R_0603", 27.0, 19.0, "R6", "4.7k", "SDA", "+3V3")     # SDA pullup
r0603("R_0603", 27.0, 22.0, "R7", "4.7k", "SCL", "+3V3")     # SCL pullup
r0603("C_0603", 20.0, 8.76, "C3", "100nF", "+3V3", "GND")    # module 3V3
r0603("C_0603", 24.0, 35.0, "C4", "100nF", "+3V3", "GND")    # spare decoupling

# ================================================================ tracks
T, B = "F.Cu", "B.Cu"

# ---- +5V: J1 VBUS -> AMS1117 VIN, C1, D1, LEDs, J2/J3
b.track(31.25, 47.85, 31.25, 48.95, 0.3, T, "+5V")    # A4-B4
b.track(33.75, 47.85, 33.75, 48.95, 0.3, T, "+5V")    # A9-B9
b.track(33.75, 47.85, 34.6, 47.85, 0.8, T, "+5V")
b.track(34.6, 47.85, 34.6, 45.0, 0.8, T, "+5V")
b.track(34.6, 45.0, 47.3, 45.0, 0.8, T, "+5V")
b.track(47.3, 45.0, 47.3, 42.1, 0.8, T, "+5V")        # U2 VIN
b.track(47.3, 45.0, 49.5, 45.0, 0.8, T, "+5V")
b.track(49.5, 45.0, 49.5, 42.1, 0.8, T, "+5V")        # C1 pad1
b.track(38.2, 45.0, 38.2, 43.0, 0.4, T, "+5V")
b.track(38.2, 43.0, 39.45, 43.0, 0.4, T, "+5V")       # D1 pin5
# 5V LED bus along y=42.3
b.track(34.6, 45.0, 34.6, 42.3, 0.8, T, "+5V")
b.track(5.95, 42.3, 34.6, 42.3, 0.8, T, "+5V")
for lx in led_x:
    b.track(lx - 1.05, 42.3, lx - 1.05, 43.15, 0.4, T, "+5V")   # VDD stub
    b.track(lx - 0.85, 42.3, lx - 0.85, 40.3, 0.4, T, "+5V")    # cap pad1
# 5V to J2 pin1 / J3 pin1 (right edge vertical x=58)
b.track(47.3, 45.0, 58.6, 45.0, 0.8, T, "+5V")
b.track(58.6, 45.0, 58.6, 16.0, 0.8, T, "+5V")
b.track(58.6, 16.0, 61.5, 16.0, 0.8, T, "+5V")        # J2 pin1
b.track(58.6, 29.0, 61.5, 29.0, 0.8, T, "+5V")        # J3 pin1

# ---- +3V3: AMS1117 VOUT/tab -> spine, module (B.Cu riser), west x=12, J4
b.track(45.0, 42.1, 45.0, 35.9, 0.8, T, "+3V3")       # VOUT-tab tie
b.track(45.0, 35.9, 48.5, 35.9, 0.8, T, "+3V3")       # C2 pad1
b.track(12.0, 38.5, 51.3, 38.5, 0.8, T, "+3V3")       # spine
# B.Cu riser x=24.9 (under module, clears D+/D- B horizontals at x>=25.7)
b.via(24.9, 38.5, net="+3V3")
b.track(24.9, 8.76, 24.9, 38.5, 0.8, B, "+3V3")
b.via(24.9, 8.76, 0.6, 0.3, "+3V3")
b.track(12.0, 8.76, 19.65, 8.76, 0.8, T, "+3V3")      # C3 pad1
b.via(19.65, 8.76, 0.6, 0.3, "+3V3")
b.track(19.65, 8.76, 23.0, 8.76, 0.8, B, "+3V3")      # under C3 GND pad
b.via(23.0, 8.76, 0.6, 0.3, "+3V3")
b.track(23.0, 8.76, 24.9, 8.76, 0.8, T, "+3V3")       # module pad2
# west vertical x=12 (B.Cu hop over EN y=10.03)
b.track(12.0, 8.76, 12.0, 9.3, 0.8, T, "+3V3")
b.via(12.0, 9.3, 0.6, 0.3, "+3V3")
b.track(12.0, 9.3, 12.0, 10.8, 0.8, B, "+3V3")
b.via(12.0, 10.8, 0.6, 0.3, "+3V3")
b.track(12.0, 10.8, 12.0, 38.5, 0.8, T, "+3V3")
# sensor branches off x=12
b.track(8.35, 12.2, 12.0, 12.2, 0.4, T, "+3V3")
b.via(8.35, 12.2, 0.6, 0.3, "+3V3")
b.track(8.35, 12.2, 8.35, 13.55, 0.4, B, "+3V3")
b.via(8.35, 13.55, 0.6, 0.3, "+3V3")                  # BH1750 VCC (in-pad)
b.track(8.55, 24.4, 12.0, 24.4, 0.4, T, "+3V3")       # SHT40 VDD
b.track(9.5, 31.0, 12.0, 31.0, 0.4, T, "+3V3")
b.via(9.5, 31.0, net="+3V3")
b.track(7.45, 31.0, 9.5, 31.0, 0.4, B, "+3V3")        # under U4 pad5 (NC)
b.via(7.45, 31.0, 0.6, 0.3, "+3V3")                   # SGP40 VDD (via-in-pad)
# R6/R7 pad2 feed: x=27.8 with B.Cu hop over short-edge pad row
b.track(27.8, 27.2, 27.8, 38.5, 0.4, T, "+3V3")
b.via(27.8, 27.2, 0.6, 0.3, "+3V3")
b.track(27.8, 23.65, 27.8, 27.2, 0.4, B, "+3V3")
b.via(27.8, 23.65, 0.6, 0.3, "+3V3")
b.track(27.8, 19.0, 27.8, 23.65, 0.4, T, "+3V3")      # R6 pad2 + R7 pad2
# R4 pad2 hop over EN y=39.2
b.track(51.3, 39.75, 51.3, 40.0, 0.4, T, "+3V3")
b.via(51.3, 39.75, 0.6, 0.3, "+3V3")
b.track(51.3, 38.5, 51.3, 39.75, 0.4, B, "+3V3")
b.via(51.3, 38.5, 0.6, 0.3, "+3V3")
# R5 pad2
b.track(51.3, 34.0, 53.0, 34.0, 0.4, T, "+3V3")
b.track(53.0, 34.0, 53.0, 38.5, 0.4, T, "+3V3")
# C4 pad1
b.track(23.2, 35.0, 23.2, 38.5, 0.4, T, "+3V3")
# 3V3 to J4 pin2 (hop 5V bus)
b.track(45.0, 42.1, 45.0, 43.8, 0.8, T, "+3V3")
b.via(45.0, 43.8, net="+3V3")
b.track(45.0, 43.8, 45.0, 45.8, 0.8, B, "+3V3")       # under 5V bus
b.via(45.0, 45.8, net="+3V3")
b.track(45.0, 45.8, 45.0, 48.0, 0.8, T, "+3V3")
b.track(45.0, 48.0, 49.54, 48.0, 0.8, T, "+3V3")
b.track(49.54, 47.2, 49.54, 48.0, 0.8, T, "+3V3")     # J4 pin2 from below

# ---- EN: module pad3 -> R4/SW1/C5 (B.Cu hop over 3V3 VOUT vertical x=45)
b.track(23.0, 10.03, 2.5, 10.03, 0.4, T, "EN")
b.track(2.5, 10.03, 2.5, 39.2, 0.4, T, "EN")
b.track(2.5, 39.2, 44.2, 39.2, 0.4, T, "EN")
b.via(44.2, 39.2, 0.6, 0.3, "EN")
b.track(44.2, 39.2, 45.8, 39.2, 0.4, B, "EN")
b.via(45.8, 39.2, 0.6, 0.3, "EN")
b.track(45.8, 39.2, 54.5, 39.2, 0.4, T, "EN")         # SW1 pad1
b.track(49.7, 39.2, 49.7, 40.0, 0.4, T, "EN")         # R4 pad1 stub
b.track(54.5, 39.0, 54.5, 41.0, 0.4, T, "EN")         # SW1 pads 1-3 tie
b.track(54.5, 41.0, 55.0, 41.0, 0.4, T, "EN")
b.via(55.0, 41.0, net="EN")
b.track(55.0, 41.0, 60.2, 41.0, 0.4, B, "EN")
b.via(60.2, 41.0, net="EN")
b.track(60.2, 40.0, 60.2, 41.0, 0.4, T, "EN")         # C5 pad1

# ---- IO0 BOOT: pad27 -> R5/SW2
b.track(42.0, 24.0, 43.0, 24.0, 0.4, T, "IO0_BOOT")
b.track(43.0, 24.0, 43.0, 33.0, 0.4, T, "IO0_BOOT")
b.track(43.0, 33.0, 54.5, 33.0, 0.4, T, "IO0_BOOT")   # SW2 pad1
b.track(49.7, 33.0, 49.7, 34.0, 0.4, T, "IO0_BOOT")   # R5 pad1 stub
b.track(54.5, 33.0, 54.5, 35.0, 0.4, T, "IO0_BOOT")   # SW2 pads 1-3 tie

# ---- I2C SDA: pad12 -> R6, SHT40, SGP40, BH1750
b.track(23.0, 21.46, 18.0, 21.46, 0.4, T, "SDA")
b.track(18.0, 19.0, 18.0, 21.46, 0.4, T, "SDA")
b.track(13.0, 19.0, 18.0, 19.0, 0.4, T, "SDA")
b.via(13.0, 19.0, net="SDA")
b.track(11.0, 19.0, 13.0, 19.0, 0.4, B, "SDA")        # hop 3V3 x=12
b.via(11.0, 19.0, net="SDA")
b.track(6.0, 19.0, 11.0, 19.0, 0.4, T, "SDA")
b.track(6.0, 19.0, 6.0, 30.5, 0.4, T, "SDA")
b.track(6.0, 23.6, 7.45, 23.6, 0.4, T, "SDA")         # SHT40 SDA
b.track(6.0, 30.5, 7.45, 30.5, 0.4, T, "SDA")         # SGP40 SDA
b.track(10.5, 15.45, 10.5, 19.0, 0.4, T, "SDA")
b.track(9.65, 15.45, 10.5, 15.45, 0.4, T, "SDA")      # BH1750 SDA
# SDA to R6 pad1 (26.2,19)
b.track(24.5, 21.46, 25.0, 21.46, 0.4, T, "SDA")
b.track(25.0, 19.0, 25.0, 21.46, 0.4, T, "SDA")
b.track(25.0, 19.0, 26.2, 19.0, 0.4, T, "SDA")        # R6 pad1

# ---- I2C SCL: pad17 (short edge) -> R7, sensors (west x=4.2 channel)
b.track(28.055, 25.25, 28.055, 26.75, 0.3, T, "SCL")
b.track(26.0, 26.75, 28.055, 26.75, 0.3, T, "SCL")
b.via(26.0, 26.75, 0.6, 0.3, "SCL")
b.track(26.0, 26.75, 26.2, 22.0, 0.3, B, "SCL")        # diagonal under pads
b.via(26.2, 22.0, 0.6, 0.3, "SCL")                    # R7 pad1 (in-pad)
b.track(20.0, 22.09, 26.2, 22.09, 0.3, T, "SCL")
b.track(20.0, 22.09, 20.0, 25.2, 0.4, T, "SCL")
b.track(13.0, 25.2, 20.0, 25.2, 0.4, T, "SCL")
b.via(13.0, 25.2, net="SCL")
b.track(11.0, 25.2, 13.0, 25.2, 0.4, B, "SCL")        # hop 3V3 x=12
b.via(11.0, 25.2, net="SCL")
b.track(7.0, 25.2, 11.0, 25.2, 0.4, T, "SCL")
b.via(7.0, 25.2, net="SCL")
b.track(5.0, 25.2, 7.0, 25.2, 0.4, B, "SCL")          # hop SDA x=6
b.via(5.0, 25.2, net="SCL")
b.track(4.2, 25.2, 5.0, 25.2, 0.4, T, "SCL")
b.track(4.2, 12.9, 4.2, 25.2, 0.4, T, "SCL")
b.track(4.2, 25.2, 4.2, 31.5, 0.4, T, "SCL")
b.track(4.2, 24.4, 5.2, 24.4, 0.4, T, "SCL")
b.via(5.2, 24.4, 0.6, 0.3, "SCL")
b.track(5.2, 24.4, 6.8, 24.4, 0.4, B, "SCL")          # hop SDA x=6
b.via(6.8, 24.4, 0.6, 0.3, "SCL")
b.track(6.8, 24.4, 7.45, 24.4, 0.4, T, "SCL")         # SHT40 SCL
b.track(4.2, 31.5, 6.9, 31.5, 0.4, T, "SCL")
b.via(6.9, 31.5, 0.6, 0.3, "SCL")
b.track(6.9, 31.5, 8.0, 31.5, 0.4, B, "SCL")          # hop U4 GND pad
b.via(8.0, 31.5, 0.6, 0.3, "SCL")
b.track(8.0, 31.5, 8.55, 31.5, 0.4, T, "SCL")         # SGP40 SCL
b.track(4.2, 12.9, 10.5, 12.9, 0.4, T, "SCL")
b.track(10.5, 12.9, 10.5, 13.55, 0.4, T, "SCL")
b.track(9.65, 13.55, 10.5, 13.55, 0.4, T, "SCL")      # BH1750 SCL

# ---- PIR: pad9 (23.75,17.65) -> J3 pin2 (60,31.54); B hops over 3V3/IO0/RX/5V
b.track(23.0, 17.65, 22.3, 17.65, 0.4, T, "PIR")
b.via(22.3, 17.65, net="PIR")
b.track(22.3, 17.65, 22.3, 30.0, 0.4, B, "PIR")
b.via(22.3, 30.0, net="PIR")
b.track(22.3, 30.0, 26.5, 30.0, 0.4, T, "PIR")
b.via(26.5, 30.0, net="PIR")
b.track(26.5, 30.0, 29.0, 30.0, 0.4, B, "PIR")        # hop 3V3 x=27.8
b.via(29.0, 30.0, net="PIR")
b.track(29.0, 30.0, 33.77, 30.0, 0.4, T, "PIR")
b.track(33.77, 23.365, 33.77, 30.0, 0.24, T, "PIR")
b.track(33.77, 23.365, 46.0, 23.365, 0.24, T, "PIR")
b.track(46.0, 23.365, 46.0, 30.0, 0.24, T, "PIR")
b.track(46.0, 30.0, 54.8, 30.0, 0.4, T, "PIR")
b.track(54.8, 30.0, 54.8, 30.9, 0.4, T, "PIR")
b.via(54.8, 30.9, net="PIR")
b.track(54.8, 30.9, 59.5, 30.9, 0.4, B, "PIR")        # under RX/TX/5V
b.via(59.5, 30.9, net="PIR")
b.track(59.5, 30.9, 61.5, 30.9, 0.4, T, "PIR")        # J3 pin2 (61.5,31.54)

# ---- LED data: pad4 (23.75,11.30) -> R3 -> D2 DIN -> chain
b.track(23.0, 11.30, 21.5, 11.30, 0.4, T, "LED_DATA")
b.track(21.5, 11.30, 21.5, 20.0, 0.4, T, "LED_DATA")
b.via(21.5, 20.0, net="LED_DATA")
b.track(21.5, 20.0, 21.5, 23.0, 0.4, B, "LED_DATA")   # hop SDA
b.via(21.5, 23.0, net="LED_DATA")
b.track(21.5, 23.0, 21.5, 37.5, 0.4, T, "LED_DATA")
b.via(21.5, 37.5, net="LED_DATA")
b.track(21.5, 37.5, 21.5, 39.8, 0.4, B, "LED_DATA")   # hop 3V3 spine + EN
b.via(21.5, 39.8, net="LED_DATA")
b.track(21.5, 39.8, 21.5, 41.5, 0.4, T, "LED_DATA")
b.track(21.5, 41.5, 23.3, 41.5, 0.4, T, "LED_DATA")
b.via(23.3, 41.5, 0.6, 0.3, "LED_DATA")
b.track(23.3, 41.5, 25.0, 41.5, 0.4, B, "LED_DATA")   # hop C9 5V stub
b.via(25.0, 41.5, 0.6, 0.3, "LED_DATA")
b.track(25.0, 41.5, 30.15, 41.5, 0.4, T, "LED_DATA")
b.track(30.15, 41.0, 30.15, 41.5, 0.4, T, "LED_DATA") # R3 pad1
b.via(31.85, 40.6, 0.6, 0.3, "LED_DIN")               # R3 pad2 (in-pad)
b.track(8.05, 40.6, 31.85, 40.6, 0.4, B, "LED_DIN")
b.track(8.05, 40.6, 8.05, 43.2, 0.4, B, "LED_DIN")
b.via(8.05, 43.2, 0.6, 0.3, "LED_DIN")                # via-in-pad D2 DIN
# chain D2->D3->D4->D5 (B.Cu hops, via-in-pad on DIN pads)
for i in range(3):
    x0 = led_x[i] + 1.05          # DOUT of Di
    x1 = led_x[i + 1] + 1.05      # DIN of Di+1
    b.via(x0, 44.6, 0.6, 0.3, f"LED_C{i+2}")            # DOUT in-pad
    b.track(x0, 44.6, x1, 43.2, 0.4, B, f"LED_C{i+2}")  # diagonal
    b.via(x1, 43.2, 0.6, 0.3, f"LED_C{i+2}")            # DIN in-pad

# ---- UART_TX: pad37 (41.25,11.30) -> J2 pin3 + J4 pin3
b.track(42.0, 11.30, 46.0, 11.30, 0.4, T, "UART_TX")
b.track(46.0, 11.30, 46.0, 15.0, 0.4, T, "UART_TX")
b.track(46.0, 15.0, 56.5, 15.0, 0.4, T, "UART_TX")
b.track(56.5, 15.0, 56.5, 21.08, 0.4, T, "UART_TX")
b.via(56.5, 21.08, net="UART_TX")
b.track(56.5, 21.08, 59.8, 21.08, 0.4, B, "UART_TX")  # under 5V vertical
b.via(59.8, 21.08, net="UART_TX")
b.track(59.8, 21.08, 61.5, 21.08, 0.4, T, "UART_TX")  # J2 pin3
b.track(56.5, 21.08, 56.5, 44.3, 0.4, T, "UART_TX")
b.track(52.08, 44.3, 56.5, 44.3, 0.4, T, "UART_TX")
b.via(52.08, 44.3, 0.6, 0.3, "UART_TX")
b.track(52.08, 44.3, 52.08, 46.5, 0.3, B, "UART_TX")   # under 5V bus
b.via(52.08, 46.5, 0.6, 0.3, "UART_TX")                # via-in-pad J4 pin3
# ---- UART_RX: pad36 (41.25,12.57) -> J2 pin4 + J4 pin4
b.track(42.0, 12.57, 44.0, 12.57, 0.4, T, "UART_RX")
b.track(44.0, 12.57, 44.0, 22.5, 0.4, T, "UART_RX")
b.track(44.0, 22.5, 55.8, 22.5, 0.4, T, "UART_RX")
b.via(55.8, 22.5, net="UART_RX")
b.track(55.8, 22.5, 59.8, 22.5, 0.4, B, "UART_RX")    # under TX + 5V
b.via(59.8, 22.5, net="UART_RX")
b.track(59.8, 22.5, 59.8, 23.62, 0.4, T, "UART_RX")
b.track(59.8, 23.62, 61.5, 23.62, 0.4, T, "UART_RX")  # J2 pin4
b.track(55.8, 22.5, 55.8, 43.6, 0.4, T, "UART_RX")
b.via(55.8, 43.6, 0.6, 0.3, "UART_RX")
b.track(55.8, 43.6, 55.8, 46.9, 0.3, B, "UART_RX")     # under TX + 5V bus
b.via(55.8, 46.9, 0.6, 0.3, "UART_RX")
b.track(55.8, 46.5, 55.8, 46.9, 0.3, T, "UART_RX")
b.track(54.62, 46.5, 55.8, 46.5, 0.3, T, "UART_RX")    # J4 pin4

# ---- USB D+/D-: J1 -> D1 (ESD) -> module IO19/IO20
b.track(32.25, 47.85, 32.25, 48.95, 0.3, T, "USB_D+")  # A6-B6 tie
b.track(32.75, 47.85, 32.75, 48.95, 0.3, T, "USB_D-")  # A7-B7 tie
b.track(32.25, 47.85, 32.25, 46.8, 0.3, T, "USB_D+")
b.via(32.25, 46.8, 0.6, 0.3, "USB_D+")
b.track(32.25, 46.8, 35.5, 46.8, 0.3, B, "USB_D+")
b.track(35.5, 44.2, 35.5, 46.8, 0.3, B, "USB_D+")
b.via(35.5, 44.2, 0.6, 0.3, "USB_D+")
b.track(35.5, 44.2, 37.55, 44.2, 0.3, T, "USB_D+")
b.track(37.55, 43.95, 37.55, 44.2, 0.3, T, "USB_D+")   # D1 pin3
b.via(37.55, 43.95, 0.6, 0.3, "USB_D+")
b.via(39.45, 43.95, 0.6, 0.3, "USB_D+")
b.track(37.55, 43.95, 39.45, 43.95, 0.3, B, "USB_D+")  # pin3-pin4 tie
b.track(32.75, 47.85, 32.75, 45.0, 0.3, T, "USB_D-")
b.track(32.75, 45.0, 33.2, 45.0, 0.3, T, "USB_D-")
b.track(33.2, 43.2, 33.2, 45.0, 0.3, T, "USB_D-")
b.via(33.2, 43.2, 0.6, 0.3, "USB_D-")
b.track(33.2, 41.3, 33.2, 43.2, 0.3, B, "USB_D-")
b.via(33.2, 41.3, 0.6, 0.3, "USB_D-")
b.track(33.2, 41.3, 37.55, 41.3, 0.3, T, "USB_D-")
b.track(37.55, 41.3, 37.55, 42.05, 0.3, T, "USB_D-")   # D1 pin1
b.track(37.55, 42.05, 39.45, 42.05, 0.3, T, "USB_D-")  # D1 pin6 tie
# D1 -> module: B.Cu risers east of module pads, B.Cu corridor under body
b.track(39.45, 43.95, 40.5, 43.95, 0.3, T, "USB_D+")  # pin4 to riser
b.via(40.5, 43.95, 0.6, 0.3, "USB_D+")
b.track(40.5, 23.1, 40.5, 43.95, 0.3, B, "USB_D+")
b.track(26.8, 23.1, 40.5, 23.1, 0.3, B, "USB_D+")
b.via(26.8, 23.1, 0.6, 0.3, "USB_D+")
b.track(26.8, 23.1, 26.8, 24.0, 0.3, T, "USB_D+")
b.track(24.5, 24.0, 26.8, 24.0, 0.3, T, "USB_D+")      # pad14 IO20
b.track(39.45, 42.05, 41.5, 42.05, 0.3, T, "USB_D-")
b.via(41.5, 42.05, 0.6, 0.3, "USB_D-")
b.track(41.5, 22.6, 41.5, 42.05, 0.3, B, "USB_D-")
b.track(27.0, 22.6, 41.5, 22.6, 0.3, B, "USB_D-")
b.via(27.0, 22.6, 0.6, 0.3, "USB_D-")
b.track(24.5, 22.6, 27.0, 22.6, 0.3, T, "USB_D-")      # pad13 IO19

# ---- USB CC pull-downs
b.via(31.75, 47.85, 0.6, 0.3, "CC1")                   # via-in-pad A5
b.track(30.5, 47.85, 31.75, 47.85, 0.3, B, "CC1")
b.track(30.5, 47.85, 30.5, 49.2, 0.3, B, "CC1")
b.track(20.7, 49.2, 30.5, 49.2, 0.3, B, "CC1")
b.via(20.7, 49.2, 0.6, 0.3, "CC1")
b.track(20.7, 48.5, 20.7, 49.2, 0.3, T, "CC1")         # R1 pad1
b.via(31.75, 48.95, 0.6, 0.3, "CC2")                   # via-in-pad B5
b.track(31.75, 48.95, 31.75, 49.75, 0.3, B, "CC2")
b.track(24.7, 49.75, 31.75, 49.75, 0.3, B, "CC2")
b.via(24.7, 49.75, 0.6, 0.3, "CC2")
b.track(24.7, 48.5, 24.7, 49.75, 0.3, T, "CC2")        # R2 pad1 (25.5,48.5)

# ---- GND stubs + vias
def g(x1, y1, x2, y2, w=0.4, layer=T):
    b.track(x1, y1, x2, y2, w, layer, "GND")
def gv(x, y, d=0.8, dr=0.4):
    b.via(x, y, d, dr, "GND")

g(29.75, 47.85, 29.75, 48.95, 0.3)          # J1 A1-B1 tie
g(35.25, 47.85, 35.25, 48.95, 0.3)          # J1 A12-B12 tie
g(29.75, 47.85, 28.5, 47.85); gv(28.5, 47.85)
g(35.25, 47.85, 36.0, 47.85, 0.3)
g(22.3, 48.5, 23.1, 48.5, 0.3); gv(23.1, 48.5, 0.6, 0.3)   # R1 pad2
g(26.3, 48.5, 27.0, 48.5, 0.3); gv(27.0, 48.5, 0.6, 0.3)   # R2 pad2
b.via(37.55, 43.0, 0.6, 0.3, "GND")             # D1 pin2 (in-pad)
g(42.7, 42.1, 42.7, 44.2, 0.4); gv(42.7, 44.2)   # U2 GND
g(51.5, 42.1, 52.5, 42.1); gv(52.5, 42.1)   # C1 pad2
g(50.5, 35.9, 51.5, 35.9); gv(51.5, 35.9)   # C2 pad2
g(61.8, 40.0, 61.8, 41.0, 0.3); gv(61.8, 41.0, 0.6, 0.3)  # C5 pad2
g(8.55, 23.6, 9.5, 23.6, 0.3); gv(9.5, 23.6, 0.6, 0.3)   # U3 GND
g(7.45, 31.5, 7.45, 32.3, 0.3); gv(7.45, 32.3, 0.6, 0.3)   # U4 GND
g(8.35, 15.45, 7.5, 15.45, 0.3); gv(7.5, 15.45, 0.6, 0.3)  # U5 GND
g(8.35, 14.5, 8.35, 15.45, 0.3)             # U5 ADDR->GND (pad2-pad3 tie)
g(60.0, 18.54, 61.0, 18.54); gv(61.0, 18.54)  # J2 pin2
g(60.0, 34.08, 61.0, 34.08); gv(61.0, 34.08)  # J3 pin3
g(47.0, 46.5, 46.0, 46.5); gv(46.0, 46.5)     # J4 pin1
g(20.8, 8.76, 20.8, 7.5, 0.3); gv(20.8, 7.5, 0.6, 0.3)   # C3 pad2
g(24.8, 35.0, 26.0, 35.0); gv(26.0, 35.0)     # C4 pad2
for lx in led_x:                            # LED GND + cap GND
    g(lx - 1.05, 44.85, lx - 1.05, 45.6); gv(lx - 1.05, 45.6, 0.6, 0.3)
    g(lx + 0.85, 40.3, lx + 1.9, 40.3, 0.3)
    g(lx + 1.9, 40.3, lx + 1.9, 39.9, 0.3); gv(lx + 1.9, 39.9, 0.6, 0.3)
# tact GND pads (right columns)
g(57.5, 39.0, 57.5, 41.0, 0.3); gv(57.5, 40.0, 0.6, 0.3)
gv(57.5, 33.0, 0.6, 0.3); gv(57.5, 35.0, 0.6, 0.3)
g(57.5, 33.0, 57.5, 35.0, 0.3)
# module GND pads + EPAD
g(23.75, 7.49, 22.5, 7.49, 0.4)             # pad1
gv(22.5, 7.49, 0.6, 0.3)
g(41.25, 7.49, 42.5, 7.49, 0.4)             # pad40
gv(42.5, 7.49, 0.6, 0.3)
gv(31.0, 15.2)                              # EPAD 41 tie
# GND stitching vias
for vx, vy in [(20, 46), (40, 46), (13.5, 34), (54, 42.5), (20, 12.5), (47, 20),
               (4, 8), (62, 8)]:
    gv(vx, vy)

# ---------------------------------------------------------------- zone
b.zone("GND", "B.Cu")   # auto-clipped below antenna keepout

# ---------------------------------------------------------------- silk
b.text("RoomNode-S3", 15.0, 48.0, 1.4)
b.text("rev B 2026-08", 14.0, 37.0, 1.0)
b.text("ESPHome", 14.0, 12.5, 1.0)
b.text("ANTENNA KEEP-OUT", 32.5, 3.0, 0.9)

# ---------------------------------------------------------------- schematic
s = Schematic("RoomNode-S3 rev B")
s.symbol("U1", "ESP32-S3-WROOM-1-N8R2", 80, 70, 40, 45, pins=[
    ("+3V3", "L", 4), ("GND", "L", 9), ("EN", "L", 14), ("IO0_BOOT", "L", 19),
    ("IO8_SDA", "L", 24), ("IO9_SCL", "L", 29),
    ("IO4_LED_DATA", "R", 4), ("UART_RX", "R", 9), ("UART_TX", "R", 14),
    ("IO16_PIR", "R", 19), ("IO19_USB_D-", "R", 24), ("IO20_USB_D+", "R", 29)])
s.symbol("U2", "AMS1117-3.3 (C6186)", 40, 30, 22, 15,
         pins=[("VIN_+5V", "L", 4), ("GND", "L", 10), ("+3V3", "R", 4)])
s.symbol("J1", "USB-C C165948 16p", 20, 55, 18, 20, pins=[
    ("+5V", "R", 4), ("CC1_R1_5k1", "R", 9), ("CC2_R2_5k1", "R", 14),
    ("USB_D+", "R", 19), ("USB_D-", "L", 4), ("GND", "L", 9)])
s.symbol("D1", "USBLC6-2SC6 ESD", 45, 55, 18, 14,
         pins=[("USB_D+", "L", 4), ("USB_D-", "L", 9), ("GND", "R", 6)])
s.symbol("U3", "SHT40", 20, 95, 16, 12,
         pins=[("SDA", "R", 4), ("SCL", "R", 9), ("+3V3", "L", 4), ("GND", "L", 9)])
s.symbol("U4", "SGP40", 50, 95, 16, 12,
         pins=[("SDA", "R", 4), ("SCL", "R", 9), ("+3V3", "L", 4), ("GND", "L", 9)])
s.symbol("U5", "BH1750", 80, 95, 16, 12,
         pins=[("SDA", "R", 4), ("SCL", "R", 9), ("+3V3", "L", 4), ("GND", "L", 9)])
s.symbol("J2", "HLK-LD2450", 130, 60, 18, 18,
         pins=[("+5V", "L", 4), ("GND", "L", 9), ("UART_TX", "L", 14), ("UART_RX", "R", 4)])
s.symbol("J3", "AM312 PIR", 130, 90, 18, 14,
         pins=[("+5V", "L", 4), ("PIR", "L", 9), ("GND", "L", 13)])
s.symbol("D2-D5", "SK6812MINI-E x4", 130, 30, 22, 16,
         pins=[("LED_DATA_R3_470R", "L", 4), ("+5V", "L", 9), ("GND", "L", 13), ("chain", "R", 4)])
s.symbol("SW1", "EN + R4 10k + C5 100nF", 100, 110, 14, 10,
         pins=[("EN", "L", 4), ("GND", "R", 4)])
s.symbol("SW2", "BOOT + R5 10k", 120, 110, 12, 10,
         pins=[("IO0_BOOT", "L", 4), ("GND", "R", 4)])
for net, x, y in [("+3V3", 60, 50), ("GND", 60, 52.5), ("SDA", 60, 55),
                  ("SCL", 60, 57.5), ("+5V", 20, 45), ("LED_DATA", 105, 70)]:
    s.label(net, x, y)

# ---------------------------------------------------------------- write all
with open(os.path.join(HERE, NAME + ".kicad_pcb"), "w") as f:
    f.write(b.to_kicad())
with open(os.path.join(HERE, NAME + ".kicad_sch"), "w") as f:
    f.write(s.to_kicad())
with open(os.path.join(HERE, NAME + ".kicad_pro"), "w") as f:
    f.write(project_file(NAME))
os.makedirs(RENDERS, exist_ok=True)
b.render(os.path.join(RENDERS, NAME + "_top.png"), side="top", scale=14)
b.render(os.path.join(RENDERS, NAME + "_bottom.png"), side="bottom", scale=14)
print("OK:", NAME)

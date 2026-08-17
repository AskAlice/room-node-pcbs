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

# ---- +3V3
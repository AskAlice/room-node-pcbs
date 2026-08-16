#!/usr/bin/env python3
"""RoomNode-C3-Mini: 40x35mm 2-layer budget room node, ESP32-C3-MINI-1-N4.

Generates roomnode-c3-mini.kicad_pcb / .kicad_sch / .kicad_pro and renders
renders/roomnode-c3-mini_top.png / _bottom.png.

Run:  python3 build.py   (from this directory, or anywhere)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from kicad_gen import Board, Footprint, Schematic, project_file

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RENDERS = os.path.join(ROOT, "renders")
NAME = "roomnode-c3-mini"

# ---------------------------------------------------------------- footprints
def r0603(name, x, y, ref, value):
    return Footprint(name, x, y, ref=ref, value=value) \
        .pad("1", -0.85, 0, 0.9, 0.95).pad("2", 0.85, 0, 0.9, 0.95).silk_rect(2.6, 1.2)

def c0805(name, x, y, ref, value):
    return Footprint(name, x, y, ref=ref, value=value) \
        .pad("1", -1.05, 0, 1.1, 1.25).pad("2", 1.05, 0, 1.1, 1.25).silk_rect(3.2, 1.6)

def tact(name, x, y, ref, value):
    fp = Footprint(name, x, y, ref=ref, value=value)
    for i, (px, py) in enumerate([(-1.7, -2.1), (1.7, -2.1), (-1.7, 2.1), (1.7, 2.1)], 1):
        fp.pad(str(i), px, py, 1.0, 0.9)
    return fp.silk_rect(4.4, 5.4)

def th_header(name, x, y, n, ref, value):
    fp = Footprint(name, x, y, ref=ref, value=value)
    for i in range(n):
        fp.pad(str(i + 1), 0, i * 2.54, 1.7, 1.7, shape="circle" if i == 0 else "rect",
               layers=("F.Cu", "B.Cu"), drill=0.9)
    return fp.silk_rect(2.6, n * 2.54 + 0.4)

b = Board(NAME)
b.rect_edge(40, 35)

# --- U1 ESP32-C3-MINI-1-N4, antenna at TOP (y small), keepout y in [0,8] ---
u1 = Footprint("ESP32-C3-MINI-1-N4", 14, 18, ref="U1", value="ESP32-C3-MINI-1-N4")
# 13 castellated pads each long edge, 1.27mm pitch
for i in range(13):
    yoff = -7.62 + i * 1.27
    u1.pad(str(i + 1), -7.35, yoff, 1.7, 0.9)       # left edge  1..13 (top->bottom)
    u1.pad(str(26 - i), 7.35, yoff, 1.7, 0.9)       # right edge 14..26 (bottom->top)
# 7 pads along bottom short edge (opposite antenna)
for i in range(7):
    u1.pad(str(27 + i), -3.81 + i * 1.27, 10.0, 0.9, 1.5)
b.add(u1.silk_rect(15.4, 20.5))
# U1 pad coordinates (module center 14,18):
#   pad2 +3V3 (6.65,11.65)  pad3 EN (6.65,12.92)  pad4 IO4 (6.65,14.19)
#   pad6 IO6 SDA (6.65,16.71)  pad7 IO7 SCL (6.65,18.00)  pad9 IO9 BOOT (6.65,20.54)
#   pad10 IO10 LED (6.65,21.81)  pad11 IO3 ALS (6.65,23.08)
#   pad19 USB_D- (21.35,19.27)  pad20 USB_D+ (21.35,18.00)

# --- J1 USB-C bottom center ---
j1 = Footprint("TYPE-C-31-M-12", 20, 31.5, ref="J1", value="USB-C")
j1.pad("SH1", -4.3, 0, 1.4, 1.8).pad("SH2", 4.3, 0, 1.4, 1.8)   # shield = GND
j1.pad("GND", -3.25, 0, 0.65, 1.6).pad("VBUS", -2.6, 0, 0.65, 1.6)
j1.pad("CC1", -1.95, 0, 0.5, 1.6).pad("D-", -1.3, 0, 0.5, 1.6)
j1.pad("D+", -0.65, 0, 0.5, 1.6).pad("CC2", 0.0, 0, 0.5, 1.6)
b.add(j1.silk_rect(9.6, 3.4))

b.add(r0603("R_0603", 25.5, 30.0, "R1", "5.1k"))   # CC1 pulldown
b.add(r0603("R_0603", 25.5, 32.6, "R2", "5.1k"))   # CC2 pulldown

# D1 USBLC6-2SC6 SOT-23-6
d1 = Footprint("SOT-23-6", 14, 31.5, ref="D1", value="USBLC6-2SC6")
for i, yoff in enumerate([-0.95, 0, 0.95]):
    d1.pad(str(i + 1), -0.95, yoff, 0.9, 0.9)
    d1.pad(str(6 - i), 0.95, yoff, 0.9, 0.9)
b.add(d1.silk_rect(3.0, 2.8))

# --- U2 ME6211 3.3V LDO SOT-23-5 + caps (top-right, below keepout) ---
u2 = Footprint("SOT-23-5", 30.5, 10.5, ref="U2", value="ME6211C33")
for i, yoff in enumerate([-0.95, 0, 0.95]):
    u2.pad(str(i + 1), -0.95, yoff, 0.9, 0.9)        # 1 VIN, 2 GND, 3 EN
u2.pad("4", 0.95, 0.95, 0.9, 0.9).pad("5", 0.95, -0.95, 0.9, 0.9)  # 4 NC, 5 VOUT
b.add(u2.silk_rect(3.0, 2.8))
b.add(c0805("C_0805", 26.0, 9.5, "C2", "10uF"))    # input cap
b.add(c0805("C_0805", 34.8, 13.0, "C1", "10uF"))   # output cap

# --- U3 SHT40 DFN-4 left edge ---
u3 = Footprint("DFN-4-SHT40", 3.4, 15.5, ref="U3", value="SHT40")
u3.pad("1", -0.5, -0.525, 0.5, 0.45).pad("2", -0.5, 0.525, 0.5, 0.45)   # SDA, SCL
u3.pad("3", 0.5, 0.525, 0.5, 0.45).pad("4", 0.5, -0.525, 0.5, 0.45)     # VDD, GND
b.add(u3.silk_rect(1.8, 1.8))

# --- U4 ALS-PT19 + R8 (top-right, outside antenna keepout) ---
b.add(r0603("ALS_0603", 37.2, 17.5, "U4", "ALS-PT19"))
b.add(r0603("R_0603", 37.2, 20.5, "R8", "10k"))

# --- D2 SK6812MINI-E + C5 + R3 ---
d2 = Footprint("SK6812MINI-E", 29.5, 17.5, ref="D2", value="SK6812MINI-E")
d2.pad("1", -1.05, -0.85, 0.85, 0.85).pad("2", 1.05, -0.85, 0.85, 0.85)  # VDD, DIN
d2.pad("3", 1.05, 0.85, 0.85, 0.85).pad("4", -1.05, 0.85, 0.85, 0.85)    # DOUT, GND
b.add(d2.silk_rect(3.6, 3.6))
b.add(r0603("C_0603", 33.6, 17.5, "C5", "100nF"))
b.add(r0603("R_0603", 29.5, 21.0, "R3", "470R"))

# --- SW1 EN, SW2 BOOT ---
b.add(tact("TACT_3x4", 26.5, 27.0, "SW1", "EN"))
b.add(tact("TACT_3x4", 33.5, 27.0, "SW2", "BOOT"))
b.add(r0603("R_0603", 24.0, 23.5, "R4", "10k"))    # EN pullup
b.add(r0603("R_0603", 30.0, 23.8, "R5", "10k"))    # BOOT pullup

# --- J2 UART 1x4 right edge, J3 PIR 1x3 left-bottom ---
b.add(th_header("HDR_1x4", 37.5, 25.0, 4, "J2", "UART 3V3/TX/RX/GND"))
b.add(th_header("HDR_1x3", 2.5, 24.5, 3, "J3", "PIR 3V3/OUT/GND"))

# --- C3 at module 3V3, I2C pullups R6/R7 ---
b.add(r0603("C_0603", 8.5, 13.5, "C3", "100nF"))
b.add(r0603("R_0603", 4.6, 19.0, "R6", "4.7k"))    # SDA pullup
b.add(r0603("R_0603", 4.6, 21.6, "R7", "4.7k"))    # SCL pullup
b.add(r0603("C_0603", 24.5, 12.5, "C4", "100nF"))  # spare decoupling near module 3V3

# ---------------------------------------------------------------- tracks
# ==== Power: VBUS/5V (0.8mm) ====
b.track(17.4, 31.5, 17.4, 29.6, 0.8)                  # J1 VBUS pad down
b.track(17.4, 29.6, 24.0, 29.6, 0.8)
b.track(24.0, 29.6, 24.0, 26.0, 0.8)
b.via(24.0, 26.0, net="+5V")
b.track(24.0, 26.0, 24.0, 25.0, 0.8, layer="B.Cu")
b.track(24.0, 25.0, 29.0, 25.0, 0.8, layer="B.Cu")
b.track(29.0, 25.0, 29.0, 18.0, 0.8, layer="B.Cu")
b.via(29.0, 18.0, net="+5V")
b.track(29.0, 18.0, 29.0, 9.55, 0.8)                  # 5V up to U2 VIN
b.track(29.0, 9.55, 29.55, 9.55, 0.8)                 # -> U2 pad1 VIN
b.track(29.55, 9.55, 27.05, 9.5, 0.8)                 # VIN -> C2 pad1
b.track(29.0, 18.0, 28.45, 16.65, 0.8)                # 5V -> D2 VDD
b.track(28.45, 16.65, 28.45, 16.0, 0.4)
b.track(28.45, 16.0, 32.75, 16.0, 0.4)                # -> C5
b.track(32.75, 16.0, 32.75, 17.5, 0.4)                # C5 pad1
# ==== Power: 3V3 (0.8mm) ====
b.via(32.0, 13.5, net="+3V3")
b.track(32.0, 13.5, 32.6, 9.55, 0.8)                  # via -> U2 VOUT node
b.track(32.6, 9.55, 31.45, 9.55, 0.8)                 # -> U2 pad5 VOUT
b.track(32.6, 9.55, 33.75, 13.0, 0.8)                 # VOUT -> C1 pad1
b.track(24.5, 10.5, 32.0, 10.5, 0.8, layer="B.Cu")    # 3V3 top rail
b.track(32.0, 10.5, 32.0, 13.5, 0.8, layer="B.Cu")
b.track(32.0, 13.5, 32.0, 31.0, 0.8, layer="B.Cu")    # 3V3 down right side
b.track(32.0, 31.0, 20.0, 31.0, 0.8, layer="B.Cu")    # 3V3 along bottom
b.track(20.0, 31.0, 20.0, 29.5, 0.8, layer="B.Cu")
b.via(20.0, 29.5, net="+3V3")
b.track(20.0, 29.5, 9.0, 29.5, 0.8)                   # under module bottom pads
b.track(9.0, 29.5, 9.0, 13.5, 0.8)                    # up left of module
b.track(9.0, 13.5, 9.35, 13.5, 0.8)                   # -> C3 pad2
b.track(7.65, 13.5, 7.65, 11.65, 0.4)                 # C3 pad1 up
b.track(7.65, 11.65, 6.65, 11.65, 0.4)                # -> U1 pad2 (3V3)
b.via(24.5, 10.5, net="+3V3")
b.track(24.5, 10.5, 23.65, 12.5, 0.4)                 # -> C4 pad1
b.track(1.2, 10.5, 24.5, 10.5, 0.8, layer="B.Cu")     # 3V3 left rail
b.track(2.5, 24.5, 1.2, 24.5, 0.4, layer="B.Cu")      # J3 pin1 3V3
b.track(1.2, 24.5, 1.2, 10.5, 0.4, layer="B.Cu")
b.track(4.2, 17.5, 4.2, 10.5, 0.4, layer="B.Cu")      # SHT40 VDD feed
b.via(4.2, 17.5, net="+3V3")
b.track(3.9, 16.025, 4.2, 16.025, 0.4)                # U3 pad3 VDD
b.track(4.2, 16.025, 4.2, 17.5, 0.4)
b.via(36.0, 25.0, net="+3V3")                         # J2 pin1 3V3
b.track(37.5, 25.0, 36.0, 25.0, 0.4)
b.track(36.0, 25.0, 32.0, 25.0, 0.4, layer="B.Cu")
b.via(38.05, 16.0, net="+3V3")                        # U4 pad2 -> 3V3
b.track(38.05, 17.5, 38.05, 16.0, 0.4)
b.track(38.05, 16.0, 32.0, 16.0, 0.4, layer="B.Cu")
b.via(25.5, 22.0, net="+3V3")                         # R4 pad2 -> 3V3
b.track(24.85, 22.0, 25.5, 22.0, 0.4)
b.track(25.5, 22.0, 25.5, 10.5, 0.4, layer="B.Cu")
b.via(32.85, 20.3, net="+3V3")                        # R5 pad2 -> 3V3
b.track(32.85, 21.5, 32.85, 20.3, 0.4)
b.track(32.85, 20.3, 32.0, 20.3, 0.4, layer="B.Cu")
# ==== USB D+/D- (0.4) ====
b.track(19.35, 31.5, 19.35, 32.45, 0.4)               # J1 D+
b.track(19.35, 32.45, 14.95, 32.45, 0.4)              # -> D1 pin6
b.track(18.7, 31.5, 18.7, 33.2, 0.4)                  # J1 D-
b.track(18.7, 33.2, 15.7, 33.2, 0.4)
b.track(15.7, 33.2, 15.7, 31.5, 0.4)
b.track(15.7, 31.5, 14.95, 31.5, 0.4)                 # -> D1 pin5
b.track(13.05, 32.45, 13.05, 29.6, 0.4)               # D1 pin3 (D+)
b.track(13.05, 29.6, 19.5, 29.6, 0.4)                 # below module bottom pads
b.track(19.5, 29.6, 19.5, 18.0, 0.4)
b.track(19.5, 18.0, 21.35, 18.0, 0.4)                 # -> U1 pad20 USB_D+
b.track(13.05, 31.5, 12.2, 31.5, 0.4)                 # D1 pin2 (D-)
b.track(12.2, 31.5, 12.2, 29.0, 0.4)
b.track(12.2, 29.0, 18.9, 29.0, 0.4)
b.track(18.9, 29.0, 18.9, 19.27, 0.4)
b.track(18.9, 19.27, 21.35, 19.27, 0.4)               # -> U1 pad19 USB_D-
# ==== CC resistors ====
b.track(18.05, 31.5, 18.05, 30.2, 0.4)                # CC1
b.track(18.05, 30.2, 24.65, 30.2, 0.4)
b.track(24.65, 30.2, 24.65, 30.0, 0.4)                # -> R1 pad1
b.track(20.0, 31.5, 20.0, 33.0, 0.4)                  # CC2
b.track(20.0, 33.0, 24.65, 33.0, 0.4)
b.track(24.65, 33.0, 24.65, 32.6, 0.4)                # -> R2 pad1
b.track(26.35, 30.0, 26.35, 29.0, 0.4)
b.via(26.35, 29.0, net="GND")                         # R1 pad2 -> GND
b.track(26.35, 32.6, 26.35, 33.4, 0.4)
b.via(26.35, 33.4, net="GND")                         # R2 pad2 -> GND
# ==== I2C: SDA=IO6 pad6 (6.65,16.71), SCL=IO7 pad7 (6.65,18.0) ====
b.track(6.65, 16.71, 4.2, 16.71, 0.4)                 # SDA out
b.track(4.2, 16.71, 2.9, 14.975, 0.4)                 # -> U3 pad1 SDA
b.track(4.2, 16.71, 3.8, 16.71, 0.4)
b.track(3.8, 16.71, 3.8, 19.0, 0.4)
b.track(3.8, 19.0, 3.75, 19.0, 0.4)                   # -> R6 pad1
b.track(6.65, 18.0, 4.4, 18.0, 0.4)                   # SCL out
b.track(4.4, 18.0, 2.9, 16.025, 0.4)                  # -> U3 pad2 SCL
b.track(4.4, 18.0, 4.4, 21.6, 0.4)
b.track(4.4, 21.6, 3.75, 21.6, 0.4)                   # -> R7 pad1
b.track(5.45, 19.0, 5.45, 20.3, 0.4)                  # R6 pad2
b.track(5.45, 20.3, 5.45, 21.6, 0.4)                  # -> R7 pad2 (join 3V3)
b.via(5.45, 20.3, net="+3V3")
# ==== ALS: IO3 pad11 (6.65,23.08) ====
b.via(6.5, 23.08, net="IO3_ALS")
b.track(6.5, 23.08, 6.5, 26.2, 0.4, layer="B.Cu")
b.via(6.5, 26.2, net="IO3_ALS")
b.track(6.5, 26.2, 6.5, 34.6, 0.4)                    # down left area
b.track(6.5, 34.6, 34.0, 34.6, 0.4)                   # along bottom edge
b.track(34.0, 34.6, 34.0, 19.6, 0.4)                  # up right side
b.track(34.0, 19.6, 36.35, 19.6, 0.4)                 # ALS sense node
b.track(36.35, 19.6, 36.35, 17.5, 0.4)                # -> U4 pad1
b.track(36.35, 19.6, 36.35, 20.5, 0.4)                # -> R8 pad1
b.track(38.05, 20.5, 38.05, 22.0, 0.4)
b.via(38.05, 22.0, net="GND")                         # R8 pad2 -> GND
# ==== LED: IO10 pad10 (6.65,21.81) -> R3 -> D2 DIN ====
b.via(6.0, 21.81, net="IO10_LED")
b.track(6.0, 21.81, 6.0, 32.4, 0.4, layer="B.Cu")
b.track(6.0, 32.4, 26.0, 25.8, 0.4, layer="B.Cu")
b.via(26.0, 25.8, net="IO10_LED")
b.track(26.0, 25.8, 28.65, 21.0, 0.4)                 # -> R3 pad1
b.track(30.35, 21.0, 30.55, 16.65, 0.4)               # R3 pad2 -> D2 DIN
b.track(28.45, 18.35, 28.45, 19.6, 0.4)
b.via(28.45, 19.6, net="GND")                         # D2 GND
# ==== EN: pad3 (6.65,12.92); BOOT: pad9 (6.65,20.54) ====
b.track(6.65, 12.92, 5.0, 12.92, 0.4)
b.via(5.0, 12.92, net="EN")
b.track(5.0, 12.92, 23.0, 12.92, 0.4, layer="B.Cu")
b.track(23.0, 12.92, 23.0, 22.9, 0.4, layer="B.Cu")
b.via(23.0, 22.9, net="EN")
b.track(23.0, 22.9, 23.15, 22.0, 0.4)                 # -> R4 pad1
b.track(23.0, 22.9, 24.8, 24.9, 0.4)                  # -> SW1 EN contact
b.track(6.65, 20.54, 4.0, 20.54, 0.4)
b.via(4.0, 20.54, net="IO9_BOOT")
b.track(4.0, 20.54, 4.0, 33.4, 0.4, layer="B.Cu")
b.track(4.0, 33.4, 31.0, 27.0, 0.4, layer="B.Cu")
b.via(31.0, 27.0, net="IO9_BOOT")
b.track(31.0, 27.0, 31.8, 24.9, 0.4)                  # -> SW2 BOOT contact
b.track(31.0, 27.0, 31.15, 21.5, 0.4)                 # -> R5 pad1
# ==== PIR J3: pin2 OUT (2.5,27.04) -> IO4 pad4 (6.65,14.19) ====
b.track(2.5, 27.04, 4.9, 27.04, 0.4)
b.via(4.9, 27.04, net="IO4_PIR")
b.track(4.9, 27.04, 4.9, 14.19, 0.4, layer="B.Cu")
b.via(4.9, 14.19, net="IO4_PIR")
b.track(4.9, 14.19, 6.65, 14.19, 0.4)
# ==== UART J2 TX/RX stubs ====
b.track(37.5, 27.54, 35.5, 27.54, 0.4)
b.via(35.5, 27.54, net="UART_TX")
b.track(37.5, 30.08, 35.5, 30.08, 0.4)
b.via(35.5, 30.08, net="UART_RX")
# ==== GND connections (to B.Cu zone) ====
b.track(16.75, 31.5, 16.75, 30.2, 0.4)
b.via(16.75, 30.2, net="GND")                         # J1 GND
b.track(15.7, 32.4, 15.7, 33.2, 0.4)
b.via(15.7, 33.2, net="GND")                          # J1 SH1
b.track(24.3, 32.4, 24.3, 33.4, 0.4)
b.via(24.3, 33.4, net="GND")                          # J1 SH2
b.track(24.95, 9.5, 24.95, 8.7, 0.4)
b.via(24.95, 8.7, net="GND")                          # C2 pad2 (outside keepout)
b.track(29.55, 10.5, 30.6, 10.5, 0.4)
b.via(30.6, 10.5, net="GND")                          # U2 GND
b.track(35.85, 13.0, 35.85, 13.9, 0.4)
b.via(35.85, 13.9, net="GND")                         # C1 pad2
b.track(25.55, 12.5, 25.55, 13.4, 0.4)
b.via(25.55, 13.4, net="GND")                         # C4 pad2
b.track(35.2, 17.5, 35.2, 17.5, 0.4)                  # (kept for clarity)
b.via(35.2, 17.5, net="GND")                          # C5 pad2 via short track below
b.track(34.45, 17.5, 35.2, 17.5, 0.4)
b.track(3.9, 14.975, 3.9, 13.8, 0.4)
b.via(3.9, 13.8, net="GND")                           # U3 pad4 GND
b.track(28.2, 29.1, 28.2, 30.3, 0.4)
b.via(28.2, 30.3, net="GND")                          # SW1 GND contacts
b.track(35.2, 24.9, 35.2, 29.1, 0.4)                  # SW2 GND contacts join
b.track(35.2, 29.1, 35.2, 30.0, 0.4)
b.track(35.2, 30.0, 34.9, 30.4, 0.4)
b.via(34.9, 30.4, net="GND")
b.track(37.5, 32.62, 36.0, 32.62, 0.4)
b.via(36.0, 32.62, net="GND")                         # J2 pin4 GND
# U2 EN (pad3) tied to VIN
b.track(29.55, 11.45, 28.4, 12.3, 0.4)
b.track(28.4, 12.3, 28.4, 9.0, 0.4)
b.track(28.4, 9.0, 29.1, 9.55, 0.4)
# GND stitching vias (outside antenna keepout y<8)
b.via(1.5, 33.5, net="GND")
b.via(20.0, 33.4, net="GND")
b.via(38.5, 33.5, net="GND")
b.via(23.0, 15.0, net="GND")

# ---------------------------------------------------------------- zone + silk
b.zone("GND", "B.Cu")          # clipped below in write_pcb (antenna keepout y<8)
b.text("RoomNode-C3-Mini", 20, 5.0, 1.3)       # silk inside keepout (ink only, no copper)
b.text("rev A  2026-08", 20, 6.8, 1.0)
b.text("ANTENNA KEEPOUT - NO COPPER", 20, 2.2, 0.8)
b.text("EN", 26.5, 23.2, 0.8)
b.text("BOOT", 33.5, 23.2, 0.8)
b.text("3V3 TX RX GND", 34.6, 23.4, 0.7)
b.text("3V3 OUT GND", 8.5, 25.8, 0.7)

def write_pcb(path):
    src = b.to_kicad()
    # Clip B.Cu GND zone to y>=8.5 (antenna keepout y in [0,8] free of copper)
    src = src.replace("(xy 0 0) (xy 40 0) (xy 40 35) (xy 0 35)",
                      "(xy 0 8.5) (xy 40 8.5) (xy 40 35) (xy 0 8.5)")
    with open(path, "w") as f:
        f.write(src)

# ---------------------------------------------------------------- schematic
s = Schematic("RoomNode-C3-Mini rev A")
s.symbol("U1", "ESP32-C3-MINI-1-N4", 90, 60, w=40, h=50, pins=[
    ("+3V3", "L", 5), ("GND", "L", 10), ("EN", "L", 15), ("IO9_BOOT", "L", 20),
    ("IO6_SDA", "L", 25), ("IO7_SCL", "L", 30), ("IO10_LED", "L", 35), ("IO3_ALS", "L", 40),
    ("IO4_PIR", "R", 5), ("USB_D+", "R", 10), ("USB_D-", "R", 15),
    ("UART_TX", "R", 20), ("UART_RX", "R", 25), ("GND", "R", 30),
])
s.symbol("U2", "ME6211C33 (3V3 LDO)", 40, 30, w=30, h=20, pins=[
    ("VIN_5V", "L", 5), ("GND", "L", 15), ("+3V3", "R", 5), ("EN_VIN", "R", 15)])
s.symbol("J1", "USB-C TYPE-C-31-M-12", 40, 80, w=30, h=25, pins=[
    ("VBUS_5V", "L", 5), ("GND", "L", 10), ("USB_D+", "R", 5), ("USB_D-", "R", 10),
    ("CC1_R1_5k1", "R", 15), ("CC2_R2_5k1", "R", 20)])
s.symbol("D1", "USBLC6-2SC6 ESD", 40, 120, w=26, h=14, pins=[
    ("USB_D+", "L", 5), ("USB_D-", "L", 10), ("GND", "R", 7)])
s.symbol("U3", "SHT40 (I2C 0x44)", 150, 40, w=30, h=16, pins=[
    ("IO6_SDA", "L", 5), ("IO7_SCL", "L", 10), ("+3V3", "R", 5), ("GND", "R", 10)])
s.symbol("U4", "ALS-PT19 + R8 10k", 150, 75, w=30, h=16, pins=[
    ("IO3_ALS_ADC", "L", 5), ("+3V3", "R", 5), ("GND_via_R8", "R", 10)])
s.symbol("D2", "SK6812MINI-E", 150, 105, w=30, h=16, pins=[
    ("IO10_LED_R3_470R", "L", 5), ("+5V", "R", 5), ("GND", "R", 10)])
s.symbol("J2", "UART 1x4", 90, 120, w=24, h=18, pins=[
    ("+3V3", "L", 4), ("UART_TX", "L", 8), ("UART_RX", "L", 12), ("GND", "L", 16)])
s.symbol("J3", "PIR AM312 1x3", 130, 120, w=24, h=14, pins=[
    ("+3V3", "L", 4), ("IO4_PIR", "L", 8), ("GND", "L", 12)])
s.symbol("SW1", "EN btn + R4 10k", 150, 140, w=26, h=12, pins=[("EN", "L", 6), ("GND", "R", 6)])
s.symbol("SW2", "BOOT btn + R5 10k", 90, 150, w=26, h=12, pins=[("IO9_BOOT", "L", 6), ("GND", "R", 6)])
s.label("I2C pullups R6/R7 4.7k to +3V3; C1/C2 10uF, C3/C4/C5 100nF", 90, 175)

# ---------------------------------------------------------------- write all
pcb = os.path.join(HERE, NAME + ".kicad_pcb")
sch = os.path.join(HERE, NAME + ".kicad_sch")
pro = os.path.join(HERE, NAME + ".kicad_pro")
write_pcb(pcb)
open(sch, "w").write(s.to_kicad())
open(pro, "w").write(project_file(NAME))
os.makedirs(RENDERS, exist_ok=True)
b.render(os.path.join(RENDERS, NAME + "_top.png"), side="top", scale=16)
b.render(os.path.join(RENDERS, NAME + "_bottom.png"), side="bottom", scale=16)
print("wrote", pcb, sch, pro)
print("rendered", os.path.join(RENDERS, NAME + "_top.png"), "and _bottom.png")

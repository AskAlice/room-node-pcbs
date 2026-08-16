#!/usr/bin/env python3
"""AirNode-S3 air-quality room node PCB generator (KiCad 8).

Board: 70 x 50 mm, 2-layer, SMD.
  U1 ESP32-S3-WROOM-1-N8R2 (antenna at TOP edge, keepout y in [0,10] copper-free)
  J1 USB-C + CC resistors + ESD, U2 AMS1117-3.3, U3 SCD41, U4 SGP40, U5 SHT40,
  J2 PMS5003 8-pin cable header, D2-D4 SK6812MINI-E, SW1 EN, SW2 BOOT, J3 UART.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from kicad_gen import Board, Footprint, Schematic, project_file

BW, BH = 70.0, 50.0          # board outline


# ---------- footprint helpers ----------
def fp_0603(name, ref, x, y, value=""):
    fp = Footprint(name, x, y, ref=ref, value=value)
    fp.pad("1", -0.85, 0, 0.9, 1.0)
    fp.pad("2", 0.85, 0, 0.9, 1.0)
    fp.silk_rect(1.8, 1.0)
    return fp

def fp_0805(name, ref, x, y, value=""):
    fp = Footprint(name, x, y, ref=ref, value=value)
    fp.pad("1", -1.05, 0, 1.2, 1.4)
    fp.pad("2", 1.05, 0, 1.2, 1.4)
    fp.silk_rect(2.2, 1.4)
    return fp

def fp_esp32s3_wroom(x, y):
    """ESP32-S3-WROOM-1: 18 x 25.5 mm castellated module, antenna toward top (-y)."""
    fp = Footprint("ESP32-S3-WROOM-1", x, y, ref="U1", value="ESP32-S3-WROOM-1-N8R2")
    for i in range(11):   # left column pins 1..11
        fp.pad(str(i + 1), -9.0, 10.0 - i * 1.8, 1.6, 0.9)
    for i in range(11):   # right column pins 30..20
        fp.pad(str(30 - i), 9.0, 10.0 - i * 1.8, 1.6, 0.9)
    for i in range(8):    # bottom row pins 12..19
        fp.pad(str(12 + i), -6.3 + i * 1.8, 12.75, 0.9, 1.6)
    fp.silk_rect(18.0, 25.5)
    return fp

def fp_usbc_31_m_12(x, y):
    fp = Footprint("TYPE-C-31-M-12", x, y, ref="J1", value="USB-C")
    for i in range(12):
        fp.pad(str(i + 1), -5.5 + i * 1.0, 0.0, 0.5, 1.6)
    for i, sx in enumerate([-4.3, 4.3]):
        fp.pad("SH%d" % (i + 1), sx, 2.6, 1.2, 2.0)
    fp.silk_rect(9.0, 7.9)
    return fp

def fp_sot223(x, y):
    fp = Footprint("SOT-223", x, y, ref="U2", value="AMS1117-3.3")
    fp.pad("1", -2.3, 3.1, 1.5, 2.2)   # GND
    fp.pad("2", 0.0, 3.1, 1.5, 2.2)    # VOUT
    fp.pad("3", 2.3, 3.1, 1.5, 2.2)    # VIN
    fp.pad("4", 0.0, -3.1, 3.6, 2.2)   # tab = VOUT
    fp.silk_rect(6.6, 7.0)
    return fp

def fp_scd41(x, y):
    """SCD41 LGA-20: 10.1 x 10.1 mm body, 5 pads per side, 1.25 mm pitch."""
    fp = Footprint("SCD41-LGA-20", x, y, ref="U3", value="SCD41")
    n = 0
    for side in range(4):
        for i in range(5):
            n += 1
            off = -2.5 + i * 1.25
            if side == 0:   fp.pad(str(n), off, -5.05, 0.6, 1.0)
            elif side == 1: fp.pad(str(n), 5.05, off, 1.0, 0.6)
            elif side == 2: fp.pad(str(n), -off, 5.05, 0.6, 1.0)
            else:           fp.pad(str(n), -5.05, -off, 1.0, 0.6)
    fp.silk_rect(10.1, 10.1)
    return fp

def fp_sgp40(x, y):
    fp = Footprint("DFN-6-SGP40", x, y, ref="U4", value="SGP40")
    fp.pad("1", -1.225, -0.95, 0.8, 0.45); fp.pad("2", -1.225, 0.0, 0.8, 0.45)
    fp.pad("3", -1.225, 0.95, 0.8, 0.45)
    fp.pad("4", 1.225, 0.95, 0.8, 0.45);  fp.pad("5", 1.225, 0.0, 0.8, 0.45)
    fp.pad("6", 1.225, -0.95, 0.8, 0.45)
    fp.silk_rect(2.44, 2.44)
    return fp

def fp_sht40(x, y):
    fp = Footprint("DFN-4-SHT40", x, y, ref="U5", value="SHT40")
    fp.pad("1", -0.75, -0.5, 0.7, 0.4); fp.pad("2", -0.75, 0.5, 0.7, 0.4)
    fp.pad("3", 0.75, 0.5, 0.7, 0.4);   fp.pad("4", 0.75, -0.5, 0.7, 0.4)
    fp.silk_rect(1.5, 1.5)
    return fp

def fp_sk6812mini_e(x, y, ref):
    fp = Footprint("SK6812MINI-E", x, y, ref=ref, value="SK6812MINI-E")
    fp.pad("1", -1.35, -1.35, 1.0, 1.0)  # VDD
    fp.pad("2", 1.35, -1.35, 1.0, 1.0)   # DOUT
    fp.pad("3", 1.35, 1.35, 1.0, 1.0)    # GND
    fp.pad("4", -1.35, 1.35, 1.0, 1.0)   # DIN
    fp.silk_rect(3.5, 3.5)
    return fp

def fp_tact(x, y, ref, value):
    fp = Footprint("TACT-4P", x, y, ref=ref, value=value)
    fp.pad("1", -2.6, -1.8, 1.2, 1.2); fp.pad("2", 2.6, -1.8, 1.2, 1.2)
    fp.pad("3", -2.6, 1.8, 1.2, 1.2);  fp.pad("4", 2.6, 1.8, 1.2, 1.2)
    fp.silk_rect(4.6, 4.6)
    return fp

def fp_pms_header(x, y):
    fp = Footprint("PMS5003-8P-1.25", x, y, ref="J2", value="PMS5003")
    for i in range(8):
        fp.pad(str(i + 1), 0.0, -4.375 + i * 1.25, 1.2, 0.8)
    fp.silk_rect(2.4, 11.0)
    return fp

def fp_uart_header(x, y):
    fp = Footprint("HDR-1x4-2.54", x, y, ref="J3", value="UART")
    for i in range(4):
        fp.pad(str(i + 1), 0.0, -3.81 + i * 2.54, 1.8, 1.2)
    fp.silk_rect(2.6, 10.5)
    return fp

def fp_usblc6(x, y):
    fp = Footprint("SOT-23-6", x, y, ref="D1", value="USBLC6-2SC6")
    for i in range(3):
        fp.pad(str(i + 1), -0.95, -0.95 + i * 0.95, 0.9, 0.5)
        fp.pad(str(6 - i), 0.95, -0.95 + i * 0.95, 0.9, 0.5)
    fp.silk_rect(3.0, 2.9)
    return fp


# ---------- board ----------
def build_board():
    b = Board("airnode-s3")
    b.rect_edge(BW, BH)

    # U1 ESP32-S3: antenna toward top edge (y=0); body 18x25.5 at (20,18)
    # -> spans y 5.25..30.75; castellated pads at y >= 10 (outside keepout).
    b.add(fp_esp32s3_wroom(20.0, 18.0))

    # J1 USB-C bottom-left (14,46) + CC resistors + ESD
    b.add(fp_usbc_31_m_12(14.0, 46.0))
    b.add(fp_0603("R_0603", "R1", 20.5, 44.0, "5.1k"))
    b.add(fp_0603("R_0603", "R2", 20.5, 47.5, "5.1k"))
    b.add(fp_usblc6(8.0, 43.0))

    # U2 AMS1117-3.3 + bulk caps
    b.add(fp_sot223(34.0, 44.0))
    b.add(fp_0805("C_0805", "C1", 28.5, 44.0, "10uF"))
    b.add(fp_0805("C_0805", "C2", 40.0, 44.0, "10uF"))

    # U3 SCD41 center-left, airflow clearance around
    b.add(fp_scd41(36.0, 22.0))
    b.add(fp_0603("C_0603", "C5", 36.0, 28.2, "100nF"))

    # U4 SGP40 + U5 SHT40 grouped right of SCD41
    b.add(fp_sgp40(44.0, 20.0))
    b.add(fp_sht40(44.0, 26.0))
    b.add(fp_0603("C_0603", "C6", 48.5, 20.0, "100nF"))
    b.add(fp_0603("C_0603", "C7", 48.5, 26.0, "100nF"))

    # J2 PMS5003 8-pin 1.25mm header, right edge
    b.add(fp_pms_header(66.0, 24.0))

    # D2-D4 SK6812MINI-E top-right, outside keepout (y > 10)
    b.add(fp_sk6812mini_e(54.0, 13.0, "D2"))
    b.add(fp_sk6812mini_e(60.0, 13.0, "D3"))
    b.add(fp_sk6812mini_e(66.0, 13.0, "D4"))
    b.add(fp_0603("C_0603", "C8", 54.0, 17.5, "100nF"))
    b.add(fp_0603("C_0603", "C9", 60.0, 17.5, "100nF"))
    b.add(fp_0603("C_0603", "C10", 66.0, 17.5, "100nF"))
    b.add(fp_0603("R_0603", "R3", 48.5, 12.6, "470R"))

    # SW1 EN, SW2 BOOT, J3 UART
    b.add(fp_tact(48.0, 44.0, "SW1", "EN"))
    b.add(fp_tact(56.0, 44.0, "SW2", "BOOT"))
    b.add(fp_uart_header(64.0, 42.0))

    # module decoupling + pull-ups
    b.add(fp_0603("C_0603", "C3", 6.0, 20.0, "100nF"))
    b.add(fp_0603("C_0603", "C4", 6.0, 24.0, "100nF"))
    b.add(fp_0603("R_0603", "R4", 10.0, 34.0, "10k"))
    b.add(fp_0603("R_0603", "R5", 14.0, 34.0, "10k"))
    b.add(fp_0603("R_0603", "R6", 18.0, 34.0, "4.7k"))
    b.add(fp_0603("R_0603", "R7", 22.0, 34.0, "4.7k"))

    T = b.track
    # ---- 5V rail (1.0 mm): J1 VBUS -> C1 -> U2 VIN(pin3) ; -> J2 pin1 (PMS 5V)
    T(19.5, 46.0, 36.3, 46.0, width=1.0, net="5V")
    T(36.3, 46.0, 36.3, 47.1, width=1.0, net="5V")
    T(27.45, 46.0, 27.45, 44.7, width=1.0, net="5V")          # C1
    T(30.0, 46.0, 30.0, 48.5, width=1.0, net="5V")
    T(30.0, 48.5, 62.5, 48.5, width=1.0, net="5V")            # bottom edge run
    T(62.5, 48.5, 62.5, 19.625, width=1.0, net="5V")          # up right side
    T(62.5, 19.625, 66.0, 19.625, width=1.0, net="5V")        # J2 pin1 = 5V
    # 5V to LED VDD (bus + stubs), all y >= 10.6 (outside antenna keepout)
    T(62.5, 19.625, 64.65, 19.625, width=1.0, net="5V")
    T(64.65, 19.625, 64.65, 10.6, width=1.0, net="5V")
    T(52.65, 10.6, 64.65, 10.6, width=1.0, net="5V")
    for vx in (52.65, 58.65, 64.65):
        T(vx, 10.6, vx, 11.15, width=1.0, net="5V")           # VDD pad stubs

    # ---- 3V3 rail (0.8 mm): U2 VOUT pin2 + tab -> C2, module, sensor bus
    T(34.0, 47.1, 38.95, 47.1, width=0.8, net="3V3")
    T(38.95, 47.1, 38.95, 44.7, width=0.8, net="3V3")         # C2
    T(34.0, 40.9, 34.0, 39.0, width=0.8, net="3V3")           # tab
    T(6.0, 39.0, 54.0, 39.0, width=0.8, net="3V3")            # main 3V3 spine
    T(6.0, 39.0, 6.0, 20.0, width=0.8, net="3V3")             # left edge up
    T(6.0, 20.0, 11.0, 20.0, width=0.8, net="3V3")            # module 3V3 + C3
    T(6.0, 24.0, 11.0, 24.0, width=0.8, net="3V3")            # module 3V3 + C4
    # sensor 3V3 bus (SCD41 bottom pads + C5 + SHT40 + SGP40)
    T(54.0, 39.0, 54.0, 29.0, width=0.8, net="3V3")
    T(35.0, 29.0, 54.0, 29.0, width=0.8, net="3V3")
    T(35.0, 29.0, 35.0, 27.55, width=0.8, net="3V3")          # SCD41 VDD pad
    T(35.15, 29.0, 35.15, 28.7, width=0.8, net="3V3")         # C5
    T(44.75, 29.0, 44.75, 26.5, width=0.8, net="3V3")         # SHT40 VDD
    T(45.225, 29.0, 45.225, 20.95, width=0.8, net="3V3")      # SGP40 VDD

    # ---- I2C (0.4 mm): U1 IO8/IO9 (left col) -> around module bottom -> SCD41
    # SDA: pad (11,20.8)
    T(11.0, 20.8, 8.0, 20.8, width=0.4, net="SDA")
    T(8.0, 20.8, 8.0, 35.0, width=0.4, net="SDA")
    T(8.0, 35.0, 27.0, 35.0, width=0.4, net="SDA")
    T(27.0, 35.0, 27.0, 32.5, width=0.4, net="SDA")
    T(27.0, 32.5, 30.95, 20.75, width=0.4, net="SDA")         # SCD41 SDA pad
    # SCL: pad (11,22.6)
    T(11.0, 22.6, 9.5, 22.6, width=0.4, net="SCL")
    T(9.5, 22.6, 9.5, 32.0, width=0.4, net="SCL")
    T(9.5, 32.0, 28.0, 32.0, width=0.4, net="SCL")
    T(28.0, 32.0, 28.0, 24.0, width=0.4, net="SCL")
    T(28.0, 24.0, 30.95, 23.25, width=0.4, net="SCL")         # SCD41 SCL pad
    # SCD41 -> SGP40 / SHT40
    T(41.05, 20.75, 42.775, 20.95, width=0.4, net="SDA")      # SGP40 SDA
    T(41.05, 24.5, 42.775, 20.0, width=0.4, net="SCL")        # SGP40 SCL
    T(41.05, 22.0, 43.25, 26.5, width=0.4, net="SDA")         # SHT40 SDA
    T(41.05, 23.25, 43.25, 25.5, width=0.4, net="SCL")        # SHT40 SCL

    # ---- UART2 (0.4 mm): U1 IO16/IO17 (right col pads y=13.6/15.4) -> J2 RX/TX
    T(29.0, 13.6, 61.0, 13.6, width=0.4, net="RX2")
    T(61.0, 13.6, 66.0, 23.375, width=0.4, net="RX2")         # J2 pin4 RX
    T(29.0, 15.4, 62.0, 15.4, width=0.4, net="TX2")
    T(62.0, 15.4, 66.0, 24.625, width=0.4, net="TX2")         # J2 pin5 TX

    # ---- LED data (0.4 mm): U1 IO12 (left col pad y=17.2) -> B.Cu under module
    T(11.0, 17.2, 10.0, 17.2, width=0.4, net="LED")
    T(10.0, 17.2, 10.0, 11.0, width=0.4, layer="B.Cu", net="LED")
    T(10.0, 11.0, 47.65, 11.0, width=0.4, layer="B.Cu", net="LED")
    T(47.65, 11.0, 47.65, 12.1, width=0.4, net="LED")         # R3 in
    T(49.35, 12.6, 52.65, 14.35, width=0.4, net="LED_DIN1")   # R3 -> D2 DIN
    T(55.35, 11.65, 58.65, 14.35, width=0.4, net="LED_D2D3")  # D2 DOUT -> D3 DIN
    T(61.35, 11.65, 64.65, 14.35, width=0.4, net="LED_D3D4")  # D3 DOUT -> D4 DIN

    # ---- EN / BOOT: B.Cu jumpers (avoid power rails on F.Cu)
    T(50.6, 42.2, 50.6, 40.0, width=0.4, net="EN")            # SW1 pad
    T(50.6, 40.0, 12.8, 29.2, width=0.4, layer="B.Cu", net="EN")
    T(12.8, 29.2, 12.8, 28.0, width=0.4, net="EN")
    T(12.8, 28.0, 11.0, 28.0, width=0.4, net="EN")            # U1 EN pad (pin3)
    T(53.4, 42.2, 53.4, 40.5, width=0.4, net="IO0")           # SW2 pad
    T(53.4, 40.5, 12.8, 30.5, width=0.4, layer="B.Cu", net="IO0")
    T(12.8, 30.5, 12.8, 26.2, width=0.4, net="IO0")
    T(12.8, 26.2, 11.0, 26.2, width=0.4, net="IO0")           # U1 IO0 pad (pin5)

    # ---- vias (none in antenna keepout y<10)
    for (vx, vy) in [(5, 12), (5, 35), (12, 39), (8, 30), (39.5, 27.8),
                     (50, 36), (67, 33), (67, 47),
                     (34, 41.5), (32.5, 44.5), (35.5, 44.5),   # U2 thermal
                     (10, 17.2), (47.65, 11.0),                 # LED data layer change
                     (50.6, 40.0), (12.8, 29.2),                # EN
                     (53.4, 40.5), (12.8, 30.5)]:               # BOOT
        b.via(vx, vy, d=0.8, drill=0.4, net="GND")

    # B.Cu GND zone (full board)
    b.zone("GND", "B.Cu")

    # ---- silkscreen
    b.text("ANTENNA KEEPOUT - NO COPPER", 45, 5, size=1.0)
    b.text("AirNode-S3", 20, 37.5, size=2.0)
    b.text("rev A  2026-08", 20, 40.5, size=1.2)
    b.text("J1 USB-C", 14, 41.5, size=0.9)
    b.text("U2 THERMAL: pour + vias", 34, 49.5, size=0.9)
    b.text("AIRFLOW - KEEP CLEAR", 37, 33.8, size=0.9)
    b.text("D2-D4 AQI LEDs", 48, 16.5, size=0.9)
    b.text("PMS5003 5V", 55, 33, size=0.9)
    b.text("J3 UART", 58, 39.5, size=0.9)
    b.text("SW1 EN", 43, 40.8, size=0.9)
    b.text("SW2 BOOT", 56, 47.5, size=0.9)
    return b


# ---------- schematic ----------
def build_schematic():
    s = Schematic("AirNode-S3 rev A")
    s.symbol("U1", "ESP32-S3-WROOM-1-N8R2", 40, 40, w=40, h=30, pins=[
        ("3V3", "L", 4), ("GND", "L", 8), ("EN", "L", 12), ("IO0", "L", 16),
        ("IO8_SDA", "R", 4), ("IO9_SCL", "R", 8), ("IO12_LED", "R", 12),
        ("IO16_RX2", "R", 16), ("IO17_TX2", "R", 20),
    ])
    s.symbol("U2", "AMS1117-3.3", 100, 20, w=25, h=15, pins=[
        ("VIN_5V", "L", 4), ("GND", "L", 10), ("VOUT_3V3", "R", 4), ("TAB_3V3", "R", 10),
    ])
    s.symbol("J1", "TYPE-C-31-M-12", 100, 45, w=25, h=18, pins=[
        ("VBUS_5V", "L", 4), ("GND", "L", 10), ("CC1_R1_5k1", "R", 4),
        ("CC2_R2_5k1", "R", 8), ("D+/D-_USBLC6", "R", 12),
    ])
    s.symbol("U3", "SCD41 CO2", 40, 80, w=25, h=15, pins=[
        ("3V3", "L", 4), ("GND", "L", 8), ("SDA", "R", 4), ("SCL", "R", 8),
    ])
    s.symbol("U4", "SGP40 VOC", 75, 80, w=25, h=15, pins=[
        ("3V3", "L", 4), ("GND", "L", 8), ("SDA", "R", 4), ("SCL", "R", 8),
    ])
    s.symbol("U5", "SHT40 T/RH", 110, 80, w=25, h=15, pins=[
        ("3V3", "L", 4), ("GND", "L", 8), ("SDA", "R", 4), ("SCL", "R", 8),
    ])
    s.symbol("J2", "PMS5003 8P", 100, 110, w=30, h=22, pins=[
        ("5V", "L", 4), ("GND", "L", 8), ("SET", "L", 12), ("RX", "L", 16),
        ("TX", "R", 4), ("RESET", "R", 8), ("NC", "R", 12), ("NC", "R", 16),
    ])
    s.symbol("D2", "SK6812MINI-E x3 (D2-D4)", 40, 110, w=30, h=15, pins=[
        ("5V", "L", 4), ("GND", "L", 8), ("DIN_R3_470R", "R", 4), ("DOUT_chain", "R", 8),
    ])
    for net, x, y in [("3V3", 88, 18), ("5V", 88, 43), ("SDA", 60, 82),
                      ("SCL", 60, 86), ("RX2", 92, 112), ("TX2", 92, 116),
                      ("LED", 60, 112), ("EN", 30, 50), ("BOOT", 30, 54),
                      ("GND", 30, 58)]:
        s.label(net, x, y)
    return s


def main():
    out = HERE
    b = build_board()
    with open(os.path.join(out, "airnode-s3.kicad_pcb"), "w") as f:
        f.write(b.to_kicad())
    s = build_schematic()
    with open(os.path.join(out, "airnode-s3.kicad_sch"), "w") as f:
        f.write(s.to_kicad())
    with open(os.path.join(out, "airnode-s3.kicad_pro"), "w") as f:
        f.write(project_file("airnode-s3"))
    rdir = os.path.join(ROOT, "renders")
    os.makedirs(rdir, exist_ok=True)
    b.render(os.path.join(rdir, "airnode-s3_top.png"), side="top", scale=12)
    b.render(os.path.join(rdir, "airnode-s3_bottom.png"), side="bottom", scale=12)
    print("OK: airnode-s3.kicad_pcb/.kicad_sch/.kicad_pro + renders")


if __name__ == "__main__":
    main()

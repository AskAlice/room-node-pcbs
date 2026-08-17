#!/usr/bin/env python3
"""Inject (model ...) 3D bindings into generated .kicad_pcb footprints.

Maps our local: footprint names to KiCad bundled STEP models
(KICAD3D = KiCad installation 3dmodels dir) or project STEP files
copied into boards/<board>/models/ and referenced via ${KIPRJMOD}.

Usage: python3 tools/add_3d_models.py <board.kicad_pcb> [...]
Idempotent: existing (model blocks are stripped first.
"""
import re, shutil, sys, os

def _find_3droot():
    for cand in (os.environ.get("KICAD3DROOT"), "/mnt/agents/tools/AppDir/share/kicad/3dmodels",
                 "/tmp/kicad/squashfs-root/usr/share/kicad/3dmodels",
                 "/tmp/kicad/AppDir/usr/share/kicad/3dmodels",
                 "/tmp/squashfs-root/usr/share/kicad/3dmodels",
                 "/usr/share/kicad/3dmodels"):
        if cand and os.path.isdir(cand):
            return cand
    return None

KICAD3D = _find_3droot() or "/usr/share/kicad/3dmodels"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# footprint name -> (source STEP path, dest name when copied into board models/)
K = KICAD3D
MODEL_MAP = {
    "R_0603":            (f"{K}/Resistor_SMD.3dshapes/R_0603_1608Metric.step", None),
    "C_0603":            (f"{K}/Capacitor_SMD.3dshapes/C_0603_1608Metric.step", None),
    "C_0805":            (f"{K}/Capacitor_SMD.3dshapes/C_0805_2012Metric.step", None),
    "SOT-23-5":          (f"{K}/Package_TO_SOT_SMD.3dshapes/SOT-23-5.step", None),
    "SOT-23":            (f"{K}/Package_TO_SOT_SMD.3dshapes/SOT-23.step", None),
    "SOT-223":           (f"{K}/Package_TO_SOT_SMD.3dshapes/SOT-223.step", None),
    "HDR-1x3":           (f"{K}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x03_P2.54mm_Vertical.step", None),
    "HDR-1x4":           (f"{K}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step", None),
    "HDR-1x6":           (f"{K}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x06_P2.54mm_Vertical.step", None),
    "HDR-1x2":           (f"{K}/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x02_P2.54mm_Vertical.step", None),
    "TYPE-C-31-M-12":    (f"{K}/Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step", None),
    "WS2812B-V5":        (f"{K}/LED_SMD.3dshapes/LED_WS2812B_PLCC4_5.0x5.0mm_P3.2mm.step", None),
    "WS2812B-MINI":      (f"{K}/LED_SMD.3dshapes/LED_SK6812MINI-E_3.2x2.8mm_P1.5mm_ReverseMount.step", None),
    "SK6812":            (f"{K}/LED_SMD.3dshapes/LED_SK6812MINI-E_3.2x2.8mm_P1.5mm_ReverseMount.step", None),
    "TACT-3x4":          (f"{K}/Button_Switch_SMD.3dshapes/Panasonic_EVQPUJ_EVQPUA.step", None),
    # project STEP models (datasheet-accurate) — copied into boards/<b>/models/
    "ESP32-S3-WROOM-1":  (f"{REPO}/models/ESP32-S3-WROOM-1.STEP", "ESP32-S3-WROOM-1.STEP"),
    "ESP32-C6-WROOM-1":  (f"{REPO}/models/ESP32-C6-WROOM-1.STEP", "ESP32-C6-WROOM-1.STEP"),
    "ESP32-C3-MINI-1":   (f"{REPO}/models/ESP32-C3-MINI-1.STEP", "ESP32-C3-MINI-1.STEP"),
    "SCD41":             (f"{REPO}/models/Sensirion_SCD4x.step", "Sensirion_SCD4x.step"),
    "SCD4":              (f"{REPO}/models/Sensirion_SCD4x.step", "Sensirion_SCD4x.step"),
}
# best-effort package generics from KiCad lib
GENERIC = [
    ("DFN-8",  f"{K}/Package_DFN_QFN.3dshapes/DFN-8-1EP_3x2mm_P0.5mm_EP1.3x1.5mm.step"),
    ("DFN-6",  f"{K}/Package_DFN_QFN.3dshapes/DFN-6-1EP_1.6x1.6mm_P0.5mm_EP0.64x1.28mm.step"),
    ("WSOF6",  f"{K}/Package_DFN_QFN.3dshapes/DFN-6-1EP_1.6x1.6mm_P0.5mm_EP0.64x1.28mm.step"),
    ("LGA-8",  f"{K}/Package_LGA.3dshapes/Bosch_LGA-8_2.5x2.5mm_P0.65mm_ClockwisePinNumbering.step"),
    ("LGA-20", f"{K}/Package_LGA.3dshapes/AMS_LGA-20_4.7x4.5mm_P0.65mm.step"),
]

def find_model(fpname):
    """fpname like local:R_0603 -> (path, project_rel or None)"""
    short = fpname.split(":", 1)[-1]
    for key, (path, dest) in MODEL_MAP.items():
        if key in short and os.path.exists(path):
            return path, dest
    for key, path in GENERIC:
        if key in short and os.path.exists(path):
            return path, None
    return None, None

def split_footprints(text):
    """yield (start, end, body) of each top-level (footprint ...) inside file"""
    out = []
    for m in re.finditer(r"\(footprint\s", text):
        depth = 0
        i = m.start()
        for j in range(i, len(text)):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    out.append((i, j + 1, text[i:j + 1]))
                    break
    return out

MODEL_BLOCK = '\n    (model "%s"\n      (offset (xyz 0 0 0))\n      (scale (xyz 1 1 1))\n      (rotate (xyz 0 0 0))\n    )'

def process(pcb_path):
    text = open(pcb_path).read()
    board_dir = os.path.dirname(pcb_path)
    models_dir = os.path.join(board_dir, "models")
    fps = split_footprints(text)
    patched = 0
    # rebuild from the end so offsets stay valid
    for start, end, body in reversed(fps):
        m = re.match(r'\(footprint\s+"([^"]+)"', body)
        if not m:
            continue
        name = m.group(1)
        # strip existing model blocks
        body2 = re.sub(r'\n?\s*\(model\s+"[^"]*"\s*(\([^()]*\([^()]*\)[^()]*\)\s*){3}\)', "", body)
        path, dest = find_model(name)
        if not path:
            continue
        if dest:  # project model: copy into board models/ and use ${KIPRJMOD}
            os.makedirs(models_dir, exist_ok=True)
            shutil.copy(path, os.path.join(models_dir, dest))
            ref = "${KIPRJMOD}/models/" + dest
        else:
            ref = path
        body2 = body2[:-1] + MODEL_BLOCK % ref + ")"
        text = text[:start] + body2 + text[end:]
        patched += 1
    open(pcb_path, "w").write(text)
    print(f"{pcb_path}: {patched}/{len(fps)} footprints got 3D models")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        process(p)

#!/usr/bin/env python3
"""Minimal KiCad 8 .kicad_pcb generator + PNG renderer for room-node boards.

Produces syntactically valid KiCad 8 board files with rectangular/SMD pads,
silkscreen labels, edge cuts, tracks and zones, then renders top/bottom PNGs.
No KiCad installation required.
"""
import uuid, math

def _u(): return str(uuid.uuid4())

LAYERS_CU = {"F.Cu", "B.Cu"}

class Pad:
    def __init__(self, num, x, y, w, h, shape="rect", layers=("F.Cu",), drill=None, net=None):
        self.num=num; self.x=x; self.y=y; self.w=w; self.h=h
        self.shape=shape; self.layers=layers; self.drill=drill; self.net=net

class Footprint:
    def __init__(self, name, x, y, rot=0, layer="F.Cu", ref="", value=""):
        self.name=name; self.x=x; self.y=y; self.rot=rot; self.layer=layer
        self.ref=ref or name; self.value=value
        self.pads=[]; self.silk=[]; self.fab_w=None; self.fab_h=None
    def pad(self, num, x, y, w, h, shape="rect", layers=("F.Cu",), drill=None, net=None):
        self.pads.append(Pad(num,x,y,w,h,shape,layers,drill,net)); return self
    def silk_rect(self, w, h):
        self.fab_w=w; self.fab_h=h; return self

class Board:
    def __init__(self, name):
        self.name=name; self.footprints=[]; self.tracks=[]; self.texts=[]
        self.edge=None; self.zones=[]; self.vias=[]
    def add(self, fp): self.footprints.append(fp); return fp
    def track(self, x1,y1,x2,y2,width=0.3,layer="F.Cu",net=""):
        self.tracks.append((x1,y1,x2,y2,width,layer,net))
    def text(self, s, x, y, size=1.2, layer="F.SilkS"):
        self.texts.append((s,x,y,size,layer))
    def rect_edge(self, w, h, x=0, y=0):
        self.edge=(x,y,w,h)
    def zone(self, net, layer="B.Cu"):
        self.zones.append((net,layer))
    def via(self, x, y, d=0.8, drill=0.4, net=""):
        self.vias.append((x,y,d,drill,net))

    # ---- KiCad 8 writer ----
    def to_kicad(self):
        out=[]
        out.append('(kicad_pcb (version 20240108) (generator "room-node-gen")')
        out.append('  (general (thickness 1.6))')
        out.append('  (paper "A4")')
        layers=['(0 "F.Cu" signal)','(31 "B.Cu" signal)',
                '(32 "B.Adhes" user "B.Adhesive")','(33 "F.Adhes" user "F.Adhesive")',
                '(36 "B.SilkS" user "B.Silkscreen")','(37 "F.SilkS" user "F.Silkscreen")',
                '(38 "B.Mask" user)','(39 "F.Mask" user)',
                '(44 "Edge.Cuts" user)','(46 "B.CrtYd" user)','(47 "F.CrtYd" user)',
                '(48 "B.Fab" user)','(49 "F.Fab" user)']
        out.append('  (layers ' + ' '.join(layers) + ')')
        out.append('  (net 0 "")')
        for fp in self.footprints:
            lay = fp.layer
            out.append(f'  (footprint "local:{fp.name}" (layer "{lay}") (uuid "{_u()}")')
            out.append(f'    (at {fp.x:.3f} {fp.y:.3f} {fp.rot})')
            out.append(f'    (property "Reference" "{fp.ref}" (at 0 -2 0) (layer "F.SilkS") (uuid "{_u()}") (effects (font (size 1 1) (thickness 0.15))))')
            out.append(f'    (property "Value" "{fp.value}" (at 0 2 0) (layer "F.Fab") (uuid "{_u()}") (effects (font (size 1 1) (thickness 0.15))))')
            if fp.fab_w:
                w,h=fp.fab_w/2,fp.fab_h/2
                out.append(f'    (fp_rect (start {-w:.3f} {-h:.3f}) (end {w:.3f} {h:.3f}) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab") (uuid "{_u()}"))')
                sw,sh=w+0.15,h+0.15
                out.append(f'    (fp_rect (start {-sw:.3f} {-sh:.3f}) (end {sw:.3f} {sh:.3f}) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS") (uuid "{_u()}"))')
            for p in fp.pads:
                shape=p.shape
                laystr=' '.join(f'"{l}"' for l in p.layers)
                drill=f' (drill {p.drill})' if p.drill else ''
                net=''
                out.append(f'    (pad "{p.num}" smd {shape} (at {p.x:.3f} {p.y:.3f}) (size {p.w:.3f} {p.h:.3f}) (layers {laystr}){drill}{net} (uuid "{_u()}"))')
            out.append('  )')
        if self.edge:
            x,y,w,h=self.edge
            for (x1,y1,x2,y2) in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:
                out.append(f'  (gr_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (uuid "{_u()}"))')
        for (x1,y1,x2,y2,width,layer,net) in self.tracks:
            out.append(f'  (segment (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (width {width}) (layer "{layer}") (net 0) (uuid "{_u()}"))')
        for (x,y,d,drill,net) in self.vias:
            out.append(f'  (via (at {x:.3f} {y:.3f}) (size {d}) (drill {drill}) (layers "F.Cu" "B.Cu") (net 0) (uuid "{_u()}"))')
        for (s,x,y,size,layer) in self.texts:
            out.append(f'  (gr_text "{s}" (at {x:.3f} {y:.3f} 0) (layer "{layer}") (uuid "{_u()}") (effects (font (size {size} {size}) (thickness 0.2))))')
        for (net,layer) in self.zones:
            x,y,w,h=self.edge
            pts=f'(xy {x} {y}) (xy {x+w} {y}) (xy {x+w} {y+h}) (xy {x} {y+h})'
            out.append(f'  (zone (net 0) (net_name "{net}") (layer "{layer}") (uuid "{_u()}") (hatch edge 0.5) (connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no) (fill (thermal_gap 0.3) (thermal_bridge_width 0.3)) (polygon (pts {pts})))')
        out.append(')')
        return '\n'.join(out)

    # ---- PNG renderer ----
    def render(self, path, side="top", scale=20):
        from PIL import Image, ImageDraw, ImageFont
        x0,y0,w,h=self.edge
        pad=4
        W=int((w+2*pad)*scale); H=int((h+2*pad)*scale)
        def T(x,y):
            xx=(x-x0+pad)*scale; yy=(y-y0+pad)*scale
            return (xx, yy if side=="top" else H-yy)
        img=Image.new("RGB",(W,H),(10,40,20))  # dark green soldermask
        d=ImageDraw.Draw(img)
        # board area
        d.rectangle([T(x0,y0),T(x0+w,y0+h)][0:1] and [*T(x0,y0 if side=="top" else y0+h),*T(x0+w,y0+h if side=="top" else y0)], fill=(18,75,35))
        # zones as copper tint
        for (net,layer) in self.zones:
            if (side=="top")==(layer=="F.Cu"):
                d.rectangle([*T(x0,y0 if side=="top" else y0+h),*T(x0+w,y0+h if side=="top" else y0)], fill=(20,82,40))
        # tracks
        for (x1,y1,x2,y2,width,layer,net) in self.tracks:
            if (side=="top")==(layer=="F.Cu"):
                d.line([T(x1,y1),T(x2,y2)], fill=(212,175,55), width=max(2,int(width*scale)))
        # footprints
        flip = side=="bottom"
        for fp in self.footprints:
            fx,fy=fp.x,fp.y
            if fp.fab_w and ((side=="top") == (fp.layer=="F.Cu")):
                hw,hh=fp.fab_w/2,fp.fab_h/2
                p1=T(fx-hw, fy+hh if flip else fy-hh); p2=T(fx+hw, fy-hh if flip else fy+hh)
                d.rectangle([p1,p2], fill=(40,40,45), outline=(200,200,200))
                # silk outline
                d.rectangle([T(fx-hw-0.15, fy+hh+0.15 if flip else fy-hh-0.15),
                             T(fx+hw+0.15, fy-hh-0.15 if flip else fy+hh+0.15)], outline=(235,235,235))
            for p in fp.pads:
                if (side=="top") == ("F.Cu" in p.layers):
                    px,py=fx+p.x, fy+p.y
                    hw,hh=p.w/2,p.h/2
                    c1=T(px-hw, py+hh if flip else py-hh); c2=T(px+hw, py-hh if flip else py+hh)
                    d.rectangle([c1,c2], fill=(230,190,80))
        for (x,y,dia,drill,net) in self.vias:
            cx,cy=T(x,y); r=dia/2*scale
            d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(230,190,80))
            rd=drill/2*scale; d.ellipse([cx-rd,cy-rd,cx+rd,cy+rd], fill=(0,0,0))
        # silk text
        for (s,x,y,size,layer) in self.texts:
            if (side=="top") == (layer=="F.SilkS"):
                cx,cy=T(x,y)
                d.text((cx,cy), s, fill=(240,240,240), anchor="mm")
        img.save(path)
        return path


class Schematic:
    """Minimal KiCad 8 .kicad_sch writer: parts as labeled boxes with pins + net wires."""
    def __init__(self, title):
        self.title=title; self.symbols=[]; self.labels=[]
    def symbol(self, ref, value, x, y, w=30, h=20, pins=None):
        # pins: list of (name, side('L'/'R'), offset_from_top)
        self.symbols.append((ref,value,x,y,w,h,pins or [])); return (x,y,w,h)
    def label(self, net, x, y):
        self.labels.append((net,x,y))
    def to_kicad(self):
        out=['(kicad_sch (version 20231120) (generator "room-node-gen")',
             f'  (uuid "{_u()}")','  (paper "A3")',
             f'  (title_block (title "{self.title}") (date "2026-08-16"))']
        libsym = ('(lib_symbols (symbol "local:Box" (pin_numbers hide) (pin_names (offset 0.5)) '
                  '(property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27)))) '
                  '(property "Value" "Box" (at 0 0 0) (effects (font (size 1.27 1.27)))) '
                  '(symbol "Box_0_1" (rectangle (start -10 -10) (end 10 10) (stroke (width 0.254) (type default)) (fill (type outline)))) '
                  '(symbol "Box_1_1" PINPLACEHOLDER)))')
        out.append('  '+libsym.replace('PINPLACEHOLDER',''))
        for (ref,value,x,y,w,h,pins) in self.symbols:
            out.append(f'  (symbol (lib_id "local:Box") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{_u()}")')
            out.append(f'    (property "Reference" "{ref}" (at {x} {y-h/2-3} 0) (effects (font (size 1.27 1.27))))')
            out.append(f'    (property "Value" "{value}" (at {x} {y+h/2+3} 0) (effects (font (size 1.27 1.27)))))')
            # draw box as sch rectangle instead of relying on pinless symbol
            out.append(f'  (rect (start {x-w/2} {y-h/2}) (end {x+w/2} {y+h/2}) (stroke (width 0.254) (type default)) (fill (type outline)) (uuid "{_u()}"))')
            for (pname,side,off) in pins:
                if side=='L': px,py,ang=x-w/2-2.54,y-h/2+off,0
                else: px,py,ang=x+w/2+2.54,y-h/2+off,180
                out.append(f'  (label "{pname}" (at {px} {py} {ang}) (effects (font (size 1.27 1.27))) (uuid "{_u()}"))')
        for (net,x,y) in self.labels:
            out.append(f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1.27 1.27))) (uuid "{_u()}"))')
        out.append(f'  (sheet_instances (path "/" (page "1")))')
        out.append(')')
        return '\n'.join(out)


def project_file(name):
    return '{"board":{"design_settings":{"defaults":{"board_thickness":1.6}}},"meta":{"filename":"%s.kicad_pro","version":1},"schematic":{"drawing":{"default_line_thickness":6}}}' % name

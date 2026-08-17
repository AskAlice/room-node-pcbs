#!/usr/bin/env python3
"""Minimal KiCad 8 .kicad_pcb generator + PNG renderer for room-node boards.

Produces syntactically valid KiCad 8 board files with rectangular/SMD pads,
silkscreen labels, edge cuts, tracks, vias, zones and rule_area keepouts,
then renders top/bottom PNGs.  No KiCad installation required.

Net handling: pads/tracks/vias/zones accept a net *name*.  Names are mapped
to KiCad net numbers in declaration order (GND is always net 1).  Any pad,
segment or via left without an explicit name inherits its net by geometric
connectivity (union-find over touching copper) so no copper stays on net 0
unless it is truly unconnected.
"""
import uuid, math

def _u(): return str(uuid.uuid4())

LAYERS_CU = {"F.Cu", "B.Cu"}

class Pad:
    def __init__(self, num, x, y, w, h, shape="rect", layers=None, drill=None,
                 net=None, rot=0):
        self.num=num; self.x=x; self.y=y; self.w=w; self.h=h
        self.shape=shape; self.drill=drill; self.net=net; self.rot=rot
        if layers is None:
            # KiCad convention: SMD pads carry F.Cu+F.Mask+F.Paste,
            # through-hole pads carry F.Cu/B.Cu + F.Mask/B.Mask.
            layers = ("F.Cu", "B.Cu", "F.Mask", "B.Mask") if drill else \
                     ("F.Cu", "F.Mask", "F.Paste")
        self.layers = tuple(layers)
    def wh(self):
        """Effective width/height after rotation."""
        return (self.h, self.w) if self.rot % 180 else (self.w, self.h)

class Footprint:
    def __init__(self, name, x, y, rot=0, layer="F.Cu", ref="", value="", lcsc=None):
        self.name=name; self.x=x; self.y=y; self.rot=rot; self.layer=layer
        self.ref=ref or name; self.value=value; self.lcsc=lcsc
        self.pads=[]; self.silk=[]; self.fab_w=None; self.fab_h=None
        self.fab_ox=0.0; self.fab_oy=0.0; self.model=None
    def pad(self, num, x, y, w, h, shape="rect", layers=None, drill=None,
            net=None, rot=0):
        self.pads.append(Pad(num,x,y,w,h,shape,layers,drill,net,rot)); return self
    def nets(self, mapping):
        """Tag pad nets from a {pad_number: net_name} dict."""
        for p in self.pads:
            if p.num in mapping: p.net = mapping[p.num]
        return self
    def silk_rect(self, w, h, ox=0.0, oy=0.0):
        self.fab_w=w; self.fab_h=h; self.fab_ox=ox; self.fab_oy=oy; return self
    def model3d(self, path, ox=0.0, oy=0.0, oz=0.0):
        self.model=(path, ox, oy, oz); return self

class Board:
    def __init__(self, name):
        self.name=name; self.footprints=[]; self.tracks=[]; self.texts=[]
        self.edge=None; self.zones=[]; self.vias=[]; self.keepouts=[]
        self._nets=[""]           # index == net number; net 0 is unnamed
        self.net_id("GND")        # GND is always net 1
    def add(self, fp): self.footprints.append(fp); return fp
    def net_id(self, name):
        if name not in self._nets: self._nets.append(name)
        return self._nets.index(name)
    def track(self, x1,y1,x2,y2,width=0.3,layer="F.Cu",net=""):
        self.tracks.append([x1,y1,x2,y2,width,layer,net])
    def text(self, s, x, y, size=1.2, layer="F.SilkS"):
        self.texts.append((s,x,y,size,layer))
    def rect_edge(self, w, h, x=0, y=0):
        self.edge=(x,y,w,h)
    def keepout(self, x1, y1, x2, y2, name="antenna keepout"):
        """Rectangular rule_area: no tracks/vias/pads/copper/footprints, all layers."""
        self.keepouts.append((min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2),name))
    def zone(self, net, layer="B.Cu", pts=None):
        self.zones.append((net,layer,pts))
    def via(self, x, y, d=0.8, drill=0.4, net=""):
        self.vias.append([x,y,d,drill,net])

    # ---- geometric net propagation ------------------------------------
    def _assign_nets(self):
        """Union-find over copper; unnamed items inherit the net of touching
        named items.  Items touching nothing named stay on net 0."""
        parent={}
        def find(a):
            parent.setdefault(a,a)
            while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
            return a
        def union(a,b): parent[find(a)]=find(b)

        pads=[]   # (id, cx, cy, hw, hh, layers, net, pad)
        for fp in self.footprints:
            for p in fp.pads:
                w,h=p.wh()
                pads.append([fp.x+p.x, fp.y+p.y, w/2, h/2, p.layers, p.net, p])
        segs=[[t[0],t[1],t[2],t[3],t[4],t[5],t[6],t] for t in self.tracks]
        vias=[[v[0],v[1],v[2]/2,v[4],v] for v in self.vias]

        def pseg_dist(px,py,x1,y1,x2,y2):
            dx,dy=x2-x1,y2-y1; L2=dx*dx+dy*dy
            t=0 if L2==0 else max(0,min(1,((px-x1)*dx+(py-y1)*dy)/L2))
            return math.hypot(px-(x1+t*dx), py-(y1+t*dy))
        def prect_dist(px,py,cx,cy,hw,hh):
            return math.hypot(max(abs(px-cx)-hw,0), max(abs(py-cy)-hh,0))
        def seg_rect_dist(s,cx,cy,hw,hh):
            """Min distance between segment centerline and pad rect."""
            if _seg_rect_intersect(s[0],s[1],s[2],s[3],cx,cy,hw,hh): return 0.0
            ds=[prect_dist(s[0],s[1],cx,cy,hw,hh), prect_dist(s[2],s[3],cx,cy,hw,hh)]
            for px,py in ((cx-hw,cy-hh),(cx+hw,cy-hh),(cx-hw,cy+hh),(cx+hw,cy+hh)):
                ds.append(pseg_dist(px,py,s[0],s[1],s[2],s[3]))
            return min(ds)
        def seg_seg_touch(s,t):
            if s[5]!=t[5]: return False
            r=(s[4]+t[4])/2-0.01
            if _seg_intersect(s[0],s[1],s[2],s[3],t[0],t[1],t[2],t[3]): return True
            for (px,py) in ((s[0],s[1]),(s[2],s[3])):
                if pseg_dist(px,py,t[0],t[1],t[2],t[3])<=r: return True
            for (px,py) in ((t[0],t[1]),(t[2],t[3])):
                if pseg_dist(px,py,s[0],s[1],s[2],s[3])<=r: return True
            return False
        def pad_seg_touch(p,s):
            if s[5] not in p[4]: return False
            return seg_rect_dist(s,p[0],p[1],p[2],p[3]) <= s[4]/2-0.01
        def pad_via_touch(p,v):
            return prect_dist(v[0],v[1],p[0],p[1],p[2],p[3]) <= v[2]-0.01
        def seg_via_touch(s,v):
            return pseg_dist(v[0],v[1],s[0],s[1],s[2],s[3])<=s[4]/2+v[2]-0.01

        for i in range(len(segs)):
            for j in range(i+1,len(segs)):
                if seg_seg_touch(segs[i],segs[j]): union(("s",i),("s",j))
        for i,p in enumerate(pads):
            for j,s in enumerate(segs):
                if pad_seg_touch(p,s): union(("p",i),("s",j))
            for j,v in enumerate(vias):
                if pad_via_touch(p,v): union(("p",i),("v",j))
        for i,v in enumerate(vias):
            for j,s in enumerate(segs):
                if seg_via_touch(s,v): union(("v",i),("s",j))

        names={}
        self.net_conflicts=[]
        coord={("p",i):(pads[i][0],pads[i][1]) for i in range(len(pads))}
        coord.update({("s",i):(segs[i][0],segs[i][1]) for i in range(len(segs))})
        coord.update({("v",i):(vias[i][0],vias[i][1]) for i in range(len(vias))})
        items=[("p",i,pads[i][5]) for i in range(len(pads))] + \
              [("s",i,segs[i][6]) for i in range(len(segs))] + \
              [("v",i,vias[i][3]) for i in range(len(vias))]
        for kind,i,net in items:
            if net:
                r=find((kind,i))
                if r in names and names[r]!=net:
                    if (names[r],net) not in [(a,b) for a,b,_ in self.net_conflicts]:
                        self.net_conflicts.append((names[r],net,r))
                        x,y=coord[(kind,i)]
                        print(f"  !! net conflict: '{names[r]}' vs '{net}' "
                              f"(copper short near {kind}:{i} @({x:.2f},{y:.2f}))")
                names.setdefault(r,net)
        for kind,i,net in items:
            n=names.get(find((kind,i)),"")
            if kind=="p": pads[i][6].net=n or pads[i][6].net
            elif kind=="s": segs[i][7][6]=n
            else: vias[i][4][4]=n

    # ---- KiCad 8 writer ----
    def to_kicad(self):
        self._assign_nets()
        out=[]
        out.append('(kicad_pcb (version 20240108) (generator "room-node-gen")')
        out.append('  (general (thickness 1.6))')
        out.append('  (paper "A4")')
        layers=['(0 "F.Cu" signal)','(31 "B.Cu" signal)',
                '(32 "B.Adhes" user "B.Adhesive")','(33 "F.Adhes" user "F.Adhesive")',
                '(34 "B.Paste" user)','(35 "F.Paste" user)',
                '(36 "B.SilkS" user "B.Silkscreen")','(37 "F.SilkS" user "F.Silkscreen")',
                '(38 "B.Mask" user)','(39 "F.Mask" user)',
                '(44 "Edge.Cuts" user)','(46 "B.CrtYd" user)','(47 "F.CrtYd" user)',
                '(48 "B.Fab" user)','(49 "F.Fab" user)']
        out.append('  (layers ' + ' '.join(layers) + ')')
        # 2-layer JLCPCB design rules live in the companion .kicad_dru file
        # (KiCad 10 rejects design_rules/defaults blocks inside setup).
        out.append('  (setup (pad_to_mask_clearance 0.05) (allow_soldermask_bridges_in_footprints no))')
        for i,name in enumerate(self._nets):
            out.append(f'  (net {i} "{name}")')
        for fp in self.footprints:
            lay = fp.layer
            out.append(f'  (footprint "local:{fp.name}" (layer "{lay}") (uuid "{_u()}")')
            out.append(f'    (at {fp.x:.3f} {fp.y:.3f} {fp.rot})')
            out.append(f'    (property "Reference" "{fp.ref}" (at 0 -2 0) (layer "F.SilkS") (uuid "{_u()}") (effects (font (size 1 1) (thickness 0.15))))')
            out.append(f'    (property "Value" "{fp.value}" (at 0 2 0) (layer "F.Fab") (uuid "{_u()}") (effects (font (size 1 1) (thickness 0.15))))')
            if fp.lcsc:
                out.append(f'    (property "LCSC" "{fp.lcsc}" (at 0 0 0) (layer "F.Fab") (uuid "{_u()}") (effects (font (size 1 1) (thickness 0.15)) (hide yes)))')
            if fp.fab_w:
                ox,oy=fp.fab_ox,fp.fab_oy
                w,h=fp.fab_w/2,fp.fab_h/2
                out.append(f'    (fp_rect (start {ox-w:.3f} {oy-h:.3f}) (end {ox+w:.3f} {oy+h:.3f}) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab") (uuid "{_u()}"))')
                sw,sh=w+0.15,h+0.15
                out.append(f'    (fp_rect (start {ox-sw:.3f} {oy-sh:.3f}) (end {ox+sw:.3f} {oy+sh:.3f}) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS") (uuid "{_u()}"))')
            for p in fp.pads:
                shape=p.shape
                laystr=' '.join(f'"{l}"' for l in p.layers)
                drill=f' (drill {p.drill})' if p.drill else ''
                rot=f' {p.rot}' if p.rot else ''
                net=f' (net {self.net_id(p.net)} "{p.net}")' if p.net else ''
                pth='thru_hole' if p.drill else 'smd'
                out.append(f'    (pad "{p.num}" {pth} {shape} (at {p.x:.3f} {p.y:.3f}{rot}) (size {p.w:.3f} {p.h:.3f}) (layers {laystr}){drill}{net} (uuid "{_u()}"))')
            out.append('  )')
        if self.edge:
            x,y,w,h=self.edge
            for (x1,y1,x2,y2) in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:
                out.append(f'  (gr_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (uuid "{_u()}"))')
        for (x1,y1,x2,y2,width,layer,net) in self.tracks:
            out.append(f'  (segment (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (width {width}) (layer "{layer}") (net {self.net_id(net) if net else 0}) (uuid "{_u()}"))')
        for (x,y,d,drill,net) in self.vias:
            out.append(f'  (via (at {x:.3f} {y:.3f}) (size {d}) (drill {drill}) (layers "F.Cu" "B.Cu") (net {self.net_id(net) if net else 0}) (uuid "{_u()}"))')
        for (s,x,y,size,layer) in self.texts:
            out.append(f'  (gr_text "{s}" (at {x:.3f} {y:.3f} 0) (layer "{layer}") (uuid "{_u()}") (effects (font (size {size} {size}) (thickness 0.2))))')
        for (net,layer,pts) in self.zones:
            if pts is None:
                pts=self._zone_pts()
            pstr=' '.join(f'(xy {px:g} {py:g})' for px,py in pts)
            out.append(f'  (zone (net {self.net_id(net)}) (net_name "{net}") (layer "{layer}") (uuid "{_u()}") (hatch edge 0.5) (connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no) (fill (thermal_gap 0.3) (thermal_bridge_width 0.3)) (polygon (pts {pstr})))')
        for (x1,y1,x2,y2,name) in self.keepouts:
            pstr=f'(xy {x1:g} {y1:g}) (xy {x2:g} {y1:g}) (xy {x2:g} {y2:g}) (xy {x1:g} {y2:g})'
            # KiCad 10 rule_area syntax: bare (keepout ...) in a net-less zone
            out.append(f'  (zone (layers "F.Cu" "B.Cu" "B.Adhes" "F.Adhes" "B.Paste" "F.Paste"'
                       f' "B.SilkS" "F.SilkS" "B.Mask" "F.Mask" "Edge.Cuts" "B.CrtYd" "F.CrtYd"'
                       f' "B.Fab" "F.Fab") (uuid "{_u()}") (name "{name}") (hatch edge 0.5)'
                       f' (connect_pads (clearance 0)) (min_thickness 0.25)'
                       f' (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed)'
                       f' (copperpour not_allowed) (footprints not_allowed))'
                       f' (fill (thermal_gap 0.5) (thermal_bridge_width 0.5) (island_removal_mode 0))'
                       f' (polygon (pts {pstr})))')
        out.append(')')
        return '\n'.join(out)

    def _zone_pts(self):
        """Board rect clipped against keepouts that touch a board edge
        (proper closed 4-corner rectangle, no repeated points)."""
        x,y,w,h=self.edge
        x0,y0,x1,y1=x,y,x+w,y+h
        m = 0.05  # clearance: keep zone edge just outside the keepout boundary
        for (kx1,ky1,kx2,ky2,_n) in self.keepouts:
            if kx1<=x and kx2>=x1:            # full-width strip
                if ky1<=y:  y0=max(y0,ky2+m)  # at top edge
                if ky2>=y1: y1=min(y1,ky1-m)  # at bottom edge
            if ky1<=y and ky2>=y1:            # full-height strip
                if kx1<=x:  x0=max(x0,kx2+m)  # at left edge
                if kx2>=x1: x1=min(x1,kx1-m)  # at right edge
        return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]

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
        for (net,layer,pts) in self.zones:
            if (side=="top")==(layer=="F.Cu"):
                d.rectangle([*T(x0,y0 if side=="top" else y0+h),*T(x0+w,y0+h if side=="top" else y0)], fill=(20,82,40))
        # keepout hatch (silk-style outline)
        for (kx1,ky1,kx2,ky2,_n) in self.keepouts:
            p1=T(kx1, ky2 if side!="top" else ky1); p2=T(kx2, ky1 if side!="top" else ky2)
            d.rectangle([p1,p2], outline=(120,120,60))
        # tracks
        for (x1,y1,x2,y2,width,layer,net) in self.tracks:
            if (side=="top")==(layer=="F.Cu"):
                d.line([T(x1,y1),T(x2,y2)], fill=(212,175,55), width=max(2,int(width*scale)))
        # footprints
        flip = side=="bottom"
        for fp in self.footprints:
            fx,fy=fp.x,fp.y
            if fp.fab_w and ((side=="top") == (fp.layer=="F.Cu")):
                ox,oy=fp.fab_ox,fp.fab_oy
                hw,hh=fp.fab_w/2,fp.fab_h/2
                p1=T(fx+ox-hw, fy+oy+hh if flip else fy+oy-hh); p2=T(fx+ox+hw, fy+oy-hh if flip else fy+oy+hh)
                d.rectangle([p1,p2], fill=(40,40,45), outline=(200,200,200))
                # silk outline
                d.rectangle([T(fx+ox-hw-0.15, fy+oy+hh+0.15 if flip else fy+oy-hh-0.15),
                             T(fx+ox+hw+0.15, fy+oy-hh-0.15 if flip else fy+oy+hh+0.15)], outline=(235,235,235))
            for p in fp.pads:
                if (side=="top") == ("F.Cu" in p.layers):
                    px,py=fx+p.x, fy+p.y
                    pw,ph=p.wh()
                    hw,hh=pw/2,ph/2
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


def _seg_intersect(ax,ay,bx,by,cx,cy,dx,dy):
    def ccw(px,py,qx,qy,rx,ry): return (qx-px)*(ry-py)-(qy-py)*(rx-px)
    d1=ccw(cx,cy,dx,dy,ax,ay); d2=ccw(cx,cy,dx,dy,bx,by)
    d3=ccw(ax,ay,bx,by,cx,cy); d4=ccw(ax,ay,bx,by,dx,dy)
    if ((d1>0)!=(d2>0)) and ((d3>0)!=(d4>0)): return True
    # collinear / endpoint-touch cases
    for px,py,qx,qy,rx,ry in ((ax,ay,cx,cy,dx,dy),(bx,by,cx,cy,dx,dy),
                              (cx,cy,ax,ay,bx,by),(dx,dy,ax,ay,bx,by)):
        if abs(ccw(qx,qy,rx,ry,px,py))<1e-9 and \
           min(qx,rx)-1e-9<=px<=max(qx,rx)+1e-9 and \
           min(qy,ry)-1e-9<=py<=max(qy,ry)+1e-9:
            return True
    return False

def _seg_rect_intersect(x1,y1,x2,y2,cx,cy,hw,hh):
    if abs(x1-cx)<=hw and abs(y1-cy)<=hh: return True
    if abs(x2-cx)<=hw and abs(y2-cy)<=hh: return True
    for ex1,ey1,ex2,ey2 in ((cx-hw,cy-hh,cx+hw,cy-hh),(cx+hw,cy-hh,cx+hw,cy+hh),
                            (cx+hw,cy+hh,cx-hw,cy+hh),(cx-hw,cy+hh,cx-hw,cy-hh)):
        if _seg_intersect(x1,y1,x2,y2,ex1,ey1,ex2,ey2): return True
    return False


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
        refs=[]
        for (ref,value,x,y,w,h,pins) in self.symbols:
            refs.append(ref)
            out.append(f'  (symbol (lib_id "local:Box") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) (uuid "{_u()}")')
            out.append(f'    (property "Reference" "{ref}" (at {x} {y-h/2-3} 0) (effects (font (size 1.27 1.27))))')
            out.append(f'    (property "Value" "{value}" (at {x} {y+h/2+3} 0) (effects (font (size 1.27 1.27))))')
            out.append(f'    (instances (project "" (path "/" (reference "{ref}") (unit 1)))))')
            # draw box as sch rectangle instead of relying on pinless symbol
            out.append(f'  (rectangle (start {x-w/2} {y-h/2}) (end {x+w/2} {y+h/2}) (stroke (width 0.254) (type default)) (fill (type outline)) (uuid "{_u()}"))')
            for (pname,side,off) in pins:
                if side=='L': px,py,ang=x-w/2-2.54,y-h/2+off,0
                else: px,py,ang=x+w/2+2.54,y-h/2+off,180
                out.append(f'  (label "{pname}" (at {px} {py} {ang}) (effects (font (size 1.27 1.27))) (uuid "{_u()}"))')
        for (net,x,y) in self.labels:
            out.append(f'  (label "{net}" (at {x} {y} 0) (effects (font (size 1.27 1.27))) (uuid "{_u()}"))')
        out.append(f'  (sheet_instances (path "/" (page "1")))')
        si='  (symbol_instances'
        for ref in refs:
            si+=f' (path "/" (reference "{ref}") (unit 1) (value "") (footprint ""))'
        out.append(si+')')
        out.append(')')
        return '\n'.join(out)


def project_file(name):
    return '{"board":{"design_settings":{"defaults":{"board_thickness":1.6}}},"meta":{"filename":"%s.kicad_pro","version":1},"schematic":{"drawing":{"default_line_thickness":6}}}' % name

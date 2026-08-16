#!/usr/bin/env python3
"""Isometric pseudo-3D renderer for room-node .kicad_pcb files (no KiCad needed).

Parses footprints (position + F.Fab rect) and extrudes component boxes with
per-type heights/colors, painter's-algorithm ordering, and soft shadows.
"""
import re, sys, math
from PIL import Image, ImageDraw, ImageFilter

HEIGHTS = [  # (match-substring, height_mm, top_color, side_color)
    ("ESP32",      3.1, (70,72,78),   (40,42,46)),
    ("USB-C",      3.2, (200,200,205),(150,150,155)),
    ("TYPE-C",     3.2, (200,200,205),(150,150,155)),
    ("SK6812",     1.8, (245,245,250),(210,210,220)),
    ("WS2812",     1.6, (245,245,250),(210,210,220)),
    ("SCD41",      6.5, (60,60,65),   (35,35,40)),
    ("LD2450",     8.5, (240,240,245),(200,200,208)),
    ("PinHeader",  8.5, (30,30,32),   (18,18,20)),
    ("Header",     8.5, (30,30,32),   (18,18,20)),
    ("Tact",       2.0, (90,90,95),   (60,60,65)),
    ("Button",     2.0, (90,90,95),   (60,60,65)),
    ("LDO",        1.1, (25,25,28),   (15,15,18)),
    ("LED",        1.8, (245,245,250),(210,210,220)),
    ("PIR",        8.5, (240,240,245),(200,200,208)),
    ("PMS",        8.5, (240,240,245),(200,200,208)),
    ("UART",       8.5, (30,30,32),   (18,18,20)),
    ("HDR",        8.5, (30,30,32),   (18,18,20)),
    ("EXP",        8.5, (30,30,32),   (18,18,20)),
    ("SW",         2.0, (90,90,95),   (60,60,65)),
    ("SHT",        0.9, (250,250,252),(220,220,225)),
    ("SGP",        0.85,(250,250,252),(220,220,225)),
    ("BME",        0.93,(120,120,128),(85,85,92)),
    ("BH1750",     0.75,(60,60,70),   (40,40,48)),
    ("ALS",        0.6, (60,60,70),   (40,40,48)),
    ("ME6211",     1.1, (25,25,28),   (15,15,18)),
    ("AMS1117",    1.6, (25,25,28),   (15,15,18)),
    ("USBLC",      1.1, (25,25,28),   (15,15,18)),
]
DEFAULT_H = (0.55, (25,25,28), (15,15,18))  # passives

ISO = 0.5  # vertical skew factor

def parse_pcb(path):
    txt = open(path).read()
    ex, ey, ew, eh = 0,0,50,40
    m = re.findall(r'gr_line \(start ([\d.\-]+) ([\d.\-]+)\) \(end ([\d.\-]+) ([\d.\-]+)\).*Edge\.Cuts', txt)
    if m:
        xs=[float(v) for l in m for v in (l[0],l[2])]; ys=[float(v) for l in m for v in (l[1],l[3])]
        ex,ey,ew,eh=min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
    fps=[]
    for fm in re.finditer(r'footprint "local:([^"]+)".*?\(at ([\d.\-]+) ([\d.\-]+)( [\d.]+)?\)(.*?)\(pad', txt, re.S):
        name,x,y,rot,body = fm.group(1),float(fm.group(2)),float(fm.group(3)),fm.group(4),fm.group(5)
        rm = re.search(r'fp_rect \(start ([\d.\-]+) ([\d.\-]+)\) \(end ([\d.\-]+) ([\d.\-]+)\) .*"F\.Fab"', body)
        if rm:
            w=abs(float(rm.group(3))-float(rm.group(1))); h=abs(float(rm.group(4))-float(rm.group(2)))
        else:
            w,h=1.6,0.8
        fps.append((name,x,y,w,h))
    return ex,ey,ew,eh,fps

def render3d(pcb_path, out_path, scale=16, title=""):
    ex,ey,ew,eh,fps = parse_pcb(pcb_path)
    pad=12; lift=14*scale/16
    W=int((ew+eh)*0.87*scale)+2*pad*scale//2 + 200
    H=int((ew+eh)*0.5*scale + 20*scale)+100
    img=Image.new("RGB",(W,H),(24,26,30)); d=ImageDraw.Draw(img)
    def P(x,y,z=0.0):
        xx=(x-ex)*0.87*scale - (y-ey)*0.87*scale + W/2
        yy=(x-ex)*0.5*scale + (y-ey)*0.5*scale - z*scale + 40
        return (xx,yy)
    # board slab
    t=1.6
    c=[P(ex,ey,t),P(ex+ew,ey,t),P(ex+ew,ey+eh,t),P(ex,ey+eh,t)]
    b=[P(ex,ey,0),P(ex+ew,ey,0),P(ex+ew,ey+eh,0),P(ex,ey+eh,0)]
    d.polygon([b[0],b[1],c[1],c[0]],fill=(14,60,28))
    d.polygon([b[1],b[2],c[2],c[1]],fill=(10,45,22))
    d.polygon(c,fill=(22,92,42),outline=(30,110,50))
    # components sorted back-to-front
    def keyf(f): return f[1]+f[2]
    shadow=Image.new("RGBA",img.size,(0,0,0,0)); sd=ImageDraw.Draw(shadow)
    for name,x,y,w,h in sorted(fps,key=keyf):
        hh,ct,cs=DEFAULT_H
        for k,v,tc,sc in HEIGHTS:
            if k.lower() in name.lower(): hh,ct,cs=v,tc,sc; break
        x0,y0,x1,y1=x-w/2,y-h/2,x+w/2,y+h/2
        base=[P(x0,y0,t),P(x1,y0,t),P(x1,y1,t),P(x0,y1,t)]
        top=[P(x0,y0,t+hh),P(x1,y0,t+hh),P(x1,y1,t+hh),P(x0,y1,t+hh)]
        sd.polygon([(px+hh*scale*0.35,py+hh*scale*0.15) for px,py in base],fill=(0,0,0,90))
        d.polygon([base[0],base[1],top[1],top[0]],fill=tuple(int(c*0.85) for c in cs))
        d.polygon([base[1],base[2],top[2],top[1]],fill=cs)
        d.polygon(top,fill=ct,outline=(0,0,0))
    shadow=shadow.filter(ImageFilter.GaussianBlur(4))
    img=Image.alpha_composite(img.convert("RGBA"),shadow).convert("RGB")
    d=ImageDraw.Draw(img)
    if title: d.text((W//2,20),title,fill=(230,230,235),anchor="mm")
    img.save(out_path); return out_path

if __name__=="__main__":
    render3d(sys.argv[1], sys.argv[2], title=sys.argv[3] if len(sys.argv)>3 else "")
    print("rendered", sys.argv[2])

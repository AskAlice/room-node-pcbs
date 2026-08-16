#!/usr/bin/env python3
"""SVG top-view renderer for room-node .kicad_pcb files (text output, git-friendly)."""
import re, sys

def parse(path):
    txt=open(path).read()
    m=re.findall(r'gr_line \(start ([\d.\-]+) ([\d.\-]+)\) \(end ([\d.\-]+) ([\d.\-]+)\).*Edge\.Cuts',txt)
    xs=[float(v) for l in m for v in (l[0],l[2])]; ys=[float(v) for l in m for v in (l[1],l[3])]
    ex,ey,ew,eh=min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
    fps=[]
    for fm in re.finditer(r'footprint "local:([^"]+)".*?\(at ([\d.\-]+) ([\d.\-]+)',txt):
        fps.append([fm.group(1),float(fm.group(2)),float(fm.group(3)),1.6,0.8,[]])
    # sizes + pads per footprint block
    for fm in re.finditer(r'footprint "local:([^"]+)" \(layer "F.Cu"\).*?\(at ([\d.\-]+) ([\d.\-]+)(.*?)(?=\(footprint|\(gr_line|\(segment|\(zone|\Z)',txt,re.S):
        name,x,y,body=fm.group(1),float(fm.group(2)),float(fm.group(3)),fm.group(4)
        rm=re.search(r'fp_rect \(start ([\d.\-]+) ([\d.\-]+)\) \(end ([\d.\-]+) ([\d.\-]+)\) [^)]*\) [^)]*"F\.Fab"',body)
        w,h=(abs(float(rm.group(3))-float(rm.group(1))),abs(float(rm.group(4))-float(rm.group(2)))) if rm else (1.6,0.8)
        pads=[(float(a),float(b),float(c),float(d)) for a,b,c,d in re.findall(r'\(pad "[^"]*" smd \w+ \(at ([\d.\-]+) ([\d.\-]+)[^)]*\) \(size ([\d.\-]+) ([\d.\-]+)\)',body)]
        for f in fps:
            if f[0]==name and abs(f[1]-x)<0.01 and abs(f[2]-y)<0.01:
                f[3],f[4],f[5]=w,h,pads
    tracks=[(float(a),float(b),float(c),float(d),float(wd),l) for a,b,c,d,wd,l in
            re.findall(r'\(segment \(start ([\d.\-]+) ([\d.\-]+)\) \(end ([\d.\-]+) ([\d.\-]+)\) \(width ([\d.]+)\) \(layer "([FB]).Cu"',txt)]
    texts=[(t,float(x),float(y)) for t,x,y in re.findall(r'\(gr_text "([^"]+)" \(at ([\d.\-]+) ([\d.\-]+)',txt)]
    return ex,ey,ew,eh,fps,tracks,texts

def render(path,out,title=""):
    ex,ey,ew,eh,fps,tracks,texts=parse(path)
    s=16; pad=6
    W=(ew+2*pad)*s; H=(eh+2*pad)*s+30
    def X(x): return (x-ex+pad)*s
    def Y(y): return (y-ey+pad)*s+30
    o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
       f'<rect width="100%" height="100%" fill="#0a2814"/>',
       f'<rect x="{X(ex):.0f}" y="{Y(ey):.0f}" width="{ew*s:.0f}" height="{eh*s:.0f}" fill="#124b23" rx="6"/>']
    for x1,y1,x2,y2,wd,l in tracks:
        if l=="F": o.append(f'<line x1="{X(x1):.0f}" y1="{Y(y1):.0f}" x2="{X(x2):.0f}" y2="{Y(y2):.0f}" stroke="#d4af37" stroke-width="{max(1.5,wd*s):.1f}" stroke-linecap="round"/>')
    for name,x,y,w,h,pads in fps:
        o.append(f'<rect x="{X(x-w/2):.0f}" y="{Y(y-h/2):.0f}" width="{w*s:.0f}" height="{h*s:.0f}" fill="#28282d" stroke="#c8c8c8" stroke-width="1.5"/>')
        for px,py,pw,ph in pads:
            o.append(f'<rect x="{X(x+px-pw/2):.0f}" y="{Y(y+py-ph/2):.0f}" width="{pw*s:.0f}" height="{ph*s:.0f}" fill="#e6be50"/>')
        o.append(f'<text x="{X(x):.0f}" y="{Y(y):.0f}" fill="#ddd" font-size="11" text-anchor="middle" font-family="monospace">{name}</text>')
    for t,x,y in texts:
        o.append(f'<text x="{X(x):.0f}" y="{Y(y):.0f}" fill="#eee" font-size="14" text-anchor="middle" font-family="monospace">{t}</text>')
    o.append(f'<text x="{W/2:.0f}" y="18" fill="#9fd" font-size="16" text-anchor="middle" font-family="monospace">{title}</text>')
    o.append('</svg>')
    open(out,'w').write('\n'.join(o))

if __name__=="__main__":
    render(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else "")
    print("svg:",sys.argv[2])

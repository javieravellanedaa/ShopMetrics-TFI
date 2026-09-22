# -*- coding: utf-8 -*-
"""Valida un .drawio y su PNG: que ELK haya corrido, que nada se superponga
y que la exportacion contenga todo el dibujo."""
import xml.etree.ElementTree as ET, sys, os
from PIL import Image

def cajas(arch):
    r = ET.parse(arch).getroot()
    out = []
    for c in r.findall('.//mxCell'):
        if c.get('parent') != '1' or c.get('vertex') != '1': continue
        g = c.find('mxGeometry')
        if g is None or g.get('x') is None or g.get('y') is None: continue
        out.append((c.get('id'), float(g.get('x')), float(g.get('y')),
                    float(g.get('width') or 0), float(g.get('height') or 0)))
    return out

def revisar(arch, png, escala):
    fallas = []
    cs = cajas(arch)
    if not cs: return ["sin cajas"]
    # 1. superposiciones
    sup = [(cs[i][0], cs[j][0]) for i in range(len(cs)) for j in range(i+1, len(cs))
           if cs[i][1] < cs[j][1]+cs[j][3] and cs[j][1] < cs[i][1]+cs[i][3]
           and cs[i][2] < cs[j][2]+cs[j][4] and cs[j][2] < cs[i][2]+cs[i][4]]
    if sup: fallas.append("%d superposiciones (%s...)" % (len(sup), sup[0]))
    # 2. el acomodo corrio: las cajas no estan en diagonal de 10/12 px
    xs = sorted(c[1] for c in cs)
    if len(set(round(b-a) for a,b in zip(xs, xs[1:]))) == 1 and len(xs) > 2:
        fallas.append("las cajas siguen en las posiciones iniciales: ELK no corrio")
    # 3. el PNG contiene todo el recuadro del dibujo
    x0 = min(c[1] for c in cs); y0 = min(c[2] for c in cs)
    x1 = max(c[1]+c[3] for c in cs); y1 = max(c[2]+c[4] for c in cs)
    cw, ch = x1-x0, y1-y0
    if not os.path.exists(png): return fallas + ["falta el PNG"]
    iw, ih = Image.open(png).size
    ew, eh = iw/escala, ih/escala
    if ew < cw - 2: fallas.append("PNG RECORTADO a lo ancho: dibujo %.0f, export %.0f" % (cw, ew))
    if eh < ch - 2: fallas.append("PNG RECORTADO a lo alto: dibujo %.0f, export %.0f" % (ch, eh))
    return fallas

if __name__ == '__main__':
    arch, png, esc = sys.argv[1], sys.argv[2], float(sys.argv[3])
    f = revisar(arch, png, esc)
    n = os.path.basename(arch)
    if f:
        print("  %-24s FALLA: %s" % (n, "; ".join(f))); sys.exit(1)
    cs = cajas(arch)
    x0=min(c[1] for c in cs); y0=min(c[2] for c in cs)
    x1=max(c[1]+c[3] for c in cs); y1=max(c[2]+c[4] for c in cs)
    iw,ih = Image.open(png).size
    print("  %-24s ok  %d cajas  dibujo %.0fx%.0f  PNG %dx%d (esc %g)"
          % (n, len(cs), x1-x0, y1-y0, iw, ih, esc))

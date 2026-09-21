# -*- coding: utf-8 -*-
"""Cuenta cuantas veces una arista atraviesa una tabla que no es su origen ni su destino."""
import xml.etree.ElementTree as ET, sys, itertools

def segmentos(cells, byid, e, cajas):
    g = e.find('mxGeometry')
    pts = []
    src, tgt = e.get('source'), e.get('target')
    if src in cajas: x,y,w,h = cajas[src]; pts.append((x+w/2, y+h/2))
    for arr in (g.findall('Array') if g is not None else []):
        for p in arr.findall('mxPoint'):
            pts.append((float(p.get('x') or 0), float(p.get('y') or 0)))
    if tgt in cajas: x,y,w,h = cajas[tgt]; pts.append((x+w/2, y+h/2))
    return [(pts[i], pts[i+1]) for i in range(len(pts)-1)]

def corta(p, q, r):
    """el segmento p-q corta el rectangulo r?"""
    x, y, w, h = r
    (x1,y1),(x2,y2) = p, q
    if max(x1,x2) < x or min(x1,x2) > x+w or max(y1,y2) < y or min(y1,y2) > y+h:
        return False
    # muestreo: suficiente para contar incidencias
    for t in [i/40 for i in range(1,40)]:
        px, py = x1+(x2-x1)*t, y1+(y2-y1)*t
        if x < px < x+w and y < py < y+h: return True
    return False

def auditar(arch, etq):
    r = ET.parse(arch).getroot()
    cells = r.findall('.//mxCell'); byid = {c.get('id'): c for c in cells}
    cajas = {}
    for c in cells:
        if c.get('parent')=='1' and c.get('vertex')=='1' and ('shape=table;' in (c.get('style') or '') or 'swimlane;' in (c.get('style') or '')):
            g = c.find('mxGeometry')
            if g is not None and g.get('x'):
                cajas[c.get('id')] = tuple(float(g.get(k)) for k in ('x','y','width','height'))
    edges = [c for c in cells if c.get('edge')=='1']
    inc = 0; con_pts = 0
    for e in edges:
        segs = segmentos(cells, byid, e, cajas)
        if len(segs) > 1: con_pts += 1
        for s in segs:
            for cid, rect in cajas.items():
                if cid in (e.get('source'), e.get('target')): continue
                if corta(s[0], s[1], rect): inc += 1; break
    print("%-22s cajas %2d  aristas %2d  con ruteo explicito %2d  ATRAVIESAN %d"
          % (etq, len(cajas), len(edges), con_pts, inc))

import sys
for p in sys.argv[1:]:
    f,e = p.split('=',1); auditar(f,e)

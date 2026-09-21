# -*- coding: utf-8 -*-
"""Render fiel del .drawio a PNG, para revisar legibilidad en A4."""
import xml.etree.ElementTree as ET, re, sys
from PIL import Image, ImageDraw, ImageFont

PW, PH, K = 1169, 826, 2          # K = factor de sobremuestreo
F = "/System/Library/Fonts/Supplemental/Arial.ttf"
FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
fuente = {}
def fnt(sz, neg=False):
    key = (sz, neg)
    if key not in fuente:
        fuente[key] = ImageFont.truetype(FB if neg else F, max(6, int(sz*K)))
    return fuente[key]

def est(s, k, d=None):
    m = re.search(k + r'=([^;]+)', s or '')
    return m.group(1) if m else d

def render(arch, salida):
    root = ET.parse(arch).getroot()
    cells = root.findall('.//mxCell')
    byid = {c.get('id'): c for c in cells}
    im = Image.new('RGB', (PW*K, PH*K), '#FFFFFF')
    d = ImageDraw.Draw(im)
    d.rectangle([0,0,PW*K-1,PH*K-1], outline='#E4E9ED', width=K)

    def abs_xy(c):
        """posicion absoluta acumulando la de los padres"""
        x = y = 0.0
        while c is not None and c.get('id') != '1':
            g = c.find('mxGeometry')
            if g is not None:
                x += float(g.get('x') or 0); y += float(g.get('y') or 0)
            c = byid.get(c.get('parent'))
        return x, y

    anclas = {}
    # --- vertices ---
    for c in cells:
        if c.get('vertex') != '1': continue
        s = c.get('style') or ''
        g = c.find('mxGeometry')
        if g is None: continue
        x, y = abs_xy(c)
        w = float(g.get('width') or 0); h = float(g.get('height') or 0)
        anclas[c.get('id')] = (x, y, w, h)
        val = (c.get('value') or '')
        val = (val.replace('&#8212;','—').replace('&#243;','ó').replace('&#183;','·')
                  .replace('&#237;','í').replace('&#225;','á').replace('&amp;','&')
                  .replace('&lt;','<').replace('&gt;','>').replace('&quot;','"'))
        fs = int(est(s,'fontSize','11')); col = est(s,'fontColor','#000000')
        neg = est(s,'fontStyle','0') in ('1','5')
        fill = est(s,'fillColor'); stroke = est(s,'strokeColor')
        R = lambda v: [v[0]*K, v[1]*K, v[2]*K, v[3]*K]

        if 'shape=table;' in s or 'swimlane;' in s:
            sw = est(s,'swimlaneFillColor','#FFFFFF')
            d.rectangle(R((x,y,x+w,y+h)), fill=sw, outline=stroke, width=K)
            ss = int(est(s,'startSize','21'))
            d.rectangle(R((x,y,x+w,y+ss)), fill=fill, outline=stroke, width=K)
            tw = d.textlength(val, font=fnt(fs,True))
            d.text(((x+w/2)*K-tw/2, (y+ss/2)*K), val, fill=col, font=fnt(fs,True), anchor="lm")
            continue
        if 'shape=tableRow' in s or 'line;' in s:
            if 'line;' in s:
                d.line([x*K,(y+h/2)*K,(x+w)*K,(y+h/2)*K], fill=stroke or '#CCC', width=K)
            continue
        if fill and fill != 'none' and 'text;' not in s:
            d.rectangle(R((x,y,x+w,y+h)), fill=fill,
                        outline=(stroke if stroke and stroke!='none' else None), width=K)
        if not val: continue
        al = est(s,'align','center')
        px = {'left': (x+int(est(s,'spacingLeft','2')))*K,
              'right': (x+w-int(est(s,'spacingRight','3')))*K,
              'center': (x+w/2)*K}[al]
        anc = {'left':'lm','right':'rm','center':'mm'}[al]
        d.text((px, (y+h/2)*K), val, fill=col, font=fnt(fs,neg), anchor=anc)

    # --- aristas: ruteo ortogonal aproximado, como entityRelationEdgeStyle ---
    for c in cells:
        if c.get('edge') != '1': continue
        s = c.get('style') or ''
        a = anclas.get(c.get('source')); b = anclas.get(c.get('target'))
        if not a or not b: continue
        ax, ay = a[0]+a[2], a[1]+a[3]/2
        bx, by = b[0], b[1]+b[3]/2
        col = est(s,'strokeColor','#4A5A68')
        if bx < ax:                       # el hijo esta a la izquierda: salir por izquierda
            ax = a[0]; mx = min(ax, bx) - 14
            pts = [(ax,ay), (mx,ay), (mx,by), (bx,by)]
        else:
            mx = (ax+bx)/2
            pts = [(ax,ay), (mx,ay), (mx,by), (bx,by)]
        for i in range(len(pts)-1):
            d.line([pts[i][0]*K,pts[i][1]*K,pts[i+1][0]*K,pts[i+1][1]*K], fill=col, width=K)
        # pie de gallo en el extremo hijo
        if 'ERmany' in s or 'ERzeroToMany' in s:
            for dy in (-4,0,4):
                d.line([(bx-9)*K,(by+dy)*K,bx*K,by*K], fill=col, width=K)
            if 'zero' in s:
                d.ellipse([(bx-16)*K,(by-3)*K,(bx-10)*K,(by+3)*K], outline=col, fill='#FFF', width=K)
        if 'diamondThin' in s:
            dx0 = -1 if bx >= ax else 1
            p = [(ax,ay),(ax+dx0*6,ay-4),(ax+dx0*12,ay),(ax+dx0*6,ay+4)]
            d.polygon([(q[0]*K,q[1]*K) for q in p], fill=col)
        if 'ERmandatoryOne' in s:
            sx = ax + (7 if bx >= ax else -7)
            d.line([sx*K,(ay-5)*K,sx*K,(ay+5)*K], fill=col, width=K)

    im.resize((PW, PH), Image.LANCZOS).save(salida)
    print("  ->", salida)

for a, o in (('ShopMetrics_DER.drawio','vista_der.png'),
             ('ShopMetrics_Clases.drawio','vista_cls.png')):
    print(a); render(a, o)

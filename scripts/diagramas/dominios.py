# -*- coding: utf-8 -*-
"""Un DER por dominio, en A4 apaisado. Las entidades de otros dominios que
el dominio referencia se dibujan como caja al margen, con su clave nada mas."""
import sys, re
sys.path.insert(0,'.')
from modelo import cargar, DOMINIOS, esc

PW, PH = 1123, 794            # A4 apaisado a 96 ppp
MARG_X, MARG_Y, TIT = 14, 14, 28
FS, FILA, ENC = 9, 18, 25
COL_K, COL_T = 17, 46
BORDE, ENCAB, GRIS, TENUE = "#333333", "#DCDCDC", "#333333", "#606060"
EXT_B, EXT_E = "#9A9A9A", "#F2F2F2"

ents, rels = cargar()

def ancho_txt(s, fs=FS): return len(s) * fs * 0.56

def tam(t, completo=True):
    campos = ents[t]['campos'] if completo else [c for c in ents[t]['campos'] if c['clave'].startswith('PK')]
    an = max(ancho_txt(t, FS) + 14,
             max(COL_K + ancho_txt(c['campo']) + 6 + COL_T for c in campos))
    return int(an) + 4, ENC + len(campos)*FILA, campos

def caja(t, x, y, completo, i):
    an, al, campos = tam(t, completo)
    cf, cb = (ENCAB, BORDE) if completo else (EXT_E, EXT_B)
    guion = "" if completo else "dashed=1;"
    o = [f'<mxCell id="t_{t}" value="{esc(t)}" style="shape=table;startSize={ENC};container=1;'
         f'collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;columnLines=0;html=1;'
         f'whiteSpace=nowrap;fillColor={cf};strokeColor={cb};{guion}fontColor=#000000;'
         f'fontSize={FS};fontStyle=1;align=center;swimlaneFillColor=#FFFFFF;resizeLast=1;" '
         f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{an}" height="{al}" as="geometry"/></mxCell>']
    an_n = an - COL_K - COL_T
    base = ('shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;'
            'overflow=hidden;html=1;whiteSpace=nowrap;')
    for j, c in enumerate(campos):
        rid = f't_{t}_r{j}'
        o.append(f'<mxCell id="{rid}" value="" style="shape=tableRow;horizontal=0;startSize=0;'
                 f'swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;'
                 f'points=[[0,0.5],[1,0.5]];portConstraint=eastwest;top=0;left=0;right=0;bottom=0;" '
                 f'vertex="1" parent="t_{t}">'
                 f'<mxGeometry y="{ENC+j*FILA}" width="{an}" height="{FILA}" as="geometry"/></mxCell>')
        k = c['clave']; badge = 'PK' if k.startswith('PK') else ('FK' if k else '')
        o.append(f'<mxCell id="{rid}_k" value="{badge}" style="{base}align=center;fontSize=7;'
                 f'fontStyle=1;" vertex="1" parent="{rid}">'
                 f'<mxGeometry width="{COL_K}" height="{FILA}" as="geometry"/></mxCell>')
        o.append(f'<mxCell id="{rid}_n" value="{esc(c["campo"])}" style="{base}align=left;'
                 f'spacingLeft=2;fontSize={FS};fontStyle={1 if badge else 0};" vertex="1" parent="{rid}">'
                 f'<mxGeometry x="{COL_K}" width="{an_n}" height="{FILA}" as="geometry"/></mxCell>')
        o.append(f'<mxCell id="{rid}_t" value="{esc(c["tipo"])}" style="{base}align=right;'
                 f'spacingRight=3;fontSize=7;fontColor={TENUE};" vertex="1" parent="{rid}">'
                 f'<mxGeometry x="{COL_K+an_n}" width="{COL_T}" height="{FILA}" as="geometry"/></mxCell>')
    return o

for dom, nombre, _c, _cl, miembros in DOMINIOS:
    dentro = set(miembros)
    # el dominio se define por sus entidades: se dibujan las relaciones donde
    # la clave foranea vive aca, mas los padres de afuera a los que apunta
    propias = [r for r in rels if r['hijo'] in dentro]
    externas = sorted({r['padre'] for r in propias if r['padre'] not in dentro})
    cel = []
    for i, t in enumerate(miembros):  cel += caja(t, 20+ i*10, 60 + i*10, True, i)
    for i, t in enumerate(externas):  cel += caja(t, 600+i*10, 60 + i*10, False, i)
    ar = []
    for n, r in enumerate(propias):
        fin = 'ERzeroToMany' if r['opcional'] else 'ERmany'
        ar.append(f'<mxCell id="e{n}" value="{esc(r["campo"])}" style="edgeStyle=orthogonalEdgeStyle;'
                  f'rounded=0;html=1;startArrow=ERmandatoryOne;startFill=0;endArrow={fin};endFill=0;'
                  f'strokeColor={GRIS};strokeWidth=1;fontSize=7;fontColor={TENUE};" edge="1" parent="1" '
                  f'source="t_{r["padre"]}" target="t_{r["hijo"]}">'
                  f'<mxGeometry relative="1" as="geometry"/></mxCell>')
    tit = ''
    xml = (f'<mxfile host="app.diagrams.net" agent="ShopMetrics" version="24.7.17">\n'
           f'  <diagram id="der-{dom}" name="{esc(nombre)}">\n'
           f'    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" '
           f'connect="1" arrows="1" fold="1" page="0" pageScale="1" '
           f'math="0" shadow="0">\n      <root>\n        <mxCell id="0"/>\n'
           f'        <mxCell id="1" parent="0"/>\n        ' + tit + "\n        "
           + "\n        ".join(cel) + "\n        " + "\n        ".join(ar)
           + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')
    open('der_%s.drawio' % dom, 'w').write(xml)
    print("%-12s %2d propias + %2d externas | %2d relaciones" % (dom, len(miembros), len(externas), len(propias)))

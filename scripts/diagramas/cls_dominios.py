# -*- coding: utf-8 -*-
"""Un diagrama de clases por dominio, en A4 apaisado."""
import sys; sys.path.insert(0,'.')
from modelo import cargar, DOMINIOS, METODOS, clase, esc, COMPOSICION

PW, PH = 1123, 794
MARG_X, FS, FILA, ENC, SEP = 14, 9, 18, 25, 10
BORDE, ENCAB, GRIS, TENUE, LINEA = "#333333", "#DCDCDC", "#333333", "#606060", "#9A9A9A"
EXT_B, EXT_E = "#9A9A9A", "#F2F2F2"
TIPO = {'UUID':'UUID','VARCHAR':'String','INT':'int','TIMESTAMP':'DateTime',
        'DECIMAL':'Decimal','BOOLEAN':'bool','DATE':'Date'}

ents, rels = cargar()
def corto(m): return m.split('):')[0] + ')' if len(m) > 25 and '):' in m else m
def atributos(t):
    return ["%s %s: %s" % ('+' if c['clave']=='PK' else '-', c['campo'], TIPO.get(c['tipo'], c['tipo']))
            for c in ents[t]['campos'] if 'FK' not in c['clave']]
def ancho_txt(s, fs=FS): return len(s) * fs * 0.56

TXT = ('text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=5;'
       'spacingRight=5;overflow=hidden;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;'
       'rotatable=0;whiteSpace=nowrap;html=1;')

def caja(t, x, y, completo):
    at = atributos(t) if completo else []
    me = [corto(m) for m in METODOS[t]] if completo else []
    if not completo: at = ["+ id: UUID"]
    an = int(max(ancho_txt(clase(t), FS) + 14,
                 max([ancho_txt(m) + 12 for m in at + me] or [90]))) + 4
    alto = ENC + len(at)*FILA + (SEP + len(me)*FILA if completo else 0)
    cf, cb = (ENCAB, BORDE) if completo else (EXT_E, EXT_B)
    g = "" if completo else "dashed=1;"
    o = [f'<mxCell id="c_{t}" value="{esc(clase(t))}" style="swimlane;fontStyle=1;align=center;'
         f'verticalAlign=middle;childLayout=stackLayout;horizontal=1;startSize={ENC};'
         f'horizontalStack=0;resizeParent=0;resizeParentMax=0;html=1;whiteSpace=nowrap;'
         f'collapsible=0;marginBottom=0;fillColor={cf};strokeColor={cb};{g}fontColor=#000000;'
         f'swimlaneFillColor=#FFFFFF;fontSize={FS};" vertex="1" parent="1">'
         f'<mxGeometry x="{x}" y="{y}" width="{an}" height="{alto}" as="geometry"/></mxCell>']
    yy = ENC
    for i, a in enumerate(at):
        o.append(f'<mxCell id="c_{t}_a{i}" value="{esc(a)}" style="{TXT}fontSize={FS};'
                 f'fontColor=#000000;" vertex="1" parent="c_{t}">'
                 f'<mxGeometry y="{yy}" width="{an}" height="{FILA}" as="geometry"/></mxCell>')
        yy += FILA
    if completo:
        o.append(f'<mxCell id="c_{t}_s" value="" style="line;strokeWidth=1;fillColor=none;'
                 f'align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=3;'
                 f'rotatable=0;labelPosition=right;points=[];portConstraint=eastwest;'
                 f'strokeColor={LINEA};" vertex="1" parent="c_{t}">'
                 f'<mxGeometry y="{yy}" width="{an}" height="{SEP}" as="geometry"/></mxCell>')
        yy += SEP
        for i, m in enumerate(me):
            o.append(f'<mxCell id="c_{t}_m{i}" value="{esc(m)}" style="{TXT}fontSize={FS};'
                     f'fontColor={GRIS};" vertex="1" parent="c_{t}">'
                     f'<mxGeometry y="{yy}" width="{an}" height="{FILA}" as="geometry"/></mxCell>')
            yy += FILA
    return o

for dom, nombre, _a, _b, miembros in DOMINIOS:
    dentro = set(miembros)
    propias = [r for r in rels if r['hijo'] in dentro]
    externas = sorted({r['padre'] for r in propias if r['padre'] not in dentro})
    cel = []
    for i, t in enumerate(miembros): cel += caja(t, 20+i*12, 60+i*12, True)
    for i, t in enumerate(externas): cel += caja(t, 640+i*12, 60+i*12, False)
    ar = []
    for n, r in enumerate(propias):
        comp = (r['padre'], r['hijo']) in COMPOSICION
        ini = 'diamondThin;startFill=1;startSize=12;' if comp else 'none;'
        mult = '1..*' if comp else '0..*'
        ar.append(f'<mxCell id="as{n}" value="" style="endArrow=none;startArrow={ini}html=1;'
                  f'edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor={GRIS};strokeWidth=1;'
                  f'endSize=6;" edge="1" parent="1" source="c_{r["padre"]}" target="c_{r["hijo"]}">'
                  f'<mxGeometry relative="1" as="geometry"/></mxCell>')
        for suf, val, pos in (("p","1",-0.8), ("h",mult,0.8)):
            ar.append(f'<mxCell id="as{n}{suf}" value="{val}" style="edgeLabel;html=1;align=center;'
                      f'verticalAlign=middle;resizable=0;points=[];fontSize=8;fontColor={TENUE};" '
                      f'vertex="1" connectable="0" parent="as{n}">'
                      f'<mxGeometry x="{pos}" relative="1" as="geometry"><mxPoint as="offset"/>'
                      f'</mxGeometry></mxCell>')
    tit = ''
    xml = (f'<mxfile host="app.diagrams.net" agent="ShopMetrics" version="24.7.17">\n'
           f'  <diagram id="cls-{dom}" name="{esc(nombre)}">\n'
           f'    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" '
           f'connect="1" arrows="1" fold="1" page="0" pageScale="1" '
           f'math="0" shadow="0">\n      <root>\n        <mxCell id="0"/>\n'
           f'        <mxCell id="1" parent="0"/>\n        ' + tit + "\n        "
           + "\n        ".join(cel) + "\n        " + "\n        ".join(ar)
           + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')
    open('cls_%s.drawio' % dom, 'w').write(xml)
    print("%-12s %2d clases + %d externas | %2d asociaciones" % (dom, len(miembros), len(externas), len(propias)))

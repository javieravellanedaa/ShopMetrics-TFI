# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'.')
from modelo import *
from der_drawio import COLUMNAS, PW, PH, MARG_Y, TIT, ancho_txt
MARG_X, GAP_X, GAP_Y = 12, 8, 12

TIPO = {'UUID':'UUID','VARCHAR':'String','INT':'int','TIMESTAMP':'DateTime',
        'DECIMAL':'Decimal','BOOLEAN':'bool','DATE':'Date'}
FS, FILA, ENC, SEP = 8, 17, 24, 9
GRIS, TENUE, LINEA = "#4A5A68", "#7C8C9A", "#C7D3DC"

ents, rels = cargar()

def corto(m):
    """en las firmas largas se omite el tipo de retorno, que igual esta en el diccionario"""
    return m.split('):')[0] + ')' if len(m) > 25 and '):' in m else m

def atributos(t):
    """UML: las FK se modelan como asociaciones, no como atributos."""
    out = []
    for c in ents[t]['campos']:
        if 'FK' in c['clave']: continue
        vis = '+' if c['clave'] == 'PK' else '-'
        out.append(f"{vis} {c['campo']}: {TIPO.get(c['tipo'], c['tipo'])}")
    return out

anchos = []
for col in COLUMNAS:
    w = 0
    for t in col:
        w = max(w, ancho_txt(clase(t), FS) + 12)
        for m in atributos(t) + [corto(x) for x in METODOS[t]]:
            w = max(w, ancho_txt(m, FS) + 11)
    anchos.append(int(w) + 2)

total = sum(anchos) + GAP_X*(len(COLUMNAS)-1)
sobra = (PW - 2*MARG_X) - total
GAP_X = max(GAP_X, min(26, GAP_X + sobra // max(1, len(COLUMNAS)-1)))
total = sum(anchos) + GAP_X*(len(COLUMNAS)-1)
MARG_X = (PW - total) // 2

crudo = [sum(ENC + len(atributos(t))*FILA + SEP + len(METODOS[t])*FILA for t in col)
         for col in COLUMNAS]
libre = (PH - MARG_Y - TIT - MARG_Y) - max(crudo)
i = crudo.index(max(crudo))
GAP_Y = max(GAP_Y, min(30, libre // max(1, len(COLUMNAS[i])-1)))
alturas = [c + GAP_Y*(len(col)-1) for c, col in zip(crudo, COLUMNAS)]
print("clases: ancho %d (sep %d)  alto %d / %d (sep %d)"
      % (total, GAP_X, max(alturas), PH-2*MARG_Y, GAP_Y))
if total > PW-2*MARG_X or max(alturas) > PH-MARG_Y-TIT-10:
    print("  !! NO ENTRA"); sys.exit(1)

cid = lambda t: "c_" + clase(t)
xy, cel, ar = {}, [], []
x = MARG_X
for col, an in zip(COLUMNAS, anchos):
    y = MARG_Y + TIT
    for t in col:
        at, me = atributos(t), METODOS[t]
        h = ENC + len(at)*FILA + SEP + len(me)*FILA
        xy[t] = (x, y, an, h)
        y += h + GAP_Y
    x += an + GAP_X

TXT = ('text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;'
       'spacingRight=4;overflow=hidden;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;'
       'rotatable=0;whiteSpace=nowrap;html=1;')
for t in ents:
    px, py, an, h = xy[t]
    dom, col_d, claro = DOM[t]
    cel.append(
      f'<mxCell id="{cid(t)}" value="{esc(clase(t))}" style="swimlane;fontStyle=1;align=center;'
      f'verticalAlign=middle;childLayout=stackLayout;horizontal=1;startSize={ENC};horizontalStack=0;'
      f'resizeParent=0;resizeParentMax=0;html=1;whiteSpace=nowrap;collapsible=0;marginBottom=0;'
      f'fillColor={col_d};strokeColor={col_d};fontColor=#FFFFFF;swimlaneFillColor=#FFFFFF;'
      f'fontSize={FS};" vertex="1" parent="1">'
      f'<mxGeometry x="{px}" y="{py}" width="{an}" height="{h}" as="geometry"/></mxCell>')
    yy = ENC
    for i, a in enumerate(atributos(t)):
        cel.append(f'<mxCell id="{cid(t)}_a{i}" value="{esc(a)}" style="{TXT}fontSize={FS};'
                   f'fontColor=#17222D;" vertex="1" parent="{cid(t)}">'
                   f'<mxGeometry y="{yy}" width="{an}" height="{FILA}" as="geometry"/></mxCell>')
        yy += FILA
    cel.append(f'<mxCell id="{cid(t)}_s" value="" style="line;strokeWidth=1;fillColor=none;'
               f'align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=3;'
               f'rotatable=0;labelPosition=right;points=[];portConstraint=eastwest;'
               f'strokeColor={LINEA};" vertex="1" parent="{cid(t)}">'
               f'<mxGeometry y="{yy}" width="{an}" height="{SEP}" as="geometry"/></mxCell>')
    yy += SEP
    for i, m in enumerate(corto(x) for x in METODOS[t]):
        cel.append(f'<mxCell id="{cid(t)}_m{i}" value="{esc(m)}" style="{TXT}fontSize={FS};'
                   f'fontColor={GRIS};" vertex="1" parent="{cid(t)}">'
                   f'<mxGeometry y="{yy}" width="{an}" height="{FILA}" as="geometry"/></mxCell>')
        yy += FILA

for n, r in enumerate(rels):
    ini = 'diamondThin;startFill=1;startSize=11;' if r['comp'] else 'none;'
    m_hijo = '0..*' if r['opcional'] else ('1..*' if r['comp'] else '0..*')
    ar.append(
      f'<mxCell id="as{n}" value="" style="endArrow=none;startArrow={ini}html=1;'
      f'edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor={GRIS};strokeWidth=1;" edge="1" parent="1" source="{cid(r["padre"])}" target="{cid(r["hijo"])}">'
      f'<mxGeometry relative="1" as="geometry"/></mxCell>')
    for suf, val, pos in (("p", "1", -0.82), ("h", m_hijo, 0.82)):
        ar.append(f'<mxCell id="as{n}{suf}" value="{val}" style="edgeLabel;html=1;align=center;'
                  f'verticalAlign=middle;resizable=0;points=[];fontSize=7;fontColor={TENUE};" '
                  f'vertex="1" connectable="0" parent="as{n}">'
                  f'<mxGeometry x="{pos}" relative="1" as="geometry">'
                  f'<mxPoint as="offset"/></mxGeometry></mxCell>')

tit = (f'<mxCell id="tit" value="ShopMetrics &#8212; Diagrama de clases de la soluci&#243;n" '
       f'style="text;html=1;align=left;verticalAlign=middle;fontSize=15;fontStyle=1;'
       f'fontColor=#17222D;" vertex="1" parent="1">'
       f'<mxGeometry x="{MARG_X}" y="10" width="640" height="24" as="geometry"/></mxCell>'
       f'<mxCell id="tit2" value="30 clases &#183; 43 asociaciones &#183; 8 composiciones &#183; '
       f'las claves for&#225;neas se modelan como asociaciones" '
       f'style="text;html=1;align=right;verticalAlign=middle;fontSize=9;fontColor={TENUE};" '
       f'vertex="1" parent="1">'
       f'<mxGeometry x="{PW-MARG_X-520}" y="12" width="520" height="20" as="geometry"/></mxCell>')

xml = (f'<mxfile host="app.diagrams.net" agent="ShopMetrics" version="24.7.17">\n'
       f'  <diagram id="clases-solucion" name="Diagrama de clases &#8212; soluci&#243;n">\n'
       f'    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" '
       f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{PW}" pageHeight="{PH}" '
       f'math="0" shadow="0">\n      <root>\n        <mxCell id="0"/>\n'
       f'        <mxCell id="1" parent="0"/>\n        ' + tit + "\n        "
       + "\n        ".join(cel) + "\n        " + "\n        ".join(ar)
       + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')
open('ShopMetrics_Clases.drawio','w').write(xml)
print("Clases escrito: %d bytes | %d celdas | %d asociaciones" % (len(xml), len(cel), len(rels)))
print("ocupa %d x %d px" % (total, MARG_Y+TIT+max(alturas)))

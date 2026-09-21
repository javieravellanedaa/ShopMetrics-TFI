# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'.')
from modelo import *

# ---- A4 apaisado a 96 dpi ----
PW, PH = 1169, 826
MARG_X, MARG_Y, TIT = 12, 34, 26

FS, FILA, ENC = 8, 17, 24
FS_ENT = 8                      # el nombre de la entidad, al mismo cuerpo que los campos
COL_K, COL_T = 15, 38           # ancho de la columna de clave y de la de tipo
GAP_X, GAP_Y = 6, 12

COLUMNAS = [
 ["evento_trafico","registro_pos"],
 ["dispositivo_iot","conector_pos"],
 ["zona","local","locatario","consentimiento"],
 ["centro_comercial","indicador","modelo_ml","rol","permiso"],
 ["usuario","usuario_rol","rol_permiso","centro_acceso","reporte"],
 ["evento_auditoria","notificacion","preferencia_notificacion","parametro_sistema"],
 ["regla_alerta","alerta","prediccion_vacancia","accion_retencion"],
 ["regla_destinatario","resolucion_alerta","recomendacion","recomendacion_decision"],
]

def ancho_txt(s, fs=FS):        # estimacion para IBM Plex Mono / Helvetica
    return len(s) * fs * 0.56

ents, rels = cargar()
assert sorted(t for c in COLUMNAS for t in c) == sorted(ents), "faltan o sobran entidades"

# ---- ancho de cada columna segun su contenido ----
anchos = []
for col in COLUMNAS:
    w = 0
    for t in col:
        w = max(w, ancho_txt(t, FS_ENT) + 12)
        for c in ents[t]['campos']:
            w = max(w, COL_K + ancho_txt(c["campo"]) + 6 + COL_T)
    anchos.append(int(w) + 4)

total = sum(anchos) + GAP_X*(len(COLUMNAS)-1)
print("ancho natural: %d px (disponible %d)" % (total, PW - 2*MARG_X))

sobra = (PW - 2*MARG_X) - total
GAP_X = max(GAP_X, min(26, GAP_X + sobra // max(1, len(COLUMNAS)-1)))
total = sum(anchos) + GAP_X*(len(COLUMNAS)-1)
MARG_X = (PW - total) // 2          # y lo que quede, centra el dibujo
print("ancho final:   %d px  (separacion entre columnas: %d px)" % (total, GAP_X))

crudo = [sum(ENC + len(ents[t]['campos'])*FILA for t in col) for col in COLUMNAS]
libre = (PH - MARG_Y - TIT - MARG_Y) - max(crudo)
mas = max(c for c in COLUMNAS if len(c) > 1 and crudo[COLUMNAS.index(c)] == max(crudo))
GAP_Y = max(GAP_Y, min(30, libre // max(1, len(mas)-1)))
alturas = [c + GAP_Y*(len(col)-1) for c, col in zip(crudo, COLUMNAS)]
print("separacion vertical: %d px" % GAP_Y)
print("alto maximo columna: %d px (disponible %d)" % (max(alturas), PH - MARG_Y - MARG_Y))
for col, a, h in zip(COLUMNAS, anchos, alturas):
    print("   %-2d ent  ancho %3d  alto %3d   %s" % (len(col), a, h, ", ".join(col)[:52]))

# ================= emision del XML de draw.io =================
GRIS, TENUE = "#333333", "#606060"
BORDE, ENCABEZADO = "#333333", "#DCDCDC"
C_PK, C_FK = "#000000", "#000000"

def sid(t): return "t_" + t

xy, cel, ar = {}, [], []
x = MARG_X
for col, an in zip(COLUMNAS, anchos):
    y = MARG_Y + TIT
    for t in col:
        xy[t] = (x, y, an)
        y += ENC + len(ents[t]['campos'])*FILA + GAP_Y
    x += an + GAP_X

fila_de = {}
for t, e in ents.items():
    px, py, an = xy[t]
    h = ENC + len(e['campos'])*FILA
    cel.append(
      f'<mxCell id="{sid(t)}" value="{esc(t)}" style="shape=table;startSize={ENC};container=1;'
      f'collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;columnLines=0;html=1;'
      f'whiteSpace=nowrap;fillColor={ENCABEZADO};strokeColor={BORDE};fontColor=#000000;fontSize={FS_ENT};'
      f'fontStyle=1;align=center;swimlaneFillColor=#FFFFFF;resizeLast=1;" vertex="1" parent="1">'
      f'<mxGeometry x="{px}" y="{py}" width="{an}" height="{h}" as="geometry"/></mxCell>')
    an_n = an - COL_K - COL_T
    for i, c in enumerate(e['campos']):
        rid = f'{sid(t)}_r{i}'
        fila_de[(t, c['campo'])] = rid
        cel.append(
          f'<mxCell id="{rid}" value="" style="shape=tableRow;horizontal=0;startSize=0;'
          f'swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;'
          f'points=[[0,0.5],[1,0.5]];portConstraint=eastwest;top=0;left=0;right=0;bottom=0;" '
          f'vertex="1" parent="{sid(t)}">'
          f'<mxGeometry y="{ENC+i*FILA}" width="{an}" height="{FILA}" as="geometry"/></mxCell>')
        k = c['clave']
        badge = 'PK' if k.startswith('PK') else ('FK' if k else '')
        ck = C_PK if badge == 'PK' else C_FK
        base = ('shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;'
                'right=0;overflow=hidden;html=1;whiteSpace=nowrap;')
        cel.append(f'<mxCell id="{rid}_k" value="{badge}" style="{base}align=center;fontSize=6;'
                   f'fontStyle=1;fontColor={ck};" vertex="1" parent="{rid}">'
                   f'<mxGeometry width="{COL_K}" height="{FILA}" as="geometry"/></mxCell>')
        neg = 1 if badge else 0
        cel.append(f'<mxCell id="{rid}_n" value="{esc(c["campo"])}" style="{base}align=left;'
                   f'spacingLeft=2;fontSize={FS};fontStyle={neg};" vertex="1" parent="{rid}">'
                   f'<mxGeometry x="{COL_K}" width="{an_n}" height="{FILA}" as="geometry"/></mxCell>')
        cel.append(f'<mxCell id="{rid}_t" value="{esc(c["tipo"])}" style="{base}align=right;'
                   f'spacingRight=3;fontSize=6;fontColor={TENUE};" vertex="1" parent="{rid}">'
                   f'<mxGeometry x="{COL_K+an_n}" width="{COL_T}" height="{FILA}" as="geometry"/></mxCell>')

def fila_pk(t):
    for i, c in enumerate(ents[t]['campos']):
        if c['clave'] == 'PK': return f'{sid(t)}_r{i}'
    return sid(t)

for n, r in enumerate(rels):
    fin = 'ERzeroToMany' if r['opcional'] else 'ERmany'
    ar.append(
      f'<mxCell id="e{n}" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;'
      f'startArrow=ERmandatoryOne;startFill=0;endArrow={fin};endFill=0;strokeColor={GRIS};'
      f'strokeWidth=1;fontSize=6;fontColor={TENUE};" '
      f'edge="1" parent="1" source="{sid(r["padre"])}" '
      f'target="{sid(r["hijo"])}"><mxGeometry relative="1" as="geometry"/></mxCell>')

# --- titulo y referencias ---
tit = (f'<mxCell id="tit" value="ShopMetrics &#8212; Diagrama Entidad-Relaci&#243;n del modelo completo" '
       f'style="text;html=1;align=left;verticalAlign=middle;fontSize=15;fontStyle=1;fontColor=#17222D;" '
       f'vertex="1" parent="1"><mxGeometry x="{MARG_X}" y="10" width="700" height="24" as="geometry"/></mxCell>'
       f'<mxCell id="tit2" value="30 entidades &#183; 152 campos &#183; 43 relaciones &#183; notaci&#243;n pata de gallo (IE)" '
       f'style="text;html=1;align=right;verticalAlign=middle;fontSize=9;fontColor={TENUE};" '
       f'vertex="1" parent="1"><mxGeometry x="{PW-MARG_X-460}" y="12" width="460" height="20" as="geometry"/></mxCell>')

lx = MARG_X
ly = MARG_Y + TIT + alturas[0] + 26
lw = anchos[0] + GAP_X + anchos[1]
ref = [f'<mxCell id="ref" value="Referencias" style="rounded=0;html=1;fillColor=#F6F8FA;'
       f'strokeColor=#C7D3DC;align=left;verticalAlign=top;spacingLeft=8;spacingTop=5;fontSize=9;'
       f'fontStyle=1;fontColor=#17222D;" vertex="1" parent="1">'
       f'<mxGeometry x="{lx}" y="{ly}" width="{lw}" height="212" as="geometry"/></mxCell>']
yy = ly + 24
for d, nom, col_d, claro, ts in DOMINIOS:
    ref.append(f'<mxCell id="rf_{d}" value="" style="rounded=1;html=1;fillColor={col_d};'
               f'strokeColor=none;" vertex="1" parent="1">'
               f'<mxGeometry x="{lx+9}" y="{yy+3}" width="11" height="11" as="geometry"/></mxCell>')
    ref.append(f'<mxCell id="rt_{d}" value="{esc(nom)} ({len(ts)})" style="text;html=1;align=left;'
               f'verticalAlign=middle;fontSize=8;fontColor=#4A5A68;" vertex="1" parent="1">'
               f'<mxGeometry x="{lx+25}" y="{yy}" width="{lw-30}" height="16" as="geometry"/></mxCell>')
    yy += 17
yy += 6
for txt, est in [("uno y solo uno", "startArrow=ERmandatoryOne;endArrow=none;"),
                 ("cero o muchos", "startArrow=ERzeroToMany;endArrow=none;"),
                 ("uno o muchos", "startArrow=ERmany;endArrow=none;")]:
    ref.append(f'<mxCell id="rn_{esc(txt[:5])}" value="" style="html=1;{est}startFill=0;endFill=0;'
               f'strokeColor={GRIS};" edge="1" parent="1">'
               f'<mxGeometry relative="1" as="geometry"><mxPoint x="{lx+12}" y="{yy+8}" as="sourcePoint"/>'
               f'<mxPoint x="{lx+52}" y="{yy+8}" as="targetPoint"/></mxGeometry></mxCell>')
    ref.append(f'<mxCell id="rl_{esc(txt[:5])}" value="{esc(txt)}" style="text;html=1;align=left;'
               f'verticalAlign=middle;fontSize=8;fontColor=#4A5A68;" vertex="1" parent="1">'
               f'<mxGeometry x="{lx+58}" y="{yy}" width="{lw-62}" height="16" as="geometry"/></mxCell>')
    yy += 18


# --- caja de convenciones, aprovechando el aire de abajo a la izquierda ---
ny = ly + 212
NOTAS = [
 ("Unidad de medida", "Cada entidad es una tabla f&#237;sica del modelo relacional."),
 ("Claves", "PK en &#225;mbar, FK en verde. La PK compuesta de las tablas"),
 ("", "asociativas se marca PK en sus dos columnas."),
 ("Lectura", "La l&#237;nea sale de la PK del padre y entra en la FK del hijo."),
 ("Opcionales", "Cuatro FK admiten nulo y llevan c&#237;rculo: regla_id y modelo_id"),
 ("", "de alerta, locatario_id de alerta y de recomendacion."),
 ("Alcance", "Modelo original, con centro comercial y locatario."),
]
ref.append(f'<mxCell id="nt" value="Convenciones" style="rounded=0;html=1;fillColor=#F6F8FA;'
           f'strokeColor=#C7D3DC;align=left;verticalAlign=top;spacingLeft=8;spacingTop=5;'
           f'fontSize=9;fontStyle=1;fontColor=#17222D;" vertex="1" parent="1">'
           f'<mxGeometry x="{lx}" y="{ny}" width="{lw}" height="{24+len(NOTAS)*17+6}" as="geometry"/></mxCell>')
yn = ny + 24
for k, v in NOTAS:
    if k:
        ref.append(f'<mxCell id="nk{yn}" value="{k}" style="text;html=1;align=left;'
                   f'verticalAlign=middle;fontSize=7;fontStyle=1;fontColor=#4A5A68;" '
                   f'vertex="1" parent="1"><mxGeometry x="{lx+9}" y="{yn}" width="{lw-18}" '
                   f'height="10" as="geometry"/></mxCell>')
        yn += 10
    ref.append(f'<mxCell id="nv{yn}" value="{v}" style="text;html=1;align=left;'
               f'verticalAlign=middle;fontSize=7;fontColor=#7C8C9A;" vertex="1" parent="1">'
               f'<mxGeometry x="{lx+9}" y="{yn}" width="{lw-18}" height="10" as="geometry"/></mxCell>')
    yn += 11


xml = (f'<mxfile host="app.diagrams.net" agent="ShopMetrics" version="24.7.17">\n'
       f'  <diagram id="der-completo" name="DER &#8212; modelo completo">\n'
       f'    <mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" '
       f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{PW}" pageHeight="{PH}" '
       f'math="0" shadow="0">\n      <root>\n'
       f'        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n        '
       + tit + "\n        " + "\n        ".join(ref) + "\n        "
       + "\n        ".join(cel) + "\n        " + "\n        ".join(ar)
       + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')

open('ShopMetrics_DER.drawio','w').write(xml)
xml_limpio = (xml.split('        <mxCell id="ref"')[0]
              + "\n        " + "\n        ".join(cel) + "\n        " + "\n        ".join(ar)
              + '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')
open('der_solo.drawio','w').write(xml_limpio)
print("\nDER escrito: %d bytes | %d celdas | %d aristas" % (len(xml), len(cel), len(ar)))
print("ocupa %d x %d px  dentro de A4 apaisado %d x %d" % (total, MARG_Y+TIT+max(alturas), PW, PH))

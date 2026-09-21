# -*- coding: utf-8 -*-
"""Acomodo concentrico por grado: nucleo al centro, hojas en la periferia."""
import sys, math, re, collections
ENTRADA = sys.argv[1] if len(sys.argv)>1 else 'der_solo.drawio'
SALIDA  = sys.argv[2] if len(sys.argv)>2 else 'der_radial.drawio'
PREFIJO = sys.argv[3] if len(sys.argv)>3 else 't_'
CLASES  = PREFIJO == 'c_'
sys.path.insert(0,'.')
from modelo import cargar

PW, PH = 1587, 1123          # A3 apaisado
MX, MY, TIT = 16, 16, 30
FILA, ENC = 17, 24

ents, rels = cargar()
from modelo import clase
nom = (lambda t: clase(t)) if CLASES else (lambda t: t)
gr = collections.Counter()
for r in rels:
    gr[r['padre']] += 1; gr[r['hijo']] += 1

TIPO = {'UUID':'UUID','VARCHAR':'String','INT':'int','TIMESTAMP':'DateTime',
        'DECIMAL':'Decimal','BOOLEAN':'bool','DATE':'Date'}
def tam(t):
    if CLASES:
        from modelo import METODOS
        at = [c for c in ents[t]['campos'] if 'FK' not in c['clave']]
        miem = (["%s %s: %s" % ('+' if c['clave']=='PK' else '-', c['campo'],
                 TIPO.get(c['tipo'],c['tipo'])) for c in at]
                + [m.split('):')[0]+')' if len(m)>25 and '):' in m else m for m in METODOS[t]])
        an = max(len(clase(t))*8*0.56 + 14, max(len(m)*8*0.56 + 11 for m in miem))
        return int(an)+2, 24 + len(at)*17 + 9 + len(METODOS[t])*17
    an = max(len(t)*8*0.56 + 14,
             max(15 + len(c['campo'])*8*0.56 + 6 + 42 for c in ents[t]['campos']))
    return int(an) + 4, ENC + len(ents[t]['campos'])*FILA

# tres anillos por grado
nucleo = [t for t in ents if gr[t] >= 6]
medio  = [t for t in ents if 3 <= gr[t] < 6]
borde  = [t for t in ents if gr[t] < 3]
nucleo.sort(key=lambda t: -gr[t])

# cada hijo se ubica en el angulo de su padre principal: asi las lineas
# quedan radiales y cortas en vez de cruzar el dibujo entero
padres = {}
for r in rels:
    padres.setdefault(r['hijo'], []).append(r['padre'])
def principal(t):
    return max(padres.get(t, []), key=lambda p: gr[p], default=None)

CX, CY = MX + (PW-2*MX)/2, MY + TIT + (PH-2*MY-TIT)/2
pos = {}

def anillo(ts, a, b, fase=0.0):
    n = len(ts)
    for i, t in enumerate(ts):
        ang = fase + 2*math.pi*i/n
        w, h = tam(t)
        pos[t] = [CX + a*math.cos(ang) - w/2, CY + b*math.sin(ang) - h/2, w, h]

# el nucleo: cuatro cajas en rombo apretado alrededor del centro
ang = {}
def anillo_ang(ts, a, b, fase=0.0):
    n = len(ts)
    for i, t in enumerate(ts):
        al = fase + 2*math.pi*i/n
        ang[t] = al
        w, h = tam(t)
        pos[t] = [CX + a*math.cos(al) - w/2, CY + b*math.sin(al) - h/2, w, h]

anillo_ang(nucleo, 205, 150, -math.pi/2)
medio.sort(key=lambda t: ang.get(principal(t), 0.0))
anillo_ang(medio, 430, 300, math.pi/9)
borde.sort(key=lambda t: ang.get(principal(t), 0.0))
anillo_ang(borde, 700, 455, 0)

# relajacion: separar lo que se superponga, empujando desde el centro
for _ in range(600):
    movio = False
    ks = list(pos)
    for i in range(len(ks)):
        for j in range(i+1, len(ks)):
            a, b = pos[ks[i]], pos[ks[j]]
            sx = (a[0]+a[2]/2) - (b[0]+b[2]/2)
            sy = (a[1]+a[3]/2) - (b[1]+b[3]/2)
            ox = (a[2]+b[2])/2 + 40 - abs(sx)
            oy = (a[3]+b[3])/2 + 28 - abs(sy)
            if ox > 0 and oy > 0:
                movio = True
                if ox < oy:
                    d = ox/2 * (1 if sx >= 0 else -1); a[0] += d; b[0] -= d
                else:
                    d = oy/2 * (1 if sy >= 0 else -1); a[1] += d; b[1] -= d
    if not movio: break

x0 = min(p[0] for p in pos.values()); y0 = min(p[1] for p in pos.values())
x1 = max(p[0]+p[2] for p in pos.values()); y1 = max(p[1]+p[3] for p in pos.values())
dx, dy = MX - x0, MY + TIT - y0
for p in pos.values(): p[0] += dx; p[1] += dy
print("anillos: nucleo %d, medio %d, borde %d" % (len(nucleo), len(medio), len(borde)))
print("ocupa %.0f x %.0f  en pagina %d x %d" % (x1-x0, y1-y0, PW, PH))
print("nucleo:", ", ".join("%s(%d)" % (t, gr[t]) for t in nucleo))

# reescribir las posiciones en el XML ya generado
s = open(ENTRADA).read()
s = s.replace('edgeStyle=entityRelationEdgeStyle;rounded=0;html=1;',
              'edgeStyle=entityRelationEdgeStyle;rounded=0;html=1;jumpStyle=arc;jumpSize=7;')
s = re.sub(r'pageWidth="\d+" pageHeight="\d+"', 'pageWidth="%d" pageHeight="%d"' % (PW, PH), s)
for t, (x, y, w, h) in pos.items():
    s = re.sub(r'(<mxCell id="%s%s" [^>]*?><mxGeometry )x="[\d.-]+" y="[\d.-]+"' % (PREFIJO, re.escape(nom(t))),
               r'\g<1>x="%d" y="%d"' % (round(x), round(y)), s)


open(SALIDA,'w').write(s)
print("escrito der_radial.drawio, con lados de salida por posicion relativa")

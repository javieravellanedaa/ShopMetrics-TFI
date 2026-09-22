# -*- coding: utf-8 -*-
"""Auditoria de balanceo entre los modelos del punto 10.

Cruza el diccionario de datos, el indice de casos de uso, los diagramas de
secuencia y de clases del Word, los exportados de Enterprise Architect y los
dos .drawio. Se corre desde la raiz del repositorio:

    python3 scripts/diagramas/balanceo.py
"""
import os, re, sys, glob, json, collections
import xml.etree.ElementTree as ET
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORD = os.path.join(RAIZ, 'documento/STF_Gomez_Javier_E1_v1.docx')
DIAG = os.path.join(RAIZ, 'documento/diagramas')
EA   = os.path.join(RAIZ, 'modelo-ea/export')
BLIP = './/{http://schemas.openxmlformats.org/drawingml/2006/main}blip'
fallas = []

def titulo(t):
    print("\n" + "="*68); print("  " + t); print("="*68)

def ok(etiqueta, valor, esperado=0):
    estado = "OK" if valor == esperado else "REVISAR"
    print("  %-46s %4s  %s" % (etiqueta, valor, estado))
    if valor != esperado: fallas.append(etiqueta)

# ---------- diccionario de datos ----------
d = Document(WORD)
els = list(d.element.body.iterchildren())

def seccion(pref):
    return next(i for i, e in enumerate(els) if e.tag.endswith('}p')
                and Paragraph(e, d).style.name.startswith('Heading')
                and Paragraph(e, d).text.strip().startswith(pref))

ents, pend = {}, None
for el in els[seccion('10.5.8'):]:
    if el.tag.endswith('}p'):
        m = re.match(r'^([a-z][a-z_]+):\s', re.sub(r'\s+', ' ', Paragraph(el, d).text).strip())
        if m: pend = m.group(1)
    elif el.tag.endswith('}tbl') and pend:
        t = Table(el, d)
        if [c.text.strip() for c in t.rows[0].cells][:2] == ['Campo', 'Tipo']:
            ents[pend] = [[c.text.strip() for c in f.cells] for f in t.rows[1:]]
        pend = None

ALIAS = {'centro': 'centro_comercial', 'conector': 'conector_pos', 'dispositivo': 'dispositivo_iot',
         'regla': 'regla_alerta', 'modelo': 'modelo_ml', 'prediccion': 'prediccion_vacancia',
         'asignado_a': 'usuario'}
rels = []
for t, campos in ents.items():
    for c in campos:
        if 'FK' not in c[2]: continue
        base = re.sub(r'_id$', '', c[0])
        rels.append((ALIAS.get(base, base), t, c[0]))

titulo("A. INTEGRIDAD REFERENCIAL")
ok("entidades sin clave primaria", sum(1 for c in ents.values() if not any(x[2].startswith('PK') for x in c)))
ok("claves foraneas sin destino", sum(1 for p, h, c in rels if p not in ents))
ok("tipos de FK distintos del de la PK referenciada",
   sum(1 for p, h, c in rels if p in ents
       and next(x[1] for x in ents[h] if x[0] == c) != next((x[1] for x in ents[p] if x[2] == 'PK'), None)))
ok("tablas asociativas con PK compuesta mal formada",
   sum(1 for t, c in ents.items()
       if len([x for x in c if x[2].startswith('PK')]) > 1
       and not all('FK' in x[2] for x in c if x[2].startswith('PK'))))
g = collections.defaultdict(set)
for p, h, c in rels: g[h].add(p)
est, ciclos = {}, []
def dfs(n):
    est[n] = 1
    for m in g[n]:
        if est.get(m) == 1: ciclos.append((n, m))
        elif est.get(m) is None: dfs(m)
    est[n] = 2
for n in ents:
    if est.get(n) is None: dfs(n)
ok("ciclos de dependencia", len(ciclos))
conect = {p for p, h, c in rels} | {h for p, h, c in rels}
ok("entidades aisladas", len(set(ents) - conect))

# ---------- casos de uso y diagramas ----------
titulo("B. BALANCEO ENTRE MODELOS")
ini = seccion('10.5.2')
cus = []
for el in els[ini:ini + 12]:
    if el.tag.endswith('}tbl'):
        t = Table(el, d)
        if 'Caso de Uso' in " ".join(c.text for c in t.rows[0].cells):
            cus = [f.cells[0].text.strip() for f in t.rows[1:]]; break

tit = {}
for el in els:
    if not el.tag.endswith('}p'): continue
    p = Paragraph(el, d)
    m = re.match(r'^(10(?:\.\d+)*)\s+(.*)$', re.sub(r'\s+', ' ', p.text).strip())
    if p.style.name.startswith('Heading') and m: tit[m.group(1)] = m.group(2)

def ids(pref):
    return [re.match(r'(CU-\d+-\d+)', v).group(1)
            for k, v in tit.items() if k.startswith(pref + '.') and re.match(r'CU-', v)]

seq, cls = ids('10.5.4'), ids('10.5.7')
ea_s = sorted(os.path.basename(p)[:-4] for p in glob.glob(EA + '/seq/*.png'))
ea_c = sorted(os.path.basename(p)[:-4] for p in glob.glob(EA + '/clases/*.png'))
print("  indice %d | secuencia %d | clases %d | EA secuencia %d | EA clases %d"
      % (len(cus), len(seq), len(cls), len(ea_s), len(ea_c)))
ok("CU del indice sin diagrama de secuencia", len(set(cus) - set(seq)))
ok("CU del indice sin diagrama de clases", len(set(cus) - set(cls)))
ok("diagramas de secuencia sin CU en el indice", len(set(seq) - set(cus)))
ok("CU del indice sin exportar de Enterprise Architect", len(set(cus) - set(ea_s)))

# una imagen por diagrama
sec, img = None, {}
for el in els:
    if el.tag.endswith('}p'):
        p = Paragraph(el, d)
        m = re.match(r'^(10\.5\.[47]\.\d+)\s', re.sub(r'\s+', ' ', p.text).strip())
        if p.style.name.startswith('Heading'):
            sec = m.group(1) if m else None
            if sec: img.setdefault(sec, 0)
    if sec: img[sec] = img.get(sec, 0) + len(el.findall(BLIP))
# cada diagrama por caso de uso lleva exactamente una imagen; el 10.5.7.1,
# que es el de la solucion completa, lleva una lamina por dominio
por_cu = {k: v for k, v in img.items() if k != '10.5.7.1'}
ok("diagramas de caso de uso sin imagen", sum(1 for v in por_cu.values() if v == 0))
ok("diagramas de caso de uso con mas de una", sum(1 for v in por_cu.values() if v > 1))
ok("laminas del diagrama de clases de la solucion", img.get('10.5.7.1', 0), 5)

# ---------- los .drawio contra el diccionario ----------
titulo("C. DIAGRAMAS .drawio CONTRA EL DICCIONARIO")
def leer(arch, marca):
    r = ET.parse(arch).getroot(); cells = r.findall('.//mxCell')
    cajas = {c.get('id'): c.get('value') for c in cells
             if c.get('parent') == '1' and c.get('vertex') == '1' and marca in (c.get('style') or '')}
    filas = collections.Counter()
    for c in cells:
        if c.get('parent') in cajas and 'shape=tableRow' in (c.get('style') or ''):
            filas[cajas[c.get('parent')]] += 1
    ar = [(cajas.get(c.get('source')), cajas.get(c.get('target')))
          for c in cells if c.get('edge') == '1']
    return cajas, filas, [a for a in ar if a[0] and a[1]]

cd, fd, ad = leer(DIAG + '/ShopMetrics_DER.drawio', 'shape=table;')
cc, _, ac = leer(DIAG + '/ShopMetrics_Clases.drawio', 'swimlane;')
ok("entidades del DER que no estan en el diccionario", len(set(cd.values()) ^ set(ents)))
ok("clases que no corresponden a una entidad", abs(len(cc) - len(ents)))
ok("entidades con distinta cantidad de campos",
   sum(1 for t, c in ents.items() if fd.get(t, 0) != len(c)))
ok("relaciones del DER distintas del diccionario",
   len({(p, h) for p, h, c in rels} ^ set(ad)))
ok("relaciones del diagrama de clases", abs(len(ac) - len(rels)))

# ---------- aristas que atraviesan cajas ----------
titulo("D. RUTEO")
def cruces(arch, marca):
    r = ET.parse(arch).getroot(); cells = r.findall('.//mxCell')
    cajas = {}
    for c in cells:
        if c.get('parent') == '1' and c.get('vertex') == '1' and marca in (c.get('style') or ''):
            g = c.find('mxGeometry')
            if g is not None and g.get('x'):
                cajas[c.get('id')] = tuple(float(g.get(k)) for k in ('x', 'y', 'width', 'height'))
    n = 0
    for e in (c for c in cells if c.get('edge') == '1'):
        g = e.find('mxGeometry'); pts = []
        if e.get('source') in cajas:
            x, y, w, h = cajas[e.get('source')]; pts.append((x + w / 2, y + h / 2))
        for arr in (g.findall('Array') if g is not None else []):
            pts += [(float(p.get('x') or 0), float(p.get('y') or 0)) for p in arr.findall('mxPoint')]
        if e.get('target') in cajas:
            x, y, w, h = cajas[e.get('target')]; pts.append((x + w / 2, y + h / 2))
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            for cid, (x, y, w, h) in cajas.items():
                if cid in (e.get('source'), e.get('target')): continue
                if any(x < x1 + (x2 - x1) * t / 40 < x + w and y < y1 + (y2 - y1) * t / 40 < y + h
                       for t in range(1, 40)):
                    n += 1; break
            else: continue
            break
    return n

ok("aristas del DER que atraviesan una tabla", cruces(DIAG + '/ShopMetrics_DER.drawio', 'shape=table;'))
ok("aristas del diagrama de clases que atraviesan una clase",
   cruces(DIAG + '/ShopMetrics_Clases.drawio', 'swimlane;'))

print("\n" + "="*68)
print("  RESULTADO: %s" % ("todo balanceado" if not fallas else "%d controles a revisar" % len(fallas)))
for f in fallas: print("     - %s" % f)
print("="*68)
sys.exit(1 if fallas else 0)

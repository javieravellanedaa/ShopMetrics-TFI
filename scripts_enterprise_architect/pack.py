# -*- coding: utf-8 -*-
"""Empaqueta las 30 entidades (con todos sus campos) en columnas,
minimizando cruces, largo de lineas y desbalance de columnas."""
import sys, io, json, random, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

E = [
 ("centro_comercial","zona"),("centro_comercial","locatario"),("centro_comercial","centro_acceso"),
 ("centro_comercial","regla_alerta"),("centro_comercial","evento_auditoria"),("centro_comercial","reporte"),
 ("centro_comercial","recomendacion"),("centro_comercial","parametro_sistema"),
 ("zona","dispositivo_iot"),("zona","local"),("zona","alerta"),
 ("locatario","local"),("locatario","conector_pos"),("locatario","consentimiento"),
 ("locatario","prediccion_vacancia"),("locatario","alerta"),("locatario","recomendacion"),
 ("conector_pos","registro_pos"),("dispositivo_iot","evento_trafico"),
 ("usuario","usuario_rol"),("usuario","centro_acceso"),("usuario","evento_auditoria"),("usuario","reporte"),
 ("usuario","notificacion"),("usuario","preferencia_notificacion"),("usuario","alerta"),
 ("usuario","regla_destinatario"),("usuario","resolucion_alerta"),("usuario","recomendacion_decision"),
 ("usuario","parametro_sistema"),
 ("rol","usuario_rol"),("rol","rol_permiso"),("rol","centro_acceso"),("permiso","rol_permiso"),
 ("indicador","regla_alerta"),("regla_alerta","alerta"),("regla_alerta","regla_destinatario"),
 ("modelo_ml","alerta"),("modelo_ml","prediccion_vacancia"),("modelo_ml","recomendacion"),
 ("alerta","resolucion_alerta"),("prediccion_vacancia","accion_retencion"),
 ("recomendacion","recomendacion_decision"),
]
dic = json.load(open("dic.json", encoding="utf-8"))
ALTO = {}
for e in dic:
    fk = any("FK" in c["clave"] for c in e["campos"])
    ALTO[e["tabla"]] = 24 + 14 + 13 * (len(e["campos"]) + 1 + (1 if fk else 0))
N = sorted(ALTO)
assert len(N) == 30

COLS, W, GAPH, GAPV = 5, 215, 40, 26
COLX = [c * (W + GAPH) for c in range(COLS)]

def geom(asig):
    """asig: lista de listas (columnas con entidades en orden) -> centro y rect de cada una"""
    pos = {}
    for c, col in enumerate(asig):
        y = 0
        for n in col:
            h = ALTO[n]
            pos[n] = (COLX[c] + W / 2.0, -(y + h / 2.0), W, h)
            y += h + GAPV
    return pos

def corta(p, q, r):
    cx, cy, w, h = r
    x0, x1, y0, y1 = cx - w/2, cx + w/2, cy - h/2, cy + h/2
    ax, ay = p; bx, by = q
    dx, dy = bx - ax, by - ay
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, ax-x0), (dx, x1-ax), (-dy, ay-y0), (dy, y1-ay)):
        if abs(pp) < 1e-12:
            if qq < 0: return False
        else:
            t = qq/pp
            if pp < 0:
                if t > t1: return False
                if t > t0: t0 = t
            else:
                if t < t0: return False
                if t < t1: t1 = t
    return t0 < t1 - 1e-9

def orient(p, q, r):
    v = (q[1]-p[1])*(r[0]-q[0]) - (q[0]-p[0])*(r[1]-q[1])
    return 0 if abs(v) < 1e-9 else (1 if v > 0 else 2)

def evalua(asig, completo=True):
    pos = geom(asig)
    segs = []
    bloq = 0
    for a, b in E:
        pa, pb = pos[a], pos[b]
        p, q = (pa[0], pa[1]), (pb[0], pb[1])
        for n, r in pos.items():
            if n == a or n == b: continue
            if corta(p, q, r): bloq += 1
        segs.append((p, q))
    largo = sum(abs(s[0][0]-s[1][0]) + abs(s[0][1]-s[1][1]) for s in segs) / 100.0
    alturas = [sum(ALTO[n] for n in col) + GAPV*max(0, len(col)-1) for col in asig]
    desbal = (max(alturas) - min(alturas)) / 100.0
    cruces = 0
    if completo:
        for i in range(len(segs)):
            p1, q1 = segs[i]
            for j in range(i+1, len(segs)):
                p2, q2 = segs[j]
                if len({p1,q1,p2,q2}) < 4: continue
                if orient(p1,q1,p2) != orient(p1,q1,q2) and orient(p2,q2,p1) != orient(p2,q2,q1):
                    cruces += 1
    return bloq, cruces, largo, desbal, max(alturas)

def S(asig):
    b, x, l, d, _ = evalua(asig, completo=False)
    return b * 120 + l + d * 4

random.seed(17)
mejor, mejorP = None, 1e18
for intento in range(3):
    orden = N[:]; random.shuffle(orden)
    asig = [[] for _ in range(COLS)]
    for i, n in enumerate(orden): asig[i % COLS].append(n)
    s = S(asig)
    for paso in range(16000):
        T = 60.0 * math.exp(-paso / 3200)
        c1 = random.randrange(COLS); c2 = random.randrange(COLS)
        if not asig[c1]: continue
        i1 = random.randrange(len(asig[c1]))
        if c1 == c2:
            if len(asig[c1]) < 2: continue
            i2 = random.randrange(len(asig[c1]))
            asig[c1][i1], asig[c1][i2] = asig[c1][i2], asig[c1][i1]
            ns = S(asig)
            if ns <= s or random.random() < math.exp((s-ns)/max(T,1e-9)): s = ns
            else: asig[c1][i1], asig[c1][i2] = asig[c1][i2], asig[c1][i1]
        else:
            n = asig[c1].pop(i1)
            i2 = random.randrange(len(asig[c2]) + 1)
            asig[c2].insert(i2, n)
            ns = S(asig)
            if ns <= s or random.random() < math.exp((s-ns)/max(T,1e-9)): s = ns
            else:
                asig[c2].pop(i2); asig[c1].insert(i1, n)
    b, x, l, d, alt = evalua(asig)
    p = b*1000 + x*8 + l
    print(f"  intento {intento}: sobre cajas={b} cruces={x} altura={alt}px", flush=True)
    if p < mejorP: mejorP, mejor = p, [c[:] for c in asig]

b, x, l, d, alt = evalua(mejor)
ancho = COLS*W + (COLS-1)*GAPH
print(f"\nMEJOR -> lineas sobre cajas: {b}   cruces: {x}   lienzo {ancho} x {alt} px "
      f"({ancho/96*2.54:.1f} x {alt/96*2.54:.1f} cm)")
for c, col in enumerate(mejor):
    print(f"  col {c}: " + ", ".join(col))
json.dump(mejor, open("pack.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(ALTO, open("altos.json", "w", encoding="utf-8"), ensure_ascii=False)

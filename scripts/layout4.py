# -*- coding: utf-8 -*-
"""Ubicacion en grilla evitando que CUALQUIER linea (tambien las diagonales)
pase por encima de una caja, y minimizando cruces."""
import sys, io, random, math, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_src = open("layout.py", encoding="utf-8").read().split("def coste")[0]
_src = "\n".join(x for x in _src.splitlines() if not x.startswith("sys.stdout"))
exec(_src)                      # E, N, COLS, ROWS, SLOTS

COLS = 4
ROWS = 11
SLOTS = [(r, c) for r in range(ROWS) for c in range(COLS)]

# geometria real de la celda (COLW=250, ROWH=68, W=220, H=40)
HW, HH = 110.0 / 250.0, 20.0 / 68.0

def centro(p): return (p[1] * 1.0, -p[0] * 1.0)

def corta_caja(p, q, celda):
    """el segmento p-q atraviesa el rectangulo de 'celda'"""
    cx, cy = centro(celda)
    x0, x1 = cx - HW, cx + HW
    y0, y1 = cy - HH, cy + HH
    ax, ay = centro(p); bx, by = centro(q)
    # Liang-Barsky
    dx, dy = bx - ax, by - ay
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, ax - x0), (dx, x1 - ax), (-dy, ay - y0), (dy, y1 - ay)):
        if abs(pp) < 1e-12:
            if qq < 0: return False
        else:
            t = qq / pp
            if pp < 0:
                if t > t1: return False
                if t > t0: t0 = t
            else:
                if t < t0: return False
                if t < t1: t1 = t
    return t0 < t1 - 1e-9

# precomputo: para cada par de celdas, que celdas atraviesa el segmento
print("precomputando bloqueos...", flush=True)
ATRAV = {}
for i, a in enumerate(SLOTS):
    for b in SLOTS[i+1:]:
        lst = [s for s in SLOTS if s != a and s != b and corta_caja(a, b, s)]
        if lst:
            ATRAV[(a, b)] = lst
            ATRAV[(b, a)] = lst
print("  pares con bloqueo potencial:", len(ATRAV) // 2, flush=True)

def orient(p, q, r):
    v = (q[1]-p[1])*(r[0]-q[0]) - (q[0]-p[0])*(r[1]-q[1])
    return 0 if abs(v) < 1e-9 else (1 if v > 0 else 2)

def evalua(pos):
    ocup = set(pos.values())
    bloq = 0
    segs = []
    for a, b in E:
        pa, pb = pos[a], pos[b]
        for s in ATRAV.get((pa, pb), ()):
            if s in ocup: bloq += 1
        segs.append((centro(pa), centro(pb)))
    cruces = 0
    for i in range(len(segs)):
        p1, q1 = segs[i]
        for j in range(i+1, len(segs)):
            p2, q2 = segs[j]
            if len({p1, q1, p2, q2}) < 4: continue
            if orient(p1,q1,p2) != orient(p1,q1,q2) and orient(p2,q2,p1) != orient(p2,q2,q1):
                cruces += 1
    largo = sum(abs(pos[a][0]-pos[b][0]) + abs(pos[a][1]-pos[b][1]) for a, b in E)
    return bloq, cruces, largo

def rapido(pos):
    ocup = set(pos.values())
    bloq = largo = 0
    for a, b in E:
        pa, pb = pos[a], pos[b]
        for s in ATRAV.get((pa, pb), ()):
            if s in ocup: bloq += 1
        largo += abs(pa[0]-pb[0]) + abs(pa[1]-pb[1])
    return bloq * 60 + largo

random.seed(5)
mejor, mejorS = None, 10**9
for intento in range(8):
    slots = SLOTS[:]; random.shuffle(slots)
    pos = {n: slots[i] for i, n in enumerate(N)}
    libres = slots[len(N):]
    s = rapido(pos)
    for paso in range(40000):
        T = 7.0 * math.exp(-paso / 7000)
        a = random.choice(N)
        if libres and random.random() < 0.35:
            k = random.randrange(len(libres)); v = pos[a]; pos[a] = libres[k]
            ns = rapido(pos)
            if ns <= s or random.random() < math.exp((s-ns)/max(T,1e-6)): libres[k] = v; s = ns
            else: pos[a] = v
        else:
            b2 = random.choice(N)
            if a == b2: continue
            pos[a], pos[b2] = pos[b2], pos[a]
            ns = rapido(pos)
            if ns <= s or random.random() < math.exp((s-ns)/max(T,1e-6)): s = ns
            else: pos[a], pos[b2] = pos[b2], pos[a]
    b, x, l = evalua(pos)
    print(f"  intento {intento}: bloqueos={b} cruces={x} largo={l}", flush=True)
    punt = b * 1000 + x * 10 + l
    if punt < mejorS: mejorS, mejor = punt, dict(pos)

b, x, l = evalua(mejor)
print(f"\nMEJOR -> lineas sobre cajas: {b}   cruces: {x}   largo: {l}")
usadas = sorted({r for r, c in mejor.values()})
remap = {r: i for i, r in enumerate(usadas)}
mejor = {n: (remap[r], c) for n, (r, c) in mejor.items()}
filas = max(r for r, c in mejor.values()) + 1
g = [["" for _ in range(COLS)] for _ in range(filas)]
for n, (r, c) in mejor.items(): g[r][c] = n
for r in range(filas): print("   " + " | ".join(f"{g[r][c]:<24}" for c in range(COLS)))
json.dump(g, open("grilla4.json", "w", encoding="utf-8"), ensure_ascii=False)

# -*- coding: utf-8 -*-
"""Fase 2: parte de la grilla sin bloqueos y baja la cantidad de cruces."""
import sys, io, random, math, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_src = open("layout.py", encoding="utf-8").read().split("random.seed")[0]
_src = "\n".join(x for x in _src.splitlines() if not x.startswith("sys.stdout"))
exec(_src)          # aporta E, N, COLS, coste()

grilla = json.load(open("grilla.json", encoding="utf-8"))
pos = {}
for r, fila in enumerate(grilla):
    for c, n in enumerate(fila):
        if n:
            pos[n] = (r, c)

ROWS2 = len(grilla) + 1
SL = [(r, c) for r in range(ROWS2) for c in range(COLS)]
ocupados = set(pos.values())
libres = [s for s in SL if s not in ocupados]

def S(p):
    b, x, l = coste(p)
    return b * 1000 + x * 10 + l

random.seed(11)
s = S(pos)
print("inicio:", coste(pos), flush=True)
mejor, mejorS = dict(pos), s

for paso in range(9000):
    T = 4.0 * math.exp(-paso / 1800)
    a = random.choice(N)
    if libres and random.random() < 0.3:
        k = random.randrange(len(libres))
        viejo = pos[a]
        pos[a] = libres[k]
        ns = S(pos)
        if ns <= s or random.random() < math.exp((s - ns) / max(T, 1e-6)):
            libres[k] = viejo
            s = ns
        else:
            pos[a] = viejo
    else:
        b2 = random.choice(N)
        if a == b2:
            continue
        pos[a], pos[b2] = pos[b2], pos[a]
        ns = S(pos)
        if ns <= s or random.random() < math.exp((s - ns) / max(T, 1e-6)):
            s = ns
        else:
            pos[a], pos[b2] = pos[b2], pos[a]
    if s < mejorS:
        mejorS, mejor = s, dict(pos)

b, x, l = coste(mejor)
print(f"FINAL -> atraviesan cajas: {b}   cruces: {x}   largo: {l}")

usadas = sorted({r for r, c in mejor.values()})
remap = {r: i for i, r in enumerate(usadas)}
mejor = {n: (remap[r], c) for n, (r, c) in mejor.items()}
filas = max(r for r, c in mejor.values()) + 1
g = [["" for _ in range(COLS)] for _ in range(filas)]
for n, (r, c) in mejor.items():
    g[r][c] = n
for r in range(filas):
    print("   " + " | ".join(f"{g[r][c]:<24}" for c in range(COLS)))
json.dump(g, open("grilla.json", "w", encoding="utf-8"), ensure_ascii=False)

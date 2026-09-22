# -*- coding: utf-8 -*-
"""Busca una ubicacion en grilla que evite lineas atravesando cajas y minimice cruces."""
import sys, io, random, math, json
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
N = sorted({x for e in E for x in e})
assert len(N) == 30, len(N)
COLS, ROWS = 3, 12
SLOTS = [(r, c) for r in range(ROWS) for c in range(COLS)]

def coste(pos):
    """pos: nombre -> (fila, col). Devuelve (bloqueos, cruces, largo)."""
    ocup = {v: k for k, v in pos.items()}
    bloq = 0
    segs = []
    for a, b in E:
        ra, ca = pos[a]; rb, cb = pos[b]
        # linea que corre por la misma columna con una caja en el medio
        if ca == cb and abs(ra - rb) > 1:
            for r in range(min(ra, rb) + 1, max(ra, rb)):
                if (r, ca) in ocup: bloq += 1
        # linea horizontal en la misma fila salteando una celda ocupada
        if ra == rb and abs(ca - cb) > 1:
            for c in range(min(ca, cb) + 1, max(ca, cb)):
                if (ra, c) in ocup: bloq += 1
        segs.append(((ca, -ra), (cb, -rb)))
    # cruces entre segmentos
    def orient(p, q, r):
        v = (q[1]-p[1])*(r[0]-q[0]) - (q[0]-p[0])*(r[1]-q[1])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else 2)
    cruces = 0
    for i in range(len(segs)):
        for j in range(i+1, len(segs)):
            p1,q1 = segs[i]; p2,q2 = segs[j]
            if len({p1,q1,p2,q2}) < 4: continue     # comparten extremo
            o1,o2,o3,o4 = orient(p1,q1,p2),orient(p1,q1,q2),orient(p2,q2,p1),orient(p2,q2,q1)
            if o1 != o2 and o3 != o4: cruces += 1
    largo = sum(abs(pos[a][0]-pos[b][0]) + abs(pos[a][1]-pos[b][1]) for a, b in E)
    return bloq, cruces, largo

def coste_rapido(pos):
    ocup = {v: k for k, v in pos.items()}
    bloq = largo = 0
    for a, b in E:
        ra, ca = pos[a]; rb, cb = pos[b]
        if ca == cb and abs(ra - rb) > 1:
            for r in range(min(ra, rb) + 1, max(ra, rb)):
                if (r, ca) in ocup: bloq += 1
        if ra == rb and abs(ca - cb) > 1:
            for c in range(min(ca, cb) + 1, max(ca, cb)):
                if (ra, c) in ocup: bloq += 1
        largo += abs(ra - rb) + abs(ca - cb)
    return bloq, largo

def score(pos):
    b, l = coste_rapido(pos)
    return b * 100 + l

random.seed(7)
mejor, mejorS = None, 10**9
for intento in range(6):
    slots = SLOTS[:]
    random.shuffle(slots)
    pos = {n: slots[i] for i, n in enumerate(N)}
    libres = slots[len(N):]
    s = score(pos)
    T = 9.0
    for paso in range(30000):
        T = 9.0 * math.exp(-paso / 5500)
        a = random.choice(N)
        if libres and random.random() < 0.35:
            k = random.randrange(len(libres))
            viejo = pos[a]; pos[a] = libres[k]
            ns = score(pos)
            if ns <= s or random.random() < math.exp((s - ns) / max(T, 1e-6)):
                libres[k] = viejo; s = ns
            else:
                pos[a] = viejo
        else:
            b = random.choice(N)
            if a == b: continue
            pos[a], pos[b] = pos[b], pos[a]
            ns = score(pos)
            if ns <= s or random.random() < math.exp((s - ns) / max(T, 1e-6)):
                s = ns
            else:
                pos[a], pos[b] = pos[b], pos[a]
    if s < mejorS:
        mejorS, mejor = s, dict(pos)
        print(f"  intento {intento}: score={s}", flush=True)

b, x, l = coste(mejor)
print(f"\nMEJOR -> lineas atravesando cajas: {b}   cruces: {x}   largo total: {l}")
# compactar filas vacias
usadas = sorted({r for r, c in mejor.values()})
remap = {r: i for i, r in enumerate(usadas)}
mejor = {n: (remap[r], c) for n, (r, c) in mejor.items()}
filas = max(r for r, c in mejor.values()) + 1
print(f"filas usadas: {filas}")
grilla = [["" for _ in range(COLS)] for _ in range(filas)]
for n, (r, c) in mejor.items(): grilla[r][c] = n
for r in range(filas):
    print("   " + " | ".join(f"{grilla[r][c]:<24}" for c in range(COLS)))
json.dump(grilla, open("grilla.json", "w", encoding="utf-8"), ensure_ascii=False)

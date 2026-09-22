# -*- coding: utf-8 -*-
"""Cuanto espacio necesita el DER completo, con todas las columnas y sus tipos."""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ent = json.load(open("dic.json", encoding="utf-8"))
PX_CHAR = 6.3      # ancho medio de caracter a 11px (medido sobre el export de EA)
LINEA   = 13       # alto de renglon
TIT     = 24       # alto del titulo
PAD     = 14

filas = []
for e in ent:
    campos = e["campos"]
    tiene_fk = any("FK" in c["clave"] for c in campos)
    compart = 1 + (1 if tiene_fk else 0)          # cabeceras «PK» y «FK»
    alto = TIT + PAD + LINEA * (len(campos) + compart)
    textos = [f"{c['campo']}: {c['tipo']}" for c in campos] + [e["tabla"]]
    ancho = max(len(t) for t in textos) * PX_CHAR + 24
    filas.append((e["tabla"], len(campos), round(ancho), alto))

filas.sort(key=lambda x: -x[3])
print(f"{'entidad':<26} {'campos':>6} {'ancho':>6} {'alto':>5}")
for f in filas[:8]:
    print(f"  {f[0]:<24} {f[1]:>6} {f[2]:>6} {f[3]:>5}")
print("  ...")
W = max(f[2] for f in filas)
H_total = sum(f[3] for f in filas)
print(f"\nancho de caja necesario: {W} px   alto total apilado: {H_total} px")

for cols in (3, 4, 5, 6):
    GAP_V, GAP_H = 20, 34
    alto_col = H_total / cols + GAP_V * (len(filas) / cols)
    ancho = cols * W + (cols - 1) * GAP_H
    wCm, hCm = ancho / 96 * 2.54, alto_col / 96 * 2.54
    for pag, uw, uh in (("A4 vertical", 16.26, 18.79), ("A4 apaisado", 24.96, 10.1),
                        ("A3 apaisado", 38.6, 23.3)):
        esc = min(uw / wCm, uh / hCm)
        pt = 7.5 * esc          # la fuente de atributos de EA ronda 7,5 pt
        marca = "OK " if pt >= 7.0 else "   "
        print(f"{marca}{cols} col -> {wCm:5.1f} x {hCm:5.1f} cm | {pag:<12} escala {esc:4.2f}  texto ~{pt:.1f} pt")
    print()

# -*- coding: utf-8 -*-
"""Arma un PDF A3 apaisado con el DER completo a tamaño real."""
import sys, io, fitz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

EA  = r"D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
PNG = EA + r"\DER_ShopMetrics_completo.png"
PDF = EA + r"\DER_ShopMetrics_completo_A3.pdf"

A3W, A3H = 1190.55, 841.89          # A3 apaisado, en puntos
MARG = 30

img = fitz.Pixmap(PNG)
natW, natH = img.width / 96 * 72, img.height / 96 * 72   # el PNG de EA sale a 96 dpi
doc = fitz.open()
pg = doc.new_page(width=A3W, height=A3H)
dw, dh = A3W - 2 * MARG, A3H - 2 * MARG - 30
esc = min(dw / natW, dh / natH)
w, h = natW * esc, natH * esc
x, y = (A3W - w) / 2, MARG + 26 + (dh - h) / 2
pg.insert_image(fitz.Rect(x, y, x + w, y + h), filename=PNG)
pg.insert_text((MARG, MARG + 14),
               "ShopMetrics - Diagrama Entidad-Relacion completo (30 entidades, 43 relaciones)",
               fontname="helv", fontsize=12)
pg.insert_text((MARG, A3H - MARG + 6),
               "Fuente: Enterprise Architect - paquete Modelo de Datos (DER)",
               fontname="helv", fontsize=8)
doc.save(PDF)
doc.close()
print(f"escala {esc:.2f} -> texto ~{7.5 * esc:.1f} pt, ocupa {w / 72 * 2.54:.1f} x {h / 72 * 2.54:.1f} cm")

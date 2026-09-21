# -*- coding: utf-8 -*-
"""Recorta el espacio blanco sobrante que deja el export de EA."""
import sys, io, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageChops

EA  = r"D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
rutas = [os.path.join(EA, "DER_ShopMetrics_integrado.png"),
         os.path.join(EA, "DER_ShopMetrics.png")] + sorted(glob.glob(os.path.join(EA, "export", "der", "*.png")))

for r in rutas:
    im = Image.open(r).convert("RGB")
    fondo = Image.new("RGB", im.size, (255, 255, 255))
    bbox = ImageChops.difference(im, fondo).getbbox()
    if not bbox: print("  (vacio)", r); continue
    m = 6
    caja = (max(0, bbox[0]-m), max(0, bbox[1]-m), min(im.width, bbox[2]+m), min(im.height, bbox[3]+m))
    rec = im.crop(caja)
    rec.save(r)
    wCm, hCm = rec.width/96*2.54, rec.height/96*2.54
    esc = min(16.26/wCm, 18.79/hCm)
    print(f"  {os.path.basename(r):<28} {im.width}x{im.height} -> {rec.width}x{rec.height}   escala A4 {esc:.2f}")

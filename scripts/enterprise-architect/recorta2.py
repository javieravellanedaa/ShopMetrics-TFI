# -*- coding: utf-8 -*-
"""Quita el marco del diagrama de EA y recorta al contenido real."""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageChops

EA = r"D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
for nombre in ["DER_ShopMetrics_integrado.png"]:
    r = os.path.join(EA, nombre)
    im = Image.open(r).convert("RGB")
    # sacar el marco exterior (borde + pestania del titulo)
    interior = im.crop((14, 26, im.width - 14, im.height - 14))
    fondo = Image.new("RGB", interior.size, (255, 255, 255))
    bbox = ImageChops.difference(interior, fondo).getbbox()
    m = 8
    caja = (max(0, bbox[0]-m), max(0, bbox[1]-m),
            min(interior.width, bbox[2]+m), min(interior.height, bbox[3]+m))
    rec = interior.crop(caja)
    rec.save(r)
    wCm, hCm = rec.width/96*2.54, rec.height/96*2.54
    esc = min(16.26/wCm, 18.79/hCm)
    print(f"  {nombre}: {im.width}x{im.height} -> {rec.width}x{rec.height}"
          f"  ({wCm:.1f}x{hCm:.1f} cm)  escala A4 = {esc:.2f}  ocupa {wCm*esc:.1f} x {hCm*esc:.1f} cm")

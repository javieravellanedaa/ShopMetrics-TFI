# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageChops
r = r"D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\DER_ShopMetrics_completo.png"
im = Image.open(r).convert("RGB")
interior = im.crop((14, 26, im.width-14, im.height-14))
bbox = ImageChops.difference(interior, Image.new("RGB", interior.size, (255,255,255))).getbbox()
m = 8
rec = interior.crop((max(0,bbox[0]-m), max(0,bbox[1]-m), min(interior.width,bbox[2]+m), min(interior.height,bbox[3]+m)))
rec.save(r)
w, h = rec.size; wCm, hCm = w/96*2.54, h/96*2.54
print(f"{im.width}x{im.height} -> {w}x{h}  ({wCm:.1f} x {hCm:.1f} cm)")
for pag, uw, uh in (("A4 apaisado",24.96,10.1), ("A3 apaisado",38.6,23.3)):
    e = min(uw/wCm, uh/hCm)
    print(f"  {pag:<12} escala {e:4.2f}  texto ~{7.5*e:.1f} pt  ocupa {wCm*e:.1f} x {hCm*e:.1f} cm")

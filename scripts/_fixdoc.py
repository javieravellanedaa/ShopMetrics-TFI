# -*- coding: utf-8 -*-
"""1) numeracion de paginas continua en todo el informe
   2) ninguna imagen mas alta que el area util real de la pagina"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from docx import Document
from docx.shared import Cm, Emu

D = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
doc = Document(D)
W  = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS = {'a':  'http://schemas.openxmlformats.org/drawingml/2006/main',
      'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}

# ---------- 1) numeracion continua ----------
sectprs = []
for p in doc.paragraphs:
    pPr = p._p.find(W + "pPr")
    if pPr is not None:
        s = pPr.find(W + "sectPr")
        if s is not None:
            sectprs.append(s)
final = doc.element.body.find(W + "sectPr")
if final is not None:
    sectprs.append(final)
print("secciones halladas:", len(sectprs))
for k, s in enumerate(sectprs):
    pn = s.find(W + "pgNumType")
    if k == 0:
        print(f"  seccion {k}: se conserva pgNumType (arranca en 1)")
        continue
    if pn is not None:
        s.remove(pn)
        print(f"  seccion {k}: pgNumType eliminado -> numeracion continua")

# ---------- 2) alto maximo de las imagenes ----------
# El encabezado del informe es alto y empuja el cuerpo: el area util real es
# ~12,2 cm en apaisado y ~20,5 cm en vertical. Se deja margen para la leyenda.
MAX_H_APAIS = Cm(9.3)
MAX_H_VERT  = Cm(16.8)

# que parrafos caen en la seccion apaisada nueva (entre los sectPr 1 y 2)
orient = []          # orientacion vigente para cada parrafo
cur = 0
for p in doc.paragraphs:
    orient.append(cur)
    pPr = p._p.find(W + "pPr")
    if pPr is not None and pPr.find(W + "sectPr") is not None:
        cur += 1
APAIS = {1, 3}       # secciones 1 y 3 son apaisadas

ajustadas = 0
for i, p in enumerate(doc.paragraphs):
    ext  = p._p.find('.//wp:extent', NS)
    aext = p._p.find('.//a:ext', NS)
    if ext is None:
        continue
    cx, cy = int(ext.get('cx')), int(ext.get('cy'))
    tope = MAX_H_APAIS if orient[i] in APAIS else MAX_H_VERT
    if cy > tope:
        f = tope / cy
        ncx, ncy = int(cx * f), int(tope)
        ext.set('cx', str(ncx)); ext.set('cy', str(ncy))
        if aext is not None:
            aext.set('cx', str(ncx)); aext.set('cy', str(ncy))
        print(f"  [{i}] {Emu(cx).cm:.1f}x{Emu(cy).cm:.1f} -> {Emu(ncx).cm:.1f}x{Emu(ncy).cm:.1f} cm")
        ajustadas += 1
print("imagenes ajustadas:", ajustadas)

doc.save(D)
print("guardado")

# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from docx import Document
from docx.shared import Emu
D = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
doc = Document(D)
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
for i, p in enumerate(doc.paragraphs):
    if not (505 <= i <= 592): continue
    st = (p.style.name or "")
    t = p.text.strip()
    ext = p._p.findall('.//wp:extent', NS)
    img = ""
    if ext:
        cx = int(ext[0].get('cx')); cy = int(ext[0].get('cy'))
        img = f"  <<IMG {Emu(cx).cm:.2f} x {Emu(cy).cm:.2f} cm>>"
    sect = "  [SECTPR]" if p._p.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sectPr') is not None else ""
    if t or img or sect:
        print(f"[{i:>4}] {st[:16]:<16} {t[:96]}{img}{sect}")

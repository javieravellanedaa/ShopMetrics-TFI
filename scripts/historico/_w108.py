# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.shared import Emu
D = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
doc = Document(D)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS = {'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
def blocks(parent):
    for ch in parent.element.body.iterchildren():
        if ch.tag == W+"p":  yield Paragraph(ch, parent)
        elif ch.tag == W+"tbl": yield Table(ch, parent)
seq = list(blocks(doc))
ini = [i for i,b in enumerate(seq) if isinstance(b,Paragraph) and b.text.strip().startswith("10.5.8")][-1]
print("10.5.8 bloque", ini, "/", len(seq))
for j in range(ini-2, min(ini+14, len(seq))):
    b = seq[j]
    if isinstance(b, Paragraph):
        ext = b._p.findall('.//wp:extent', NS)
        img = f"  <<IMG {Emu(int(ext[0].get('cx'))).cm:.2f}x{Emu(int(ext[0].get('cy'))).cm:.2f}cm>>" if ext else ""
        print(f"[{j}] P  {b.style.name[:8]:<8} {b.text.strip()[:110]}{img}")
    else:
        print(f"[{j}] TBL {len(b.rows)}x{len(b.columns)}  primera fila: {[c.text.strip()[:18] for c in b.rows[0].cells]}")

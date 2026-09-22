# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
D = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
doc = Document(D)
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
def blocks(parent):
    for ch in parent.element.body.iterchildren():
        if ch.tag == W+"p":  yield Paragraph(ch, parent)
        elif ch.tag == W+"tbl": yield Table(ch, parent)
seq = list(blocks(doc))
pos = [i for i,b in enumerate(seq) if isinstance(b,Paragraph) and b.text.strip().startswith("10.5.3 Casos de Uso")]
pos4 = [i for i,b in enumerate(seq) if isinstance(b,Paragraph) and b.text.strip().startswith("10.5.4 Diagramas")]
print("ocurrencias 10.5.3:", pos, " 10.5.4:", pos4)
ini, fin = pos[-1], pos4[-1]
print("rango", ini, fin, " tablas:", sum(1 for b in seq[ini:fin] if isinstance(b,Table)))
for b in seq[ini:fin]:
    if isinstance(b, Table):
        print("filas:", len(b.rows), "cols:", len(b.columns))
        for r in b.rows:
            print("   |", " || ".join(c.text.strip().replace("\n"," / ")[:85] for c in r.cells))
        break

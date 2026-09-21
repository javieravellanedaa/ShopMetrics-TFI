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
print("bloques:", len(seq))
# localizar la seccion 10.5.3
ini = fin = None
for i, b in enumerate(seq):
    if isinstance(b, Paragraph):
        if b.text.strip().startswith("10.5.3 Casos de Uso") and ini is None and i > 100: ini = i
        if b.text.strip().startswith("10.5.4 Diagramas") and ini is not None: fin = i; break
print("10.5.3 bloques", ini, "->", fin)
ntab = 0
for b in seq[ini:fin]:
    if isinstance(b, Table): ntab += 1
print("tablas de CU:", ntab)
# estructura de la primera tabla de CU
for b in seq[ini:fin]:
    if isinstance(b, Table):
        print("--- primera tabla, filas:", len(b.rows), "cols:", len(b.columns))
        for r in b.rows[:14]:
            print("   |", " || ".join(c.text.strip().replace("\n"," / ")[:70] for c in r.cells))
        break

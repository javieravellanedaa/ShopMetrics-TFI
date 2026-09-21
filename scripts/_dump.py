# -*- coding: utf-8 -*-
import sys, io, re
from docx import Document
D = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
ps = Document(D).paragraphs
out = []
for i in range(876, 1521):
    t = ps[i].text.strip()
    if t and not t.startswith("https://"): out.append(t)
open("casos_uso.txt","w",encoding="utf-8").write("\n".join(out))
print("lineas:", len(out), "chars:", sum(len(x) for x in out))

# -*- coding: utf-8 -*-
import sys, io, json
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
ini = [i for i,b in enumerate(seq) if isinstance(b,Paragraph) and b.text.strip().startswith("10.5.8")][-1]
ent, act = [], None
for b in seq[ini:]:
    if isinstance(b, Paragraph):
        t = b.text.strip()
        if ":" in t and not t.startswith("10.") and len(t.split(":")[0].split()) == 1 and t.split(":")[0].islower():
            act = {"tabla": t.split(":")[0], "desc": t.split(":",1)[1].strip(), "campos": []}
            ent.append(act)
    elif act is not None:
        for r in b.rows[1:]:
            c = [x.text.strip() for x in r.cells]
            act["campos"].append({"campo": c[0], "tipo": c[1], "clave": c[2], "desc": c[3]})
        act = None
json.dump(ent, open("dic.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("entidades:", len(ent))
for e in ent:
    fks = [c["campo"] for c in e["campos"] if "FK" in c["clave"]]
    pks = [c["campo"] for c in e["campos"] if "PK" in c["clave"]]
    print(f"  {e['tabla']:<24} campos={len(e['campos']):<3} PK={','.join(pks) or '-':<28} FK={','.join(fks) or '-'}")

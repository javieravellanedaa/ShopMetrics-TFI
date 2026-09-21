# -*- coding: utf-8 -*-
import openpyxl,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
p=r"D:\Javier\UAI\UAI - SAP\STF\STF\Ejemplos de catedra\Presupuesto financiero EJEMPLO V1.xlsx"
ws=openpyxl.load_workbook(p)["Anexo capacidad operativa"]
for r in range(1,125):
    fila=[]
    for c in range(1,30):
        cf=ws.cell(r,c)
        if cf.value is None: continue
        fila.append(f"{cf.coordinate}={repr(cf.value)[:58]}")
    if fila: print(f"[{r:>3}] "+" | ".join(fila))

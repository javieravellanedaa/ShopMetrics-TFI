# -*- coding: utf-8 -*-
import openpyxl,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
p=r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
f=openpyxl.load_workbook(p,data_only=False)["Anexo capacidad operativa"]
print("--- restos fuera del bloque A1:G40 ---")
cnt=0
for r in range(1,311):
    for c in range(1,30):
        cf=f.cell(r,c)
        if cf.value is None: continue
        if r<=40 and c<=7: continue
        cnt+=1
        if cnt<=40: print(f"  {cf.coordinate} = {repr(cf.value)[:90]}")
print("TOTAL celdas con contenido fuera del bloque:", cnt)

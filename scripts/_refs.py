# -*- coding: utf-8 -*-
import openpyxl,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
p=r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
wb=openpyxl.load_workbook(p,data_only=False)
for sn in wb.sheetnames:
    ws=wb[sn]
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value,str) and "apacidad operativa" in c.value and c.value.startswith("="):
                print(f"{sn}!{c.coordinate} = {c.value[:120]}")
print("--- filas 55-70 de Hipotesis (lista de precios/planes) ---")
h=wb["Hipótesis"]; hv=openpyxl.load_workbook(p,data_only=True)["Hipótesis"]
for r in range(54,66):
    fila=[]
    for c in range(1,8):
        cf=h.cell(r,c); cv=hv.cell(r,c)
        if cf.value is None and cv.value is None: continue
        s=f"{cf.coordinate}="+(f"{cv.value}" if isinstance(cf.value,str) and cf.value.startswith("=") else repr(cf.value)[:60])
        fila.append(s)
    if fila: print(f"[{r}]"," | ".join(fila))

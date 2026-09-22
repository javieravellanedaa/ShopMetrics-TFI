# -*- coding: utf-8 -*-
import openpyxl, sys, io
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter as gl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
wb = openpyxl.load_workbook(P); ws = wb["Anexo capacidad operativa"]

for k, v in {"A":26,"B":30,"C":15,"D":15,"E":16,"F":13,"G":13,
             "H":15,"I":30,"J":15,"K":15,"L":16}.items():
    ws.column_dimensions[k].width = v

# bloque horas laborables: C13/C14 con wrap y alto suficiente
for cc in ("C13","C14","A13"):
    ws[cc].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
ws.row_dimensions[12].height = 32   # "Horas laborables anuales por empleado"
ws.row_dimensions[13].height = 34
ws.row_dimensions[14].height = 40

# bloques de tareas: encabezado 50, filas 30, totales 40/44
for r0 in (18, 37, 56):
    ws.row_dimensions[r0].height     = 20
    ws.row_dimensions[r0+1].height   = 50
    for r in range(r0+2, r0+14):
        ws.row_dimensions[r].height  = 30
    ws.row_dimensions[r0+14].height  = 40
    ws.row_dimensions[r0+15].height  = 46

wb.save(P); print("OK")

# -*- coding: utf-8 -*-
import openpyxl, sys, io
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
wb = openpyxl.load_workbook(P); ws = wb["Anexo capacidad operativa"]
AMAR = PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="BFBFBF")
BOX  = Border(left=thin, right=thin, top=thin, bottom=thin)
LFT  = Alignment(horizontal="left", vertical="center", wrap_text=True)

ws.row_dimensions[13].height = 46
ws.row_dimensions[14].height = 52

USADAS = {18: 5, 37: 7, 56: 8}   # tareas efectivamente cargadas por bloque
for r0, n in USADAS.items():
    for i in range(12):
        ws.row_dimensions[r0+2+i].height = 30 if i < n else 16
    rt = r0 + 14
    # etiquetas de totales: fusionar C:D y J:K para que entre el texto
    for rr in (rt, rt+1):
        for a, b in (("C", "D"), ("J", "K")):
            ws.merge_cells(f"{a}{rr}:{b}{rr}")
            c = ws[f"{a}{rr}"]
            if c.value is None:                       # el texto estaba en D / K
                pass
            c.alignment = LFT
        # mover el texto de D->C y de K->J
    ws.row_dimensions[rt].height   = 40
    ws.row_dimensions[rt+1].height = 52
wb.save(P); print("merges listos")

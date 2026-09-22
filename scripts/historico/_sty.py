# -*- coding: utf-8 -*-
import openpyxl,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
p=r"D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
wb=openpyxl.load_workbook(p)
for sn,cells in [("Anexo capacidad operativa",["A3","A4","B4","A13","B14","C14","A32","D33","A34","B34"]),
                 ("Costos RRHH",["B13","B14","E15","B16","D16"])]:
    ws=wb[sn]; print("=== ",sn)
    for cc in cells:
        c=ws[cc]
        print(f"  {cc}: fill={c.fill.fgColor.rgb if c.fill and c.fill.fgColor else None} bold={c.font.b} sz={c.font.sz} color={c.font.color.rgb if c.font.color else None} fmt={c.number_format} border_b={c.border.bottom.style}")
    print("  widths:", {k:v.width for k,v in list(ws.column_dimensions.items())[:10]})

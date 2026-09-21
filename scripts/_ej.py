# -*- coding: utf-8 -*-
import openpyxl, glob
for p in [r"D:\Javier\UAI\UAI - SAP\STF\STF\Ejemplos de catedra\Ejemplo PresupuestoFinanciero.xlsx",
          r"D:\Javier\UAI\UAI - SAP\STF\STF\Ejemplos de catedra\Presupuesto financiero EJEMPLO V1.xlsx"]:
    print("="*70); print(p.split("\\")[-1])
    try:
        wb=openpyxl.load_workbook(p, data_only=True)
        print("hojas:", wb.sheetnames)
    except Exception as e:
        print("ERR", e)

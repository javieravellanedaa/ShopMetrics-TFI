$ErrorActionPreference="Stop"
$p = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($p)
$xl.CalculateFullRebuild()
$ws = $wb.Worksheets.Item("Anexo capacidad operativa")
"Hojas: " + $wb.Worksheets.Count
"Instalacion  Basico=" + $ws.Range("E32").Value2 + "h  Vidriera=" + $ws.Range("E51").Value2 + "h  Cadena=" + $ws.Range("E70").Value2 + "h"
"Soporte/mes  Basico=" + $ws.Range("L32").Value2 + "h  Vidriera=" + $ws.Range("L51").Value2 + "h  Cadena=" + $ws.Range("L70").Value2 + "h"
"Costo MO alta Basico=" + $ws.Range("B32").Value2 + " vs precio " + $ws.Range("B33").Value2
"Costo MO alta Vidriera=" + $ws.Range("B51").Value2 + " vs precio " + $ws.Range("B52").Value2
"Costo MO alta Cadena=" + $ws.Range("B70").Value2 + " vs precio " + $ws.Range("B71").Value2
foreach ($y in @(@(2026,86,87),@(2027,97,98),@(2028,108,109))) {
  "" + $y[0] + ": HH anual=" + [math]::Round($ws.Cells.Item($y[1],2).Value2,2) + "  tecnicos=" + $ws.Cells.Item($y[2],2).Value2
}
# integridad del resto del libro
$pv = $wb.Worksheets.Item("Proy. ventas")
"Proy.ventas D32=" + $pv.Range("D32").Value2
$me = $wb.Worksheets.Item("Mod. egresos")
"Mod.egresos B13=" + $me.Range("B13").Value2
$wb.Save(); $wb.Close($true); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

$ErrorActionPreference="Stop"
$p = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($p)
$xl.CalculateFullRebuild()
$wb.Save()
$ws = $wb.Worksheets.Item("Anexo capacidad operativa")
"E32=" + $ws.Range("E32").Value2 + "  E51=" + $ws.Range("E51").Value2 + "  E70=" + $ws.Range("E70").Value2
"L32=" + $ws.Range("L32").Value2 + "  L51=" + $ws.Range("L51").Value2 + "  L70=" + $ws.Range("L70").Value2
"2026 TOT hs=" + $ws.Range("B86").Value2 + "  tecnicos=" + $ws.Range("B87").Value2
"2027 TOT hs=" + $ws.Range("B97").Value2 + "  tecnicos=" + $ws.Range("B98").Value2
"2028 TOT hs=" + $ws.Range("B108").Value2 + "  tecnicos=" + $ws.Range("B109").Value2
"pico 2026=" + $ws.Range("C114").Value2 + " 2027=" + $ws.Range("C115").Value2 + " 2028=" + $ws.Range("C116").Value2
"MO 2026=" + $ws.Range("F114").Value2 + " 2027=" + $ws.Range("F115").Value2 + " 2028=" + $ws.Range("F116").Value2
"tecnicos x mes 2028: " + (4..26 | Where-Object {$_ % 2 -eq 1} | ForEach-Object { $ws.Cells.Item(109,$_).Value2 }) -join " "
$wb.Close($true); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

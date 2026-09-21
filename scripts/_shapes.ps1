$ErrorActionPreference="Stop"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$false; $xl.DisplayAlerts=$false
foreach ($f in @("D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx",
                 "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Backups\Presupuesto financiero ShopMetrics V1.BACKUP-preanexo.xlsx",
                 "D:\Javier\UAI\UAI - SAP\STF\STF\Ejemplos de catedra\Presupuesto financiero EJEMPLO V1.xlsx")) {
  $wb = $xl.Workbooks.Open($f, 0, $true)
  $ws = $wb.Worksheets.Item("Anexo capacidad operativa")
  $n = $ws.Shapes.Count
  $nom = @(); for ($i=1; $i -le $n; $i++) { $nom += $ws.Shapes.Item($i).Name }
  (Split-Path $f -Leaf) + "  ->  shapes=$n  " + ($nom -join ", ")
  $wb.Close($false)
}
$xl.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

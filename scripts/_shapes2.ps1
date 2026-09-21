$ErrorActionPreference="Stop"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$false; $xl.DisplayAlerts=$false
foreach ($f in @("D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx",
                 "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Backups\Presupuesto financiero ShopMetrics V1.BACKUP-preriesgos.xlsx")) {
  "=== " + (Split-Path $f -Leaf)
  $wb = $xl.Workbooks.Open($f, 0, $true)
  foreach ($ws in $wb.Worksheets) { if ($ws.Shapes.Count -gt 0) { "   " + $ws.Name + " -> " + $ws.Shapes.Count } }
  $wb.Close($false)
}
$xl.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

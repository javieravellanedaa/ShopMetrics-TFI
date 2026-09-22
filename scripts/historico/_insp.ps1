$ErrorActionPreference="Stop"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open("D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Backups\Presupuesto financiero ShopMetrics V1.BACKUP-preriesgos.xlsx", 0, $true)
foreach ($n in @("Anexo capacidad operativa","Mod. ingresos","Costos fijos","Amortizaciones")) {
  $ws = $wb.Worksheets.Item($n)
  "=== $n ($($ws.Shapes.Count) shapes)"
  for ($i=1; $i -le $ws.Shapes.Count; $i++) {
    $s = $ws.Shapes.Item($i)
    $txt = ""; try { $txt = $s.TextFrame.Characters().Text } catch {}
    $lnk = ""; try { $lnk = $s.Hyperlink.SubAddress } catch {}
    "   [$i] name=$($s.Name) type=$($s.Type) top=$([math]::Round($s.Top)) left=$([math]::Round($s.Left)) w=$([math]::Round($s.Width)) h=$([math]::Round($s.Height)) txt='$txt' link='$lnk'"
  }
}
$wb.Close($false); $xl.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

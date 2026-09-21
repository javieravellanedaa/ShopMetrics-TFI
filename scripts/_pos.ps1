$ErrorActionPreference="Stop"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$false; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open("D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx",0,$true)
$ws = $wb.Worksheets.Item("Anexo capacidad operativa")
for ($i=1; $i -le $ws.Shapes.Count; $i++) { $s=$ws.Shapes.Item($i)
  $t=""; try{$t=$s.TextFrame.Characters().Text}catch{}
  $l=""; try{$l=$s.Hyperlink.SubAddress}catch{}
  "[$i] '$t' top=$([math]::Round($s.Top)) left=$([math]::Round($s.Left)) visible=$($s.Visible) link='$l'" }
$wb.Close($false); $xl.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)|Out-Null

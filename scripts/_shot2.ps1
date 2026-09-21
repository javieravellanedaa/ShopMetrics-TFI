$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$p = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$out = "C:\Users\javie\AppData\Local\Temp\claude\D--Javier-UAI-UAI---SAP-STF\c435bfd7-fad9-400e-8645-4e6760655262\scratchpad"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$true; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($p)
$ws = $wb.Worksheets.Item("Anexo capacidad operativa"); $ws.Activate()
"F32=" + $ws.Range("F32").Value2 + " F51=" + $ws.Range("F51").Value2 + " F70=" + $ws.Range("F70").Value2
"kit W28=" + $ws.Range("W28").Value2 + " W47=" + $ws.Range("W47").Value2 + " W65=" + $ws.Range("W65").Value2
"sop AC28=" + $ws.Range("AC28").Value2 + " AC47=" + $ws.Range("AC47").Value2 + " AC65=" + $ws.Range("AC65").Value2
"2026 TOT B86=" + $ws.Range("B86").Value2 + "  2027 B97=" + $ws.Range("B97").Value2 + "  2028 B108=" + $ws.Range("B108").Value2
$rangos = @{ "v_bloque1" = "A1:L34"; "v_kit" = "O1:AC30"; "v_2026" = "A77:Z86"; "v_concl" = "A110:H116" }
foreach ($k in $rangos.Keys) {
  $r = $ws.Range($rangos[$k])
  for ($i=0; $i -lt 6; $i++) {
    try { $r.CopyPicture(1,2); Start-Sleep -Milliseconds 400
          $img = [System.Windows.Forms.Clipboard]::GetImage()
          if ($img) { $img.Save("$out\$k.png",[System.Drawing.Imaging.ImageFormat]::Png); $img.Dispose(); break } }
    catch { Start-Sleep -Milliseconds 500 }
  }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

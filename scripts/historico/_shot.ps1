$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$p = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$out = "C:\Users\javie\AppData\Local\Temp\claude\D--Javier-UAI-UAI---SAP-STF\c435bfd7-fad9-400e-8645-4e6760655262\scratchpad"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$true; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($p)
$ws = $wb.Worksheets.Item("Anexo capacidad operativa")
$ws.Activate()
$rangos = @{ "chk_tareas" = "A1:L34"; "chk_2026" = "A77:Z87"; "chk_2028" = "A100:Z109"; "chk_concl" = "A112:L122" }
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
Get-ChildItem "$out\chk_*.png" | ForEach-Object { "$($_.Name) $($_.Length)" }

$ErrorActionPreference="Stop"
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$p = "D:\Javier\UAI\UAI - SAP\STF\STF\Ejemplos de catedra\Ejemplo PresupuestoFinanciero.xlsx"
$out = "C:\Users\javie\AppData\Local\Temp\claude\D--Javier-UAI-UAI---SAP-STF\c435bfd7-fad9-400e-8645-4e6760655262\scratchpad"
$xl = New-Object -ComObject Excel.Application
$xl.Visible=$true; $xl.DisplayAlerts=$false
$wb = $xl.Workbooks.Open($p, 0, $true)
$ws = $wb.Worksheets.Item("Anexo capacidad operativa"); $ws.Activate()
$r = $ws.Range("A1:L34")
for ($i=0; $i -lt 6; $i++) {
  try { $r.CopyPicture(1,2); Start-Sleep -Milliseconds 400
        $img = [System.Windows.Forms.Clipboard]::GetImage()
        if ($img) { $img.Save("$out\ej_bloque1.png",[System.Drawing.Imaging.ImageFormat]::Png); $img.Dispose(); break } }
  catch { Start-Sleep -Milliseconds 500 }
}
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

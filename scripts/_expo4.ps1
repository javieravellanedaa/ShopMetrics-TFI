$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$orig = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$tmp  = "C:\Users\javie\AppData\Local\Temp\claude\D--Javier-UAI-UAI---SAP-STF\c435bfd7-fad9-400e-8645-4e6760655262\scratchpad\_tmp2.xlsx"
$out  = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\img_punto8"
Copy-Item $orig $tmp -Force

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $true; $xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Open($tmp)
$ws = $wb.Worksheets.Item("Anexo capacidad operativa")
$ws.Activate()

function Sacar($rango, $nombre) {
  $r = $ws.Range($rango)
  for ($i = 0; $i -lt 8; $i++) {
    try {
      $r.CopyPicture(1, 2); Start-Sleep -Milliseconds 450
      $img = [System.Windows.Forms.Clipboard]::GetImage()
      if ($img) {
        $img.Save("$out\$nombre.png", [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Output ("$nombre|" + $img.Width + "|" + $img.Height); $img.Dispose(); return
      }
    } catch { Start-Sleep -Milliseconds 600 }
  }
  Write-Output "$nombre|FALLO"
}

# ---- normalizar altos y ocultar renglones de tarea vacios ----
# bloque -> cantidad de tareas cargadas (instalacion, soporte)
$BLQ = @( @(18, 5, 3), @(37, 7, 4), @(56, 8, 4) )
foreach ($b in $BLQ) {
  $r0 = $b[0]
  $ws.Rows.Item($r0).RowHeight       = 22        # titulo
  $ws.Rows.Item($r0 + 1).RowHeight   = 46        # encabezado
  for ($i = 0; $i -lt 12; $i++) { $ws.Rows.Item($r0 + 2 + $i).RowHeight = 16 }
  $ws.Rows.Item($r0 + 14).RowHeight  = 48        # horas totales
  $ws.Rows.Item($r0 + 15).RowHeight  = 50        # capacidad operativa
}
# horas laborables: sacar las bandas vacias
for ($r = 6; $r -le 12; $r++) { $ws.Rows.Item($r).RowHeight = 17 }
$ws.Rows.Item(13).RowHeight = 30
$ws.Rows.Item(14).RowHeight = 34
Sacar "A6:C14" "AN01_horas_laborables"

# instalacion: ocultar tareas no usadas (columnas A:E)
foreach ($b in $BLQ) {
  $r0 = $b[0]; $ni = $b[1]; $nsop = $b[2]
  $desde = $r0 + 2 + $ni; $hasta = $r0 + 13
  if ($desde -le $hasta) { $ws.Range("${desde}:${hasta}").EntireRow.Hidden = $true }
  $nom = switch ($r0) { 18 {"AN02_inst_basico"} 37 {"AN03_inst_vidriera"} default {"AN04_inst_cadena"} }
  Sacar "A${r0}:E$($r0+15)" $nom
  $ws.Rows.Item("$($r0):$($r0+15)").Hidden = $false
}
# soporte: ocultar tareas no usadas (columnas H:L)
foreach ($b in $BLQ) {
  $r0 = $b[0]; $nsop = $b[2]
  $desde = $r0 + 2 + $nsop; $hasta = $r0 + 13
  if ($desde -le $hasta) { $ws.Range("${desde}:${hasta}").EntireRow.Hidden = $true }
  $nom = switch ($r0) { 18 {"AN05_sop_basico"} 37 {"AN06_sop_vidriera"} default {"AN07_sop_cadena"} }
  Sacar "H${r0}:L$($r0+15)" $nom
  $ws.Rows.Item("$($r0):$($r0+15)").Hidden = $false
}

$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
Remove-Item $tmp -Force

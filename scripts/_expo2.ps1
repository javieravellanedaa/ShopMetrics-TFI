$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$orig = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$tmp  = "C:\Users\javie\AppData\Local\Temp\claude\D--Javier-UAI-UAI---SAP-STF\c435bfd7-fad9-400e-8645-4e6760655262\scratchpad\_tmp.xlsx"
$out  = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\img_punto8"

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $true; $xl.DisplayAlerts = $false

# ---- 1) corregir el formato de moneda en las filas de instalacion (archivo del usuario) ----
$wu = $xl.Workbooks.Open($orig)
$wsu = $wu.Worksheets.Item("Anexo capacidad operativa")
$fmt = $wsu.Range("V21").NumberFormat
foreach ($r in @(20, 43, 62)) {
  $wsu.Range("V$r").NumberFormat = $fmt
  $wsu.Range("W$r").NumberFormat = $fmt
}
Write-Output ("formato aplicado: " + $fmt)
$wu.Save(); $wu.Close($true)

# ---- 2) exportar las tablas anuales desde una copia ----
Copy-Item $orig $tmp -Force
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
        $w = $img.Width; $h = $img.Height; $img.Dispose()
        Write-Output ("$nombre -> ${w}x${h} px")
        return
      }
    } catch { Start-Sleep -Milliseconds 600 }
  }
  Write-Output "$nombre : FALLO"
}

# volver a sacar los kits con el formato ya corregido
Sacar "S17:W29" "AN08_kit_basico"
Sacar "S36:W48" "AN09_kit_vidriera"
Sacar "S55:W66" "AN10_kit_cadena"

# angostar solo para las tablas anuales
$ws.Columns.Item(1).ColumnWidth = 44
$ws.Columns.Item(2).ColumnWidth = 16
for ($c = 3; $c -le 26; $c++) { $ws.Columns.Item($c).ColumnWidth = 8 }
foreach ($r in @(78, 79, 89, 90, 100, 101)) { $ws.Rows.Item($r).RowHeight = 46 }

$mapa = @{ "2026" = @(78, 86, "11", "12"); "2027" = @(89, 97, "13", "14"); "2028" = @(100, 108, "15", "16") }
foreach ($an in @("2026", "2027", "2028")) {
  $r0 = $mapa[$an][0]; $r1 = $mapa[$an][1]
  $ws.Range("O:Z").EntireColumn.Hidden = $true
  Sacar "A${r0}:Z${r1}" ("AN" + $mapa[$an][2] + "_hh_${an}_s1")
  $ws.Range("O:Z").EntireColumn.Hidden = $false
  $ws.Range("C:N").EntireColumn.Hidden = $true
  Sacar "A${r0}:Z${r1}" ("AN" + $mapa[$an][3] + "_hh_${an}_s2")
  $ws.Range("C:N").EntireColumn.Hidden = $false
}

$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
Remove-Item $tmp -Force
Write-Output "--- listo ---"

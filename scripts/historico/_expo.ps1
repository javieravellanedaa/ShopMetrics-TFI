$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$orig = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$tmp  = "C:\Users\javie\AppData\Local\Temp\claude\D--Javier-UAI-UAI---SAP-STF\c435bfd7-fad9-400e-8645-4e6760655262\scratchpad\_tmp.xlsx"
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
        $w = $img.Width; $h = $img.Height; $img.Dispose()
        Write-Output ("$nombre : $rango -> ${w}x${h} px  (" + [math]::Round($w/96*2.54,1) + " x " + [math]::Round($h/96*2.54,1) + " cm)")
        return
      }
    } catch { Start-Sleep -Milliseconds 600 }
  }
  Write-Output "$nombre : FALLO"
}

# --- anchos originales del usuario ---
Sacar "A6:C14"    "AN01_horas_laborables"
Sacar "A18:E33"   "AN02_inst_basico"
Sacar "A37:E52"   "AN03_inst_vidriera"
Sacar "A56:E71"   "AN04_inst_cadena"
Sacar "H18:L33"   "AN05_sop_basico"
Sacar "H37:L52"   "AN06_sop_vidriera"
Sacar "H56:L71"   "AN07_sop_cadena"
Sacar "S17:W29"   "AN08_kit_basico"
Sacar "S36:W48"   "AN09_kit_vidriera"
Sacar "S55:W66"   "AN10_kit_cadena"
Sacar "A110:H116" "AN17_conclusion"

# --- copia: angostar columnas solo para las tablas anuales ---
$ws.Columns.Item(1).ColumnWidth = 30
$ws.Columns.Item(2).ColumnWidth = 14
for ($c = 3; $c -le 26; $c++) { $ws.Columns.Item($c).ColumnWidth = 8 }

foreach ($y in @(@("2026", 78, 86), @("2027", 89, 97), @("2028", 100, 108))) {
  $an = $y[0]; $r0 = [int]$y[1]; $r1 = [int]$y[2]
  # primer semestre: ocultar O:Z
  $ws.Range("O:Z").EntireColumn.Hidden = $true
  Sacar "A${r0}:Z${r1}" ("AN1" + $(if ($an -eq "2026") {"1"} elseif ($an -eq "2027") {"3"} else {"5"}) + "_hh_${an}_s1")
  $ws.Range("O:Z").EntireColumn.Hidden = $false
  # segundo semestre: ocultar C:N
  $ws.Range("C:N").EntireColumn.Hidden = $true
  Sacar "A${r0}:Z${r1}" ("AN1" + $(if ($an -eq "2026") {"2"} elseif ($an -eq "2027") {"4"} else {"6"}) + "_hh_${an}_s2")
  $ws.Range("C:N").EntireColumn.Hidden = $false
}

$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
Remove-Item $tmp -Force
Write-Output "--- listo ---"

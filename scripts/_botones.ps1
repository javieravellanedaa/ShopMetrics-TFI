$ErrorActionPreference = "Stop"
$dst = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$bk  = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Backups\Presupuesto financiero ShopMetrics V1.BACKUP-preriesgos.xlsx"

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $true; $xl.DisplayAlerts = $false
$wd = $xl.Workbooks.Open($dst)
$wo = $xl.Workbooks.Open($bk, 0, $true)

function TextoDe($s) { try { return $s.TextFrame.Characters().Text } catch { return "" } }

$rep = 0
foreach ($wso in $wo.Worksheets) {
  $nom = $wso.Name
  $wsd = $null
  try { $wsd = $wd.Worksheets.Item($nom) } catch { continue }

  # textos de los botones que ya existen en el destino
  $ya = @()
  for ($i = 1; $i -le $wsd.Shapes.Count; $i++) { $ya += (TextoDe $wsd.Shapes.Item($i)) }

  for ($i = 1; $i -le $wso.Shapes.Count; $i++) {
    $s = $wso.Shapes.Item($i)
    if ($s.Type -ne 1) { continue }                       # solo autoformas (los botones)
    $t = TextoDe $s
    if ($t -eq "") { continue }
    if ($ya -contains $t) { continue }                    # ya esta
    $s.Copy()
    Start-Sleep -Milliseconds 250
    $wsd.Activate()
    $wsd.Paste() | Out-Null
    $nuevo = $wsd.Shapes.Item($wsd.Shapes.Count)
    $nuevo.Top = $s.Top; $nuevo.Left = $s.Left
    $nuevo.Width = $s.Width; $nuevo.Height = $s.Height
    "restaurado en '$nom': $t"
    $rep++
  }
}
"total restaurados: $rep"

$wo.Close($false)
$wd.Save()

# verificacion
foreach ($ws in $wd.Worksheets) { if ($ws.Shapes.Count -gt 0) { "   " + $ws.Name + " -> " + $ws.Shapes.Count } }
$wd.Close($true); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

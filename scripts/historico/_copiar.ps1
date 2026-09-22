$ErrorActionPreference = "Stop"
$dst = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\Presupuesto financiero ShopMetrics V1.xlsx"
$src = "D:\Javier\UAI\UAI - SAP\STF\STF\Ejemplos de catedra\Presupuesto financiero EJEMPLO V1.xlsx"
$NOM = "Anexo capacidad operativa"

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
$wd = $xl.Workbooks.Open($dst)
$wo = $xl.Workbooks.Open($src, 0, $true)   # solo lectura

$idx = $wd.Worksheets.Item($NOM).Index
"indice original: $idx"

# copiar la hoja del template DESPUES de la actual
$wo.Worksheets.Item($NOM).Copy([System.Reflection.Missing]::Value, $wd.Worksheets.Item($idx))
$nueva = $wd.Worksheets.Item($idx + 1)
"copia creada como: " + $nueva.Name

# borrar la vieja y renombrar la copia
$wd.Worksheets.Item($idx).Delete()
$nueva.Name = $NOM
"indice final: " + $wd.Worksheets.Item($NOM).Index

# quitar las referencias externas al libro de origen
$nueva.Cells.Replace("[Presupuesto financiero EJEMPLO V1.xlsx]", "", 2, 1, $false) | Out-Null

$wo.Close($false)
$xl.CalculateFullRebuild()
$wd.Save()

# verificacion
"hojas: " + $wd.Worksheets.Count
"A3  = " + $nueva.Range("A3").Formula
"A80 = " + $nueva.Range("A80").Formula
"C80 = " + $nueva.Range("C80").Formula
"B14 = " + $nueva.Range("B14").Value2
$ext = $wd.LinkSources(1)
if ($ext) { "VINCULOS EXTERNOS: " + ($ext -join ", ") } else { "sin vinculos externos" }
$wd.Close($true); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null

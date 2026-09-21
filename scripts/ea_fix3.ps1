$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$dia = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($dia.PackageID)
$ent = @{}; foreach ($e in $pkg.Elements) { $ent[$e.Name] = $e }

# ---------------------------------------------------- 6) ORDEN DE ATRIBUTOS: PK, FK, resto
foreach ($e in $pkg.Elements) {
  $lista = @()
  foreach ($a in $e.Attributes) { $lista += $a }
  $pk  = @($lista | Where-Object { $_.Stereotype -like "*PK*" })
  $fk  = @($lista | Where-Object { $_.Stereotype -like "*FK*" -and $_.Stereotype -notlike "*PK*" })
  $res = @($lista | Where-Object { $_.Stereotype -notlike "*PK*" -and $_.Stereotype -notlike "*FK*" })
  $i = 0
  foreach ($a in ($pk + $fk + $res)) { $a.Pos = $i; $a.Update(); $i++ }
  $e.Attributes.Refresh()
}
Write-Output "6) atributos reordenados (PK, luego FK, luego el resto)"

# ---------------------------------------------------- 7) UBICAR LAS ENTIDADES NUEVAS EN EL DIAGRAMA
$yaEnDia = @{}
foreach ($o in $dia.DiagramObjects) { $yaEnDia[$o.ElementID] = $o }
$nuevas = @("regla_destinatario","resolucion_alerta","recomendacion","recomendacion_decision","parametro_sistema")
$x = 1200
foreach ($n in $nuevas) {
  $e = $ent[$n]
  if ($yaEnDia.ContainsKey($e.ElementID)) { Write-Output ("7) ya estaba en el diagrama: " + $n); continue }
  $t = -1100; $b = $t - 130
  $o = $dia.DiagramObjects.AddNew(("l=" + $x + ";r=" + ($x + 200) + ";t=" + $t + ";b=" + $b + ";"), "")
  $o.ElementID = $e.ElementID
  $o.Update()
  $x += 230
  Write-Output ("7) + al diagrama: " + $n)
}
$dia.DiagramObjects.Refresh()
$dia.Update()
$rep.SaveDiagram(2) | Out-Null

# ---------------------------------------------------- 8) AUTO-LAYOUT DE EA
$prj = $rep.GetProjectInterface()
# lsCycleRemoveGreedy(4) + lsLayeringLongestPathSink(16) + lsInitializeDFSOut(256) + lsCrossingReduceGreedy(1024)
$estilo = 4 + 16 + 256 + 1024
$prj.LayoutDiagramEx($dia.DiagramGUID, $estilo, 6, 90, 90, $true) | Out-Null
Write-Output ("8) auto-layout aplicado (estilo " + $estilo + ", espaciado 90)")
$rep.ReloadDiagram(2)

# ---------------------------------------------------- 9) VERIFICAR NOTACION
$d2 = $rep.GetDiagramByID(2)
if ($d2.StyleEx -match "TConnectorNotation=([^;]*)") { Write-Output ("9) notacion de conectores: " + $Matches[1]) }

# ---------------------------------------------------- 10) EXPORTAR PNG
$png = Join-Path $OUT "DER_ShopMetrics.png"
$r = $prj.PutDiagramImageToFile($d2.DiagramGUID, $png, 1)
Write-Output ("10) export -> " + $png + "  ok=" + $r)

$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
if (Test-Path $png) { $im = [System.Drawing.Image]::FromFile($png); Write-Output ("    PNG " + $im.Width + "x" + $im.Height); $im.Dispose() }
Write-Output "`nFASE 3 OK"

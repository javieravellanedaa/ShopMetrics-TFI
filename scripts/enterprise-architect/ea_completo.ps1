$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
$NOMBRE = "DER - ShopMetrics (completo)"

# columnas por area tematica: dentro de cada area las relaciones son densas,
# entre areas son pocas -> menos cruces y ademas se lee por bloques
$COLS = @(
  @("permiso","rol_permiso","rol","usuario_rol"),
  @("usuario","centro_acceso","notificacion","preferencia_notificacion","reporte","evento_auditoria"),
  @("indicador","regla_alerta","regla_destinatario","alerta","resolucion_alerta"),
  @("centro_comercial","parametro_sistema","zona","locatario","consentimiento"),
  @("modelo_ml","prediccion_vacancia","accion_retencion","recomendacion","recomendacion_decision"),
  @("local","conector_pos","registro_pos","dispositivo_iot","evento_trafico")
)

$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$base = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($base.PackageID)
$ent = @{}; $nCampos = @{}; $tieneFK = @{}
foreach ($e in $pkg.Elements) {
  $ent[$e.Name] = $e
  $nCampos[$e.Name] = $e.Attributes.Count
  $fk = $false
  foreach ($a in $e.Attributes) { if ($a.Stereotype -like "*FK*") { $fk = $true } }
  $tieneFK[$e.Name] = $fk
}

for ($i = $pkg.Diagrams.Count - 1; $i -ge 0; $i--) {
  if ($pkg.Diagrams.GetAt($i).Name -eq $NOMBRE) { $pkg.Diagrams.Delete($i) }
}
$pkg.Diagrams.Refresh()
$d = $pkg.Diagrams.AddNew($NOMBRE, "Logical"); $d.Update()
$d.StyleEx = $base.StyleEx; $d.Update()

$W = 215; $GAPH = 75; $GAPV = 30; $X0 = 30; $Y0 = -30
$n = 0
for ($c = 0; $c -lt $COLS.Count; $c++) {
  $x = $X0 + $c * ($W + $GAPH)
  $y = $Y0
  foreach ($nom in $COLS[$c]) {
    if (-not $ent.ContainsKey($nom)) { Write-Output ("  FALTA " + $nom); continue }
    $comp = 1; if ($tieneFK[$nom]) { $comp = 2 }
    $h = 38 + 13 * ($nCampos[$nom] + $comp)
    $o = $d.DiagramObjects.AddNew(("l=" + $x + ";r=" + ($x + $W) + ";t=" + $y + ";b=" + ($y - $h) + ";"), "")
    $o.ElementID = $ent[$nom].ElementID
    $o.Update()
    $y = $y - $h - $GAPV
    $n++
  }
}
Write-Output ("entidades colocadas: " + $n)
$d.DiagramObjects.Refresh(); $d.Update()
$rep.SaveDiagram($d.DiagramID) | Out-Null
$rep.ReloadDiagram($d.DiagramID)

$prj = $rep.GetProjectInterface()
$png = Join-Path $OUT "DER_ShopMetrics_completo.png"
$prj.PutDiagramImageToFile($d.DiagramGUID, $png, 1) | Out-Null
$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Add-Type -AssemblyName System.Drawing
$im = [System.Drawing.Image]::FromFile($png)
Write-Output ("PNG {0}x{1}px = {2:N1} x {3:N1} cm" -f $im.Width, $im.Height, ($im.Width/96*2.54), ($im.Height/96*2.54))
$im.Dispose()

$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
$NOMBRE = "DER - ShopMetrics (integrado)"

$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$base = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($base.PackageID)
$ent = @{}; foreach ($e in $pkg.Elements) { $ent[$e.Name] = $e }

# 3 columnas: los dos hubs (usuario y centro_comercial) en la columna del medio,
# con sus satelites compartidos entre ambos. El hueco de R4C1 deja un canal
# limpio para la linea centro_comercial -> evento_auditoria.
$grilla = @(
  @("permiso",                "rol",              "usuario_rol"),
  @("rol_permiso",            "notificacion",     "preferencia_notificacion"),
  @("regla_destinatario",     "usuario",          "resolucion_alerta"),
  @("reporte",                "evento_auditoria", "centro_acceso"),
  @("parametro_sistema",      "",                 "alerta"),
  @("recomendacion",          "centro_comercial", "regla_alerta"),
  @("recomendacion_decision", "locatario",        "zona"),
  @("prediccion_vacancia",    "consentimiento",   "indicador"),
  @("accion_retencion",       "conector_pos",     "local"),
  @("modelo_ml",              "registro_pos",     "dispositivo_iot"),
  @("",                       "",                 "evento_trafico")
)

for ($i = $pkg.Diagrams.Count - 1; $i -ge 0; $i--) {
  if ($pkg.Diagrams.GetAt($i).Name -eq $NOMBRE) { $pkg.Diagrams.Delete($i) }
}
$pkg.Diagrams.Refresh()
$d = $pkg.Diagrams.AddNew($NOMBRE, "Logical"); $d.Update()
$d.StyleEx = $base.StyleEx; $d.Update()

$COLW = 250; $ROWH = 92; $W = 225; $H = 44; $X0 = 30; $Y0 = -30
$n = 0
for ($r = 0; $r -lt $grilla.Count; $r++) {
  for ($c = 0; $c -lt 3; $c++) {
    $nom = $grilla[$r][$c]
    if ([string]::IsNullOrEmpty($nom)) { continue }
    if (-not $ent.ContainsKey($nom)) { Write-Output ("  FALTA " + $nom); continue }
    $l = $X0 + $c * $COLW; $t = $Y0 - $r * $ROWH
    $o = $d.DiagramObjects.AddNew(("l=" + $l + ";r=" + ($l + $W) + ";t=" + $t + ";b=" + ($t - $H) + ";"), "")
    $o.ElementID = $ent[$nom].ElementID
    $o.Style = "AttPub=0;AttPri=0;AttPro=0;AttPkg=0;OpPub=0;OpPri=0;OpPro=0;OpPkg=0;"
    $o.Update(); $n++
  }
}
Write-Output ("entidades colocadas: " + $n)
$d.DiagramObjects.Refresh(); $d.Update()
$rep.SaveDiagram($d.DiagramID) | Out-Null
$rep.ReloadDiagram($d.DiagramID)

$prj = $rep.GetProjectInterface()
$png = Join-Path $OUT "DER_ShopMetrics_integrado.png"
$prj.PutDiagramImageToFile($d.DiagramGUID, $png, 1) | Out-Null
$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null

Add-Type -AssemblyName System.Drawing
$im = [System.Drawing.Image]::FromFile($png)
$wCm = $im.Width / 96 * 2.54; $hCm = $im.Height / 96 * 2.54
$esc = [math]::Min(16.26 / $wCm, 18.79 / $hCm)
Write-Output ("PNG {0}x{1}px = {2:N1} x {3:N1} cm  ->  en A4 vertical escala {4:N2}  ({5:N1} x {6:N1} cm)" -f `
  $im.Width, $im.Height, $wCm, $hCm, $esc, ($wCm*$esc), ($hCm*$esc))
$im.Dispose()

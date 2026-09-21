$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
$NOMBRE = "DER - ShopMetrics (integrado)"

$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$base = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($base.PackageID)
$ent = @{}; foreach ($e in $pkg.Elements) { $ent[$e.Name] = $e }

# grilla 4 columnas x 8 filas: relacionadas juntas, flujo de arriba hacia abajo
$grilla = @(
  @("permiso",                  "rol",              "indicador",          "modelo_ml"),
  @("rol_permiso",              "usuario_rol",      "regla_alerta",       "prediccion_vacancia"),
  @("preferencia_notificacion", "usuario",          "regla_destinatario", "accion_retencion"),
  @("notificacion",             "centro_acceso",    "alerta",             "recomendacion"),
  @("reporte",                  "evento_auditoria", "resolucion_alerta",  "recomendacion_decision"),
  @("parametro_sistema",        "centro_comercial", "zona",               "locatario"),
  @("",                         "consentimiento",   "dispositivo_iot",    "local"),
  @("",                         "conector_pos",     "evento_trafico",     "registro_pos")
)

# borrar version previa
for ($i = $pkg.Diagrams.Count - 1; $i -ge 0; $i--) {
  if ($pkg.Diagrams.GetAt($i).Name -eq $NOMBRE) { $pkg.Diagrams.Delete($i) }
}
$pkg.Diagrams.Refresh()

$d = $pkg.Diagrams.AddNew($NOMBRE, "Logical"); $d.Update()
# mismo estilo que el maestro (incluye la notacion pata de gallo)
$d.StyleEx = $base.StyleEx; $d.Update()

$COLW = 185; $ROWH = 108; $W = 170; $H = 48; $X0 = 40; $Y0 = -40
$n = 0
for ($r = 0; $r -lt $grilla.Count; $r++) {
  for ($c = 0; $c -lt 4; $c++) {
    $nom = $grilla[$r][$c]
    if ([string]::IsNullOrEmpty($nom)) { continue }
    if (-not $ent.ContainsKey($nom)) { Write-Output ("  FALTA " + $nom); continue }
    $l = $X0 + $c * $COLW; $t = $Y0 - $r * $ROWH
    $o = $d.DiagramObjects.AddNew(("l=" + $l + ";r=" + ($l + $W) + ";t=" + $t + ";b=" + ($t - $H) + ";"), "")
    $o.ElementID = $ent[$nom].ElementID
    # ocultar los compartimentos de atributos: solo nombre de entidad
    $o.Style = "AttPub=0;AttPri=0;AttPro=0;AttPkg=0;OpPub=0;OpPri=0;OpPro=0;OpPkg=0;"
    $o.Update()
    $n++
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
Write-Output ("PNG {0}x{1}px = {2:N1} x {3:N1} cm   escala en A4 vertical = {4:N2}" -f $im.Width, $im.Height, $wCm, $hCm, $esc)
$im.Dispose()

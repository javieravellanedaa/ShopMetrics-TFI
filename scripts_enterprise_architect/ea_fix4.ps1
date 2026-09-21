$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$dia = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($dia.PackageID)

# cuantos atributos tiene cada entidad (para calcular el alto de la caja)
$natt = @{}
foreach ($e in $pkg.Elements) { $natt[$e.Name] = $e.Attributes.Count }

# grilla por area tematica: fila -> columnas
$grilla = @(
  @("permiso",             "rol",               "usuario",            "preferencia_notificacion", "notificacion",    "reporte"),
  @("rol_permiso",         "usuario_rol",       "centro_acceso",      "parametro_sistema",        "evento_auditoria","consentimiento"),
  @("indicador",           "regla_alerta",      "regla_destinatario", "centro_comercial",         "locatario",       "local"),
  @("modelo_ml",           "alerta",            "resolucion_alerta",  "zona",                     "conector_pos",    "registro_pos"),
  @("prediccion_vacancia", "accion_retencion",  "recomendacion",      "recomendacion_decision",   "dispositivo_iot", "evento_trafico")
)

$COLW = 300; $ROWH = 250; $W = 230; $X0 = 60; $Y0 = -60

# indice de objetos del diagrama por nombre de elemento
$objs = @{}
foreach ($o in $dia.DiagramObjects) {
  $el = $rep.GetElementByID($o.ElementID)
  $objs[$el.Name] = $o
}
Write-Output ("objetos en el diagrama: " + $objs.Count)

$puestos = 0
for ($r = 0; $r -lt $grilla.Count; $r++) {
  for ($c = 0; $c -lt $grilla[$r].Count; $c++) {
    $n = $grilla[$r][$c]
    if (-not $objs.ContainsKey($n)) { Write-Output ("  FALTA en el diagrama: " + $n); continue }
    $o = $objs[$n]
    $h = 42 + 13 * [int]$natt[$n]
    if ($h -lt 70) { $h = 70 }
    $l = $X0 + $c * $COLW
    $t = $Y0 - $r * $ROWH
    $o.left = $l; $o.right = $l + $W
    $o.top = $t;  $o.bottom = $t - $h
    $o.Update()
    $puestos++
  }
}
Write-Output ("entidades reubicadas: " + $puestos)
$dia.DiagramObjects.Refresh()
$dia.Update()
$rep.SaveDiagram(2) | Out-Null
$rep.ReloadDiagram(2)

$prj = $rep.GetProjectInterface()
$png = Join-Path $OUT "DER_ShopMetrics.png"
$prj.PutDiagramImageToFile($dia.DiagramGUID, $png, 1) | Out-Null
$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Add-Type -AssemblyName System.Drawing
$im = [System.Drawing.Image]::FromFile($png); Write-Output ("PNG " + $im.Width + "x" + $im.Height); $im.Dispose()

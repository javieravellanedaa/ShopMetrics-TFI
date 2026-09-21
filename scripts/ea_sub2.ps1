$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\export\der"
if (-not (Test-Path $OUT)) { New-Item -ItemType Directory -Force -Path $OUT | Out-Null }
Get-ChildItem "$OUT\*.png" -ErrorAction SilentlyContinue | Remove-Item -Force

$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$maestro = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($maestro.PackageID)
$estilo = $maestro.StyleEx
$ent = @{}; $natt = @{}
foreach ($e in $pkg.Elements) { $ent[$e.Name] = $e; $natt[$e.Name] = $e.Attributes.Count }

# 2 columnas para que el texto entre legible en la hoja vertical
$sub = @(
  @{ f="DER_1_estructura";     t="DER 1 - Estructura del centro";
     g=@( @("centro_comercial","zona"), @("locatario","local"), @("consentimiento") ) },
  @{ f="DER_2_seguridad";      t="DER 2 - Seguridad y acceso";
     g=@( @("usuario","rol"), @("usuario_rol","permiso"), @("centro_acceso","rol_permiso") ) },
  @{ f="DER_3_integraciones";  t="DER 3 - Integraciones e ingesta de datos";
     g=@( @("locatario","zona"), @("conector_pos","dispositivo_iot"), @("registro_pos","evento_trafico") ) },
  @{ f="DER_4_reglas";         t="DER 4 - Reglas y generacion de alertas";
     g=@( @("indicador","usuario"), @("regla_alerta","regla_destinatario"), @("modelo_ml","alerta") ) },
  @{ f="DER_5_resolucion";     t="DER 5 - Resolucion de alertas";
     g=@( @("zona","locatario"), @("alerta","usuario"), @("resolucion_alerta") ) },
  @{ f="DER_6_ml";             t="DER 6 - Prediccion y recomendaciones";
     g=@( @("modelo_ml","locatario"), @("prediccion_vacancia","recomendacion"), @("accion_retencion","recomendacion_decision") ) },
  @{ f="DER_7_auditoria";      t="DER 7 - Auditoria y reportes";
     g=@( @("usuario","centro_comercial"), @("evento_auditoria","reporte") ) },
  @{ f="DER_8_notificaciones"; t="DER 8 - Notificaciones y parametros";
     g=@( @("usuario","centro_comercial"), @("notificacion","parametro_sistema"), @("preferencia_notificacion") ) }
)

$prj = $rep.GetProjectInterface()
$COLW = 340; $ROWH = 290; $W = 250; $X0 = 40; $Y0 = -40

# borrar sub-diagramas previos (por nombre viejo y nuevo)
$viejos = @("DER 1 - Estructura del centro","DER 2 - Seguridad y acceso","DER 3 - Integraciones e ingesta de datos",
            "DER 4 - Alertas y su resolucion","DER 5 - Modelos de ML, predicciones y recomendaciones",
            "DER 6 - Auditoria, reportes y notificaciones")
foreach ($s in $sub) { $viejos += $s.t }
for ($i = $pkg.Diagrams.Count - 1; $i -ge 0; $i--) {
  if ($viejos -contains $pkg.Diagrams.GetAt($i).Name) { $pkg.Diagrams.Delete($i) }
}
$pkg.Diagrams.Refresh()

foreach ($s in $sub) {
  $d = $pkg.Diagrams.AddNew($s.t, "Logical"); $d.Update()
  $d.StyleEx = $estilo; $d.Update()
  $n = 0
  for ($r = 0; $r -lt $s.g.Count; $r++) {
    for ($c = 0; $c -lt $s.g[$r].Count; $c++) {
      $nom = $s.g[$r][$c]
      $h = 42 + 13 * [int]$natt[$nom]; if ($h -lt 70) { $h = 70 }
      $l = $X0 + $c * $COLW; $t = $Y0 - $r * $ROWH
      $o = $d.DiagramObjects.AddNew(("l=" + $l + ";r=" + ($l + $W) + ";t=" + $t + ";b=" + ($t - $h) + ";"), "")
      $o.ElementID = $ent[$nom].ElementID; $o.Update(); $n++
    }
  }
  $d.DiagramObjects.Refresh(); $d.Update()
  $rep.SaveDiagram($d.DiagramID) | Out-Null
  $rep.ReloadDiagram($d.DiagramID)
  $prj.PutDiagramImageToFile($d.DiagramGUID, (Join-Path $OUT ($s.f + ".png")), 1) | Out-Null
  Write-Output ("+ " + $s.t + " (" + $n + ")")
}

$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Add-Type -AssemblyName System.Drawing
Get-ChildItem "$OUT\*.png" | Sort-Object Name | ForEach-Object {
  $im = [System.Drawing.Image]::FromFile($_.FullName)
  $anchoCm = $im.Width / 96 * 2.54
  $escala = [math]::Round(16.26 / $anchoCm, 2)
  Write-Output ("   {0,-24} {1}x{2}px  nominal {3:N1}cm  escala a 16,26cm = {4}" -f $_.Name, $im.Width, $im.Height, $anchoCm, $escala)
  $im.Dispose()
}

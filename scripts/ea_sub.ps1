$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\export\der"
if (-not (Test-Path $OUT)) { New-Item -ItemType Directory -Force -Path $OUT | Out-Null }

$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$maestro = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($maestro.PackageID)
$estilo = $maestro.StyleEx
$ent = @{}; $natt = @{}
foreach ($e in $pkg.Elements) { $ent[$e.Name] = $e; $natt[$e.Name] = $e.Attributes.Count }

# nombre corto de archivo -> @(titulo, @(filas de entidades))
$sub = @(
  @{ f = "DER_1_estructura"; t = "DER 1 - Estructura del centro";
     g = @( @("centro_comercial","zona","local"), @("locatario","consentimiento") ) },
  @{ f = "DER_2_seguridad"; t = "DER 2 - Seguridad y acceso";
     g = @( @("usuario","rol","permiso"), @("usuario_rol","rol_permiso","centro_acceso"), @("centro_comercial") ) },
  @{ f = "DER_3_integraciones"; t = "DER 3 - Integraciones e ingesta de datos";
     g = @( @("locatario","conector_pos","registro_pos"), @("zona","dispositivo_iot","evento_trafico") ) },
  @{ f = "DER_4_alertas"; t = "DER 4 - Alertas y su resolucion";
     g = @( @("indicador","regla_alerta","regla_destinatario"), @("modelo_ml","alerta","resolucion_alerta"), @("zona","locatario","usuario") ) },
  @{ f = "DER_5_ml"; t = "DER 5 - Modelos de ML, predicciones y recomendaciones";
     g = @( @("modelo_ml","prediccion_vacancia","accion_retencion"), @("recomendacion","recomendacion_decision"), @("centro_comercial","locatario","usuario") ) },
  @{ f = "DER_6_cumplimiento"; t = "DER 6 - Auditoria, reportes y notificaciones";
     g = @( @("evento_auditoria","reporte","parametro_sistema"), @("notificacion","preferencia_notificacion"), @("usuario","centro_comercial") ) }
)

$prj = $rep.GetProjectInterface()
$COLW = 340; $ROWH = 280; $W = 250; $X0 = 60; $Y0 = -60

# borrar versiones previas de estos sub-diagramas (idempotencia)
foreach ($s in $sub) {
  for ($i = $pkg.Diagrams.Count - 1; $i -ge 0; $i--) {
    if ($pkg.Diagrams.GetAt($i).Name -eq $s.t) { $pkg.Diagrams.Delete($i) }
  }
}
$pkg.Diagrams.Refresh()

foreach ($s in $sub) {
  $d = $pkg.Diagrams.AddNew($s.t, "Logical")
  $d.Update()
  $d.StyleEx = $estilo
  $d.Update()
  $n = 0
  for ($r = 0; $r -lt $s.g.Count; $r++) {
    for ($c = 0; $c -lt $s.g[$r].Count; $c++) {
      $nom = $s.g[$r][$c]
      if (-not $ent.ContainsKey($nom)) { Write-Output ("   FALTA " + $nom); continue }
      $h = 42 + 13 * [int]$natt[$nom]; if ($h -lt 70) { $h = 70 }
      $l = $X0 + $c * $COLW; $t = $Y0 - $r * $ROWH
      $o = $d.DiagramObjects.AddNew(("l=" + $l + ";r=" + ($l + $W) + ";t=" + $t + ";b=" + ($t - $h) + ";"), "")
      $o.ElementID = $ent[$nom].ElementID
      $o.Update()
      $n++
    }
  }
  $d.DiagramObjects.Refresh(); $d.Update()
  $rep.SaveDiagram($d.DiagramID) | Out-Null
  $rep.ReloadDiagram($d.DiagramID)
  $png = Join-Path $OUT ($s.f + ".png")
  $prj.PutDiagramImageToFile($d.DiagramGUID, $png, 1) | Out-Null
  Write-Output ("+ " + $s.t + "  (" + $n + " entidades)")
}

$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Add-Type -AssemblyName System.Drawing
Get-ChildItem "$OUT\*.png" | ForEach-Object {
  $im = [System.Drawing.Image]::FromFile($_.FullName)
  Write-Output ("   {0,-24} {1}x{2}" -f $_.Name, $im.Width, $im.Height); $im.Dispose()
}

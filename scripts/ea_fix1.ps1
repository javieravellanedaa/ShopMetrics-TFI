$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }

$dia = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($dia.PackageID)
Write-Output ("Diagrama: " + $dia.Name + "   Paquete: " + $pkg.Name + " (id " + $pkg.PackageID + ")")

# indice de entidades por nombre
$ent = @{}
foreach ($e in $pkg.Elements) { $ent[$e.Name] = $e }
Write-Output ("entidades en el paquete: " + $ent.Count)

# ------------------------------------------------------------------ 1) NOTACION PATA DE GALLO
$s = $dia.StyleEx
$s = $s -replace "TConnectorNotation=[^;]*;", "TConnectorNotation=Information Engineering;"
if ($s -notmatch "TConnectorNotation=") { $s += "TConnectorNotation=Information Engineering;" }
$dia.StyleEx = $s
$dia.Update()
Write-Output "1) notacion -> Information Engineering (pata de gallo)"

# ------------------------------------------------------------------ 2) CARDINALIDADES ERRONEAS
# conector_id -> @(cardOrigen, cardDestino, motivo)
$card = @{
  38 = @("0..1", "0..*", "alerta ML no nace de una regla (CU-007)")
  39 = @("0..1", "0..*", "hay alertas de locatario y de centro, no solo de zona (CU-008/CU-026)")
  32 = @("1",    "1..*", "un locatario ocupa al menos un local y puede ocupar varios (CU-005)")
}
foreach ($k in $card.Keys) {
  $c = $rep.GetConnectorByID([int]$k)
  $c.ClientEnd.Cardinality   = $card[$k][0]
  $c.SupplierEnd.Cardinality = $card[$k][1]
  $c.ClientEnd.Update(); $c.SupplierEnd.Update(); $c.Update()
  Write-Output ("2) [{0}] {1} {2} -> {3} : {4}" -f $k, $c.Name, $card[$k][0], $card[$k][1], $card[$k][2])
}

# ------------------------------------------------------------------ 3) ATRIBUTOS FK FALTANTES
# entidad -> @( @(campo, tipo, estereotipo, nota) )
$nuevosAttr = @{
  "alerta" = @(
    @("modelo_id",   "UUID", "FK", "Modelo de ML que genero la alerta (CU-007 paso 10). Nulo si la alerta nace de una regla de umbral."),
    @("locatario_id","UUID", "FK", "Locatario afectado, cuando la alerta es de negocio y no de zona (CU-008, CU-012)."),
    @("asignado_a",  "UUID", "FK", "Usuario responsable de atender la alerta (CU-028-001, CU-028-002).")
  )
  "local" = @(,
    @("zona_id", "UUID", "FK", "Zona del centro donde se ubica el local (CU-004 mapa del centro).")
  )
  "regla_alerta" = @(,
    @("centro_id", "UUID", "FK", "Centro al que pertenece la regla (CU-006).")
  )
  "evento_auditoria" = @(,
    @("centro_id", "UUID", "FK", "Centro sobre el que se ejecuto la accion (CU-016, CU-020).")
  )
  "reporte" = @(,
    @("centro_id", "UUID", "FK", "Centro sobre el que se genero el reporte (CU-015, CU-016).")
  )
  "centro_acceso" = @(,
    @("rol_id", "UUID", "PK,FK", "Rol del usuario dentro de ese centro (reemplaza el VARCHAR denormalizado).")
  )
}
foreach ($en in $nuevosAttr.Keys) {
  $e = $ent[$en]
  $ya = @(); foreach ($a in $e.Attributes) { $ya += $a.Name }
  foreach ($d in $nuevosAttr[$en]) {
    if ($ya -contains $d[0]) { Write-Output ("3) ya existia $en.$($d[0])"); continue }
    $a = $e.Attributes.AddNew($d[0], $d[1])
    $a.Update()
    $a.Stereotype = $d[2]
    $a.Notes = $d[3]
    $a.Update()
    Write-Output ("3) + $en.$($d[0]) ($($d[2]))")
  }
  $e.Attributes.Refresh()
}
# quitar el rol VARCHAR denormalizado de centro_acceso
$e = $ent["centro_acceso"]
for ($i = $e.Attributes.Count - 1; $i -ge 0; $i--) {
  $a = $e.Attributes.GetAt($i)
  if ($a.Name -eq "rol" -and $a.Type -eq "VARCHAR") {
    $e.Attributes.Delete($i); Write-Output "3) - centro_acceso.rol (VARCHAR denormalizado)"
  }
}
$e.Attributes.Refresh()

$rep.SaveDiagram(2) | Out-Null
$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Write-Output "`nFASE 1 OK"

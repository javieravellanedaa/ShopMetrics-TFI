$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$dia = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($dia.PackageID)

function Idx { $h = @{}; foreach ($e in $pkg.Elements) { $h[$e.Name] = $e }; return $h }
$ent = Idx

# ------------------------------------------------------------------ 4) ENTIDADES NUEVAS
$nuevas = @(
  @{ n = "regla_destinatario"; d = "Destinatarios de una regla de alerta y canal de envio (CU-006 paso 6).";
     a = @( @("regla_id","UUID","PK,FK","Regla de alerta."),
            @("usuario_id","UUID","PK,FK","Usuario destinatario."),
            @("canal","VARCHAR","","Canal de envio (push, email, WhatsApp).") ) },
  @{ n = "resolucion_alerta"; d = "Resolucion en terreno de una alerta (CU-007 pasos 7-8, CU-028-001 pasos 5-6).";
     a = @( @("id","UUID","PK","Identificador unico de la resolucion."),
            @("alerta_id","UUID","FK","Alerta resuelta."),
            @("usuario_id","UUID","FK","Operario que la resolvio."),
            @("causa","VARCHAR","","Causa identificada (max 500 caracteres)."),
            @("accion_tomada","VARCHAR","","Accion tomada (resolver, escalar, derivar)."),
            @("checklist_resumen","VARCHAR","","Resumen del resultado del checklist ejecutado."),
            @("fecha_resolucion","TIMESTAMP","","Fecha y hora de cierre de la alerta.") ) },
  @{ n = "recomendacion"; d = "Recomendacion generada por un modelo de optimizacion (CU-009 mix optimo, CU-010 por local).";
     a = @( @("id","UUID","PK","Identificador unico de la recomendacion."),
            @("modelo_id","UUID","FK","Modelo de ML que la genero."),
            @("centro_id","UUID","FK","Centro sobre el que aplica."),
            @("locatario_id","UUID","FK","Locatario destinatario. Nulo si la recomendacion es del centro (CU-009)."),
            @("tipo","VARCHAR","","Tipo (sumar rubro, reducir rubro, reubicar, accion de local)."),
            @("rubro_objetivo","VARCHAR","","Rubro sobre el que recae la recomendacion."),
            @("impacto_estimado","DECIMAL","","Impacto estimado en facturacion."),
            @("confianza","DECIMAL","","Nivel de confianza del modelo (0.0 a 1.0)."),
            @("prioridad","VARCHAR","","Prioridad (alta, media, baja)."),
            @("fecha","TIMESTAMP","","Fecha y hora de generacion.") ) },
  @{ n = "recomendacion_decision"; d = "Decision del usuario sobre una recomendacion; realimenta al modelo (CU-009 pasos 7-8, CU-010).";
     a = @( @("id","UUID","PK","Identificador unico de la decision."),
            @("recomendacion_id","UUID","FK","Recomendacion evaluada."),
            @("usuario_id","UUID","FK","Usuario que decide."),
            @("decision","VARCHAR","","Decision (adoptada, descartada)."),
            @("fecha","TIMESTAMP","","Fecha y hora de la decision.") ) },
  @{ n = "parametro_sistema"; d = "Parametro general de configuracion del sistema por centro (CU-024).";
     a = @( @("id","UUID","PK","Identificador unico del parametro."),
            @("centro_id","UUID","FK","Centro al que aplica el parametro."),
            @("usuario_id","UUID","FK","Usuario que realizo la ultima modificacion."),
            @("clave","VARCHAR","","Nombre del parametro."),
            @("valor","VARCHAR","","Valor configurado."),
            @("tipo_dato","VARCHAR","","Tipo de dato del valor."),
            @("fecha_modificacion","TIMESTAMP","","Fecha y hora del ultimo cambio.") ) }
)

foreach ($nu in $nuevas) {
  if ($ent.ContainsKey($nu.n)) { Write-Output ("4) ya existia " + $nu.n); continue }
  $e = $pkg.Elements.AddNew($nu.n, "Entity")
  $e.Update()
  $e.Notes = $nu.d
  $e.Update()
  $i = 0
  foreach ($d in $nu.a) {
    $a = $e.Attributes.AddNew($d[0], $d[1]); $a.Update()
    $a.Stereotype = $d[2]; $a.Notes = $d[3]; $a.Pos = $i; $a.Update()
    $i++
  }
  $e.Attributes.Refresh(); $e.Update()
  Write-Output ("4) + entidad " + $nu.n + " (" + $nu.a.Count + " campos)")
}
$pkg.Elements.Refresh()
$ent = Idx

# ------------------------------------------------------------------ 5) CONECTORES NUEVOS
# origen, destino, cardOrigen, cardDestino, motivo
$rel = @(
  @("modelo_ml",        "alerta",                 "0..1", "0..*", "alerta generada por ML (CU-007)"),
  @("locatario",        "alerta",                 "0..1", "0..*", "alerta de negocio sobre un locatario (CU-008/CU-012)"),
  @("usuario",          "alerta",                 "0..1", "0..*", "operario responsable de la alerta (CU-028-002)"),
  @("zona",             "local",                  "1",    "0..*", "ubicacion del local en el mapa (CU-004)"),
  @("centro_comercial", "regla_alerta",           "1",    "0..*", "la regla pertenece al centro (CU-006)"),
  @("centro_comercial", "evento_auditoria",       "0..1", "0..*", "auditoria por centro (CU-016/CU-020)"),
  @("centro_comercial", "reporte",                "1",    "0..*", "reporte por centro (CU-015/CU-016)"),
  @("rol",              "centro_acceso",          "1",    "0..*", "rol del usuario en cada centro (CU-019)"),
  @("regla_alerta",     "regla_destinatario",     "1",    "0..*", "destinatarios de la regla (CU-006 paso 6)"),
  @("usuario",          "regla_destinatario",     "1",    "0..*", "destinatarios de la regla (CU-006 paso 6)"),
  @("alerta",           "resolucion_alerta",      "1",    "0..1", "resolucion de la alerta (CU-028-001)"),
  @("usuario",          "resolucion_alerta",      "1",    "0..*", "operario que resuelve (CU-028-001)"),
  @("modelo_ml",        "recomendacion",          "1",    "0..*", "modelo que genera la recomendacion (CU-009)"),
  @("centro_comercial", "recomendacion",          "1",    "0..*", "recomendacion de mix del centro (CU-009)"),
  @("locatario",        "recomendacion",          "0..1", "0..*", "recomendacion para el local (CU-010)"),
  @("recomendacion",    "recomendacion_decision", "1",    "0..*", "decision adoptar/descartar (CU-009 paso 7)"),
  @("usuario",          "recomendacion_decision", "1",    "0..*", "usuario que decide (CU-009 paso 7)"),
  @("centro_comercial", "parametro_sistema",      "1",    "0..*", "parametros por centro (CU-024)"),
  @("usuario",          "parametro_sistema",      "1",    "0..*", "ultima modificacion (CU-024)")
)

# conectores ya existentes, para no duplicar
$hay = @{}
foreach ($e in $pkg.Elements) {
  foreach ($c in $e.Connectors) { $hay[("" + $c.ClientID + ">" + $c.SupplierID)] = $true }
}
$n = 0
foreach ($r in $rel) {
  $src = $ent[$r[0]]; $dst = $ent[$r[1]]
  if (-not $src -or -not $dst) { Write-Output ("5) FALTA entidad: " + $r[0] + " / " + $r[1]); continue }
  $k = "" + $src.ElementID + ">" + $dst.ElementID
  if ($hay.ContainsKey($k)) { Write-Output ("5) ya existia " + $r[0] + " -> " + $r[1]); continue }
  $c = $src.Connectors.AddNew("", "Association")
  $c.SupplierID = $dst.ElementID
  $c.Update()
  $c.ClientEnd.Cardinality = $r[2]; $c.ClientEnd.Update()
  $c.SupplierEnd.Cardinality = $r[3]; $c.SupplierEnd.Update()
  $c.Update()
  $hay[$k] = $true; $n++
  Write-Output ("5) + {0} ({1}) --> {2} ({3})   {4}" -f $r[0], $r[2], $r[1], $r[3], $r[4])
}
Write-Output ("conectores nuevos: " + $n)

$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Write-Output "`nFASE 2 OK"

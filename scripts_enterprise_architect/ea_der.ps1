$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { Write-Output "NO ABRE"; exit 1 }

function Q($sql) {
  $xml = $rep.SQLQuery($sql)
  if (-not $xml) { return @() }
  [xml]$x = $xml
  if (-not $x.EADATA.Dataset_0.Data) { return @() }
  return @($x.EADATA.Dataset_0.Data.Row)
}

Write-Output "=== PROPIEDADES DEL DIAGRAMA DER (id=2) ==="
foreach ($r in Q "SELECT Name, Diagram_Type, StyleEx, Styleex AS S2, PDATA AS P FROM t_diagram WHERE Diagram_ID=2") {
  Write-Output ("  Name       : " + $r.Name)
  Write-Output ("  Tipo       : " + $r.Diagram_Type)
  Write-Output ("  StyleEx    : " + $r.StyleEx)
}

Write-Output "`n=== ELEMENTOS EN EL DER ==="
$els = Q "SELECT o.Object_ID, o.Name, o.Object_Type, o.Stereotype, do.RectLeft, do.RectTop, do.RectRight, do.RectBottom FROM t_diagramobjects do INNER JOIN t_object o ON do.Object_ID = o.Object_ID WHERE do.Diagram_ID = 2 ORDER BY o.Name"
Write-Output ("  total: " + $els.Count)
foreach ($r in $els) {
  Write-Output ("  [{0,4}] {1,-26} tipo={2,-10} estereotipo={3,-10} pos=({4},{5})-({6},{7})" -f `
    $r.Object_ID, $r.Name, $r.Object_Type, $r.Stereotype, $r.RectLeft, $r.RectTop, $r.RectRight, $r.RectBottom)
}

Write-Output "`n=== CONECTORES EN EL DER ==="
$cs = Q @"
SELECT c.Connector_ID, c.Name, c.Connector_Type, c.Stereotype,
       so.Name AS Origen, do2.Name AS Destino,
       c.SourceCard, c.DestCard, c.SourceRole, c.DestRole, c.SourceAccess, c.DestAccess
FROM ((t_connector c
  INNER JOIN t_object so  ON c.Start_Object_ID = so.Object_ID)
  INNER JOIN t_object do2 ON c.End_Object_ID  = do2.Object_ID)
WHERE c.Connector_ID IN (SELECT ConnectorID FROM t_diagramlinks WHERE DiagramID = 2)
ORDER BY so.Name
"@
Write-Output ("  total: " + $cs.Count)
foreach ($r in $cs) {
  Write-Output ("  [{0,4}] {1,-22} --{2,-12}--> {3,-24} card: '{4}' -> '{5}'  stereo={6}" -f `
    $r.Connector_ID, $r.Origen, $r.Connector_Type, $r.Destino, $r.SourceCard, $r.DestCard, $r.Stereotype)
}

$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null

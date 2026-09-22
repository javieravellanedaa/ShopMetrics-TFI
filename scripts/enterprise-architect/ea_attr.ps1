$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { Write-Output "NO ABRE"; exit 1 }
function Q($sql) {
  $xml = $rep.SQLQuery($sql); if (-not $xml) { return @() }
  [xml]$x = $xml; if (-not $x.EADATA.Dataset_0.Data) { return @() }
  return @($x.EADATA.Dataset_0.Data.Row)
}
Write-Output "=== ATRIBUTOS POR ENTIDAD DEL DER ==="
$rows = Q @"
SELECT o.Name AS Ent, a.Name AS Campo, a.Type AS Tipo, a.Stereotype AS Est, a.Notes AS N, a.Pos
FROM (t_object o INNER JOIN t_attribute a ON o.Object_ID = a.Object_ID)
WHERE o.Object_ID IN (SELECT Object_ID FROM t_diagramobjects WHERE Diagram_ID = 2)
ORDER BY o.Name, a.Pos
"@
$actual = ""
foreach ($r in $rows) {
  if ($r.Ent -ne $actual) { $actual = $r.Ent; Write-Output ("`n  " + $actual) }
  Write-Output ("      {0,-24} {1,-12} {2}" -f $r.Campo, $r.Tipo, $r.Est)
}
Write-Output ("`ntotal atributos: " + $rows.Count)
$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null

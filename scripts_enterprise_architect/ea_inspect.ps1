$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"

Write-Output ("EA.exe corriendo: " + ((Get-Process EA -ErrorAction SilentlyContinue) -ne $null))

$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { Write-Output "NO SE PUDO ABRIR"; exit 1 }
Write-Output ("abierto: " + $rep.ProjectGUID)

# --- diagramas del proyecto ---
$sql = "SELECT d.Diagram_ID, d.Name, d.Diagram_Type, p.Name AS Paquete FROM t_diagram d LEFT JOIN t_package p ON d.Package_ID = p.Package_ID"
$xml = $rep.SQLQuery($sql)
[xml]$x = $xml
Write-Output "`n--- DIAGRAMAS ---"
foreach ($r in $x.EADATA.Dataset_0.Data.Row) {
  Write-Output ("  [{0}] {1,-46} tipo={2,-14} paq={3}" -f $r.Diagram_ID, $r.Name, $r.Diagram_Type, $r.Paquete)
}

$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null

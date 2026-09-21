$ErrorActionPreference = "Stop"
$rep = New-Object -ComObject EA.Repository
$rep.OpenFile("D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx") | Out-Null
$dia = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($dia.PackageID)
$sb = New-Object System.Text.StringBuilder
foreach ($e in $pkg.Elements) {
  foreach ($a in $e.Attributes) {
    [void]$sb.AppendLine(($e.Name + "|" + $a.Name + "|" + $a.Type + "|" + $a.Stereotype))
  }
}
[void]$sb.AppendLine("---CONECTORES---")
$vistos = @{}
foreach ($e in $pkg.Elements) {
  foreach ($c in $e.Connectors) {
    if ($vistos.ContainsKey($c.ConnectorID)) { continue }
    $vistos[$c.ConnectorID] = $true
    $s = $rep.GetElementByID($c.ClientID).Name
    $t = $rep.GetElementByID($c.SupplierID).Name
    [void]$sb.AppendLine(($s + "|" + $c.ClientEnd.Cardinality + "|" + $t + "|" + $c.SupplierEnd.Cardinality))
  }
}
$out = Join-Path $PSScriptRoot "modelo_ea.txt"
[System.IO.File]::WriteAllText($out, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Output ("exportado -> " + $out)
$rep.CloseFile(); $rep.Exit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null

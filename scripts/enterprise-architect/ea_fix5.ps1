$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }

[xml]$x = $rep.SQLQuery("SELECT COUNT(*) AS n FROM t_diagramlinks WHERE DiagramID=2")
Write-Output ("t_diagramlinks antes: " + $x.EADATA.Dataset_0.Data.Row.n)

# borrar la geometria vieja de los conectores: EA los re-rutea con el trazado por defecto
$rep.Execute("DELETE FROM t_diagramlinks WHERE DiagramID=2") | Out-Null

[xml]$x2 = $rep.SQLQuery("SELECT COUNT(*) AS n FROM t_diagramlinks WHERE DiagramID=2")
Write-Output ("t_diagramlinks despues: " + $x2.EADATA.Dataset_0.Data.Row.n)

$rep.ReloadDiagram(2)
$dia = $rep.GetDiagramByID(2)
$prj = $rep.GetProjectInterface()
$png = Join-Path $OUT "DER_ShopMetrics.png"
$prj.PutDiagramImageToFile($dia.DiagramGUID, $png, 1) | Out-Null
$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Add-Type -AssemblyName System.Drawing
$im = [System.Drawing.Image]::FromFile($png); Write-Output ("PNG " + $im.Width + "x" + $im.Height); $im.Dispose()

$ErrorActionPreference = "Stop"
$EAP = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect\shopMetrics.eapx"
$OUT = "D:\Javier\UAI\UAI - SAP\shopMetrics\shopMetrics\enterprise_architect"
$rep = New-Object -ComObject EA.Repository
if (-not $rep.OpenFile($EAP)) { throw "no abre" }
$dia = $rep.GetDiagramByID(2)
$pkg = $rep.GetPackageByID($dia.PackageID)

# ---- borrar el atributo basura 'c : e' que dejo una corrida abortada ----
foreach ($e in $pkg.Elements) {
  for ($i = $e.Attributes.Count - 1; $i -ge 0; $i--) {
    $a = $e.Attributes.GetAt($i)
    if ($a.Name.Length -le 2 -and $a.Type.Length -le 2) {
      Write-Output ("  - basura: " + $e.Name + "." + $a.Name + " : " + $a.Type)
      $e.Attributes.Delete($i)
    }
  }
  $e.Attributes.Refresh()
}

# ---- mostrar los atributos en el orden definido (PK, FK, resto) ----
$s = $dia.StyleEx
$s = $s -replace "AttPkg=\d;", "AttPkg=0;"
$dia.StyleEx = $s
$dia.Update()
if ($dia.StyleEx -match "AttPkg=(\d)") { Write-Output ("AttPkg = " + $Matches[1] + " (0 = respeta el orden PK/FK/resto)") }

$rep.SaveDiagram(2) | Out-Null
$rep.ReloadDiagram(2)
$prj = $rep.GetProjectInterface()
$png = Join-Path $OUT "DER_ShopMetrics.png"
$prj.PutDiagramImageToFile($dia.DiagramGUID, $png, 1) | Out-Null
$rep.CloseFile(); $rep.Exit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($rep) | Out-Null
Add-Type -AssemblyName System.Drawing
$im = [System.Drawing.Image]::FromFile($png); Write-Output ("PNG " + $im.Width + "x" + $im.Height); $im.Dispose()

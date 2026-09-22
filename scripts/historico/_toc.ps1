$ErrorActionPreference = "Stop"
$D = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"

$wd = New-Object -ComObject Word.Application
$wd.Visible = $false
$wd.DisplayAlerts = 0
$doc = $wd.Documents.Open($D, $false, $false)

Write-Output ("TOCs encontrados: " + $doc.TablesOfContents.Count)
for ($i = 1; $i -le $doc.TablesOfContents.Count; $i++) {
  $toc = $doc.TablesOfContents.Item($i)
  $toc.Update()
  Write-Output ("  TOC $i actualizado, entradas de texto: " + $toc.Range.Paragraphs.Count)
}
$doc.Fields.Update() | Out-Null
$doc.Repaginate()
Write-Output ("paginas: " + $doc.ComputeStatistics(2))
Write-Output ("secciones: " + $doc.Sections.Count)
Write-Output ("imagenes inline: " + $doc.InlineShapes.Count)

# primeras lineas del indice, para comprobar que cargo
$toc = $doc.TablesOfContents.Item(1)
$txt = $toc.Range.Text -split "`r"
for ($i = 0; $i -lt [math]::Min(12, $txt.Count); $i++) { if ($txt[$i].Trim()) { Write-Output ("   | " + $txt[$i].Trim()) } }

$doc.Save()
$doc.Close(0)
$wd.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($wd) | Out-Null

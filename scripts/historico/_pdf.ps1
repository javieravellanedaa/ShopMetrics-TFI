$ErrorActionPreference="Stop"
$D = "D:\Javier\UAI\UAI - SAP\STF\STF\Primera entrega\STF_Gomez_Javier_E1_v1.docx"
$P = "C:\Users\javie\AppData\Local\Temp\claude\D--Javier-UAI-UAI---SAP-STF\c435bfd7-fad9-400e-8645-4e6760655262\scratchpad\informe.pdf"
$wd = New-Object -ComObject Word.Application
$wd.Visible=$false; $wd.DisplayAlerts=0
$doc = $wd.Documents.Open($D,$false,$true)
$f = $doc.Content.Find; $f.ClearFormatting(); $f.Text="8.4.1 Anexo de capacidad operativa"
if ($f.Execute()) { Write-Output ("8.4.1 esta en la pagina " + $f.Parent.Information(3)) }
$f2 = $doc.Content.Find; $f2.ClearFormatting(); $f2.Text="Figura 8.30"
if ($f2.Execute()) { Write-Output ("Figura 8.30 en la pagina " + $f2.Parent.Information(3)) }
$doc.SaveAs2($P, 17)
$doc.Close(0); $wd.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($wd)|Out-Null

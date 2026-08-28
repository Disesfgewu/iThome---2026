Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bmp = New-Object Drawing.Bitmap(1280, 720)
$g = [Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, [Drawing.Size]::new(1280, 720))
$bmp.Save("C:\Users\marti\Desktop\iThome---2026\days\images\day23\01_interview_cabin_stt.png")
Write-Host "Saved"

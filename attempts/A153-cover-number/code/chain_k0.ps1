$ErrorActionPreference='SilentlyContinue'
$d='C:\Users\esumm\code\packing\attempts\A153-cover-number'
while (Get-Process -Id 70912 -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 20 }
$env:PYTHONDONTWRITEBYTECODE='1'
$p=Start-Process -FilePath 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' -ArgumentList 'code/run153.py','--pop','k0','--exact-limit','14' -WorkingDirectory $d -RedirectStandardOutput "$d\logs\k0.log" -RedirectStandardError "$d\logs\k0.err" -PassThru
$p.PriorityClass='BelowNormal'
$p.Id | Out-File "$d\logs\k0.pid"

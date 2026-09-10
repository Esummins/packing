param([string]$ArgLine, [string]$Log)
$env:PYTHONDONTWRITEBYTECODE = "1"
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$code = "C:\Users\esumm\code\packing\attempts\A189-noroom\code"
$p = Start-Process -FilePath $py -ArgumentList ("-u `"$code\noroom189.py`" " + $ArgLine) `
     -WorkingDirectory $code -PassThru -NoNewWindow -RedirectStandardOutput $Log -RedirectStandardError ($Log + ".err")
Start-Sleep -Milliseconds 300
try { $p.PriorityClass = "BelowNormal"; $p.ProcessorAffinity = 0xFFFF } catch {}
Write-Output ("pid " + $p.Id)

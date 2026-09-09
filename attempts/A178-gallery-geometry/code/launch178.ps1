param([string]$A = "", [string]$Log = "logs/run178.log")
$env:PYTHONDONTWRITEBYTECODE = "1"
$p = Start-Process -FilePath python -ArgumentList ("code/run178.py " + $A) -RedirectStandardOutput $Log -RedirectStandardError ($Log + ".err") -PassThru -WindowStyle Hidden
$p.PriorityClass = "BelowNormal"
$p.ProcessorAffinity = 0xFFFF
$p.Id | Out-File -Append logs/pids.txt
Write-Output $p.Id

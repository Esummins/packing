param([string]$A = "", [string]$Log = "logs/run199.log")
# BelowNormal, affinity 0xFFFF; run from attempts/A199-corner-seal
$env:PYTHONDONTWRITEBYTECODE = "1"
$p = Start-Process -FilePath python -ArgumentList ("-u code/run199.py " + $A) -RedirectStandardOutput $Log -RedirectStandardError ($Log + ".err") -PassThru -WindowStyle Hidden
$p.PriorityClass = "BelowNormal"
$p.ProcessorAffinity = 0xFFFF
$p.Id | Out-File -Append logs/pids.txt
Write-Output $p.Id

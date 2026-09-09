# A180 launcher: one python at BelowNormal / affinity 0xFFFF; pid appended to logs/pids.txt (never deleted)
param([string]$RunArgs = "--only c0_Y1033 --capture --max-nodes 400 --deadline 5400 --lp 1", [string]$Log = "c0_Y1033")
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$base = Split-Path -Parent $here
$env:PYTHONDONTWRITEBYTECODE = "1"
$n = (Get-Process python -ErrorAction SilentlyContinue | Measure-Object).Count
if ($n -ge 16) { Write-Output "box ceiling: $n pythons, not launching"; exit 2 }
$p = Start-Process -FilePath python -ArgumentList ("run180.py " + $RunArgs) -WorkingDirectory $here -PassThru `
     -RedirectStandardOutput "$base\logs\$Log.log" -RedirectStandardError "$base\logs\$Log.err" -WindowStyle Hidden
$p.PriorityClass = "BelowNormal"
$p.ProcessorAffinity = 0xFFFF
Add-Content "$base\logs\pids.txt" ("{0} {1} {2}" -f $p.Id, (Get-Date -Format s), $RunArgs)
Write-Output ("launched pid {0} ({1} pythons before)" -f $p.Id, $n)

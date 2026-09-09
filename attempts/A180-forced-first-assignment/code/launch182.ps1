# A182 launcher: one python at BelowNormal / affinity 0xFFFF; pid appended to logs/pids.txt (never deleted).
# Box ceiling 12 pythons, counted with a filter that catches relative command lines (CIM Name like 'python%').
param([string]$RunArgs = "--only c0_Y1033 --capture --max-nodes 600 --deadline 7200 --lp 1", [string]$Log = "c0_Y1033_182")
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$base = Split-Path -Parent $here
$env:PYTHONDONTWRITEBYTECODE = "1"
$n = (Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Measure-Object).Count
if ($n -ge 12) { Write-Output "box ceiling: $n pythons, not launching"; exit 2 }
$p = Start-Process -FilePath python -ArgumentList ("run182.py " + $RunArgs) -WorkingDirectory $here -PassThru `
     -RedirectStandardOutput "$base\logs\$Log.log" -RedirectStandardError "$base\logs\$Log.err" -WindowStyle Hidden
$p.PriorityClass = "BelowNormal"
$p.ProcessorAffinity = 0xFFFF
Add-Content "$base\logs\pids.txt" ("{0} {1} A182 {2}" -f $p.Id, (Get-Date -Format s), $RunArgs)
Write-Output ("launched pid {0} ({1} pythons before)" -f $p.Id, $n)

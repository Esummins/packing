# A193 launcher: two workers (one per class), BelowNormal / affinity 0xFFFF, then the certify phase (one process +
# the verifier child).  Lab ceiling 12 pythons excluding "Claude Extensions" is polled by the workers themselves
# before every LP; this script only counts once before launching.
$ErrorActionPreference = "Continue"
$env:PYTHONDONTWRITEBYTECODE = "1"
$base = Split-Path -Parent $PSScriptRoot
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$n = (Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Where-Object { $_.CommandLine -notlike "*Claude Extensions*" -and $_.CommandLine -notlike "*windows-mcp*" }).Count
"lab pythons before launch: $n"
if ($n -gt 10) { "box has $n lab pythons: waiting is left to the workers (they gate before every LP)" }
# ONE worker at a time: the box holds 11 lab pythons (ceiling 12), so the classes run in sequence
foreach ($cls in @("corners4", "k4_05")) {
  $log = Join-Path $base ("logs\run193b_" + $cls + ".log")
  $p = Start-Process -FilePath $py -ArgumentList @("-u", (Join-Path $base "code\probe193.py"), "--cls", $cls, "--mode", "s0", "--root-lp", "0", "--lp-cap", "300", "--max-lp", "3", "--max-nodes", "900", "--deadline", "3000") -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") -PassThru -WindowStyle Hidden
  try { $p.PriorityClass = "BelowNormal"; $p.ProcessorAffinity = 0xFFFF } catch {}
  "started $cls pid $($p.Id) " + (Get-Date)
  $p.WaitForExit()
}
"both workers done: " + (Get-Date)
$log = Join-Path $base "logs\run193b_certify.log"
$p = Start-Process -FilePath $py -ArgumentList @("-u", (Join-Path $base "code\probe193.py"), "--certify") -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") -PassThru -WindowStyle Hidden
try { $p.PriorityClass = "BelowNormal"; $p.ProcessorAffinity = 0xFFFF } catch {}
$p.WaitForExit()
"certify done: " + (Get-Date)

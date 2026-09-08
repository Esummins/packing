# A156 -- the clean pause: sentinel, drain, reap, prove zero.
#
# The SENTINEL path (PAUSED.md v2 §7a, scoped base): every A156 worker checks
# attempts\A156-day-shift\PAUSE between nodes, so the node in flight finishes, its row is written
# and only then does the worker exit.  Nothing in flight is discarded and nothing is killed here
# except a genuine orphan (a node137 child of THIS attempt whose supervisor is gone).
#
# It never touches A57's own PAUSE, A137's PAUSE, or any other chore's pidfile or sentinel.
param(
  [string]$Base = "C:\Users\esumm\code\packing\attempts\A156-day-shift",
  [string]$Reason = "A156 day shift ended",
  [int]$DrainMinutes = 30,
  [switch]$NoWait
)
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$txt = @"
$Reason ($stamp PDT) -- A156 day shift, Opus owner.

This is the SENTINEL path: every A156 worker (run156.py) checks this file between nodes, so the
node in flight finishes and is recorded before the worker exits.  Nothing is killed and nothing is
discarded.  The scaler (scale156.ps1) exits on this file too and launches nothing further.

Scoped to A156 (pausegate.paused(base=...)).  A57's own PAUSE and A137's PAUSE were reported at
every worker's start and never touched.

To resume: delete THIS file, rebuild the queue with code\mkqueue156.py, then follow the resume
block of attempts\A57-shadow-trees\PAUSED.md (v4).
"@
Set-Content -Path "$Base\PAUSE" -Value $txt -Encoding utf8
"$stamp sentinel set: $Base\PAUSE"

if (-not $NoWait) {
  $deadline = (Get-Date).AddMinutes($DrainMinutes)
  while ((Get-Date) -lt $deadline) {
    $w = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
           Where-Object { $_.CommandLine -like '*run156.py*' })
    $n = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
           Where-Object { $_.CommandLine -like '*node137.py*' -and $_.CommandLine -like '*A156-day-shift*' })
    if ($w.Count -eq 0 -and $n.Count -eq 0) { "$(Get-Date -Format 'HH:mm:ss') drained: 0 A156 workers, 0 A156 node children"; break }
    "$(Get-Date -Format 'HH:mm:ss') draining: $($w.Count) workers, $($n.Count) node children still finishing their node"
    Start-Sleep -Seconds 60
  }
}

# --- reap: a node child of THIS attempt whose supervisor is gone (never another chore's) -------
$live = @{}
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | ForEach-Object { $live[[int]$_.ProcessId] = $true }
$orphans = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
             Where-Object { $_.CommandLine -like '*node137.py*' -and
                            $_.CommandLine -like '*A156-day-shift*' -and
                            -not $live.ContainsKey([int]$_.ParentProcessId) })
foreach ($o in $orphans) {
  "REAPING orphan A156 node child pid $($o.ProcessId) (dead supervisor $($o.ParentProcessId))"
  Stop-Process -Id $o.ProcessId -Force -ErrorAction SilentlyContinue
}
if ($orphans.Count -eq 0) { "no orphaned A156 node children" }

# --- prove zero -------------------------------------------------------------------------------
$mine = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
          Where-Object { $_.CommandLine -like '*A156-day-shift*' -or $_.CommandLine -like '*run156.py*' })
$a57  = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" |
          Where-Object { $_.CommandLine -like '*tree57.py*' -or $_.CommandLine -like '*deepen.py*' -or
                         $_.CommandLine -like '*param96.py*' })
$scal = @(Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" |
          Where-Object { $_.CommandLine -like '*scale156.ps1*' })
"A156 python processes remaining: $($mine.Count)"
foreach ($m in $mine) { "   pid $($m.ProcessId): $(($m.CommandLine -replace '\s+',' ').Substring(0,[Math]::Min(140,($m.CommandLine -replace '\s+',' ').Length)))" }
"A57 tree/deepen/param drivers running: $($a57.Count)"
"A156 scalers still up: $($scal.Count)"
foreach ($s in $scal) { "   scaler pid $($s.ProcessId) -- it exits on its own at the sentinel check" }

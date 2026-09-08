# A137 -- the pause: sentinel, drain, reap, confirm.  Never kills a worker: the drivers stop
# BETWEEN nodes, so the in-flight node finishes and its row is written (the 2026-09-06 pause
# killed drivers and lost every in-flight node; PAUSED.md v2 exists because of it).
#
#   powershell -File code\pause137.ps1 -Reason "shift end 07:00" [-MaxWaitMin 30]
param(
  [string]$Base = "C:\Users\esumm\code\packing\attempts\A137-night-shift-2",
  [string]$Reason = "A137 night shift ended",
  [int]$MaxWaitMin = 30
)
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
@"
$Reason

Set $stamp PDT by A137 (night shift 2, Opus owner). This is the SENTINEL path: every A137
driver checks it between nodes, so the node in flight finishes and is recorded before the
worker exits. Nothing is killed and nothing is discarded.

This sentinel is A137-scoped (pausegate.paused(base=...), PAUSED.md v2 section 7a). A57's own
PAUSE was never touched and is still the A123 one.
"@ | Set-Content -Path "$Base\PAUSE" -Encoding utf8
"$(Get-Date -Format 'HH:mm:ss') sentinel written: $Base\PAUSE"

$deadline = (Get-Date).AddMinutes($MaxWaitMin)
while ($true) {
  $w = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
         Where-Object { $_.CommandLine -like "*run137.py*" -or $_.CommandLine -like "*node137.py*" -or $_.CommandLine -like "*emit137.py*" })
  if ($w.Count -eq 0) { "$(Get-Date -Format 'HH:mm:ss') all A137 workers have exited"; break }
  if ((Get-Date) -gt $deadline) {
    "$(Get-Date -Format 'HH:mm:ss') STILL RUNNING after $MaxWaitMin min (per-node wall is 1500 s, so this should not happen):"
    $w | Select-Object ProcessId, @{n='CL';e={$_.CommandLine.Substring(0,[Math]::Min(110,$_.CommandLine.Length))}} | Format-List
    break
  }
  "$(Get-Date -Format 'HH:mm:ss') draining: $($w.Count) A137 process(es) still finishing their node"
  Start-Sleep -Seconds 60
}

# the scaler exits on its own when it sees the sentinel; report it rather than killing it
$sc = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
        Where-Object { $_.CommandLine -like "*scaleup137.ps1*" })
"$(Get-Date -Format 'HH:mm:ss') scaler processes still up: $($sc.Count) (it exits at its next 10-min poll)"

# orphan reaper -- A57's own, dry-run first; it never deletes a pidfile
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
& $py "C:\Users\esumm\code\packing\attempts\A57-shadow-trees\code\pausegate.py" --reap --dry-run
"$(Get-Date -Format 'HH:mm:ss') box python processes now: " + @(Get-Process python -ErrorAction SilentlyContinue).Count
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Select-Object ProcessId, @{n='CL';e={$_.CommandLine.Substring(0,[Math]::Min(100,$_.CommandLine.Length))}} |
  Format-Table -AutoSize

# A137 scaler -- adds ONE LP worker at a time as the other campaigns' processes exit.
#
# Guards (all of them hard):
#   * never launches if the A137 PAUSE sentinel exists;
#   * never launches at or after -StopHM (default 06:00; the shift's hard no-launch line is 07:15);
#   * never launches unless the whole box's python count leaves room for the worker AND its one
#     node child (so <= -MaxPy python processes on the box at all times);
#   * never exceeds -MaxWorkers A137 workers;
#   * one launch per pass, then a full sleep, so a burst of exits cannot oversubscribe;
#   * writes a pidfile per worker and never deletes another chore's anything.
param(
  [string]$Base = "C:\Users\esumm\code\packing\attempts\A137-night-shift-2",
  [int]$MaxPy = 16,
  [int]$MaxWorkers = 5,
  [string]$StopHM = "06:00",
  [int]$SleepSec = 600,
  [string]$Deadline = "07:00"
)
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$env:PYTHONDONTWRITEBYTECODE = "1"
$stop = [datetime]::ParseExact((Get-Date -Format "yyyy-MM-dd") + " " + $StopHM, "yyyy-MM-dd HH:mm", $null)
if ($stop -lt (Get-Date)) { $stop = $stop.AddDays(1) }

while ($true) {
  if (Test-Path "$Base\PAUSE") { "$(Get-Date -Format 'HH:mm:ss') PAUSE sentinel: scaler exits"; break }
  if ((Get-Date) -ge $stop) { "$(Get-Date -Format 'HH:mm:ss') past ${StopHM}: scaler exits (no launches)"; break }
  # queues, in the coordinator's priority order: (b) fresh emission, then (c) deepen
  $queues = @()
  foreach ($f in Get-ChildItem "$Base\results\emitq_*.json" | Sort-Object Name) {
    $tag = $f.BaseName -replace '^emitq_', ''
    $out = "$Base\results\emit_lp_$tag.jsonl"
    $n = (Get-Content $f.FullName -Raw | ConvertFrom-Json).Count
    $doneN = 0
    if (Test-Path $out) { $doneN = (Get-Content $out | Measure-Object -Line).Lines }
    if ($doneN -lt $n) { $queues += [pscustomobject]@{ tag = $tag; file = $f.FullName; out = $out; left = ($n - $doneN) } }
  }
  $live = @(Get-Process python -ErrorAction SilentlyContinue).Count
  $mine = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*run137.py*" }).Count
  if ($queues.Count -gt 0 -and $live -le ($MaxPy - 2) -and $mine -lt $MaxWorkers) {
    $q = $queues[0]
    $w = "e" + (Get-Date -Format "HHmm")
    $args = @("-u", "code\run137.py", "--worker", $w, "--targets", $q.file, "--out", $q.out,
              "--wall", "1500", "--cap", "420", "--rounds", "2", "--jobs", "1", "--deadline", $Deadline)
    $p = Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $Base `
         -RedirectStandardOutput "$Base\logs\$w.out" -RedirectStandardError "$Base\logs\$w.err" `
         -WindowStyle Hidden -PassThru
    Set-Content -Path "$Base\progress\$w.pid" -Value $p.Id -Encoding utf8
    "$(Get-Date -Format 'HH:mm:ss') launched $w on $($q.tag) ($($q.left) left); box python was $live, A137 workers now $($mine+1)"
  } else {
    "$(Get-Date -Format 'HH:mm:ss') hold: box python $live (cap $MaxPy), A137 workers $mine, queues $($queues.Count)"
  }
  Start-Sleep -Seconds $SleepSec
}

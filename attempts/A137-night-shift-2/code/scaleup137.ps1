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
#
# The queue is rebuilt every pass by mkqueue137.py -- ONE combined file, (b) fresh level-1 shard
# children first and then (c) the level-2 deepen children, with recorded AND CLAIMED ids dropped.
# (Counting a queue's remainder from its out-file instead launches workers onto queues whose every
# job is already claimed: that wasted three slots at 02:16-02:36.)
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
$qfile = Join-Path $Base "results\queue_bc.json"
$qout  = Join-Path $Base "results\emit_lp_combined.jsonl"

while ($true) {
  if (Test-Path "$Base\PAUSE") { "$(Get-Date -Format 'HH:mm:ss') PAUSE sentinel: scaler exits"; break }
  if ((Get-Date) -ge $stop) { "$(Get-Date -Format 'HH:mm:ss') past ${StopHM}: scaler exits (no launches)"; break }
  $left = [int](& $py (Join-Path $Base "code\mkqueue137.py"))
  $live = @(Get-Process python -ErrorAction SilentlyContinue).Count
  $mine = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*run137.py*" }).Count
  if ($left -gt 0 -and $live -le ($MaxPy - 2) -and $mine -lt $MaxWorkers) {
    $w = "e" + (Get-Date -Format "HHmm")
    $wargs = @("-u", "code\run137.py", "--worker", $w, "--targets", $qfile, "--out", $qout,
               "--wall", "1500", "--cap", "420", "--rounds", "2", "--jobs", "1", "--deadline", $Deadline)
    $p = Start-Process -FilePath $py -ArgumentList $wargs -WorkingDirectory $Base `
         -RedirectStandardOutput "$Base\logs\$w.out" -RedirectStandardError "$Base\logs\$w.err" `
         -WindowStyle Hidden -PassThru
    Set-Content -Path "$Base\progress\$w.pid" -Value $p.Id -Encoding utf8
    "$(Get-Date -Format 'HH:mm:ss') launched $w on the combined queue ($left unclaimed); box python was $live, A137 workers now $($mine+1)"
  } else {
    "$(Get-Date -Format 'HH:mm:ss') hold: box python $live (cap $MaxPy), A137 workers $mine, unclaimed $left"
  }
  Start-Sleep -Seconds $SleepSec
}

# A182 watchdog: every 60 s read logs/heartbeat_<nid>.json of every A182 runner; a node in flight older than its
# wall (1,500 s) gets its process TREE killed (taskkill /T /F on the runner's pid; the journal already holds every
# finished node, so a relaunch resumes at that node).  Also logs the python count.  Stops when logs/watch182.stop exists.
param([int]$Every = 60)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$base = Split-Path -Parent $here
$log = "$base\logs\watch182.log"
while (-not (Test-Path "$base\logs\watch182.stop")) {
  $n = (Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Measure-Object).Count
  $now = [double]::Parse(((Get-Date) - (Get-Date "1970-01-01T00:00:00Z").ToUniversalTime()).TotalSeconds.ToString([Globalization.CultureInfo]::InvariantCulture))
  foreach ($f in Get-ChildItem "$base\logs\heartbeat_*.json" -ErrorAction SilentlyContinue) {
    try { $h = Get-Content $f.FullName -Raw | ConvertFrom-Json } catch { continue }
    if ($null -eq $h.label) { continue }
    $age = $now - [double]$h.t0
    $alive = Get-Process -Id $h.pid -ErrorAction SilentlyContinue
    if ($null -eq $alive) { continue }
    if ($age -gt [double]$h.wall) {
      Add-Content $log ("{0} KILL pid {1} nid {2} node {3} age {4:N0}s > wall {5}" -f (Get-Date -Format s), $h.pid, $h.nid, $h.label, $age, $h.wall)
      taskkill /PID $h.pid /T /F | Out-Null
      Add-Content "$base\logs\pids.txt" ("{0} killed by watch182 {1} (node {2} exceeded {3}s)" -f $h.pid, (Get-Date -Format s), $h.label, $h.wall)
    }
  }
  Add-Content $log ("{0} pythons={1}" -f (Get-Date -Format s), $n)
  Start-Sleep -Seconds $Every
}

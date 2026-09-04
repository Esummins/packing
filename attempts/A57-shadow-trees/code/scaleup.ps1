# A57 auto-scaler: wait for A56's final_sweep.py to disappear, then take the freed slots.
# Keeps A57 at <= 3 heavy processes while A56 runs and <= 5 afterwards.
# Detached:  Start-Process powershell -ArgumentList '-File','code\scaleup.ps1' -WindowStyle Hidden
$base = Split-Path -Parent $PSScriptRoot
$log  = "$base\logs\scaleup.log"
$py   = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
# T18 pinning, set HERE so every child this script starts inherits it.  launch.ps1 sets these in
# its own process, but the deepen.py launch below is a direct Start-Process from the scaler and
# would otherwise run unpinned -- ~20 OpenBLAS threads per worker, which is what took out a tree
# shard and a deepen job simultaneously.
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
function Note($m) {
  # Add-Content can lose a line to file-lock contention when two processes write at once,
  # which is how the "launched ..." entries went missing during the scaler outage.  Retry.
  $line = "$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')) $m"
  for ($k = 0; $k -lt 5; $k++) {
    try { Add-Content -Path $log -Value $line -ErrorAction Stop; return } catch { Start-Sleep -Milliseconds 200 }
  }
}

# --- single-instance guard -------------------------------------------------
# Two scalers would each hold their own queue index and launch the SAME shard twice, so two
# tree57 processes would race on one jsonl and redo one another's children.  Oldest wins.
# NB match '-File ...scaleup.ps1', NOT just 'scaleup.ps1': any `powershell -Command` that merely
# MENTIONS the script (every status check does) would otherwise count as a running scaler.  That
# false positive already cost one scaler -- checks looked like restarts, and the guard would make
# every genuine new instance exit.
$mine = $PID
$pidFile = "$base\logs\scaleup.pid"
# Command-line matching alone is NOT enough, and the earlier fix was still wrong: a status check
# run as `powershell -NonInteractive -Command '... -File ...\scaleup.ps1 ...'` contains BOTH
# '-File' and 'scaleup.ps1' in its own command line, so the guard saw a tool session as a running
# scaler and made the genuine one exit ("another scaler (pid 7368) is older" -- 7368 was a
# transient tool session).  Belt and braces now: a pidfile is the primary record, and the
# command-line scan additionally excludes -NonInteractive (every tool session sets it) and self.
$isLiveScaler = {
  param($procId)
  if (-not $procId) { return $false }
  $p = Get-CimInstance Win32_Process -Filter "ProcessId=$procId" -ErrorAction SilentlyContinue
  return ($p -and $p.Name -like 'powershell*' -and $p.CommandLine -like '*scaleup.ps1*' -and
          $p.CommandLine -notlike '*-NonInteractive*' -and $p.ProcessId -ne $mine)
}
$prior = $null
if (Test-Path $pidFile) { $prior = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1) -as [int] }
if (& $isLiveScaler $prior) {
  Note "scaler pid $prior already running (pidfile); this one ($mine) exits"
  exit 0
}
$others = @(Get-CimInstance Win32_Process -Filter "Name like 'powershell%'" |
            Where-Object { $_.CommandLine -like '*-File*scaleup.ps1*' -and $_.ProcessId -ne $mine -and
                           $_.CommandLine -notlike '*-NonInteractive*' } |
            Sort-Object CreationDate)
if ($others.Count -gt 0) {
  $oldest = $others[0]
  if ($oldest.CreationDate -lt (Get-Process -Id $mine).StartTime) {
    Note "another scaler (pid $($oldest.ProcessId)) is older; this one ($mine) exits"
    exit 0
  }
}
Set-Content -Path $pidFile -Value $mine -Encoding utf8


function A57Count {
  @(Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like '*A57-shadow-trees*' -and
                   ($_.CommandLine -like '*tree57.py*' -or $_.CommandLine -like '*ladder57.py*' -or
                    $_.CommandLine -like '*deepen.py*' -or $_.CommandLine -like '*zonescan.py*' -or
                    $_.CommandLine -like '*certify.py*' -or $_.CommandLine -like '*epsladder.py*' -or
                    $_.CommandLine -like '*sweepfails.py*') }).Count
}
function CommitFreeGB {
  # T19: the binding constraint on this box is the COMMIT limit (RAM 31.7 + pagefile), not RAM.
  # A worker reserves ~2-4 GB of commit against a ~0.5-1.2 GB working set, so "free physical
  # memory" badly overstates how much room there is to launch another one.
  $os = Get-CimInstance Win32_OperatingSystem
  [math]::Round($os.FreeVirtualMemory / 1MB, 2)
}

function A56Running {
  @(Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like '*final_sweep*' -or $_.CommandLine -like '*A56-sparametric*' }).Count -gt 0
}

# shards to add, in priority order, once the cap rises to 5
$queue = @()
# T29 (advisor/PI): after side 1, run the remaining grid sides BOTTOM-UP -- 4, then 3, then 2.
# Each completed side is a standalone record lower bound (s(11) > 3.833212, then > 3.847780,
# then > 3.862404) once the protected classes and trump5 are killed at the same side, because a
# side's PASS rules out every packing in the slab below it.  Top-down would yield nothing until
# all four landed.  Zero extra cost: all four sides are needed either way.
# side 1 shard 0/6 of each stratum is launched by hand (it is not in this queue).
$sides = @(
  @{tag='G1'; s='969271/250000'; shards=@('1/6','2/6','3/6','4/6','5/6')},   # 3.877084  (top slab)
  @{tag='G4'; s='958303/250000'; shards=@('0/6','1/6','2/6','3/6','4/6','5/6')},  # 3.833212 -> s(11) > 3.833212
  @{tag='G3'; s='192389/50000';  shards=@('0/6','1/6','2/6','3/6','4/6','5/6')},  # 3.847780 -> s(11) > 3.847780
  @{tag='G2'; s='965601/250000'; shards=@('0/6','1/6','2/6','3/6','4/6','5/6')}   # 3.862404 -> s(11) > 3.862404
)
# A96 FREEZE.  Sides listed in code\FREEZE_TAGS.txt are dropped from the queue outright: A96
# replaces them with parametric certificates over the whole window [191/50, s0] (A95 measured
# 0.062 of the four fixed sides).  G1 stays -- it is running and is the fixed-side fallback.
# launch.ps1 carries the same gate independently, so a scaler that predates this edit (its queue
# is in memory) still cannot start a frozen side.
$frozenTags = @()
$freezeFile = "$base\code\FREEZE_TAGS.txt"
if (Test-Path $freezeFile) {
  $frozenTags = @(Get-Content $freezeFile | ForEach-Object { $_.Trim() } |
                  Where-Object { $_ -ne '' -and -not $_.StartsWith('#') })
}
foreach ($sd in $sides) {
  if ($frozenTags -contains $sd.tag) { Note "queue: side $($sd.tag) is FROZEN, skipped"; continue }
  foreach ($sh in $sd.shards) {
    foreach ($nm in @('k5_11','k5_16')) {
      # Idempotent restart: a shard that was already launched once has its pidfile on disk.  The
      # queue index $qi is in memory only, so without this a restarted scaler would relaunch every
      # shard from the top of the queue and race the running tree57 on its jsonl.
      $si0 = ($sh -split '/')[0]
      if (Test-Path "$base\logs\$($nm)_interior_$($sd.tag)_s$si0.pid") { continue }
      $queue += @{n=$nm; s=$sh; tag=$sd.tag; side=$sd.s}
    }
  }
}
Note "queue built: $($queue.Count) shard(s); frozen tags = $($frozenTags -join ',')"
$qi = 0
Note "scaleup started; A57=$(A57Count) A56running=$(A56Running)"
for ($i = 0; $i -lt 5000; $i++) {
  $cap = if (A56Running) { 3 } else { 5 }
  $now = A57Count
  # Commit gate.  The PI moved the pagefile to F:\pagefile.sys at 25 GB initial / 100 GB max, so
  # the commit limit now GROWS ON DEMAND to ~130 GB and commit is no longer the binding
  # constraint (it was: 61 GB limit, 57.9 GB used, and A60 lost a shard to a 38 MiB allocation).
  # The gate stays as a safety net -- a growing pagefile still takes time to extend, and a burst
  # of launches into a momentarily tight window would still hurt other campaigns -- but the
  # threshold drops from 10.5 GB to 6 GB: roughly one worker's peak plus a small cushion.
  $commitFree = CommitFreeGB
  if ($commitFree -lt 6.0) {
    Note "commit headroom ${commitFree} GB < 6 GB: NOT launching (running=$now cap=$cap)"
    Start-Sleep -Seconds 180
    continue
  }
  if ($now -lt $cap -and $qi -lt $queue.Count) {
    $j = $queue[$qi]; $qi++
    & powershell -ExecutionPolicy Bypass -File "$base\code\launch.ps1" -Name $j.n -Shard $j.s `
        -Tag $j.tag -Side $j.side -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000 | Out-Null
    Note "cap=$cap running=$now -> launched $($j.n) $($j.tag) side=$($j.side) shard $($j.s)"
    Start-Sleep -Seconds 45
  } elseif ($now -lt $cap) {
    # L1 queue exhausted: keep freed slots on depth 2.  deepen.py owns every ALIVE-at-LP /
    # cert-FAIL record of a level-1 key and is resumable, so re-launching it is safe.
    foreach ($k in @('k5_11_interior_G1', 'k5_16_interior_G1')) {
      if ((A57Count) -ge $cap) { break }
      $running = @(Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
                   Where-Object { $_.CommandLine -like "*deepen.py*$k*" }).Count
      if ($running -eq 0) {
        Start-Process -FilePath $py -ArgumentList @('-u', "$base\code\deepen.py", '--key', $k,
            '--levels', '3', '--time_limit', '240', '--cert_time', '240', '--pin_delta', '0.01') -WorkingDirectory $base `
            -RedirectStandardOutput "$base\logs\deepen_$k.out" `
            -RedirectStandardError "$base\logs\deepen_$k.err" -WindowStyle Hidden | Out-Null
        Note "cap=$cap -> launched deepen $k"
      }
    }
    Start-Sleep -Seconds 300
  } else {
    Start-Sleep -Seconds 120
  }
}
Note "scaleup exit"

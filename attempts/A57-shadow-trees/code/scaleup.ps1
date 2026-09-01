# A57 auto-scaler: wait for A56's final_sweep.py to disappear, then take the freed slots.
# Keeps A57 at <= 3 heavy processes while A56 runs and <= 5 afterwards.
# Detached:  Start-Process powershell -ArgumentList '-File','code\scaleup.ps1' -WindowStyle Hidden
$base = Split-Path -Parent $PSScriptRoot
$log  = "$base\logs\scaleup.log"
$py   = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
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
$others = @(Get-CimInstance Win32_Process -Filter "Name like 'powershell%'" |
            Where-Object { $_.CommandLine -like '*-File*scaleup.ps1*' -and $_.ProcessId -ne $mine } |
            Sort-Object CreationDate)
if ($others.Count -gt 0) {
  $oldest = $others[0]
  if ($oldest.CreationDate -lt (Get-Process -Id $mine).StartTime) {
    Note "another scaler (pid $($oldest.ProcessId)) is older; this one ($mine) exits"
    exit 0
  }
}


function A57Count {
  @(Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like '*A57-shadow-trees*' -and
                   ($_.CommandLine -like '*tree57.py*' -or $_.CommandLine -like '*ladder57.py*' -or
                    $_.CommandLine -like '*deepen.py*' -or $_.CommandLine -like '*zonescan.py*' -or
                    $_.CommandLine -like '*certify.py*' -or $_.CommandLine -like '*epsladder.py*' -or
                    $_.CommandLine -like '*sweepfails.py*') }).Count
}
function A56Running {
  @(Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like '*final_sweep*' -or $_.CommandLine -like '*A56-sparametric*' }).Count -gt 0
}

# shards to add, in priority order, once the cap rises to 5
$queue = @(
  @{n='k5_11'; s='1/6'}, @{n='k5_16'; s='1/6'},
  @{n='k5_11'; s='2/6'}, @{n='k5_16'; s='2/6'},
  @{n='k5_11'; s='3/6'}, @{n='k5_16'; s='3/6'},
  @{n='k5_11'; s='4/6'}, @{n='k5_16'; s='4/6'},
  @{n='k5_11'; s='5/6'}, @{n='k5_16'; s='5/6'}
)
$qi = 0
Note "scaleup started; A57=$(A57Count) A56running=$(A56Running)"
for ($i = 0; $i -lt 5000; $i++) {
  $cap = if (A56Running) { 3 } else { 5 }
  $now = A57Count
  if ($now -lt $cap -and $qi -lt $queue.Count) {
    $j = $queue[$qi]; $qi++
    & powershell -ExecutionPolicy Bypass -File "$base\code\launch.ps1" -Name $j.n -Shard $j.s `
        -Tag L1 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000 | Out-Null
    Note "cap=$cap running=$now -> launched $($j.n) shard $($j.s)"
    Start-Sleep -Seconds 45
  } elseif ($now -lt $cap) {
    # L1 queue exhausted: keep freed slots on depth 2.  deepen.py owns every ALIVE-at-LP /
    # cert-FAIL record of a level-1 key and is resumable, so re-launching it is safe.
    foreach ($k in @('k5_11_interior_L1', 'k5_16_interior_L1')) {
      if ((A57Count) -ge $cap) { break }
      $running = @(Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
                   Where-Object { $_.CommandLine -like "*deepen.py*$k*" }).Count
      if ($running -eq 0) {
        Start-Process -FilePath $py -ArgumentList @('-u', "$base\code\deepen.py", '--key', $k,
            '--levels', '3', '--time_limit', '240', '--cert_time', '240') -WorkingDirectory $base `
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

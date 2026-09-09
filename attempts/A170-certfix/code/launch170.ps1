# A170 -- launch the re-certification workers: <= 4 processes, BelowNormal, affinity 0xFFFF.
# Every worker honours the sentinels (repo PAUSE/STOP, attempt PAUSE/STOP) between records and is
# resumable (it skips ids already present in its --out jsonl).
param(
  [int]$K0Shards = 2,
  [double]$Wall = 7200
)
$ErrorActionPreference = "Stop"
$base = Split-Path -Parent $PSScriptRoot
$py   = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:OMP_NUM_THREADS = "1"; $env:OPENBLAS_NUM_THREADS = "1"; $env:MKL_NUM_THREADS = "1"

function Start-Worker($name, $argv) {
  $log = Join-Path $base "logs\$name.log"
  $p = Start-Process -FilePath $py -ArgumentList $argv -WorkingDirectory $base `
        -RedirectStandardOutput $log -RedirectStandardError "$log.err" -PassThru -WindowStyle Hidden
  Start-Sleep -Milliseconds 400
  try { $p.PriorityClass = "BelowNormal"; $p.ProcessorAffinity = 0xFFFF } catch {}
  Write-Host ("started {0} pid {1} -> {2}" -f $name, $p.Id, $log)
  return $p
}

for ($i = 0; $i -lt $K0Shards; $i++) {
  Start-Worker "k0_s$i" @("code\recert170.py","--mode","k0","--out","results\recert170_k0.s$i.jsonl",
                          "--shard","$i","--nshards","$K0Shards","--jobs","1","--wall","$Wall") | Out-Null
}

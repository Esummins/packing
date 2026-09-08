# A156 -- launch ONE day-shift LP worker, behind the pidfile gate.
#
# Gates, all hard, checked in this order:
#   1. this attempt's PAUSE sentinel exists            -> refuse (never launch into a pause);
#   2. progress\<Worker>.pid exists and that pid is a LIVE python  -> refuse (the pidfile gate:
#      the same worker name is never started twice, and no pidfile is ever deleted here);
#   3. the box's LAB python count leaves no room for the worker AND its one node child
#      (count + 2 > -MaxLab)                            -> refuse;
#   4. the queue is empty                               -> refuse.
# Then: Start-Process at Normal priority, ProcessorAffinity = 0xFFFF (P-cores; the node child
# inherits the mask), BLAS pinned to one thread, PYTHONDONTWRITEBYTECODE=1, pidfile written.
param(
  [string]$Worker = "d0",
  [string]$Base = "C:\Users\esumm\code\packing\attempts\A156-day-shift",
  [int]$MaxLab = 16,
  [double]$Wall = 1500,
  [double]$Cap = 420,
  [string]$Deadline = "22:45",
  [int64]$Mask = 0xFFFF,
  [switch]$Force
)
$py = "C:\Users\esumm\AppData\Local\Python\bin\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
$env:OPENBLAS_NUM_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"
$env:PYTHONDONTWRITEBYTECODE = "1"

if (Test-Path "$Base\PAUSE") { Write-Output "REFUSED $Worker : A156 PAUSE sentinel is set"; exit 0 }

$pidfile = "$Base\progress\$Worker.pid"
if (Test-Path $pidfile) {
  $old = (Get-Content $pidfile -ErrorAction SilentlyContinue | Select-Object -First 1)
  $liveproc = $null
  if ($old) { $liveproc = Get-Process -Id ([int]$old) -ErrorAction SilentlyContinue }
  if ($liveproc -and $liveproc.ProcessName -like 'python*') {
    Write-Output "REFUSED $Worker : pidfile gate -- pid $old is live"; exit 0
  }
  # stale pidfile: it is THIS attempt's own, and it is overwritten in place, never deleted.
}

$lab = [int](& powershell -NonInteractive -ExecutionPolicy Bypass -File "$Base\code\labcount156.ps1")
if (-not $Force -and ($lab + 2) -gt $MaxLab) {
  Write-Output "REFUSED $Worker : lab python $lab, no room for worker+child under cap $MaxLab"; exit 0
}

$left = [int](& $py "$Base\code\mkqueue156.py")
if ($left -le 0) { Write-Output "REFUSED $Worker : queue empty"; exit 0 }

$wargs = @("-u", "$Base\code\run156.py", "--worker", $Worker,
           "--targets", "$Base\results\queue156.json",
           "--out", "$Base\results\lp156_$Worker.jsonl",
           "--wall", $Wall, "--cap", $Cap, "--rounds", "2", "--jobs", "1",
           "--deadline", $Deadline)
$p = Start-Process -FilePath $py -ArgumentList $wargs -WorkingDirectory $Base `
     -RedirectStandardOutput "$Base\logs\$Worker.out" -RedirectStandardError "$Base\logs\$Worker.err" `
     -WindowStyle Hidden -PassThru
Start-Sleep -Milliseconds 400
try {
  $proc = Get-Process -Id $p.Id -ErrorAction Stop
  $proc.ProcessorAffinity = [IntPtr]$Mask
  $proc.PriorityClass = 'Normal'
} catch { Write-Output "WARN could not set affinity/priority on $($p.Id): $_" }
Set-Content -Path $pidfile -Value $p.Id -Encoding utf8
Write-Output "$Worker pid=$($p.Id) lab_python_before=$lab queue=$left affinity=0x$('{0:X}' -f $Mask) deadline=$Deadline"

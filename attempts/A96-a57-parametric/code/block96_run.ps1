# A96 block-first pilot driver: one process at a time (two only during certification).
# Free-physical gate, BLAS pinned, resumable (both stages skip finished tags).
$ErrorActionPreference = "Continue"
$env:OMP_NUM_THREADS = "1"; $env:OPENBLAS_NUM_THREADS = "1"; $env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"; $env:VECLIB_MAXIMUM_THREADS = "1"
$code = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $code
$log = Join-Path $code "..\logs\block96_driver.log"
function Gate {
  while ($true) {
    $os = Get-CimInstance Win32_OperatingSystem
    $freeMB = [int]($os.FreePhysicalMemory / 1KB)
    if ($freeMB -gt 3072) { return }
    "$(Get-Date -f HH:mm:ss) free ${freeMB} MB <= 3072, waiting 60 s" | Out-File -Append -Encoding utf8 $log
    Start-Sleep -Seconds 60
  }
}
Gate
"$(Get-Date -f HH:mm:ss) blocklp (39 subsumed block boxes) start" | Out-File -Append -Encoding utf8 $log
python block96.py --stage blocklp --bids ..\results\block96\subsumed_bids.json --time_limit 900 --cert_time 240 --wall 1500 2>&1 | Out-File -Append -Encoding utf8 $log
Gate
"$(Get-Date -f HH:mm:ss) nodelp start" | Out-File -Append -Encoding utf8 $log
python block96.py --stage nodelp --time_limit 900 --cert_time 240 --wall 4200 2>&1 | Out-File -Append -Encoding utf8 $log
"$(Get-Date -f HH:mm:ss) DONE" | Out-File -Append -Encoding utf8 $log

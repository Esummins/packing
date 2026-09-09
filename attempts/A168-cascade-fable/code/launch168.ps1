# A168 -- launch ONE lab python at BelowNormal, affinity 0xFFFF, BLAS pinned, after waiting for a
# slot under the 16-lab-python box ceiling.  Usage:
#   powershell -File launch168.ps1 <logname> <script.py> [args...]
$ErrorActionPreference = 'Continue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OPENBLAS_NUM_THREADS = '1'; $env:OMP_NUM_THREADS = '1'; $env:MKL_NUM_THREADS = '1'
$py   = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$code = 'C:\Users\esumm\code\packing\attempts\A168-cascade-fable\code'
$logs = 'C:\Users\esumm\code\packing\attempts\A168-cascade-fable\logs'
Set-Location $code
$name = $args[0]
$rest = $args[1..($args.Count - 1)]

function WaitSlot($need) {
  for ($k = 0; $k -lt 90; $k++) {
    $n = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
           Where-Object { $_.CommandLine -like '*code\packing\attempts*' }).Count
    $os = Get-CimInstance Win32_OperatingSystem
    $free = [math]::Round($os.FreePhysicalMemory / 1KB, 0)
    if (($n + $need) -le 16 -and $free -ge 3072) { Write-Output ("slot ok: lab-python={0} freeMB={1}" -f $n, $free); return $true }
    Start-Sleep -Seconds 20
  }
  Write-Output ("SKIPPED: no slot after 30 min (lab-python={0})" -f $n)
  return $false
}
if (-not (WaitSlot 1)) { exit 1 }
$argv = @('-u') + $rest
$p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
      -RedirectStandardOutput "$logs\$name.log" -RedirectStandardError "$logs\$name.err"
$p.ProcessorAffinity = 0xFFFF
$p.PriorityClass = 'BelowNormal'
Write-Output ("{0} pid {1} started" -f $name, $p.Id)

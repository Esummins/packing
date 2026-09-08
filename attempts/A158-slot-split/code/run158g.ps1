# A158b -- the YES child as an LP node.  c0_Y0076 first, then the other five PI cells.
# One A158 python at a time; wait for a slot; never exceed 16 lab pythons.
$ErrorActionPreference = 'Continue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$py   = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$code = 'C:\Users\esumm\code\packing\attempts\A158-slot-split\code'
$logs = 'C:\Users\esumm\code\packing\attempts\A158-slot-split\logs'
Set-Location $code

function Run($name, $argv, $wallMs) {
  $n = 99; $free = 0
  for ($k = 0; $k -lt 240; $k++) {
    $n = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
           Where-Object { $_.CommandLine -like '*code\packing\attempts*' -or
                          $_.CommandLine -like '*158.py*' }).Count
    $os = Get-CimInstance Win32_OperatingSystem
    $free = [math]::Round($os.FreePhysicalMemory / 1KB, 0)
    if ($n -lt 16 -and $free -ge 3072) { break }
    Start-Sleep -Seconds 20
  }
  Write-Output ("[{0}] start  lab-python={1} freePhysMB={2}" -f $name, $n, $free)
  if ($n -ge 16 -or $free -lt 3072) { Write-Output ("[{0}] SKIPPED (gate held 80 min)" -f $name); return }
  $p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
        -RedirectStandardOutput "$logs\$name.log" -RedirectStandardError "$logs\$name.err"
  $p.ProcessorAffinity = 0xFFFF
  $p.PriorityClass = 'Normal'
  if (-not $p.WaitForExit($wallMs)) { $p.Kill(); Write-Output ("[{0}] WALL-CAP (never a verdict)" -f $name); return }
  Write-Output ("[{0}] done exit={1}" -f $name, $p.ExitCode)
}

# 1. c0_Y0076 alone, first
Run 'yeslp_y0076' @('-u','yeslp158.py','--jobs','../results/y0076_job.jsonl','--r','0.10','--tt','10','--cap','240','--cap2','900','--budget_s','3000') 3600000
# 2. the other five PI cells
Run 'yeslp_named'  @('-u','yeslp158.py','--jobs','../results/all_jobs.jsonl','--r','0.10','--tt','10','--cap','240','--cap2','900','--budget_s','4200') 5400000
Write-Output 'A158 run158g.ps1 finished'

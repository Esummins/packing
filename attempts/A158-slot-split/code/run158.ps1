# A158 -- the remaining runs, STRICTLY SEQUENTIAL (one lab python of this attempt at a time,
# so the box stays at <= 16).  Normal priority, affinity 0xFFFF, PYTHONDONTWRITEBYTECODE=1.
$ErrorActionPreference = 'Continue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$py  = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$code = 'C:\Users\esumm\code\packing\attempts\A158-slot-split\code'
$logs = 'C:\Users\esumm\code\packing\attempts\A158-slot-split\logs'
Set-Location $code

function Run($name, $argv) {
  # the other campaigns' workers spawn and reap children, so the box oscillates between 15 and 16
  # lab python processes: WAIT for a slot rather than skip (up to 40 min), never exceed 16.
  $n = 99; $free = 0
  for ($k = 0; $k -lt 120; $k++) {
    $n = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
           Where-Object { $_.CommandLine -like '*code\packing\attempts*' }).Count
    $os = Get-CimInstance Win32_OperatingSystem
    $free = [math]::Round($os.FreePhysicalMemory / 1KB, 0)
    if ($n -lt 16 -and $free -ge 3072) { break }
    Start-Sleep -Seconds 20
  }
  Write-Output ("[{0}] start  lab-python={1} freePhysMB={2}" -f $name, $n, $free)
  if ($n -ge 16) { Write-Output ("[{0}] SKIPPED: box stayed at {1} lab python processes for 40 min" -f $name, $n); return }
  if ($free -lt 3072) { Write-Output ("[{0}] SKIPPED: free physical {1} MB < 3072" -f $name, $free); return }
  $p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
        -RedirectStandardOutput "$logs\$name.log" -RedirectStandardError "$logs\$name.err"
  $p.ProcessorAffinity = 0xFFFF
  $p.PriorityClass = 'Normal'
  $p.WaitForExit()
  Write-Output ("[{0}] done exit={1}" -f $name, $p.ExitCode)
}

# 1. bisect the NO threshold on c0_Y0076 (kill at 0.05, no-kill at 0.02)
Run 'no_y0076_bisect' @('-u','no158.py','--nid','c0_Y0076','--slot','TL(0,0)','--radii','0.03,0.04,0.045','--tt','10','--cap','240','--emit','0')

# 2. the YES side of the three PI cells (c0_Y0959 added by the coordinator)
Run 'xover_named2' @('-u','xover158.py','--jobs','../results/xover_jobs.jsonl','--n','400000','--tilts','0,0.5,1,2,5,10,15','--out','../results/xover158_tt.jsonl')

# 3. the NO side of c0_Y0787 and c0_Y0959 at the PI's radius, with certificates
Run 'no_named' @('-u','no158.py','--jobs','../results/named_jobs.jsonl','--radii','0.10','--tt','10','--cap','240','--emit','1')

# 4. their NO thresholds
Run 'no_named_grid' @('-u','no158.py','--jobs','../results/named_jobs.jsonl','--radii','0.05,0.02','--tt','10','--cap','240','--emit','0')

# 4b. the tilt threshold of the NO side on c0_Y0076 (kill at tt = 2, no-kill at tt = 1)
Run 'no_y0076_tt15' @('-u','no158.py','--nid','c0_Y0076','--slot','TL(0,0)','--radii','0.10','--tt','1.5','--cap','240','--emit','0')

# 5. the top-20 of the population
Run 'mktop' @('-u','mktop158.py','--n','20')

# 6. the YES side of the top-20
Run 'xover_top' @('-u','xover158.py','--jobs','../results/top158.jsonl','--n','400000','--tilts','0,10','--out','../results/xover158.jsonl','--budget','2400')

# 7. the NO side of the top-20 at the PI's radius
Run 'no_top' @('-u','no158.py','--jobs','../results/top158.jsonl','--radii','0.10','--tt','10','--cap','240','--emit','0','--budget','2700')

Write-Output 'A158 run158.ps1 finished'

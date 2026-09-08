# A158 -- follow-up: the fourth PI cell k5_11_interior_Y0130 TR(0,0) (A57, level 1, alive,
# tau 5.5 vs budget 5, A141 NEAR-MISS LANE 1 / M 1), plus anything run158.ps1 could not fit.
# Same discipline: one lab python of this attempt at a time, wait for a slot, never exceed 16.
$ErrorActionPreference = 'Continue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$py   = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$code = 'C:\Users\esumm\code\packing\attempts\A158-slot-split\code'
$logs = 'C:\Users\esumm\code\packing\attempts\A158-slot-split\logs'
Set-Location $code

function Run($name, $argv) {
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
  if ($n -ge 16 -or $free -lt 3072) { Write-Output ("[{0}] SKIPPED (gate)" -f $name); return }
  $p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
        -RedirectStandardOutput "$logs\$name.log" -RedirectStandardError "$logs\$name.err"
  $p.ProcessorAffinity = 0xFFFF
  $p.PriorityClass = 'Normal'
  $p.WaitForExit()
  Write-Output ("[{0}] done exit={1}" -f $name, $p.ExitCode)
}

# the fast YES screen at the PI's box over the whole top-20 (3 s/cell)
Run 'yesscreen_top' @('-u','yesscreen158.py','--jobs','../results/top158.jsonl','--r','0.10','--tt','10','--budget','1800')
# the YES side (the conditional lane's sampled refutation and the crossover radius)
Run 'xover_y0130' @('-u','xover158.py','--jobs','../results/y0130_jobs.jsonl','--n','400000','--tilts','0,0.5,1,2,5,10,15','--out','../results/xover158_tt.jsonl')
# the NO side at the PI's radius, with a certificate, then the threshold grid
Run 'no_y0130' @('-u','no158.py','--jobs','../results/y0130_jobs.jsonl','--radii','0.10','--tt','10','--cap','900','--emit','1')
Run 'no_y0130_grid' @('-u','no158.py','--jobs','../results/y0130_jobs.jsonl','--radii','0.15,0.05','--tt','10,15','--cap','900','--emit','0','--budget','2400')
# how big does S have to be before the NO child bites on the cells where r = 0.10 did not?
Run 'no_big' @('-u','no158.py','--jobs','../results/named_jobs.jsonl','--radii','0.15,0.25','--tt','10,20','--cap','300','--emit','0','--budget','2100')
# the STRONG refutation: an explicit (pose in S, free second meeter) interior-disjoint pair
Run 'pair_named' @('-u','pair158.py','--jobs','../results/all_jobs.jsonl','--radii','0.10,0.05,0.01','--tt','10,2,0.5')
Write-Output 'A158 run158b.ps1 finished'

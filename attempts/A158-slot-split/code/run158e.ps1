# A158 -- the CONTROL run: the same A135 exact-core re-solve with NO NoFam, on every cell where
# the NO child reported a kill (and on the six PI cells).  Without it a `tau < budget` cannot be
# attributed to the slot box: A135's exact cores are strictly larger than the stored ones, and
# several A57 records are `converged = false, dead_unconverged = true` (their stored tau is not a
# bound).  `--radii -1` is the control marker in no158.py.
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
           Where-Object { $_.CommandLine -like '*code\packing\attempts*' -or
                          $_.CommandLine -like '*158.py*' }).Count
    $os = Get-CimInstance Win32_OperatingSystem
    $free = [math]::Round($os.FreePhysicalMemory / 1KB, 0)
    if ($n -lt 16 -and $free -ge 3072) { break }
    Start-Sleep -Seconds 20
  }
  Write-Output ("[{0}] start  lab-python={1}(+1 self) freePhysMB={2}" -f $name, $n, $free)
  if ($n -ge 16 -or $free -lt 3072) { Write-Output ("[{0}] SKIPPED (gate)" -f $name); return }
  $p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
        -RedirectStandardOutput "$logs\$name.log" -RedirectStandardError "$logs\$name.err"
  $p.ProcessorAffinity = 0xFFFF
  $p.PriorityClass = 'Normal'
  $p.WaitForExit()
  Write-Output ("[{0}] done exit={1}" -f $name, $p.ExitCode)
}

# the ONE cell whose YES side the 400,000-pose screen does not refute: certify it.
Run 'yesscreen_y1110' @('-u','yesscreen158.py','--jobs','../results/yes_candidates.jsonl','--r','0.10','--tt','10','--n','800000','--nm','400000','--budget','600')
Run 'yescert_y1110'   @('-u','yescert158.py','--jobs','../results/yes_candidates.jsonl','--r','0.10','--tt','10','--wall','420')

# close the one unmeasured tilt window: caselp exempts nothing below tt = 0.3 deg (EPS_TH), and
# the YES child was measured to fail at tt = 0.5 -- so (0.3, 0.5) is the only band where the two
# sides could conceivably meet.  Measure the YES side there.
Run 'xover_gap'     @('-u','xover158.py','--jobs','../results/all_jobs.jsonl','--n','400000','--tilts','0.31,0.4,0.49','--out','../results/xover158_gap.jsonl','--budget','1800')
Run 'no_gap'        @('-u','no158.py','--jobs','../results/all_jobs.jsonl','--radii','0.10,0.20','--tt','0.4','--cap','240','--emit','0','--budget','1500')
Run 'mkcontrol'     @('-u','mkcontrol158.py')
Run 'control_kills' @('-u','no158.py','--jobs','../results/control_jobs.jsonl','--radii','-1','--tt','10','--cap','240','--emit','0','--budget','2400')
Run 'summary2'      @('-u','sum158.py')
Write-Output 'A158 run158e.ps1 finished'

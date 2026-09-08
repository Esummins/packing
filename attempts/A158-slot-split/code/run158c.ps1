# A158 -- the essential remainder, re-ordered by value (the fast YES screen replaces the slow
# per-cell bisection over the top-20; the bisection is kept only for the five PI cells).
# One lab python of this attempt at a time; wait for a slot; never exceed 16.
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

# --- essential: task 2's two columns over the top-20
Run 'yesscreen_top' @('-u','yesscreen158.py','--jobs','../results/top158.jsonl','--r','0.10','--tt','10','--budget','1500')
Run 'no_top'        @('-u','no158.py','--jobs','../results/top158.jsonl','--radii','0.10','--tt','10','--cap','240','--emit','1','--budget','2700')

# --- essential: the two A57 PI cells (Y0130, Y0147), both children
Run 'xover_y0130' @('-u','xover158.py','--jobs','../results/y0130_jobs.jsonl','--n','400000','--tilts','0,0.5,10','--out','../results/xover158_tt.jsonl','--budget','1500')
Run 'no_y0130'    @('-u','no158.py','--jobs','../results/y0130_jobs.jsonl','--radii','0.10','--tt','10','--cap','600','--emit','1','--budget','1500')

# --- the strong refutation, and the NO thresholds on the cells r = 0.10 did not kill
Run 'pair_named' @('-u','pair158.py','--jobs','../results/all_jobs.jsonl','--radii','0.10,0.01','--tt','10,0.5')
Run 'no_big'     @('-u','no158.py','--jobs','../results/named_jobs.jsonl','--radii','0.20','--tt','20','--cap','300','--emit','0','--budget','900')
Write-Output 'A158 run158c.ps1 finished'

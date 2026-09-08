# A158 -- the population-level YES screen: a random sample of the 1,238 selected cells, to say
# whether the YES child is refuted everywhere or only on the top-20.
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

Run 'sample_jobs'    @('-u','sample158.py','--n','120')
Run 'yesscreen_pop'  @('-u','yesscreen158.py','--jobs','../results/sample158.jsonl','--r','0.10','--tt','10','--out','../results/yesscreen_pop158.jsonl','--budget','1500')
Run 'summary'        @('-u','sum158.py')
Write-Output 'A158 run158d.ps1 finished'

# A158 -- run the FROZEN verifiers on the emitted NO-child certificates, one process at a time.
# verify_case.py is the arbiter (A136 checks its sha 521cb01f...); verify_param.py at the
# degenerate window [s0, s0] is the second, independent implementation (A135's run_param).
# A cap can only ABORT, never decide (A120's rule / A124's CAP-is-never-a-verdict).
$ErrorActionPreference = 'Continue'
$env:PYTHONDONTWRITEBYTECODE = '1'
$py    = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$root  = 'C:\Users\esumm\code\packing'
$case  = "$root\attempts\A57-shadow-trees\code\verify_case.py"
$param = "$root\attempts\A96-a57-parametric\code\verify_param.py"
$certs = "$root\attempts\A158-slot-split\certs"
$logs  = "$root\attempts\A158-slot-split\logs"

"verify_case.py  sha256 = " + (Get-FileHash $case  -Algorithm SHA256).Hash.ToLower()
"verify_param.py sha256 = " + (Get-FileHash $param -Algorithm SHA256).Hash.ToLower()
"expected verify_case (A136 a136lib.VERIFY_CASE_SHA) = 521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af"

foreach ($f in Get-ChildItem "$certs\no_*.json" | Where-Object { $_.Name -notlike '*.report.json' -and $_.Name -notlike '*.witnesses.json' }) {
  $b = $f.BaseName
  foreach ($v in @(@('case', $case, @($f.FullName, '--jobs', '1', '--depth', '56', '--max-witnesses', '64', '--report', '--quiet')),
                   @('param', $param, @($f.FullName, '--slo', '969271/250000', '--shi', '969271/250000', '--jobs', '1', '--depth', '56', '--report', '--quiet')))) {
    $tag = $v[0]; $script = $v[1]; $argv = @('-u', $script) + $v[2]
    # count BOTH absolute-path lab pythons and A158's own relative-path children ("*158.py*"),
    # and WAIT for a slot rather than skipping
    for ($w = 0; $w -lt 240; $w++) {
      $n = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
             Where-Object { $_.CommandLine -like '*code\packing\attempts*' -or $_.CommandLine -like '*158.py*' }).Count
      if ($n -lt 16) { break }
      Start-Sleep -Seconds 20
    }
    if ($n -ge 16) { Write-Output "[$b/$tag] SKIPPED: $n lab python processes"; continue }
    Write-Output "[$b/$tag] start (lab-python=$n)"
    $t0 = Get-Date
    $p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -PassThru `
          -RedirectStandardOutput "$logs\verify_${b}_$tag.log" -RedirectStandardError "$logs\verify_${b}_$tag.err"
    $p.ProcessorAffinity = 0xFFFF
    $p.PriorityClass = 'Normal'
    if (-not $p.WaitForExit(1500000)) { $p.Kill(); Write-Output "[$b/$tag] ABORT at the 1500 s wall (never a verdict)"; continue }
    $dt = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
    Write-Output ("[{0}/{1}] exit={2} in {3} s" -f $b, $tag, $p.ExitCode, $dt)
    Get-Content "$logs\verify_${b}_$tag.log" -Tail 6 | ForEach-Object { "    $_" }
  }
}
Write-Output 'A158 verify158.ps1 finished'

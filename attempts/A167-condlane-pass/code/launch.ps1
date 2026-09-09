# A167 launcher: one python worker at BelowNormal with affinity 0xFFFF, stdout+stderr to a log.
#   powershell -File launch.ps1 -Log ..\logs\x.log -Args "runcond167.py --nid c0_Y0169 ..."
param([Parameter(Mandatory=$true)][string]$Log,
      [Parameter(Mandatory=$true)][string]$PyArgs)
$env:PYTHONDONTWRITEBYTECODE = "1"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$p = Start-Process -FilePath "python" -ArgumentList ("-u " + $PyArgs) -WorkingDirectory $here `
     -PassThru -WindowStyle Hidden -RedirectStandardOutput $Log -RedirectStandardError ($Log + ".err")
Start-Sleep -Milliseconds 400
try { $p.PriorityClass = "BelowNormal" } catch { "priority set failed: $_" }
try { $p.ProcessorAffinity = [IntPtr]0xFFFF } catch { "affinity set failed: $_" }
"pid $($p.Id) priority $($p.PriorityClass) affinity $($p.ProcessorAffinity) log $Log"

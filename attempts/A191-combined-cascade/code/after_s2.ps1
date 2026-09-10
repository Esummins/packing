# A191 -- after the S2 shards exit: (A) the coarse S3 children of the S2 survivors (s3_191, one process);
# (B) the canary l1_153 S2 node at full cap, then the FROZEN v1 verifier over every v1 kill certificate, then the LP
# on A183's fine S3 records (a sample).  Two processes, gated as before.
$base = "C:\Users\esumm\code\packing\attempts\A191-combined-cascade"
Set-Location $base
$env:PYTHONDONTWRITEBYTECODE = '1'
$py = 'C:\Users\esumm\AppData\Local\Python\bin\python.exe'
$ids = (Get-Content logs/pids191.txt) -split ' ' | ForEach-Object { [int]$_ }
Wait-Process -Id $ids -ErrorAction SilentlyContinue
"S2 shards exited " + (Get-Date -Format HH:mm) | Out-File -Append -Encoding utf8 logs/after_s2.log
$pA = Start-Process -FilePath $py -ArgumentList '-u','code/s3_191.py','--cell','l1_104','--parents','auto','--per-parent','1','--max-nodes','24','--cap','240','--wfrac','0.2' -RedirectStandardOutput 'logs/s3coarse.log' -RedirectStandardError 'logs/s3coarse.err' -WindowStyle Hidden -PassThru
$cmdB = "& '$py' -u code/run191.py --cell l1_153 --step S2 --cap 300 --wfrac 0.25 *> logs/canary_s2.log; " +
        "`$certs = Get-ChildItem certs -Filter '*_v1.certify.json' | Where-Object { (Get-Content `$_.FullName -Raw) -match '\"result\": \"PASS\"' } | ForEach-Object { `$_.FullName -replace '\.certify\.json$', '.json' }; " +
        "& '$py' -u code/frozen191.py @certs *> logs/frozen191_all.log; " +
        "& '$py' -u code/run191.py --cell l1_104 --step S3 --max-nodes 10 --cap 240 --wfrac 0.2 *> logs/s3fine_lp.log"
$pB = Start-Process -FilePath 'powershell' -ArgumentList '-NoProfile','-Command',$cmdB -WindowStyle Hidden -PassThru
"launched A=$($pA.Id) B=$($pB.Id) " + (Get-Date -Format HH:mm) | Out-File -Append -Encoding utf8 logs/after_s2.log

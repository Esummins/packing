#!/bin/sh
CNT() { powershell.exe -NoProfile -Command '(Get-CimInstance Win32_Process -Filter "Name=''python.exe''" | Where-Object { $_.CommandLine -like "*code\packing*" } | Measure-Object).Count' | tr -d '\r'; }
while [ "$(CNT)" -gt 15 ]; do sleep 30; done
echo "launching shard 0/1 at $(date)"
cd /c/Users/esumm/code/packing/attempts/A161-chord-lane/code
PYTHONDONTWRITEBYTECODE=1 powershell.exe -NoProfile -Command "\$p = Start-Process -FilePath 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' -ArgumentList '-u','run161.py','--shard','0/1','--out','../results/t3.jsonl','--progress','../progress/t3.json','--cap_s','7000' -WorkingDirectory 'C:\Users\esumm\code\packing\attempts\A161-chord-lane\code' -RedirectStandardOutput '..\logs\t3.log' -RedirectStandardError '..\logs\t3.err' -PassThru; \$p.PriorityClass='BelowNormal'; \$p.ProcessorAffinity=0xFFFF; \$p.WaitForExit(7600000); 'exit ' + \$p.ExitCode"
echo "shard 0/1 finished at $(date)"

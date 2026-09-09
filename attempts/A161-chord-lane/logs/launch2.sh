#!/bin/sh
CNT() { powershell.exe -NoProfile -Command '(Get-CimInstance Win32_Process -Filter "Name=$([char]39)python.exe$([char]39)" | Where-Object { $_.CommandLine -like "*code\packing*" } | Measure-Object).Count' | tr -d '\r'; }
while [ "$(CNT)" -gt 15 ] 2>/dev/null; do sleep 30; done
echo "launching at $(date)"
PYTHONDONTWRITEBYTECODE=1 powershell.exe -NoProfile -Command "\$p = Start-Process -FilePath 'C:\Users\esumm\AppData\Local\Python\bin\python.exe' -ArgumentList '-u','run161.py','--shard','0/1','--out','../results/t3.jsonl','--progress','../progress/t3.json','--cap_s','6600','--pair_s','40','--maxopen','12000' -WorkingDirectory 'C:\Users\esumm\code\packing\attempts\A161-chord-lane\code' -RedirectStandardOutput '..\logs\t3b.log' -RedirectStandardError '..\logs\t3b.err' -PassThru; \$p.PriorityClass='BelowNormal'; \$p.ProcessorAffinity=0xFFFF; \$p.WaitForExit(7200000); 'exit ' + \$p.ExitCode"
echo "finished at $(date)"

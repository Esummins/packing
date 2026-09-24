@echo off
cd /d C:\Users\esumm\code\packing\attempts\A279-nest-residual\code
set PYTHONDONTWRITEBYTECODE=1
if exist ..\logs\STOP goto fin
python nest279.py --stage nest --restarts 24 --seeds 1,2,3,4 >> ..\logs\nest279.log 2>&1
if exist ..\logs\STOP goto fin
python nest279.py --stage nest --restarts 24 --seeds 1,2 --hv 0.5 >> ..\logs\nest279.log 2>&1
if exist ..\logs\STOP goto fin
python nest279.py --stage cell --restarts 8 --seeds 1,2 >> ..\logs\nest279.log 2>&1
:fin
echo DONE >> ..\logs\nest279.log
cd /d C:\Users\esumm\code\packing
git add attempts/A279-nest-residual/results/nest279.jsonl attempts/A279-nest-residual/logs/nest279.log
git commit -q -m "A279: nest279 rows (stage nest / cell) -- search finished at its own pace" -- attempts/A279-nest-residual/results/nest279.jsonl attempts/A279-nest-residual/logs/nest279.log

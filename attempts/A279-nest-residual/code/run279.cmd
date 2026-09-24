@echo off
cd /d C:\Users\esumm\code\packing\attempts\A279-nest-residual\code
set PYTHONDONTWRITEBYTECODE=1
python nest279.py --stage nest --restarts 24 --seeds 1,2,3,4 >> ..\logs\nest279.log 2>&1
python nest279.py --stage nest --restarts 24 --seeds 1,2 --hv 0.5 >> ..\logs\nest279.log 2>&1
python nest279.py --stage cell --restarts 8 --seeds 1,2 >> ..\logs\nest279.log 2>&1
echo DONE >> ..\logs\nest279.log

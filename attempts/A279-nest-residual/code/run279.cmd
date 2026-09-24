@echo off
cd /d C:\Users\esumm\code\packing\attempts\A279-nest-residual\code
set PYTHONDONTWRITEBYTECODE=1
python nest279.py --restarts 6 --seeds 1,2,3 >> ..\logs\nest279.log 2>&1
python nest279.py --restarts 6 --seeds 1,2 --hv 0.4 >> ..\logs\nest279.log 2>&1
python nest279.py --restarts 6 --seeds 1,2 --hv 0.7 >> ..\logs\nest279.log 2>&1
echo DONE >> ..\logs\nest279.log

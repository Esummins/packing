#!/bin/bash
# A262 chain3 launcher: waits for chain2 (adv -> span -> search) to end, then runs chain3 (float2 -> pair3 -> verify ->
# jam [8 h budget] -> verify -> held -> sector) and commits results / certs indices.  ONE python at a time.  logs/STOP stops.
cd "$(dirname "$0")" || exit 1
# chain2 has ended when its last stage (search262) has started and no chain2 python is alive any more
alive() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -match 'adv262|span262|search262' } | Measure-Object | Select-Object -ExpandProperty Count" 2>/dev/null | tr -d ' '; }
while [ ! -e ../results/search262.jsonl ] || [ "$(alive)" != "0" ]; do
  [ -e ../logs/STOP ] && exit 0
  sleep 60
done
sleep 30
bash run262.sh chain3
echo "CHAIN3 END $(date)"
cd ../../.. || exit 1
git add attempts/A262-no-jam/results/*.json attempts/A262-no-jam/results/*.jsonl attempts/A262-no-jam/certs/*index.jsonl > /dev/null 2>&1
git commit -q -m "A262: chain3 results (float2, pair3 + jam trees, verifier, held, sector) at CHAIN3 END

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- attempts/A262-no-jam/results attempts/A262-no-jam/certs/pair3262_index.jsonl attempts/A262-no-jam/certs/jam262_index.jsonl

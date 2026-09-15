#!/bin/bash
# A229 -- the LIVE verification of notes/parallel229.md on a CLOSED page, in ISOLATED certificate directories, with
# at most ONE python of its own running at any moment (the pass-6 workers p6a/p6b/p6c are never touched: nothing here
# writes attempts/A211-coarse-tree/{certs,results} or docs/residue_map).
#
#   bash attempts/A229-start-parallel/code/verify229.sh [NID] [PAD] [WALL0] [WALL]
#
#   phase 0  the SHARED PRIOR STATE: the page run on a SHORT wall in an empty cert dir -> certs/verify/base
#   phase W  the WHOLE page from that state, one process, all start nodes      -> certs/verify/whole
#   phase 1..3  the SAME state, three `--start` SHARDS, one per third of the start nodes, each in its own dir
#   phase M  the three shard certificates + the base certificate in one dir    -> certs/verify/merge
#   phase C  test_inherit_multi229.py --compare whole merge: identical DEAD path set, identical next START nodes
#
# Resumable: each phase is skipped when its stamp file exists.  rm -rf attempts/A229-start-parallel/certs/verify to redo.
cd "$(dirname "$0")/../../.." || exit 1
A229=attempts/A229-start-parallel; A211=attempts/A211-coarse-tree
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
NID=${1:-k5_16_interior_Y0500}; PAD=${2:-g1}; WALL0=${3:-600}; WALL=${4:-3000}
V=$A229/certs/verify; RES=$A229/results/verify229.jsonl; LOG=$A229/logs/verify229.log
mkdir -p "$V" "$A229/logs" "$A229/results"
say() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a $LOG; }
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
gate() { while [ "$(labcount)" -ge 10 ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done; }

# $1 stamp  $2 cert dir  $3.. extra run211 args
phase() {
  local ST=$1 D=$2; shift 2
  if [ -f "$V/$ST.done" ]; then say "phase $ST: already done ($(cat "$V/$ST.done"))"; return 0; fi
  mkdir -p "$D"; gate
  local T0; T0=$(date +%s)
  say "phase $ST: run211 $NID --pads $PAD $* (cert dir $D, lab $(labcount), free $(freemb) MB)"
  A229_CERT_DIR=$(cd "$D" && pwd -W 2>/dev/null || cd "$D" && pwd) \
    python $A211/code/run211.py page "$NID" --pads "$PAD" --cert-dir "$D" --results "$RES" --no-fig "$@" >> "$V/$ST.log" 2>&1
  local RC=$? SECS=$(( $(date +%s) - T0 ))
  echo "rc=$RC seconds=$SECS" > "$V/$ST.done"
  say "phase $ST: rc=$RC ${SECS}s   $(grep -o "== $NID: g1 [^|]*| pad0 [^(]*" "$V/$ST.log" | tail -1)"
  [ $RC -eq 0 ] || say "phase $ST: NON-ZERO EXIT -- the comparison below is not meaningful"
}

# ---- phase 0: the shared prior state (a short wall leaves several start nodes open) -------------------------------
phase base "$V/base" --wall "$WALL0"
BASECERT="$V/base/coarsetree211_$NID.json"
[ -f "$BASECERT" ] || { say "no base certificate $BASECERT -- stop"; exit 1; }

# ---- the start nodes of that state, longest-first ----------------------------------------------------------------
if [ ! -f "$V/starts.txt" ]; then
  gate
  A229_CERT_DIR=$(cd "$V/base" && pwd -W 2>/dev/null || cd "$V/base" && pwd) \
    python $A229/code/queue229.py "$NID" --pads "$PAD" --wall "$WALL" 2>>"$V/queue.log" \
    | grep -v '^#' | awk '{print $2}' | sed "s/^$PAD://" > "$V/starts.txt"
fi
N=$(grep -c . "$V/starts.txt"); say "the shared state has $N start node(s) at pad $PAD: $(tr '\n' ' ' < "$V/starts.txt")"
[ "$N" -ge 2 ] || { say "fewer than 2 start nodes: nothing to shard (raise WALL0 or pick another page) -- stop"; exit 1; }

# ---- phase W: the WHOLE page from the shared state ----------------------------------------------------------------
[ -f "$V/whole/coarsetree211_$NID.json" ] || { mkdir -p "$V/whole"; cp "$BASECERT" "$V/whole/"; }
phase whole "$V/whole" --wall "$WALL"

# ---- phases 1..3: the same state as three --start shards, one python at a time --------------------------------------
for K in 1 2 3; do
  SEL=$(awk -v k=$K -v n=3 'NR % n == (k % n) {printf "%s%s", sep, $0; sep=","}' "$V/starts.txt")
  [ -z "$SEL" ] && { say "phase s$K: empty share -- skipped"; echo "rc=0 seconds=0 (empty share)" > "$V/s$K.done"; continue; }
  [ -f "$V/s$K/coarsetree211_$NID.json" ] || { mkdir -p "$V/s$K"; cp "$BASECERT" "$V/s$K/"; }
  say "phase s$K: share = $SEL"
  phase "s$K" "$V/s$K" --wall "$WALL" --start "$SEL" --cert-suffix "s$K"
done

# ---- phase M: the base certificate + the three shard certificates in ONE directory ---------------------------------
mkdir -p "$V/merge"; cp "$BASECERT" "$V/merge/"
for K in 1 2 3; do [ -f "$V/s$K/coarsetree211_${NID}__s$K.json" ] && cp "$V/s$K/coarsetree211_${NID}__s$K.json" "$V/merge/"; done
say "merge dir: $(ls "$V/merge" | tr '\n' ' ')"

# ---- phase C: whole vs merged shards --------------------------------------------------------------------------------
gate
python $A229/code/test_inherit_multi229.py --compare "$V/whole" "$V/merge" --nid "$NID" --pad "$PAD" 2>&1 | tee -a $LOG
RC=${PIPESTATUS[0]}
say "verify229: comparison rc=$RC"
python $A229/code/report229.py "$NID" "$PAD" > $A229/results/verify229.md 2>>$LOG
say "verify229: wrote $A229/results/verify229.md"
for i in 1 2 3 4 5 6; do
  git add -- $A229 2>/dev/null
  git commit -q -m "A229 verify: $NID $PAD whole vs 3 --start shards merged (rc=$RC)" -- $A229 2>/dev/null && break
  sleep $((5*i))
done
exit $RC

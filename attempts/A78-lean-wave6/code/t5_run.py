#!/usr/bin/env python3
"""A78 T5 runner: build the per-certificate Lean replay modules cheapest first,
ONE `lake build` invocation per certificate (that is also the isolation demo: a
re-run of one certificate re-evaluates nothing else).  lakeb.py serialises the
builds repo-wide and runs lake below normal priority.

Three times are recorded per certificate:
  lean_check_s  lake's own `Built <Check module> (Xs)` -- the native_decide cost;
  lean_data_s   ditto for the data module;
  lake_s        lakeb's `-> exit N in X s` (the lake invocation, no lock wait);
  lean_wall_s   this runner's wall clock (INCLUDES waiting for the shared lock
                when another A78 agent is building -- not a cost of the replay).

Cap: T5_CAP_S (default 2400 s = 40 min) per certificate.  A certificate that hits
it is recorded PENDING with its measured partial time; after TWO consecutive caps
every remaining (strictly larger) certificate is recorded PENDING unattempted.

Order file: results/t5_order.json (`python lean/gen_corpus_lean.py --manifest`)
Output:     results/t5_timings.jsonl, logs/t5_build.log
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
A78 = REPO / "attempts" / "A78-lean-wave6"
LAKEB = A78 / "code" / "lakeb.py"
LOCK = A78 / ".lake_lock"
ORDER = A78 / "results" / "t5_order.json"
OUT = A78 / "results" / "t5_timings.jsonl"
LOG = A78 / "logs" / "t5_build.log"
CAP_S = float(os.environ.get("T5_CAP_S", 2400))
BUILT_RE = re.compile(r"Built (PackingCertMathlib\.Corpus\.[\w.]+) \(([\d.]+)(m?s)\)")
LAKEB_RE = re.compile(r"lakeb: .*-> exit (-?\d+) in ([\d.]+) s")


def secs(v, unit):
    return float(v) / 1000.0 if unit == "ms" else float(v)


def already():
    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("status") == "OK":
                    done.add(r["module"])
    return done


def run_one(r, logf):
    mod = r["module"]
    cmd = [sys.executable, str(LAKEB), mod]
    t0 = time.time()
    p = subprocess.Popen(cmd, cwd=str(REPO), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                         errors="replace")
    try:
        out, _ = p.communicate(timeout=CAP_S)
        wall = time.time() - t0
        status = "OK" if p.returncode == 0 else "ERROR"
    except subprocess.TimeoutExpired:
        wall = time.time() - t0
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        try:
            out, _ = p.communicate(timeout=60)
        except Exception:
            out = ""
        try:
            LOCK.unlink()
        except OSError:
            pass
        status = "PENDING"
    out = out or ""
    logf.write("\n\n===== %s (%s, wall %.1f s) =====\n%s" % (mod, status, wall, out))
    logf.flush()
    mods = {m: secs(v, u) for m, v, u in BUILT_RE.findall(out)}
    lk = LAKEB_RE.search(out)
    d = dict(r)
    d.update(status=status, lean_wall_s=round(wall, 1),
             lake_s=float(lk.group(2)) if lk else None,
             lean_check_s=mods.get(mod),
             lean_data_s=mods.get(mod.replace(".Check_", ".Data_")),
             returncode=p.returncode, cached=(status == "OK" and mod not in mods),
             ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
    return d


def main():
    rows = json.loads(ORDER.read_text(encoding="utf-8"))
    rows.sort(key=lambda r: (r["boxes"], r["atoms"]))
    done = already()
    LOG.parent.mkdir(parents=True, exist_ok=True)
    consec, give_up = 0, False
    with LOG.open("a", encoding="utf-8") as logf, OUT.open("a", encoding="utf-8") as outf:
        for i, r in enumerate(rows, 1):
            if r["module"] in done:
                print("skip (done) %s" % r["name"], flush=True)
                continue
            if give_up:
                d = dict(r, status="PENDING", lean_wall_s=0.0, cached=False,
                         note="not attempted: two consecutive caps at %.0f s and this "
                              "certificate is strictly larger" % CAP_S,
                         ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
                outf.write(json.dumps(d) + "\n"); outf.flush()
                print("PENDING (skipped) %-24s boxes=%d" % (r["name"], r["boxes"]), flush=True)
                continue
            print("[%2d/%d] %-24s boxes=%-9d ..." % (i, len(rows), r["name"], r["boxes"]),
                  flush=True)
            d = run_one(r, logf)
            outf.write(json.dumps(d) + "\n"); outf.flush()
            print("   -> %s check=%ss lake=%ss wall=%.0fs"
                  % (d["status"], d["lean_check_s"], d["lake_s"], d["lean_wall_s"]), flush=True)
            if d["status"] == "ERROR":
                print("ERROR on %s -- stopping" % r["name"], flush=True)
                return 1
            consec = consec + 1 if d["status"] == "PENDING" else 0
            if consec >= 2:
                give_up = True
                print("two consecutive caps -- remaining certificates recorded PENDING",
                      flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

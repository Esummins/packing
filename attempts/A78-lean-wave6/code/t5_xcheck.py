#!/usr/bin/env python3
"""A78 T5 deliverable (e): re-run the frozen Python verifier with the float
pre-pass DISABLED on the cheapest and the most expensive certificates of the
corpora -- decision-neutrality evidence next to the Lean timings (as A70/A75 did).

Single job, BELOW-NORMAL priority (the machine is shared).
Output: results/t5_xcheck.jsonl, logs/t5_xcheck.log
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
A78 = REPO / "attempts" / "A78-lean-wave6"
VERIFY = REPO / "attempts" / "A53-simple-strata" / "code" / "verify_case.py"
ORDER = A78 / "results" / "t5_order.json"
OUT = A78 / "results" / "t5_xcheck.jsonl"
LOG = A78 / "logs" / "t5_xcheck.log"
STAT = re.compile(r"boxes = (\d+).*?covered = (\d+).*?exempt = (\d+).*?split = (\d+)", re.S)


def main():
    names = sys.argv[1:]
    rows = {r["name"]: r for r in json.loads(ORDER.read_text(encoding="utf-8"))}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as logf, OUT.open("a", encoding="utf-8") as outf:
        for nm in names:
            r = rows[nm]
            cmd = [sys.executable, str(VERIFY), str(REPO / r["cert"]),
                   "--depth", str(r["depth"]), "--jobs", "1",
                   "--no-float-prepass", "--quiet"]
            t0 = time.time()
            flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
            p = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", creationflags=flags)
            wall = time.time() - t0
            out = (p.stdout or "") + (p.stderr or "")
            logf.write("\n\n===== %s (exit %d, %.1f s) =====\n%s" % (nm, p.returncode, wall, out))
            logf.flush()
            m = STAT.search(out)
            res = "PASS" if "\nPASS:" in out or out.startswith("PASS:") else (
                "FAIL" if "FAIL" in out else "?")
            rec = dict(name=nm, corpus=r["corpus"], cert=r["cert"], depth=r["depth"],
                       result=res, returncode=p.returncode,
                       boxes_nofloat=int(m.group(1)) if m else None,
                       covered_nofloat=int(m.group(2)) if m else None,
                       exempt_nofloat=int(m.group(3)) if m else None,
                       split_nofloat=int(m.group(4)) if m else None,
                       boxes_report=r["boxes"], time_s=round(wall, 1),
                       ts=time.strftime("%Y-%m-%dT%H:%M:%S"))
            outf.write(json.dumps(rec) + "\n"); outf.flush()
            print("%-24s %s boxes(no-float)=%s report=%s %.1f s"
                  % (nm, res, rec["boxes_nofloat"], r["boxes"], wall), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

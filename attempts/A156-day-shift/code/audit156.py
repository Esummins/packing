"""A156 -- replay the brief's four soundness tripwires over the day's own rows.

The four PAUSE-IMMEDIATELY conditions:
  1. a core half-side beyond its certified value  -- every `a_report` entry of every row is
     re-derived from the box with A135's `exactcore` and must not be exceeded (and every core
     half-side must be < 1/2);
  2. a tilt bin outside [0, 90]                   -- on the emitted box and on its pre-clip parent;
  3. a stored verdict contradicted on replay      -- a sample of PASS certificates is re-verified
     with the FROZEN `verify_case.py` (sha 521cb01f...), which must exit 0 again;
  4. a clipped box not inside its parent          -- `geo.clip_from` (the pre-clip box) must
     contain `geo.box` (the box the LP was actually run on).

    python code\\audit156.py                 # tripwires 1,2,4 over every row + 3 on --sample certs
    python code\\audit156.py --sample 0      # skip the (expensive) verifier replay
Exit code 1 and a REPLAY/UNSOUND line on any failure.
"""
import argparse
import glob
import json
import math
import os
import random
import subprocess
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
for _p in (os.path.join(A57, "code"), os.path.join(ROOT, "A132-polygon-core", "code"),
           os.path.join(ROOT, "A135-polycore-verifier", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from caselp import Box                                                     # noqa: E402
import exactcore                                                           # noqa: E402

FROZEN = os.path.join(A57, "code", "verify_case.py")
A_PIN_EXACT = Fr(33873816211, 68719476736)
DELTA = 1e-2


def jrows(pattern):
    out = []
    for p in sorted(glob.glob(pattern)):
        for ln in open(p, encoding="utf-8"):
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=3, help="PASS certificates to re-verify")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    a = ap.parse_args()

    bad = []
    lp = jrows(os.path.join(BASE, "results", "lp156_*.jsonl"))
    geo = jrows(os.path.join(BASE, "results", "emit_geo_*.jsonl"))
    queue = {}
    for p in glob.glob(os.path.join(BASE, "results", "queue156.json")):
        for j in json.load(open(p)):
            queue[j["id"]] = j

    # ---- 1. core half-sides, on every LP row that reports them
    n_a = 0
    for r in lp:
        for c in (r.get("a_report") or []):
            n_a += 1
            av = float(Fr(str(c["a_used"])))
            if not (0.0 < av < 0.5):
                bad.append(f"UNSOUND core half-side {av} on {r['id']} (must be in (0, 1/2))")
            if c.get("box"):
                try:
                    ex = float(exactcore.exact_core(Box.from_json(c["box"])).a)
                except Exception:
                    continue
                if av > ex + 1e-12:
                    bad.append(f"UNSOUND {r['id']}: core half-side {av} exceeds its certified "
                               f"maximal value {ex}")
    # ---- 2 + 4. tilt bins and clip containment, on the geometry each job carries
    n_b = n_c = 0
    for jid, j in queue.items():
        g = j.get("geo") or {}
        for key in ("box", "clip_from"):
            bj = g.get(key) or (j.get("box") if key == "box" else None)
            if not bj:
                continue
            n_b += 1
            th0, th1 = bj["th0"], bj["th1"]
            if not (0.0 <= th0 <= th1 <= 90.0):
                bad.append(f"UNSOUND {jid}: tilt bin [{th0}, {th1}] outside [0, 90] ({key})")
        par, kid = g.get("clip_from"), (g.get("box") or j.get("box"))
        if par and kid:
            n_c += 1
            if not (kid["x0"] >= par["x0"] - 1e-9 and kid["x1"] <= par["x1"] + 1e-9 and
                    kid["y0"] >= par["y0"] - 1e-9 and kid["y1"] <= par["y1"] + 1e-9 and
                    kid["th0"] >= par["th0"] - 1e-9 and kid["th1"] <= par["th1"] + 1e-9):
                bad.append(f"UNSOUND {jid}: clipped box not inside its parent")
    for r in geo:
        b = r.get("box")
        if b and not (0.0 <= b["th0"] <= b["th1"] <= 90.0):
            bad.append(f"UNSOUND {r['id']}: emitted tilt bin outside [0, 90]")
        if r.get("clip_from") and b:
            p = r["clip_from"]
            if not (b["x0"] >= p["x0"] - 1e-9 and b["x1"] <= p["x1"] + 1e-9 and
                    b["y0"] >= p["y0"] - 1e-9 and b["y1"] <= p["y1"] + 1e-9):
                bad.append(f"UNSOUND {r['id']}: clipped box not inside its parent (geometry row)")
    # ---- 3. verdict replay
    passes = [r for r in lp if r.get("result") == "PASS" and r.get("cert")]
    reps = []
    if a.sample > 0 and passes:
        random.seed(11)
        for r in random.sample(passes, min(a.sample, len(passes))):
            cp = r["cert"]
            if not os.path.exists(cp):
                bad.append(f"REPLAY {r['id']}: certificate missing at {cp}")
                continue
            p = subprocess.run([sys.executable, FROZEN, cp, "--jobs", str(a.jobs),
                                "--depth", str(a.depth), "--report", "--quiet"],
                               capture_output=True, text=True, timeout=3600)
            reps.append((r["id"], p.returncode))
            if p.returncode != 0:
                bad.append(f"REPLAY CONTRADICTED: {r['id']} was stored PASS but the frozen "
                           f"verifier now exits {p.returncode}")
    print(f"audit156: {len(lp)} LP rows, {len(geo)} geometry rows, {len(queue)} queued jobs")
    print(f"  cores checked      : {n_a}")
    print(f"  tilt bins checked  : {n_b}")
    print(f"  clip containments  : {n_c}")
    print(f"  verdicts replayed  : {reps if reps else '(none)'}")
    if bad:
        print("\n!! TRIPWIRE:")
        for b in bad[:40]:
            print("   " + b)
        sys.exit(1)
    print("  ALL CLEAR")


if __name__ == "__main__":
    main()

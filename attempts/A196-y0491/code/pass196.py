"""A196 step 6 -- the same pipeline over the other ALIVE k5_16 pages of docs/shadows/STATUS.md (a pass), one page at a
time (page196.py runs its stages as children under the 1,500 s wall; <= 3 own pythons in total).

    python pass196.py [--skip k5_16_interior_Y0491] [--only ID,ID] [--stages geo,rows,waste,lpa,lpb] [--cap 300]
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, HERE)
import prio196                                                   # noqa: E402


def alive_k5_16():
    out = []
    for ln in open(os.path.join(ROOT, "docs", "shadows", "STATUS.md"), encoding="utf-8"):
        m = re.match(r"\| \[ \] \[`(k5_16_interior_Y\d+)\.svg`\].*\*\*ALIVE\*\*", ln)
        if m:
            out.append(m.group(1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip", default="k5_16_interior_Y0491")
    ap.add_argument("--only", default="")
    ap.add_argument("--stages", default="geo,rows,waste,lpa,lpb")
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--deadline", type=float, default=600.0)
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    skip = set(a.skip.split(","))
    pages = [p for p in alive_k5_16() if p not in skip]
    if a.only:
        pages = [p for p in pages if p in set(a.only.split(","))]
    done = set()
    if not a.redo and os.path.exists(os.path.join(RES, "pages196.jsonl")):
        import json
        for ln in open(os.path.join(RES, "pages196.jsonl"), encoding="utf-8"):
            if ln.strip():
                done.add(json.loads(ln)["nid"])
    pages = [p for p in pages if p not in done]
    print("pass196: %d pages (%d done before)" % (len(pages), len(done)), flush=True)
    for nid in pages:
        if os.path.exists(os.path.join(HERE, "..", "PAUSE")):
            print("PAUSE sentinel: stopping", flush=True)
            break
        prio196.wait_mine(limit=2, max_wait=7200)
        cmd = [sys.executable, "-u", os.path.join(HERE, "page196.py"), nid, "--stages", a.stages, "--cap", str(a.cap), "--deadline", str(a.deadline)]
        p = subprocess.run(cmd, cwd=HERE, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, text=True)
        print((p.stdout or "").strip().splitlines()[-1] if p.stdout else "?", flush=True)


if __name__ == "__main__":
    main()

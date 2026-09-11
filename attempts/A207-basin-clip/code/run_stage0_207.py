"""A207 -- the stage-0 pass with the basin clip over every ALIVE a57v4 page (docs/shadows/STATUS.md) whose class has a certified
basin, at the g1 pad (and the window pad when the basins cover it).  One process; resumable (rows in results/s0basin207.jsonl).
    python run_stage0_207.py [--pads g1,window] [--cls k5_16] [--force]"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import stage0_207 as S                                         # noqa: E402
import clip207 as C                                            # noqa: E402
import poly204 as P                                            # noqa: E402
import run206 as R6                                            # noqa: E402


def alive_pages():
    out = []
    for line in open(os.path.join(ROOT, "docs", "shadows", "STATUS.md"), encoding="utf-8"):
        m = re.match(r"\| \[ \] \[`([^`]+)\.svg`\]\([^)]*\) \| `([^`]+)` \| `([^`]+)` \|.*\*\*ALIVE\*\*", line)
        if m and m.group(3) in ("k5_11", "k5_16"):
            out.append((m.group(2), m.group(3)))
    return out


def done():
    seen = set()
    if os.path.exists(S.RES):
        for l in open(S.RES, encoding="utf-8"):
            try:
                d = json.loads(l)
                seen.add((d["nid"], d["pad"]))
            except Exception:
                pass
    return seen


if __name__ == "__main__":
    R6.belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("--pads", default="g1")
    ap.add_argument("--cls", default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    seen = done()
    for nid, cls in alive_pages():
        if a.cls and cls != a.cls:
            continue
        for pad in a.pads.split(","):
            if (nid, pad) in seen and not a.force:
                print("   %s %s: cached" % (nid, pad), flush=True)
                continue
            if not C.load_basins(cls, pad, P.QP.PADS[pad]):
                print("   %s %s: no basin covers this pad's window" % (nid, pad), flush=True)
                continue
            try:
                S.run(nid, pad)
            except Exception as e:                                # noqa: BLE001
                import traceback
                traceback.print_exc()
                print("== %s %s: ERROR %r" % (nid, pad, e), flush=True)
